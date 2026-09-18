# Project 1 — Student Performance Analyzer

A beginner-friendly Python project that analyzes student examination results from a CSV file.

## Objective

Read student marks, calculate performance values and grades, identify the highest and lowest performers, create basic graphs, and export the final results.

## Tools Used

- Python 3
- `csv` module
- Matplotlib

## Project Files

```text
project 1/
├── StudentsPerformance.csv
├── student_performance_analyzer.py
├── requirements.txt
├── README.md
└── output/                         # Created after running the program
```

## How to Run

Open Terminal and enter:

```bash
cd "/Users/vishnu/Desktop/projects/project 1"
python3 student_performance_analyzer.py
```

Install the required package once:

```bash
python3 -m pip install -r requirements.txt
```

## Features

- Reads math, reading, and writing scores from `StudentsPerformance.csv`
- Calculates total, average, percentage, and grade for every student
- Shows class and subject averages
- Finds the top 5 and bottom 5 students
- Exports calculated results to CSV files
- Creates three Matplotlib bar charts

## Output Files

After running the program, these files are created inside `output/`:

| File | Description |
| --- | --- |
| `student_results.csv` | Original data with total, average, percentage, and grade |
| `class_summary.csv` | Overall class average and subject averages |
| `subject_averages.png` | Comparison of average marks by subject |
| `grade_distribution.png` | Number of students in each grade |
| `top_10_students.png` | Top 10 students by percentage |

## Grade Scale

| Percentage | Grade |
| --- | --- |
| 90–100 | A |
| 80–89 | B |
| 70–79 | C |
| 60–69 | D |
| 50–59 | E |
| Below 50 | F |

## Note

The dataset does not contain student names. The program creates IDs such as `Student-001` and `Student-002` so each record can be identified.
