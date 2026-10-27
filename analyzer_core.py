"""CSV validation and analysis, independent of reports and plotting."""

import csv
import math
from pathlib import Path

SUBJECTS = ("math score", "reading score", "writing score")
BACKGROUND_FIELDS = {
    "gender": "gender",
    "race/ethnicity": "race_ethnicity",
    "parental level of education": "parent_education",
    "lunch": "lunch",
    "test preparation course": "test_preparation",
}
REQUIRED_COLUMNS = (*BACKGROUND_FIELDS, *SUBJECTS)


def calculate_grade(percentage):
    """Grade a finite, unrounded percentage between 0 and 100."""
    if not math.isfinite(percentage) or not 0 <= percentage <= 100:
        raise ValueError("Percentage must be a finite number between 0 and 100.")
    for minimum, grade in ((90, "A"), (80, "B"), (70, "C"), (60, "D"), (50, "E")):
        if percentage >= minimum:
            return grade
    return "F"


def read_students(input_file):
    """Load validated records, reporting CSV line numbers in input errors."""
    students = []
    with Path(input_file).open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        try:
            headers = reader.fieldnames or []
            missing = sorted(set(REQUIRED_COLUMNS) - set(headers))
            if missing:
                raise ValueError("Missing required columns: " + ", ".join(missing))
            if len(set(headers)) != len(headers):
                raise ValueError("CSV headers must be unique.")
            for row in reader:
                line = reader.line_num
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"CSV line {line}: column count does not match the header.")
                for column in REQUIRED_COLUMNS:
                    if not row[column].strip():
                        raise ValueError(f"CSV line {line}, column '{column}': value is required.")
                scores = []
                for column in SUBJECTS:
                    value = row[column].strip()
                    if not value.isascii() or not value.isdecimal() or not 0 <= int(value) <= 100:
                        raise ValueError(
                            f"CSV line {line}, column '{column}': expected an integer from 0 to 100; got {value!r}."
                        )
                    scores.append(int(value))
                total = sum(scores)
                average = total / len(SUBJECTS)
                students.append({
                    "student_id": f"Student-{len(students) + 1:03d}",
                    **{target: row[source].strip() for source, target in BACKGROUND_FIELDS.items()},
                    **dict(zip(("math", "reading", "writing"), scores)),
                    "total": total,
                    "average": average,
                    "percentage": average,
                    "grade": calculate_grade(average),
                })
        except csv.Error as error:
            raise ValueError(f"CSV line {reader.line_num}: {error}") from error
    if not students:
        raise ValueError("The CSV file contains no student records.")
    return students


def summarize_students(students):
    """Return metrics without printing or writing files; ties retain input order."""
    if not students:
        raise ValueError("Cannot summarize an empty dataset.")
    return {
        "count": len(students),
        "class_average": sum(s["average"] for s in students) / len(students),
        "subject_averages": {
            label: sum(s[key] for s in students) / len(students)
            for label, key in (("Math", "math"), ("Reading", "reading"), ("Writing", "writing"))
        },
        "ranked": sorted(students, key=lambda s: s["average"], reverse=True),
    }
