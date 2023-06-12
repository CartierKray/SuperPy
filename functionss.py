import csv
import argparse
import datetime
import os
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import sys


INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"
DATE_FILE = "date.txt"
USAGE_GUIDE_FILE = "usage_guide.txt"


def read_csv_file(file_path):
    rows = []
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    return rows


def write_csv_file(file_path, rows, fieldnames):
    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_current_date():
    with open(DATE_FILE, "r") as file:
        date_str = file.read().strip()
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def set_current_date(date):
    date_str = date.strftime("%Y-%m-%d")
    with open(DATE_FILE, "w") as file:
        file.write(date_str)


def advance_time(days):
    try:
        with open("date.txt", "r") as file:
            current_date = datetime.datetime.strptime(file.read().strip(), "%Y-%m-%d")

        new_date = current_date + datetime.timedelta(days=days)

        with open("date.txt", "w") as file:
            file.write(new_date.strftime("%Y-%m-%d"))

        print(f"Date changed to: {new_date.strftime('%Y-%m-%d')}")

    except FileNotFoundError:
        print("date.txt file not found.")


def buy_product(product_name, price, expiration_date, quantity):
    inventory = read_csv_file(INVENTORY_FILE)
    next_id = max([int(item["id"]) for item in inventory], default=0) + 1
    item = {
        "id": str(next_id),
        "product_name": product_name,
        "buy_date": get_current_date().strftime("%Y-%m-%d"),
        "buy_price": str(price),
        "expiration_date": expiration_date,
        "quantity": str(quantity),
    }
    inventory.append(item)
    write_csv_file(INVENTORY_FILE, inventory, item.keys())
    print(
        f"You want to buy {quantity} {product_name} for ${price} each, expiring on {expiration_date}"
    )


def sell_product(product_name, price):
    inventory = read_csv_file(INVENTORY_FILE)
    sales = read_csv_file(SALES_FILE)
    current_date = get_current_date()

    item = next(
        (item for item in inventory if item["product_name"] == product_name), None
    )
    if item:
        expiration_date = datetime.datetime.strptime(
            item["expiration_date"], "%Y-%m-%d"
        ).date()
        if expiration_date >= current_date:
            next_id = max([int(sale["id"]) for sale in sales], default=0) + 1
            sale = {
                "id": str(next_id),
                "product_name": str(product_name),
                "bought_id": item["id"],
                "sell_date": current_date.strftime("%Y-%m-%d"),
                "sell_price": str(price),
            }
            sales.append(sale)
            write_csv_file(SALES_FILE, sales, sale.keys())

            inventory.remove(item)
            write_csv_file(INVENTORY_FILE, inventory, item.keys())
            print(f"Product '{product_name}' sold successfully.")
        else:
            print("ERROR: Product expired and cannot be sold.")
    else:
        print("ERROR: Product not in stock.")


def generate_inventory_report(report_date):
    inventory = read_csv_file(INVENTORY_FILE)

    print(f"Inventory Report - {report_date}\n")
    print("Item\t\tQuantity")

    for item in inventory:
        if "quantity" in item:
            print(f"{item['product_name']}\t\t{item['quantity']}")
        else:
            print(f"{item['product_name']}\t\t0")

    total_items = sum(int(item.get("quantity", 0)) for item in inventory)
    print(f"\nTotal Items: {total_items}")


def generate_revenue_report(start_date, end_date):
    sales = read_csv_file(SALES_FILE)
    console = Console()

    total_revenue = 0
    for sale in sales:
        sell_date = datetime.datetime.strptime(sale["sell_date"], "%Y-%m-%d").date()
        if start_date <= sell_date <= end_date:
            total_revenue += float(sale["sell_price"])

    console.print(
        f"Revenue from {start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}: {total_revenue}"
    )


def generate_profit_report(start_date, end_date):
    inventory = read_csv_file(INVENTORY_FILE)
    sales = read_csv_file(SALES_FILE)
    console = Console()

    total_cost = 0
    for item in inventory:
        expiration_date = datetime.datetime.strptime(
            item["expiration_date"], "%Y-%m-%d"
        ).date()
        if expiration_date >= start_date and item["id"] not in [
            sale["bought_id"] for sale in sales
        ]:
            total_cost += float(item["buy_price"])

    total_revenue = 0
    for sale in sales:
        sell_date = datetime.datetime.strptime(sale["sell_date"], "%Y-%m-%d").date()
        if start_date <= sell_date <= end_date:
            total_revenue += float(sale["sell_price"])

    total_profit = total_revenue - total_cost
    console.print(
        f"Profit from {start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}: {total_profit}"
    )


def export_report(report_type, start_date, end_date, export_file):
    if report_type == "inventory":
        inventory = read_csv_file(INVENTORY_FILE)
        rows = []
        for item in inventory:
            expiration_date = datetime.datetime.strptime(
                item["expiration_date"], "%Y-%m-%d"
            ).date()
            if start_date <= expiration_date <= end_date:
                rows.append(item)
        write_csv_file(export_file, rows, rows[0].keys())

    elif report_type == "sales":
        sales = read_csv_file(SALES_FILE)
        rows = []
        for sale in sales:
            sell_date = datetime.datetime.strptime(sale["sell_date"], "%Y-%m-%d").date()
            if start_date <= sell_date <= end_date:
                rows.append(sale)
        write_csv_file(export_file, rows, rows[0].keys())

    elif report_type == "revenue":
        sales = read_csv_file(SALES_FILE)
        rows = []
        for sale in sales:
            sell_date = datetime.datetime.strptime(sale["sell_date"], "%Y-%m-%d").date()
            if start_date <= sell_date <= end_date:
                rows.append(sale)
        write_csv_file(export_file, rows, rows[0].keys())

    elif report_type == "profit":
        inventory = read_csv_file(INVENTORY_FILE)
        sales = read_csv_file(SALES_FILE)
        rows = []
        for item in inventory:
            expiration_date = datetime.datetime.strptime(
                item["expiration_date"], "%Y-%m-%d"
            ).date()
            if expiration_date >= start_date and item["id"] not in [
                sale["bought_id"] for sale in sales
            ]:
                rows.append(item)
        write_csv_file(export_file, rows, rows[0].keys())

    else:
        print("ERROR: Invalid report type.")


def visualize_statistics(report_type, start_date, end_date):
    if report_type == "revenue":
        sales = read_csv_file(SALES_FILE)
        x = []
        y = []
        for sale in sales:
            sell_date = datetime.datetime.strptime(sale["sell_date"], "%Y-%m-%d").date()
            if start_date <= sell_date <= end_date:
                x.append(sell_date)
                y.append(float(sale["sell_price"]))

        plt.plot(x, y)
        plt.xlabel("Date")
        plt.ylabel("Revenue")
        plt.title("Revenue Trend")
        plt.show()

    elif report_type == "profit":
        inventory = read_csv_file(INVENTORY_FILE)
        sales = read_csv_file(SALES_FILE)
        x = []
        y = []
        for item in inventory:
            expiration_date = datetime.datetime.strptime(
                item["expiration_date"], "%Y-%m-%d"
            ).date()
            if expiration_date >= start_date and item["id"] not in [
                sale["bought_id"] for sale in sales
            ]:
                x.append(expiration_date)
                y.append(float(item["buy_price"]))

        plt.plot(x, y)
        plt.xlabel("Date")
        plt.ylabel("Cost")
        plt.title("Cost Trend")
        plt.show()

    else:
        print("ERROR: Invalid report type.")
