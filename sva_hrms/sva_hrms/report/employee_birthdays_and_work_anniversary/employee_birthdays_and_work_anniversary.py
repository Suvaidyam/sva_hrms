import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar


def execute(filters=None):
    if not filters:
        filters = {}

    current_date = datetime.now()
    start_date = None
    end_date = None
    current_year = current_date.year
    current_month = current_date.month

    if filters.get("date_range") == "this_week":
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif filters.get("date_range") == "this_month":
        start_date = datetime(current_year, current_month, 1)
        end_date = datetime(
            current_year,
            current_month,
            calendar.monthrange(current_year, current_month)[1],
        )
    elif filters.get("date_range") == "next_week":
        start_date = current_date + timedelta(days=(7 - current_date.weekday()))
        end_date = start_date + timedelta(days=6)
    elif filters.get("date_range") == "next_month":
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_year = current_year if current_month < 12 else current_year + 1
        start_date = datetime(next_month_year, next_month, 1)
        end_date = datetime(
            next_month_year,
            next_month,
            calendar.monthrange(next_month_year, next_month)[1],
        )

    employees = frappe.get_all(
        "Employee",
        fields=["name", "employee_name", "date_of_birth", "date_of_joining"],
    )

    birthday_data = []
    anniversary_data = []

    columns = [
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": "Employee Name",
            "hidden": 0,
            "width": "150",
        },
        {"fieldname": "date", "fieldtype": "Date", "label": "Date", "width": "120"},
        {"fieldname": "event", "fieldtype": "Data", "label": "Event", "width": "120"},
        {
            "fieldname": "count",
            "fieldtype": "Int",
            "label": "Count",
            "hidden": 1,
            "width": "120",
        },
    ]

    if filters.get("event") == "Work Anniversary":
        columns.insert(2, _("Years") + ":Int:80")  # Years column conditionally shown

    for employee in employees:
        if employee.date_of_birth:
            birth_date = employee.date_of_birth
            birth_month_day = datetime(current_year, birth_date.month, birth_date.day)
            if start_date <= birth_month_day <= end_date:
                age = current_year - birth_date.year
                birthday_data.append(
                    {
                        "employee_name": employee.employee_name,
                        "date": birth_month_day,
                        "years": age,
                        "event": "Birthday",  # Add event type
                        "count": 1,
                    }
                )

        if employee.date_of_joining:
            joining_date = employee.date_of_joining
            joining_month_day = datetime(
                current_year, joining_date.month, joining_date.day
            )
            if start_date <= joining_month_day <= end_date:
                experience = current_year - joining_date.year
                anniversary_data.append(
                    {
                        "employee_name": employee.employee_name,
                        "date": joining_date,
                        "years": experience,
                        "event": "Work Anniversary",  # Add event type
                        "count": 1,
                    }
                )

    # Combine birthday and anniversary data
    all_data = []  # Initialize an empty list

    # Event filtering:
    if filters.get("event") == "Birthday" or not filters.get(
        "event"
    ):  # show birthday if not filter selected
        all_data.extend(birthday_data)  # Add birthday data if selected or no filter
    if filters.get("event") == "Work Anniversary" or not filters.get(
        "event"
    ):  # show work anniversary if not filter selected
        all_data.extend(
            anniversary_data
        )  # Add anniversary data if selected or no filter

    chart_labels = [data["employee_name"] for data in all_data]
    chart_values = [data["years"] for data in all_data]  # Use 'years'
    chart_colors = [
        "#FF6384" if data["event"] == "Birthday" else "#36A2EB" for data in all_data
    ]

    chart = {
        "data": {
            "labels": chart_labels,
            "datasets": [{"name": "Years", "values": chart_values}],
        },
        "type": "bar",
        "colors": chart_colors,
    }

    return columns, all_data
