#!/usr/bin/env python3
"""Simple command-line expense tracker."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


DATA_FILE = Path(__file__).with_name("expenses.csv")


@dataclass
class Expense:
    date: str
    category: str
    amount: float
    description: str

    @classmethod
    def from_row(cls, row: dict) -> "Expense":
        return cls(
            date=row["date"],
            category=row["category"],
            amount=float(row["amount"]),
            description=row["description"],
        )

    def to_row(self) -> dict:
        return {
            "date": self.date,
            "category": self.category,
            "amount": f"{self.amount:.2f}",
            "description": self.description,
        }


class ExpenseTracker:
    def __init__(self, file_path: Path = DATA_FILE):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with self.file_path.open("w", newline="") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=["date", "category", "amount", "description"],
                )
                writer.writeheader()

    def _read_expenses(self) -> List[Expense]:
        expenses: List[Expense] = []
        if self.file_path.stat().st_size == 0:
            return expenses

        with self.file_path.open("r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row:
                    continue
                expenses.append(Expense.from_row(row))
        return expenses

    def add_expense(self, date: str, category: str, amount: float, description: str) -> None:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        expense = Expense(date=date, category=category, amount=amount, description=description)
        with self.file_path.open("a", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["date", "category", "amount", "description"],
            )
            writer.writerow(expense.to_row())

        print(f"Added expense: {expense.date} | {expense.category} | ${expense.amount:.2f} | {expense.description}")

    def list_expenses(self, category: str | None = None, month: str | None = None) -> List[Expense]:
        expenses = self._read_expenses()
        filtered = []

        for expense in expenses:
            if category and expense.category.lower() != category.lower():
                continue
            if month and not expense.date.startswith(month):
                continue
            filtered.append(expense)

        if not filtered:
            print("No expenses found.")
            return []

        print("\nExpenses:")
        for index, expense in enumerate(filtered, start=1):
            print(f"{index}. {expense.date} | {expense.category} | ${expense.amount:.2f} | {expense.description}")
        return filtered

    def summary(self, month: str | None = None) -> None:
        expenses = self._read_expenses()
        if month:
            expenses = [e for e in expenses if e.date.startswith(month)]

        if not expenses:
            print("No expenses to summarize.")
            return

        total = sum(e.amount for e in expenses)
        category_totals: dict[str, float] = defaultdict(float)
        for expense in expenses:
            category_totals[expense.category] += expense.amount

        print(f"\nTotal spent: ${total:.2f}")
        print("Category totals:")
        for category, amount in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
            print(f"- {category}: ${amount:.2f}")

    def delete_expense(self, index: int) -> None:
        expenses = self._read_expenses()
        if index < 1 or index > len(expenses):
            raise ValueError("Index out of range.")

        removed = expenses.pop(index - 1)
        with self.file_path.open("w", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["date", "category", "amount", "description"],
            )
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense.to_row())

        print(f"Deleted: {removed.date} | {removed.category} | ${removed.amount:.2f} | {removed.description}")


def parse_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format.") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track your personal expenses.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--date", required=True, type=parse_date, help="Expense date (YYYY-MM-DD)")
    add_parser.add_argument("--category", required=True, help="Expense category, e.g. Food")
    add_parser.add_argument("--amount", required=True, type=float, help="Expense amount")
    add_parser.add_argument("--description", required=True, help="Expense description")

    list_parser = subparsers.add_parser("list", help="List expenses")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--month", help="Filter by month (YYYY-MM)")

    summary_parser = subparsers.add_parser("summary", help="Show expense summary")
    summary_parser.add_argument("--month", help="Filter by month (YYYY-MM)")

    delete_parser = subparsers.add_parser("delete", help="Delete an expense")
    delete_parser.add_argument("--index", required=True, type=int, help="Expense index to delete (1-based)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    tracker = ExpenseTracker()

    try:
        if args.command == "add":
            tracker.add_expense(args.date, args.category, args.amount, args.description)
        elif args.command == "list":
            tracker.list_expenses(category=args.category, month=args.month)
        elif args.command == "summary":
            tracker.summary(month=args.month)
        elif args.command == "delete":
            tracker.delete_expense(args.index)
    except ValueError as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")


if __name__ == "__main__":
    main()
