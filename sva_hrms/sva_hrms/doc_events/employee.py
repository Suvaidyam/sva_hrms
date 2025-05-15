import frappe
from frappe.utils import today
def before_save(doc, method):
    if doc.is_new():
        if doc.custom_employee_no:
            doc.employee_number = doc.custom_employee_no  # Assign value directly
            doc.name = doc.custom_employee_no
        else:
            frappe.throw("Please enter Employee Number")  

# def Validate(doc, method):
    
#     # Step 1: Get employee ID from employee name
#     employee = frappe.get_value("Employee", {"employee_name": doc.employee_name}, "name")
   
#     if not employee:
#         frappe.msgprint(f"No employee found with name: {doc.employee_name}")
#         return    
#     if doc.time:
       
#         if doc.log_type == "OUT":
#             out_time = doc.time
#         else:
#             in_time = doc.time
#         #frappe.throw(out_time)
#         # Step 3: Get or create today's attendance record
#         attendance = frappe.get_doc("Attendance",
#             {
#                 "employee": employee,
#                 "attendance_date": today()
#             }
#         ) if frappe.db.exists("Attendance", {"employee": employee, "attendance_date": today()}) else frappe.new_doc("Attendance")

#         attendance.employee = employee
#         attendance.attendance_date = today()
#         if doc.log_type == "OUT":
#             attendance.out_time = out_time
#         else:
#             attendance.in_time = in_time
        
        
#         #attendance.status = "Present"  # You can customize logic here
#         attendance.save(ignore_permissions=True)
#         frappe.db.commit()
#         frappe.msgprint(f"Updated Attendance Time for {doc.employee_name} ")
#     else:
#         frappe.msgprint(f"No 'IN' check-in found today for {doc.employee_name}.")
 