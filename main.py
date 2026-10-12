"""Crop Cost and Profitability Analysis (beginner-friendly SQLite project)."""

import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "crop_profitability.db"
REPORT_DIR = BASE_DIR / "reports"


def connect_db():
    """Open the project database and make rows accessible by column name."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    """Create the table and add sample records the first time the app runs."""
    with connect_db() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS crop_records (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   crop_name TEXT NOT NULL,
                   area_acres REAL NOT NULL CHECK (area_acres >= 0),
                   production_cost REAL NOT NULL CHECK (production_cost >= 0),
                   yield_quintals REAL NOT NULL CHECK (yield_quintals >= 0),
                   selling_price REAL NOT NULL CHECK (selling_price >= 0)
               )"""
        )
        count = connection.execute("SELECT COUNT(*) FROM crop_records").fetchone()[0]
        if count == 0:
            # The first row reproduces the sample shown in the project specification.
            sample_records = [
                ("Rice", 5, 48000, 22, 2600),
                ("Wheat", 4, 36000, 18, 2400),
                ("Maize", 3, 27000, 14, 2200),
                ("Cotton", 5, 52000, 16, 3900),
                ("Pulses", 2, 15000, 8, 3000),
            ]
            connection.executemany(
                """INSERT INTO crop_records
                   (crop_name, area_acres, production_cost, yield_quintals, selling_price)
                   VALUES (?, ?, ?, ?, ?)""",
                sample_records,
            )


def read_number(prompt, minimum=0):
    """Read a valid number; reject text, negatives, NaN, and infinity."""
    while True:
        raw_value = input(prompt).strip().replace(",", "").replace("₹", "")
        try:
            value = float(raw_value)
            if value != value or value in (float("inf"), float("-inf")):
                raise ValueError
            if value < minimum:
                print(f"Please enter a number that is at least {minimum}.")
                continue
            return value
        except ValueError:
            print("Invalid number. Enter a numeric value such as 5 or 2500.50.")


def calculate_finances(record):
    """Return a dictionary containing calculated values for one record."""
    total_cost = float(record["production_cost"])
    revenue = float(record["yield_quintals"]) * float(record["selling_price"])
    profit = revenue - total_cost
    if profit > 0:
        status = "Profitable"
    elif profit == 0:
        status = "Break-even"
    else:
        status = "Not profitable"
    return {"total_cost": total_cost, "revenue": revenue, "profit": profit, "status": status}


def money(amount):
    """Format an amount in Indian rupees."""
    return f"₹{amount:,.2f}" if amount % 1 else f"₹{amount:,.0f}"


def add_record():
    print("\nEnter crop details (use non-negative numbers).")
    crop_name = input("Crop name: ").strip()
    while not crop_name:
        print("Crop name cannot be blank.")
        crop_name = input("Crop name: ").strip()
    area = read_number("Area in acres: ")
    cost = read_number("Production cost in rupees: ")
    crop_yield = read_number("Yield in quintals: ")
    price = read_number("Selling price per quintal in rupees: ")
    with connect_db() as connection:
        connection.execute(
            """INSERT INTO crop_records
               (crop_name, area_acres, production_cost, yield_quintals, selling_price)
               VALUES (?, ?, ?, ?, ?)""",
            (crop_name, area, cost, crop_yield, price),
        )
    result = calculate_finances({
        "production_cost": cost, "yield_quintals": crop_yield, "selling_price": price
    })
    print_result(crop_name, result)


def print_result(crop_name, result):
    print(f"\n{crop_name} — Total Cost: {money(result['total_cost'])}")
    print(f"Revenue: {money(result['revenue'])}")
    print(f"Profit: {money(result['profit'])}")
    print(f"Profitability: {result['status']}")


def list_records():
    with connect_db() as connection:
        records = connection.execute("SELECT * FROM crop_records ORDER BY id").fetchall()
    if not records:
        print("No crop records have been saved yet.")
        return
    print("\nSaved crop records")
    print("ID  Crop       Area (acres)  Cost          Yield (q)  Price/q       Profit")
    print("-" * 83)
    for record in records:
        result = calculate_finances(record)
        print(
            f"{record['id']:<3} {record['crop_name']:<10} "
            f"{record['area_acres']:>12.2f}  {money(result['total_cost']):>12}  "
            f"{record['yield_quintals']:>9.2f}  {money(record['selling_price']):>12}  "
            f"{money(result['profit']):>12}"
        )


