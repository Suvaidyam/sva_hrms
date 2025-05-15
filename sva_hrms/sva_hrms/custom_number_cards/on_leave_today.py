import frappe


# dhwani_hrms.dhwani_hrms.custom_number_cards.on_leave_today.get_on_leave_employees_today
@frappe.whitelist(allow_guest=True)
def get_on_leave_employees_today():
    report = frappe.get_doc("Report", "Today OnLeave Report")
    from_date = frappe.utils.nowdate()
    to_date = frappe.utils.nowdate()
    columns, data = report.get_data(
        filters={"from_date": from_date, "to_date": to_date}, as_dict=True
    )
    if data:
        values = data[-1].get("count")
    else:
        values = 0
    return {
        "value": values,
        "fieldtype": "Int",
        "route_options": {
            "from_date": frappe.utils.nowdate(),
            "to_date": frappe.utils.nowdate(),
        },
        "route": ["query-report", "Today OnLeave Report"],
    }
