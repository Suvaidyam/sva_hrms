import frappe
from frappe.utils import today,getdate

# dhwani_hrms.dhwani_hrms.api.employee_checkIn_permission.validate_employee_checkin
@frappe.whitelist(allow_guest=True)
def validate_employee_checkin(doc, method):
    perm_wfh = frappe.db.get_value('Employee',doc.employee,'custom_permanent_work_from_home')
    if not perm_wfh:
        roles = frappe.get_roles(frappe.session.user)

        if "System Manager" in roles:
            return  # Allow System Managers to check-in without restrictions

        # Fetch today's Attendance Request for this employee
        attendance_request = frappe.db.sql(
        f"""
            SELECT
                name,
                from_date,
                to_date
            FROM
                `tabAttendance Request`
            WHERE
                employee = '{doc.employee}'
            AND
                from_date <= CURDATE()
            AND 
                to_date >= CURDATE()
        """, as_dict=True)

        # print(attendance_request,getdate(),doc.employee,'====================================')
        # If no Attendance Request exists for today or the reason is not "Work From Home", throw an error # or attendance_request[0].get("workflow_state") != "Review"
        if not attendance_request:
            frappe.throw("You cannot mark check-in unless you have an Attendance Request with reason 'Work From Home' for today.")

# Hook this function to the on_update event in hooks.py
