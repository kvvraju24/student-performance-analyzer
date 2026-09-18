# Student Performance Analyzer

A beginner-friendly Python project that analyzes student examination results from a CSV file, plus a bonus interactive HTML dashboard for exploring the same data in the browser.

## Objective

Read student marks, calculate performance values and grades, identify the highest and lowest performers, create basic graphs, and export the final results.

## Tools Used

- Python 3
- `csv` module
- Matplotlib

## Project Files

```text
student-performance-analyzer/
├── StudentsPerformance.csv
├── student_performance_analyzer.py
├── index.html                      # bonus interactive dashboard (see below)
├── requirements.txt
├── README.md
└── output/                         # created / refreshed after running the program
    ├── student_results.csv
    ├── class_summary.csv
    ├── subject_averages.png
    ├── grade_distribution.png
    └── top_10_students.png
```

## How to Run

1. Clone the repository and move into it:

   ```bash
   git clone https://github.com/<your-username>/student-performance-analyzer.git
   cd student-performance-analyzer
   ```

2. Install the one dependency (Matplotlib):

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Run the analyzer:

   ```bash
   python3 student_performance_analyzer.py
   ```

The script always looks for `StudentsPerformance.csv` next to itself, so it works from any folder you clone it into.

## Features

- Reads math, reading, and writing scores from `StudentsPerformance.csv`
- Calculates total, average, percentage, and grade for every student
- Shows class and subject averages
- Finds the top 5 and bottom 5 students
- Exports calculated results to CSV files
- Creates three Matplotlib bar charts

## Output Files

After running the program, these files are created (or refreshed) inside `output/`:

| File | Description |
| --- | --- |
| `student_results.csv` | Original data with total, average, percentage, and grade |
| `class_summary.csv` | Overall class average and subject averages |
| `subject_averages.png` | Comparison of average marks by subject |
| `grade_distribution.png` | Number of students in each grade |
| `top_10_students.png` | Top 10 students by percentage |

The `output/` folder is committed with sample results already in it, so anyone browsing the repo can see the charts immediately without running anything.

## Grade Scale

| Percentage | Grade |
| --- | --- |
| 90–100 | A |
| 80–89 | B |
| 70–79 | C |
| 60–69 | D |
| 50–59 | E |
| Below 50 | F |

## Bonus: Interactive Web Dashboard

`index.html` is a self-contained, dependency-free dashboard for exploring the same dataset in the browser — filter by gender, lunch type, test preparation, race/ethnicity, and parental education; see live metrics, per-group bar charts, a score distribution histogram, and a searchable, paginated student table.

Because it loads `StudentsPerformance.csv` with `fetch()`, browsers won't allow it to run from a plain double-clicked file (`file://` URLs block that for security). Serve it locally instead:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/index.html` in your browser. Keep `index.html` and `StudentsPerformance.csv` in the same folder.

## Note

The dataset does not contain student names. The program creates IDs such as `Student-001` and `Student-002` so each record can be identified.
