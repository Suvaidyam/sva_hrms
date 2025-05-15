import frappe
from frappe.utils import today


#dhwani_hrms\dhwani_hrms\dhwani_hrms\api\employee_checkin_attendence\get_attendance_request
@frappe.whitelist()
def get_attendance_request(user):
    # Get Employee linked to the session user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    
    if not employee:
        return {"error": "Employee not found for the user"}

    # Fetch latest Attendance Request for today
    attendance = frappe.get_all(
        "Attendance Request",
        filters={"employee": employee,"from_date": today()},
        fields=["reason", "from_date"],
        order_by="creation desc",
        limit_page_length=1
    )
    if attendance:
        return attendance[0]  # Return first matching record
    else:
        return {"error": "No Attendance Request found for Work from home"}
