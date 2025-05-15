import frappe


def send_email_notification(doc, recipient, workflow_state_message, approver_name=None):
    try:
        """Common function to send email notifications for Work From Home requests,Comp-Off,Regularize."""
        if not frappe.db.exists("Email Account", "Work From Home Request"):
            return

        if not recipient:
            return

        email_template = frappe.get_doc(
            "Email Template", "Work From Home Request Notification"
        )
        context = {
            "employee_name": doc.employee_name,
            "reason": doc.reason,
            "from_date": doc.from_date,
            "to_date": doc.to_date,
            "workflow_state": doc.workflow_state,
            "name": doc.name,  # Needed for doc link
            "approver_name": approver_name,  # Optional, will be None if not provided
        }
        rendered_subject = frappe.render_template(email_template.subject, context)
        rendered_message = frappe.render_template(email_template.response, context)

        frappe.sendmail(
            recipients=recipient, subject=rendered_subject, message=rendered_message
        )

        frappe.msgprint(f"{workflow_state_message} Email sent to {approver_name}")
        return
    except Exception as e:
        frappe.log_error(f"Error sending email: {e}", "send_email_notification")
        return
