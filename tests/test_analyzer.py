import contextlib
import csv
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analyzer_core import REQUIRED_COLUMNS, calculate_grade, read_students, summarize_students
from student_performance_analyzer import export_results

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/students.csv"


class AnalyzerTests(unittest.TestCase):
    def test_grade_boundaries(self):
        for score, expected in ((0, "F"), (49.999, "F"), (50, "E"), (59.999, "E"),
                                (60, "D"), (69.999, "D"), (70, "C"), (79.999, "C"),
                                (80, "B"), (89.999, "B"), (90, "A"), (100, "A")):
            with self.subTest(score=score):
                self.assertEqual(calculate_grade(score), expected)

    def test_invalid_percentages(self):
        for score in (-1, 101, float("nan"), float("inf")):
            with self.subTest(score=score), self.assertRaises(ValueError):
                calculate_grade(score)

    def test_fixture_calculations(self):
        students = read_students(FIXTURE)
        self.assertEqual([s["total"] for s in students], [270, 150])
        self.assertEqual([s["average"] for s in students], [90, 50])
        self.assertEqual([s["grade"] for s in students], ["A", "E"])
        summary = summarize_students(students)
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["class_average"], 70)
        self.assertEqual(summary["subject_averages"], {"Math": 70, "Reading": 70, "Writing": 70})
        self.assertEqual([s["student_id"] for s in summary["ranked"]], ["Student-001", "Student-002"])

    def test_ties_preserve_input_order(self):
        students = [{"student_id": i, "average": 70, "math": 70, "reading": 70, "writing": 70} for i in (2, 1)]
        self.assertEqual([s["student_id"] for s in summarize_students(students)["ranked"]], [2, 1])

    def test_dataset_regression(self):
        summary = summarize_students(read_students(ROOT / "StudentsPerformance.csv"))
        self.assertEqual(summary["count"], 1000)
        self.assertAlmostEqual(summary["class_average"], 67.7706666667)
        for subject, value in {"Math": 66.089, "Reading": 69.169, "Writing": 68.054}.items():
            self.assertAlmostEqual(summary["subject_averages"][subject], value)

    def test_invalid_scores_identify_line_and_column(self):
        with FIXTURE.open(newline="") as file:
            row = next(csv.DictReader(file))
        for value in ("", " ", "abc", "70.5", "-1", "101", "NaN", "Infinity"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "bad.csv"
                with path.open("w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=REQUIRED_COLUMNS)
                    writer.writeheader()
                    writer.writerow({**row, "math score": value})
                with self.assertRaisesRegex(ValueError, "CSV line 2, column 'math score'"):
                    read_students(path)

    def test_empty_missing_duplicate_and_malformed_input(self):
        headers = FIXTURE.read_text().splitlines()[0]
        cases = (("", "Missing required columns"), (headers + "\n", "no student records"),
                 (headers.replace("math score", "other") + "\n", "Missing required columns"),
                 (headers + ",math score\n", "unique"),
                 (headers + ",total score\n", "reserved"),
                 (headers + '\n"unterminated', "CSV line"),
                 (headers + "\nfemale,group A\n", "column count"))
        for text, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "bad.csv"
                path.write_text(text)
                with self.assertRaisesRegex(ValueError, message):
                    read_students(path)

    def test_bom_and_quoted_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "students.csv"
            path.write_text('\ufeff' + FIXTURE.read_text().replace("bachelor's degree", '"degree, with honors"'))
            self.assertEqual(read_students(path)[0]["parent_education"], "degree, with honors")

    def test_empty_summary(self):
        with self.assertRaisesRegex(ValueError, "empty dataset"):
            summarize_students([])

    def test_csv_exports(self):
        students = read_students(FIXTURE)
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            export_results(students, summarize_students(students)["subject_averages"], folder)
            with (Path(folder) / "student_results.csv").open(newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["percentage"], "90.00")
            with (Path(folder) / "class_summary.csv").open(newline="") as file:
                summary = dict(list(csv.reader(file))[1:])
            self.assertEqual(summary["overall class average"], "70.00")

    def test_cli_success_from_other_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "nested" / "reports"
            result = subprocess.run([sys.executable, str(ROOT / "student_performance_analyzer.py"),
                                     "--input", str(FIXTURE), "--output", str(output)],
                                    cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list(output.iterdir())), 5)
            for path in output.glob("*.png"):
                self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_cli_failure_creates_no_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.csv"
            path.write_text("wrong,headers\n1,2\n")
            output = Path(folder) / "reports"
            for source in (path, Path(folder) / "missing.csv"):
                result = subprocess.run([sys.executable, str(ROOT / "student_performance_analyzer.py"),
                                         "--input", str(source), "--output", str(output)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

class ExpandedDataTests(unittest.TestCase):
    def test_synthetic_dataset_shape_and_ranges(self):
        students = read_students(ROOT / 'data/synthetic_students.csv')
        self.assertEqual(len(students), 5000)
        self.assertEqual(len(students[0]['scores']), 8)
        self.assertEqual(len({s['student_id'] for s in students}), 5000)
        self.assertTrue(all(0 <= value <= 100 for s in students for value in s['scores'].values()))
        self.assertEqual(len(summarize_students(students)['subject_averages']), 8)
        self.assertAlmostEqual(students[0]['average'], sum(students[0]['scores'].values()) / 8)

    def test_csv_formula_text_is_neutralized(self):
        students = read_students(FIXTURE)
        students[0]['parent_education'] = '=HYPERLINK("https://example.com")'
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            export_results(students, summarize_students(students)['subject_averages'], folder)
            with (Path(folder) / 'student_results.csv').open(newline='') as file:
                self.assertTrue(next(csv.DictReader(file))['parent_education'].startswith("'="))
