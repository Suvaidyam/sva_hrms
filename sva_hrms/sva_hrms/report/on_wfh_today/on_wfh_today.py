# Copyright (c) 2025, Vivek Kumar and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime

def execute(filters=None):
    filters = filters or {}
    today = frappe.utils.today()

    columns = [
        {"fieldname": "employee_name", "fieldtype": "Data", "label": "Employee Name", "width": 150},
        {"fieldname": "reason", "fieldtype": "Data", "label": "Reason", "width": 150},
        {"fieldname": "from_date", "fieldtype": "Data", "label": "From Date", "width": 150},
        {"fieldname": "to_date", "fieldtype": "Data", "label": "To Date", "width": 150},
        {"fieldname": "workflow_state", "fieldtype": "Data", "label": "WFH Status", "width": 120},
        {"fieldname": "count", "fieldtype": "Int", "label": "Total Count", "hidden": 1},
    ]

    query = """
        SELECT name, employee_name, reason, from_date, to_date, workflow_state
        FROM `tabAttendance Request`
        WHERE %(today)s BETWEEN from_date AND to_date
    """

    if filters.get("employee"):
        query += " AND employee = %(employee)s"
    if filters.get("from_date"):
        query += " AND from_date >= %(from_date)s"
    if filters.get("to_date"):
        query += " AND to_date <= %(to_date)s"

    data = frappe.db.sql(query, {
        "today": today,
        "employee": filters.get("employee"),
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
    }, as_dict=True)

    total_count = len(data)

    # Format the dates and add count field
    for row in data:
        row["from_date"] = datetime.strftime(row["from_date"], "%d-%B-%Y")
        row["to_date"] = datetime.strftime(row["to_date"], "%d-%B-%Y")
        row["count"] = total_count

    return columns, data
