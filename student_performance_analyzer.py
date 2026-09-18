import csv
from pathlib import Path

import matplotlib

# Save graphs directly as PNG files. This also lets the program work on systems
# without a graphical desktop session.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_FOLDER = Path(__file__).parent
INPUT_FILE = PROJECT_FOLDER / "StudentsPerformance.csv"
OUTPUT_FOLDER = PROJECT_FOLDER / "output"

SUBJECTS = ("math score", "reading score", "writing score")


def calculate_grade(percentage):
    """Return a letter grade from a percentage."""
    if percentage >= 90:
        return "A"
    if percentage >= 80:
        return "B"
    if percentage >= 70:
        return "C"
    if percentage >= 60:
        return "D"
    if percentage >= 50:
        return "E"
    return "F"


def read_students():
    """Read the CSV and add calculated fields to every student record."""
    students = []

    with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for student_number, row in enumerate(reader, start=1):
            math = int(row["math score"])
            reading = int(row["reading score"])
            writing = int(row["writing score"])

            total = math + reading + writing
            average = total / len(SUBJECTS)
            # Each subject is scored out of 100, so the average is also the percentage.
            percentage = average

            students.append(
                {
                    "student_id": f"Student-{student_number:03d}",
                    "gender": row["gender"],
                    "race_ethnicity": row["race/ethnicity"],
                    "parent_education": row["parental level of education"],
                    "lunch": row["lunch"],
                    "test_preparation": row["test preparation course"],
                    "math": math,
                    "reading": reading,
                    "writing": writing,
                    "total": total,
                    "average": average,
                    "percentage": percentage,
                    "grade": calculate_grade(percentage),
                }
            )

    return students


def print_summary(students):
    """Print the main analysis in the terminal."""
    subject_averages = {
        "Math": sum(s["math"] for s in students) / len(students),
        "Reading": sum(s["reading"] for s in students) / len(students),
        "Writing": sum(s["writing"] for s in students) / len(students),
    }
    class_average = sum(s["average"] for s in students) / len(students)
    ranked = sorted(students, key=lambda student: student["average"], reverse=True)

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
    for position, student in enumerate(reversed(ranked[-5:]), start=1):
        print(
            f"  {position}. {student['student_id']} — "
            f"{student['percentage']:.2f}% ({student['grade']})"
        )

    return subject_averages, ranked


def export_results(students, subject_averages):
    """Save calculated student results and a small class summary as CSV files."""
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    results_file = OUTPUT_FOLDER / "student_results.csv"
    columns = [
        "student_id", "gender", "race_ethnicity", "parent_education", "lunch",
        "test_preparation", "math", "reading", "writing", "total", "average",
        "percentage", "grade",
    ]
    with results_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for student in students:
            # Keep numbers in the export easy to read.
            row = student.copy()
            row["average"] = f"{student['average']:.2f}"
            row["percentage"] = f"{student['percentage']:.2f}"
            writer.writerow(row)

    summary_file = OUTPUT_FOLDER / "class_summary.csv"
    with summary_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["measure", "value"])
        writer.writerow(["students analyzed", len(students)])
        writer.writerow(["overall class average", f"{sum(s['average'] for s in students) / len(students):.2f}"])
        for subject, average in subject_averages.items():
            writer.writerow([f"{subject} average", f"{average:.2f}"])

    print(f"\nExported: {results_file.name} and {summary_file.name}")


def make_graphs(students, subject_averages, ranked):
    """Create three simple Matplotlib charts and save them as PNG images."""
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
    plt.savefig(OUTPUT_FOLDER / "subject_averages.png", dpi=160)
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
    plt.savefig(OUTPUT_FOLDER / "grade_distribution.png", dpi=160)
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
    plt.savefig(OUTPUT_FOLDER / "top_10_students.png", dpi=160)
    plt.close()

    print("Created graphs: subject_averages.png, grade_distribution.png, top_10_students.png")


def main():
    if not INPUT_FILE.exists():
        print(f"Error: Cannot find {INPUT_FILE.name} in {PROJECT_FOLDER}")
        return

    students = read_students()
    if not students:
        print("Error: The CSV file contains no student records.")
        return

    subject_averages, ranked = print_summary(students)
    export_results(students, subject_averages)
    make_graphs(students, subject_averages, ranked)
    print(f"All project files are in: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()
