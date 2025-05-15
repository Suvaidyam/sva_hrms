import frappe
from frappe.utils import today, add_days, get_datetime, is_invalid_date_string
import datetime

from dateutil import parser
from dateutil.parser import ParserError


def getdate(string_date, parse_day_first: bool = False):
    """
    Converts string date (yyyy-mm-dd) to datetime.date object.
    If no input is provided, current date is returned.
    """
    if not string_date:
        return get_datetime().date()
    if isinstance(string_date, datetime.datetime):
        return string_date.date()

    elif isinstance(string_date, datetime.date):
        return string_date

    if is_invalid_date_string(string_date):
        return None
    return parser.parse(string_date, dayfirst=parse_day_first).date()


def execute(filters):
    today_date = getdate(today())
    current_month = today_date.month
    # Get filter values for from_date and to_date
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # Ensure from_date and to_date are datetime.date objects
    if from_date:
        from_date = getdate(from_date)
    else:
        from_date = today_date

    if to_date:
        to_date = getdate(to_date)
    else:
        to_date = add_days(today_date, 7)  # Default to 7 days range

    # Fetch active employees with date_of_birth
    data = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["employee_name", "date_of_birth"],
    )

    # Filter employees and format date & day
    filtered_data = []
    for emp in data:
        if not emp["date_of_birth"]:
            continue  # Skip if date_of_birth is missing
        birth_date = getdate(emp["date_of_birth"])
        try:
            birthday_this_year = getdate(
                f"{today_date.year}-{birth_date.month}-{birth_date.day}"
            )
        except Exception:
            # Handle leap year issue (e.g., Feb 29 in a non-leap year)
            if birth_date.month == 2 and birth_date.day == 29:
                birthday_this_year = getdate(
                    f"{today_date.year}-02-28"
                )  # <- Sets to Feb 28
            else:
                continue  # Skip if the birth date is invalid for the current year

        # Check if the birthday falls within the given range
        if from_date <= birthday_this_year <= to_date:
            formatted_date = birthday_this_year.strftime("%d-%B-%Y")  # 👈 Format date
            filtered_data.append(
                {
                    "employee_name": emp["employee_name"],
                    "day": birthday_this_year.strftime("%A"),  # Get weekday name
                    "date": formatted_date,  # 👈 Formatted string instead of date object
                    "month": birthday_this_year.month,
                    "count": 1,
                }
            )
    filtered_data.sort(key=lambda x: (x["month"] != current_month, x["date"]))
    # Define columns
    columns = [
        {
            "fieldname": "employee_name",
            "label": "Employee Name",
            "fieldtype": "Data",
            "width": 220,
        },
        {"fieldname": "day", "label": "Day", "fieldtype": "Data", "width": 220},
        {"fieldname": "date", "label": "Date", "fieldtype": "Data", "width": 220},  # 👈 Changed from Date to Data
        {
            "fieldname": "count",
            "fieldtype": "Int",
            "label": "Count",
            "hidden": 1,
            "width": "220",
        },
    ]

    return columns, filtered_data


def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    return False
