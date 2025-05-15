import frappe
from datetime import datetime, timedelta


# dhwani_hrms.dhwani_hrms.custom_number_cards.work_anniversary_card.get_upcoming_work_anniversary
@frappe.whitelist(allow_guest=True)
def get_upcoming_work_anniversary():
    report = frappe.get_doc("Report", "Work Anniversary")
    to_date = (datetime.now() + timedelta(days=30)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)
    to_date = to_date.strftime("%Y-%m-%d")

    from_date = frappe.utils.nowdate()
    to_date = frappe.utils.get_last_day(frappe.utils.add_days(from_date, 30))

    columns, data = report.get_data(
        filters={"from_date": from_date, "to_date": to_date}, as_dict=True
    )

    values = sum(row["count"] for row in data)

    return {
        "value": values,
        "fieldtype": "Int",
        "route_options": {
            "from_date": from_date,
            "to_date": to_date,
        },
        "route": ["query-report", "Work Anniversary"],
    }
