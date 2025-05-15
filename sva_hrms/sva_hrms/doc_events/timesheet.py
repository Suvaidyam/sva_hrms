import frappe


def before_save(doc, method):
    for i in doc.time_logs:
        i.activity_type = frappe.db.get_value("Task", i.task, "custom_activity_type")


def validate(doc, method):
    employee = doc.employee
    custom_dates = [i.custom_date for i in doc.time_logs]
    
    query = frappe.db.sql(
        f"""
        SELECT name
        FROM `tabTimesheet`
        WHERE employee = '{employee}'
        AND name != '{doc.name}'
        AND docstatus != 2
        AND EXISTS (
            SELECT 1
            FROM `tabTimesheet Detail`
            WHERE parent = `tabTimesheet`.name
            AND custom_date IN ({', '.join(f"'{date}'" for date in custom_dates)})
        )
        """,
        as_dict=True,
    )
    
    if query:
        frappe.throw("Timesheet already exists for this date", title="Error")
