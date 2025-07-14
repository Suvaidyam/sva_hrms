import frappe
from frappe.utils import today, formatdate

@frappe.whitelist()
def send_birthday_email():
    today_date = today()
    today_month_day = frappe.utils.getdate(today_date).strftime('%m-%d')
    employees = frappe.get_all("Employee", fields=["name", "employee_name", "date_of_birth","company_email"])
    
    all_emails = [emp.company_email for emp in employees if emp.company_email]
    for emp in employees:
        try:
            if emp.date_of_birth:
                dob_month_day = emp.date_of_birth.strftime('%m-%d')
                if dob_month_day == today_month_day:
                    if frappe.db.exists("Email Template",'Employee Birthday Wish'):
                        emat_temp = frappe.get_doc("Email Template",'Employee Birthday Wish')
                        html_temp = frappe.render_template(emat_temp.response_html,{"doc": emp})
                        subject = frappe.render_template(emat_temp.subject,{"doc": emp})
                        
                        frappe.sendmail(
                            recipients= all_emails,
                            subject=subject,
                            message=html_temp,
                            now=True
                        )
                    else:
                        frappe.log_error('Birthday email template not found',emp)    
        except Exception as e:
            # Log any unexpected error for this employee
            frappe.log_error(title="Birthday Email Error", message=f"Error sending email to {emp.name}: {str(e)}")