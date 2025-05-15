import frappe
from datetime import datetime


# dhwani_hrms.dhwani_hrms.custom_number_cards.me.get_current_user_timesheet
@frappe.whitelist()
def get_current_user_timesheet():
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    current_year = datetime.now().year
    timesheet_count = frappe.db.count("Timesheet", filters={
        "employee": employee,
        "start_date": ["between", [f"{current_year}-01-01", f"{current_year}-12-31"]]
    })
    return {
        "value": timesheet_count,
        "fieldtype": "int",
        "route_options": {"employee": employee},
        "route": ["List", "Timesheet"],
    }


# dhwani_hrms.dhwani_hrms.custom_number_cards.me.get_current_user_leaves
@frappe.whitelist()
def get_current_user_leaves():
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    current_year = datetime.now().year
    leave_count = frappe.db.count("Leave Application", filters={
        "employee": employee,
        "posting_date": ["between", [f"{current_year}-01-01", f"{current_year}-12-31"]]
    })
    return {
        "value": leave_count,
        "fieldtype": "int",
        "route_options": {"employee": employee},
        "route": ["List", "Leave Application"],
    }

#dhwani_hrms.dhwani_hrms.custom_number_cards.me.get_current_user_attendance
@frappe.whitelist()
def get_current_user_attendance():
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    current_year = datetime.now().year
    leave_count = frappe.db.count("Attendance", filters={
        "employee": employee,
        "attendance_date": ["between", [f"{current_year}-01-01", f"{current_year}-12-31"]]
    })
    return {
        "value": leave_count,
        "fieldtype": "int",
        "route_options": {"employee": employee},
        "route": ["List", "Attendance"],
    }