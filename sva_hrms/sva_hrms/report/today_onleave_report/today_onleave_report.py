import frappe
from frappe import _


def execute(filters=None):
    # Define the columns for the report
    columns = [
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": "Employee Name",
            "hidden": 0,
            "width": "150",
        },
        {
            "fieldname": "leave_type",
            "fieldtype": "Data",
            "label": "Leave Type",
            "hidden": 0,
            "width": "150",
        },
        {
            "fieldname": "from_date",
            "fieldtype": "Data",
            "label": "From Date",
            "width": "120",
        },
        {
            "fieldname": "to_date",
            "fieldtype": "Data",
            "label": "To Date",
            "width": "120",
        },
        {
            "fieldname": "status",
            "fieldtype": "Data",
            "label": "Leave Status",
            "width": "120",
        },
        {
            "fieldname": "count",
            "fieldtype": "Int",
            "label": "Count",
            "width": "120",
            "hidden": 1,
        },
    ]

    # Getting Leave Type list
    leave_types = frappe.get_all("Leave Type", fields=["name"])
    leave_type_options = [lt["name"] for lt in leave_types]

    # Default filter values if none are passed
    from_date = filters.get("from_date") or frappe.datetime.get_today()
    to_date = filters.get("to_date") or frappe.datetime.get_today()
    leave_type = (
        filters.get("leave_type")
        if filters.get("leave_type") in leave_type_options
        else ""
    )

    # Build the query based on filters
    conditions = ["from_date BETWEEN %(from_date)s AND %(to_date)s"]
    if leave_type:
        conditions.append("leave_type = %(leave_type)s")

    conditions.append("status = 'Approved'")
    # Query the leave records
    leave_data = frappe.db.sql(
        """
        SELECT employee_name, leave_type, status, from_date, to_date
        FROM `tabLeave Application`
        WHERE {conditions}
    """.format(
            conditions=" AND ".join(conditions)
        ),
        {"from_date": from_date, "to_date": to_date, "leave_type": leave_type},
        as_dict=True,
    )

    # Prepare the data for the report
    data = []
    for record in leave_data:
        formatted_from_date = frappe.utils.getdate(record.from_date).strftime("%d-%B-%Y")
        formatted_to_date = frappe.utils.getdate(record.to_date).strftime("%d-%B-%Y")
        data.append(
            {
                "employee_name": record.employee_name,
                "leave_type": record.leave_type,
                "from_date":formatted_from_date,
                "to_date":formatted_to_date,
                "status": record.status,
                "count": 1,
            }
        )

    return columns, data
