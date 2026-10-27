"""CSV validation and analysis, independent of reports and plotting."""

import csv
import math
import re
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
    seen_ids = set()
    with Path(input_file).open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        try:
            headers = reader.fieldnames or []
            missing = sorted(set(REQUIRED_COLUMNS) - set(headers))
            if missing:
                raise ValueError("Missing required columns: " + ", ".join(missing))
            if len(set(headers)) != len(headers):
                raise ValueError("CSV headers must be unique.")
            subjects = [column for column in headers if column.endswith(" score")]
            if len(subjects) > 12 or any(not re.fullmatch(r"[a-z][a-z ]{0,39} score", column) for column in subjects):
                raise ValueError("Use at most 12 subjects with lowercase ASCII names followed by ' score'.")
            reserved = {"student_id", "cohort", "gender", "race_ethnicity", "parent_education", "lunch", "test_preparation", "total", "average", "percentage", "grade", "scores"}
            if any(column.removesuffix(" score").replace(" ", "_") in reserved for column in subjects):
                raise ValueError("Subject name conflicts with a reserved output field.")
            for row in reader:
                line = reader.line_num
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"CSV line {line}: column count does not match the header.")
                for column in (*BACKGROUND_FIELDS, *subjects):
                    if not row[column].strip():
                        raise ValueError(f"CSV line {line}, column '{column}': value is required.")
                if "student_id" in row:
                    identifier = row["student_id"].strip()
                    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", identifier) or identifier in seen_ids:
                        raise ValueError(f"CSV line {line}, column 'student_id': use a unique 1–32 character code.")
                    row["student_id"] = identifier
                    seen_ids.add(identifier)
                if "cohort" in row and not re.fullmatch(r"[A-Za-z0-9 _-]{1,40}", row["cohort"].strip()):
                    raise ValueError(f"CSV line {line}, column 'cohort': invalid cohort label.")
                if "cohort" in row:
                    row["cohort"] = row["cohort"].strip()
                scores = []
                for column in subjects:
                    value = row[column].strip()
                    if not value.isascii() or not value.isdecimal() or len(value.lstrip("0")) > 3 or not 0 <= int(value[-3:] or "0") <= 100:
                        raise ValueError(
                            f"CSV line {line}, column '{column}': expected an integer from 0 to 100; got {value!r}."
                        )
                    scores.append(int(value[-3:] or "0"))
                total = sum(scores)
                average = total / len(subjects)
                students.append({
                    "student_id": row.get("student_id", f"Student-{len(students) + 1:03d}"),
                    "cohort": row.get("cohort", "Unspecified"),
                    "scores": {column.removesuffix(" score").title(): value for column, value in zip(subjects, scores)},
                    **{target: row[source].strip() for source, target in BACKGROUND_FIELDS.items()},
                    **{column.removesuffix(" score").replace(" ", "_"): value for column, value in zip(subjects, scores)},
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
            for label, key in ((name, name.lower().replace(" ", "_")) for name in students[0].get("scores", {"Math": 0, "Reading": 0, "Writing": 0}))
        },
        "ranked": sorted(students, key=lambda s: s["average"], reverse=True),
    }
