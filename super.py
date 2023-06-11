import csv
import argparse
import datetime
import os
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table


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
    current_date = get_current_date()
    new_date = current_date + datetime.timedelta(days=days)
    set_current_date(new_date)
    print(
        f"Time advanced by {days} days. Current date is {new_date.strftime('%Y-%m-%d')}."
    )


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


def create_usage_guide():
    usage_guide = """
    SuperPy - Inventory Management System

    Commands:

      buy             Buy a product
      sell            Sell a product
      report          Generate reports

    Examples:

    Buy a product:
        python super.py buy --product-name banana --price 2.8 --expiration-date 2023-06-30 --quantity 1

    Sell a product:
        python super.py sell --product-name orange --price 2

    Generate inventory report:
        python super.py report inventory --now

    Generate revenue report:
        python super.py report revenue --start-date 2023-05 --end-date 2023-06

    Generate profit report:
        python super.py report profit --start-date 2023-05 --end-date 2023-06

    Visualize revenue statistics:
        python super.py report revenue --start-date 2023-05 --end-date 2023-06 --visualize

    """
    with open(USAGE_GUIDE_FILE, "w") as file:
        file.write(usage_guide)


def main():
    parser = argparse.ArgumentParser(
        description="SuperPy - Inventory Management System"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Buy Command
    buy_parser = subparsers.add_parser("buy", help="Buy a product")
    buy_parser.add_argument("--product-name", required=True, help="Name of the product")
    buy_parser.add_argument(
        "--price", type=float, required=True, help="Price of the product"
    )
    buy_parser.add_argument(
        "--expiration-date", required=True, help="Expiration date of the product"
    )
    buy_parser.add_argument("--quantity", type=int, help="Quantity of the product")

    # Sell Command
    sell_parser = subparsers.add_parser("sell", help="Sell a product")
    sell_parser.add_argument(
        "--product-name", required=True, help="Name of the product"
    )
    sell_parser.add_argument(
        "--price", type=float, required=True, help="Price of the product"
    )

    # Report Command
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_subparsers = report_parser.add_subparsers(dest="report_type")

    # Inventory Report Subcommand
    inventory_report_parser = report_subparsers.add_parser(
        "inventory", help="Generate inventory report"
    )
    inventory_report_parser.add_argument(
        "--now", action="store_true", help="Generate report for the current date"
    )

    # Revenue Report Subcommand
    revenue_report_parser = report_subparsers.add_parser(
        "revenue", help="Generate revenue report"
    )
    revenue_report_parser.add_argument(
        "--start-date", required=True, help="Start date of the report"
    )
    revenue_report_parser.add_argument(
        "--end-date", required=True, help="End date of the report"
    )
    revenue_report_parser.add_argument(
        "--visualize", action="store_true", help="Visualize revenue statistics"
    )

    # Profit Report Subcommand
    profit_report_parser = report_subparsers.add_parser(
        "profit", help="Generate profit report"
    )
    profit_report_parser.add_argument(
        "--start-date", required=True, help="Start date of the report"
    )
    profit_report_parser.add_argument(
        "--end-date", required=True, help="End date of the report"
    )

    # Export Subcommand
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument(
        "--report-type", required=True, help="Type of the report to export"
    )
    export_parser.add_argument(
        "--start-date", required=True, help="Start date of the report"
    )
    export_parser.add_argument(
        "--end-date", required=True, help="End date of the report"
    )
    export_parser.add_argument(
        "--export-file", required=True, help="File to export the report"
    )

    args = parser.parse_args()

    if args.command == "buy":
        buy_product(args.product_name, args.price, args.expiration_date, args.quantity)
        print("Product bought successfully.")

    elif args.command == "sell":
        sell_product(args.product_name, args.price)
        print("Product sold successfully.")

    elif args.command == "report":
        if args.report_type == "inventory":
            report_date = (
                get_current_date()
                if args.now
                else datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
            )
            generate_inventory_report(report_date)

        elif args.report_type == "revenue":
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m").date()
            end_date = datetime.datetime.strptime(args.end_date, "%Y-%m").date()
            generate_revenue_report(start_date, end_date)

            if args.visualize:
                visualize_statistics("revenue", start_date, end_date)

        elif args.report_type == "profit":
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m").date()
            end_date = datetime.datetime.strptime(args.end_date, "%Y-%m").date()
            generate_profit_report(start_date, end_date)

        else:
            print("ERROR: Invalid report type.")

    elif args.command == "export":
        start_date = datetime.datetime.strptime(args.start_date, "%Y-%m").date()
        end_date = datetime.datetime.strptime(args.end_date, "%Y-%m").date()
        export_report(args.report_type, start_date, end_date, args.export_file)

        print(f"Report exported to {args.export_file} successfully.")

    else:
        parser.print_help()


if __name__ == "__main__":
    if not os.path.exists(INVENTORY_FILE):
        write_csv_file(
            INVENTORY_FILE,
            [],
            ["id", "product_name", "buy_date", "buy_price", "expiration_date"],
        )

    if not os.path.exists(SALES_FILE):
        write_csv_file(SALES_FILE, [], ["id", "bought_id", "sell_date", "sell_price"])

    if not os.path.exists(DATE_FILE):
        set_current_date(datetime.date.today())

    if not os.path.exists(USAGE_GUIDE_FILE):
        create_usage_guide()

    main()
