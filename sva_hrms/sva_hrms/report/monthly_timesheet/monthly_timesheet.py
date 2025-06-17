import frappe
from frappe.utils import getdate, nowdate
from datetime import datetime, timedelta

def execute(filters=None):
    filters = filters or {}

    # Map full month names to numbers
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Get selected month and year (default: current)
    today = getdate(nowdate())
    month = month_map.get(filters.get("month"), today.month)
    year = int(filters.get("year", today.year))  # Default: Current Year

    first_day_of_month = datetime(year, month, 1).date()
    last_day_of_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    # Generate list of days in selected month
    days_in_month = [(first_day_of_month + timedelta(days=i)) for i in range((last_day_of_month - first_day_of_month).days + 1)]

    # Filter employees
    employee_filters = {"status": "Active"}
    if filters.get("employee"):
        employee_filters["name"] = filters["employee"]

    employees = frappe.get_all("Employee", filters=employee_filters, fields=["name", "employee_name"])

    # Get timesheets
    timesheets = frappe.get_all("Timesheet",
        filters={"start_date": ["between", [first_day_of_month, last_day_of_month]]},
        fields=["employee", "start_date", "workflow_state"],
        order_by="creation ASC"
    )

    # Map timesheet by (employee, date)
    timesheet_map = {}
    for ts in timesheets:
        date_str = ts.start_date.strftime('%Y-%m-%d')
        key = (ts.employee, date_str)
        timesheet_map[key] = ts.workflow_state or "Unknown"  # Fallback for None

    # Prepare data rows
    data = []
    for emp in employees:
        row = {"employee_name": emp.employee_name}
        for day in days_in_month:
            day_str = day.strftime('%Y-%m-%d')
            display_date = day.strftime('%d-%b-%Y')
            key = (emp.name, day_str)
            if key in timesheet_map:
                state = timesheet_map[key]
                color = get_color(state)
                row[display_date] = f"<span style='color: {color}; font-weight: bold'>{state}</span>"
            else:
                row[display_date] = "<span style='color: gray;'>Not Submitted</span>"
        data.append(row)

    # Prepare columns
    columns = [{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200}]
    for day in days_in_month:
        display_date = day.strftime('%d-%b-%Y')
        columns.append({
            "label": display_date,
            "fieldname": display_date,
            "fieldtype": "HTML",
            "width": 120
        })

    return columns, data

def get_color(state):
    if not state:
        return "gray"  # Default color for undefined states
    state = state.lower()
    if "reject" in state:
        return "red"
    elif "approve" in state:
        return "green"
    elif "review" in state:
        return "orange"
    else:
        return "black"