def crop_wise_summary():
    """Use SQL aggregation to combine all records with the same crop name."""
    query = """SELECT crop_name,
                      COUNT(*) AS record_count,
                      SUM(area_acres) AS total_area,
                      SUM(production_cost) AS total_cost,
                      SUM(yield_quintals) AS total_yield,
                      SUM(yield_quintals * selling_price) AS total_revenue
               FROM crop_records
               GROUP BY crop_name COLLATE NOCASE
               ORDER BY crop_name COLLATE NOCASE"""
    with connect_db() as connection:
        rows = connection.execute(query).fetchall()
    summaries = []
    for row in rows:
        # Lists and dictionaries make the summaries easy for beginners to compare.
        item = dict(row)
        item["profit"] = item["total_revenue"] - item["total_cost"]
        item["status"] = (
            "Profitable" if item["profit"] > 0 else
            "Break-even" if item["profit"] == 0 else "Not profitable"
        )
        summaries.append(item)
    return summaries


def build_report():
    summaries = crop_wise_summary()
    if not summaries:
        return "No crop records are available for analysis."

    total_cost = sum(item["total_cost"] for item in summaries)
    total_revenue = sum(item["total_revenue"] for item in summaries)
    total_profit = total_revenue - total_cost
    high_profit = max(summaries, key=lambda item: item["profit"])
    low_profit = min(summaries, key=lambda item: item["profit"])
    high_cost = max(summaries, key=lambda item: item["total_cost"])
    low_cost = min(summaries, key=lambda item: item["total_cost"])
    categories = {
        "Profitable": [item["crop_name"] for item in summaries if item["status"] == "Profitable"],
        "Break-even": [item["crop_name"] for item in summaries if item["status"] == "Break-even"],
        "Not profitable": [item["crop_name"] for item in summaries if item["status"] == "Not profitable"],
    }

    lines = [
        "CROP COST AND PROFITABILITY ANALYSIS",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 72,
        "Crop-wise summary (same crop names are combined):",
        f"{'Crop':<14}{'Records':>8}{'Area (acres)':>14}{'Cost':>14}{'Revenue':>14}{'Profit':>14}",
        "-" * 78,
    ]
    for item in summaries:
        lines.append(
            f"{item['crop_name']:<14}{item['record_count']:>8}{item['total_area']:>14.2f}"
            f"{money(item['total_cost']):>14}{money(item['total_revenue']):>14}"
            f"{money(item['profit']):>14}"
        )
    overall_status = "Profitable" if total_profit > 0 else "Break-even" if total_profit == 0 else "Not profitable"
    lines.extend([
        "-" * 78,
        f"Overall total cost: {money(total_cost)}",
        f"Overall revenue:   {money(total_revenue)}",
        f"Overall profit:    {money(total_profit)} ({overall_status})",
        "",
        "Analysis and interpretation:",
        f"Highest-profit crop: {high_profit['crop_name']} ({money(high_profit['profit'])})",
        f"Lowest-profit crop:  {low_profit['crop_name']} ({money(low_profit['profit'])})",
        f"Highest-cost crop:   {high_cost['crop_name']} ({money(high_cost['total_cost'])})",
        f"Lowest-cost crop:    {low_cost['crop_name']} ({money(low_cost['total_cost'])})",
    ])
    for label, crop_names in categories.items():
        lines.append(f"{label} crops: {', '.join(crop_names) if crop_names else 'None'}")
    lines.extend([
        "",
        "Formula: Revenue = yield (quintals) × selling price per quintal.",
        "Profit = revenue − production cost.",
    ])
    return "\n".join(lines)


def show_and_save_report():
    report = build_report()
    print("\n" + report)
    if report.startswith("No crop records"):
        return
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / f"crop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path.write_text(report + "\n", encoding="utf-8")
    print(f"\nReport saved to: {report_path}")


def main():
    create_table()
    print("Crop Cost and Profitability Analysis")
    print(f"Database: {DB_PATH}")
    while True:
        print("\n1. Add a crop record")
        print("2. View saved records")
        print("3. Analyze crops and save a text report")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            add_record()
        elif choice == "2":
            list_records()
        elif choice == "3":
            show_and_save_report()
        elif choice == "4":
            print("Goodbye. Your records are saved in the SQLite database.")
            break
        else:
            print("Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
