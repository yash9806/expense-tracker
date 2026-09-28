# Expense Tracker

A simple Python expense tracker built with the standard library.

Features:
- Add expenses
- View all expenses
- Filter by category and month
- Delete an expense
- View totals by category

## Run the app

```bash
python expense_tracker.py --help
```

### Add an expense

```bash
python expense_tracker.py add --date 2026-09-28 --category Food --amount 25.50 --description Lunch
```

### List expenses

```bash
python expense_tracker.py list
```

### Monthly summary

```bash
python expense_tracker.py summary --month 2026-09
```

### Delete an expense

```bash
python expense_tracker.py delete --index 1
```

The app stores data in `expenses.csv` in the project root.
