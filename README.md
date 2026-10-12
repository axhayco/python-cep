# Crop Cost and Profitability Analysis

A beginner-friendly, manual Python + DBMS course-end project. It uses Python functions, lists and dictionaries together with SQLite (a lightweight relational database included with Python). No third-party packages are needed.

## Requirements

- Python 3.8 or newer
- Windows, macOS, or Linux

## Run the application

1. Download or copy this project folder to your computer.
2. Open a terminal (Command Prompt or PowerShell on Windows) in this folder.
3. Run:

   ```text
   python main.py
   ```

   If your computer uses `python3` for Python 3, run `python3 main.py` instead.
4. Choose an option from the menu. Select **3** to view the crop-wise analysis and save a text report.

On its first run, the program creates `crop_profitability.db` and adds sample records. The first sample reproduces the supplied example. Later runs reuse the same database, so records remain saved. The report is written into the `reports` folder.

## Sample input and calculation

The supplied example is preloaded as a record:

```text
Crop: Rice
Area: 5 acres
Production Cost: ₹48,000
Yield: 22 quintals
Selling Price: ₹2,600 per quintal
```

```text
Total Cost: ₹48,000
Revenue: ₹57,200       (22 × ₹2,600)
Profit: ₹9,200         (₹57,200 − ₹48,000)
Profitability: Profitable
```

Other sample crops are included so the crop comparisons have useful results on the first run. Add more records through menu option **1**. Numerical inputs must be non-negative; text, negative values, and blank crop names are rejected.

## What the project demonstrates

- **Data entry and validation:** crop name, area in acres, production cost, yield in quintals, and selling price per quintal.
- **Functions:** separate functions for database setup, validation, calculations, summaries, and report generation.
- **Lists and dictionaries:** SQL results are collected into a list of dictionaries for comparisons and profitability categories.
- **DBMS:** `crop_records` is stored in a local SQLite database using parameterized SQL statements.
- **SQL aggregation:** records are grouped by crop name using `GROUP BY`; costs, area, yield, and revenue are combined with `SUM`.
- **Analysis:** identifies the highest- and lowest-profit crops, highest- and lowest-cost crops, and profitable, break-even, and not-profitable categories.
- **File handling:** a dated plain-text report is created in `reports/` each time option **3** is selected.

## Reset the sample database

To start fresh, close the program and delete `crop_profitability.db`. The next run recreates it with the sample records. Existing text reports in `reports/` are separate and can be kept or removed.
