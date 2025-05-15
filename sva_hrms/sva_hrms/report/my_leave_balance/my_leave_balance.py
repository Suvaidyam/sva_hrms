import frappe
from frappe.utils import flt
from hrms.hr.doctype.leave_application.leave_application import get_leave_details


def execute(filters=None):
    columns = get_columns()
    user = frappe.session.user
    data = get_data(user, filters)
    chart = get_chart_data(data)
    return columns, data, None, chart
    # return columns, data


def get_columns():
    return [
        {
            "fieldname": "leave_type",
            "label": "Leave Type",
            "fieldtype": "Link",
            "options": "Leave Type",
            "width": 150,
        },
        {
            "fieldname": "total_leaves_allocated",
            "label": "Total Leaves Allocated",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "fieldname": "leaves_taken",
            "label": "Leaves Taken",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "leaves_pending_approval",
            "label": "Leaves Pending Approval",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "fieldname": "remaining_leaves",
            "label": "Remaining Leaves",
            "fieldtype": "Float",
            "width": 150,
        },
    ]


def get_data(user, filters={}):

    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        return []

    leave_details = get_leave_details(employee, date=frappe.utils.nowdate())

    data = []

    for leave_type, details in leave_details.get("leave_allocation", {}).items():
        if leave_type in ["Paternity Leave", "Maternity Leave"]:
            continue  # Skip Paternity Leave and Maternity Leave
        if isinstance(details, dict) and details.get("total_leaves", 0) > 0:
            if filters.get("leave_type") and leave_type != filters.get("leave_type"):
                continue
            data.append(
                {
                    "leave_type": leave_type,
                    "total_leaves_allocated": flt(
                        details.get("total_leaves", 0), 2
                    ),  # Use get to handle missing keys
                    "leaves_taken": flt(details.get("leaves_taken", 0), 2),
                    "leaves_pending_approval": flt(
                        details.get("leaves_pending_approval", 0), 2
                    ),
                    "remaining_leaves": flt(details.get("remaining_leaves", 0), 2),
                }
            )
    return data


def get_chart_data(data):
    """Creates chart data for the report."""

    labels = []
    leave_taken = []
    remaining_leaves = []
    total_allocated = []

    for row in data:  # assumes data is in correct structure
        labels.append(row["leave_type"])
        leave_taken.append(row["leaves_taken"])
        remaining_leaves.append(row["remaining_leaves"])
        total_allocated.append(row["total_leaves_allocated"])

    return {
        "data": {
            "labels": labels,
            "datasets": [
                # {"name": "Leaves Taken", "values": leave_taken},
                {"name": "Remaining Leaves", "values": remaining_leaves},
                # {"name": "Total Allocated", "values": total_allocated},
            ],
        },
        "type": "donut",  # or 'line', 'pie', etc. as needed
        "height": 300,  # Adjust height as desired
    }
