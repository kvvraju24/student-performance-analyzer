import argparse
import csv
import sys
from pathlib import Path

from analyzer_core import read_students, summarize_students

PROJECT_FOLDER = Path(__file__).parent
INPUT_FILE = PROJECT_FOLDER / "StudentsPerformance.csv"
OUTPUT_FOLDER = PROJECT_FOLDER / "output"


def print_summary(students):
    """Print the main analysis in the terminal."""
    summary = summarize_students(students)
    subject_averages = summary["subject_averages"]
    class_average = summary["class_average"]
    ranked = summary["ranked"]

    print("\n" + "=" * 58)
    print("             STUDENT PERFORMANCE ANALYZER")
    print("=" * 58)
    print(f"Students analyzed: {len(students)}")
    print(f"Overall class average: {class_average:.2f}%")
    print("\nSubject averages:")
    for subject, average in subject_averages.items():
        print(f"  {subject:<8}: {average:.2f}")

    print("\nTop 5 students (the dataset has no student names):")
    for position, student in enumerate(ranked[:5], start=1):
        print(
            f"  {position}. {student['student_id']} — "
            f"{student['percentage']:.2f}% ({student['grade']})"
        )

    print("\nBottom 5 students:")
    for position, student in enumerate(sorted(students, key=lambda student: student["average"])[:5], start=1):
        print(
            f"  {position}. {student['student_id']} — "
            f"{student['percentage']:.2f}% ({student['grade']})"
        )

    return subject_averages, ranked


def export_results(students, subject_averages, output_folder=OUTPUT_FOLDER):
    """Save calculated student results and a small class summary as CSV files."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    results_file = output_folder / "student_results.csv"
    subject_columns = [name.lower().replace(" ", "_") for name in students[0]["scores"]]
    columns = ["student_id", "cohort", "gender", "race_ethnicity", "parent_education", "lunch", "test_preparation", *subject_columns, "total", "average", "percentage", "grade"]
    with results_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for student in students:
            # Keep numbers in the export easy to read.
            row = {key: student[key] for key in columns}
            row["average"] = f"{student['average']:.2f}"
            row["percentage"] = f"{student['percentage']:.2f}"
            # Prevent spreadsheet formula execution if an input text field is untrusted.
            for key, value in row.items():
                if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                    row[key] = "'" + value
            writer.writerow(row)

    summary_file = output_folder / "class_summary.csv"
    with summary_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["measure", "value"])
        writer.writerow(["students analyzed", len(students)])
        writer.writerow(["overall class average", f"{sum(s['average'] for s in students) / len(students):.2f}"])
        for subject, average in subject_averages.items():
            writer.writerow([f"{subject} average", f"{average:.2f}"])

    print(f"\nExported: {results_file.name} and {summary_file.name}")


def make_graphs(students, subject_averages, ranked, output_folder=OUTPUT_FOLDER):
    """Create three simple Matplotlib charts and save them as PNG images."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    plt.style.use("ggplot")

    # Graph 1: compare average score in each subject.
    plt.figure(figsize=(7, 4.5))
    names = list(subject_averages.keys())
    values = list(subject_averages.values())
    bars = plt.bar(names, values, color=["#4C78A8", "#59A14F", "#F28E2B"])
    plt.ylim(0, 100)
    plt.title("Average Score by Subject")
    plt.ylabel("Average score (out of 100)")
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value:.1f}", ha="center")
    plt.tight_layout()
    plt.savefig(output_folder / "subject_averages.png", dpi=160)
    plt.close()

    # Graph 2: count how many students received each grade.
    grade_order = ["A", "B", "C", "D", "E", "F"]
    grade_counts = {grade: 0 for grade in grade_order}
    for student in students:
        grade_counts[student["grade"]] += 1
    plt.figure(figsize=(7, 4.5))
    bars = plt.bar(grade_order, grade_counts.values(), color="#7B61FF")
    plt.title("Grade Distribution")
    plt.xlabel("Grade")
    plt.ylabel("Number of students")
    for bar, count in zip(bars, grade_counts.values()):
        plt.text(bar.get_x() + bar.get_width() / 2, count + 4, str(count), ha="center")
    plt.tight_layout()
    plt.savefig(output_folder / "grade_distribution.png", dpi=160)
    plt.close()

    # Graph 3: compare the 10 highest overall averages.
    top_ten = ranked[:10]
    plt.figure(figsize=(9, 5))
    labels = [student["student_id"] for student in top_ten]
    scores = [student["percentage"] for student in top_ten]
    plt.bar(labels, scores, color="#2A9D8F")
    plt.ylim(0, 100)
    plt.title("Top 10 Students by Percentage")
    plt.xlabel("Student ID")
    plt.ylabel("Percentage")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(output_folder / "top_10_students.png", dpi=160)
    plt.close()

    print("Created graphs: subject_averages.png, grade_distribution.png, top_10_students.png")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate student scores and generate CSV reports and charts.")
    parser.add_argument("--input", type=Path, default=INPUT_FILE, help="Input CSV (default: bundled dataset)")
    parser.add_argument("--output", type=Path, default=OUTPUT_FOLDER, help="Output directory (existing reports are replaced)")
    args = parser.parse_args(argv)
    try:
        students = read_students(args.input)
        subject_averages, ranked = print_summary(students)
        export_results(students, subject_averages, args.output)
        make_graphs(students, subject_averages, ranked, args.output)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"All project files are in: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
