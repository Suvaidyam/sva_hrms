import frappe
from frappe.utils import today, add_days, getdate, formatdate  # type: ignore

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

    # Fetch active employees with date_of_joining
    data = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["employee_name", "date_of_joining"],
    )

    # Filter employees and format date & day
    filtered_data = []
    for emp in data:
        if not emp["date_of_joining"]:
            continue  # Skip if date_of_joining is missing

        joining_date = getdate(emp["date_of_joining"])

        try:
            # Construct work anniversary date in the current year
            anniversary_this_year = getdate(f"{today_date.year}-{joining_date.month}-{joining_date.day}")
        except ValueError:
            # Handle leap year issue (e.g., Feb 29 in a non-leap year)
            if joining_date.month == 2 and joining_date.day == 29:
                anniversary_this_year = getdate(f"{today_date.year}-02-28")
            else:
                continue  # Skip if the date is invalid for the current year

        # Check if the work anniversary falls within the given range
        if from_date <= anniversary_this_year <= to_date:
            formatted_date = anniversary_this_year.strftime("%d-%B-%Y")  # 👈 Format date
            filtered_data.append({
                "employee_name": emp["employee_name"],
                "day": anniversary_this_year.strftime("%A"),  # Get weekday name
                "date": formatted_date,  # 👈 Formatted string instead of date object
                "month": anniversary_this_year.month,
                "count": 1,
            })
    
    # Sort: current month anniversaries first, then others in ascending order
    filtered_data.sort(key=lambda x: (x["month"] != current_month, x["date"]))

    # Define columns
    columns = [
        {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "width": 220},
        {"fieldname": "day", "label": "Day", "fieldtype": "Data", "width": 220},
        {"fieldname": "date", "label": "Anniversary Date", "fieldtype": "Data", "width": 220},
        {"fieldname": "count","fieldtype": "Int","label": "Count","hidden": 1,"width": "120"},
    ]

    return columns, filtered_data