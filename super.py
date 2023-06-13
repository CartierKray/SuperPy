import csv
import argparse
import datetime
import os
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import sys
from functionss import *


def create_usage_guide():
    usage_guide = """
    SuperPy - Inventory Management System

    Commands:

      buy                Buy a product
      sell               Sell a product
      report             Generate reports
      export             Export data to CSV
      advance_time       Advance or reverse the current date

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

    Change the time :
        python super.py advance_time 2 ( changes the date with 2 days ahead )
        python super.py advance_time -2 ( changes the date with -2 days back )

    
    For a more detailed explanation you can visit the user_guide.txt file for specifications of the command lines and their purposes.

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

    # Advance Time Command
    advance_time_parser = subparsers.add_parser(
        "advance_time", help="Advance or reverse the current date"
    )
    advance_time_parser.add_argument(
        "days",
        type=int,
        help="Number of days to advance (positive) or reverse (negative) the current date",
    )

    args = parser.parse_args()

    if args.command == "buy":
        buy_product(args.product_name, args.price, args.expiration_date, args.quantity)

    elif args.command == "sell":
        sell_product(args.product_name, args.price)

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

        elif args.command == "advance_time":
            days = args.days
            advance_time(days)

        else:
            print("ERROR: Invalid report type.")

    elif args.command == "export":
        start_date = datetime.datetime.strptime(args.start_date, "%Y-%m").date()
        end_date = datetime.datetime.strptime(args.end_date, "%Y-%m").date()
        export_report(args.report_type, start_date, end_date, args.export_file)

        print(f"Report exported to {args.export_file} successfully.")

    elif args.command == "advance_time":
        days = args.days
        advance_time(days)

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
