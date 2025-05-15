# Copyright (c) 2025, Alok Shukla and contributors
# For license information, please see license.txt
from frappe import _
import frappe
from frappe.utils import flt, getdate
from dateutil.relativedelta import relativedelta, MO
from erpnext.accounts.utils import get_fiscal_year
from frappe import scrub


def execute(filters=None):
    filters["company"] = "DhwaniRIS"
    if not filters:
        filters = {}
    if not filters.get("range"):
        filters["range"] = "Monthly"

    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(data, columns)
    return columns, data, None, chart


def get_chart_data(data, columns):
    labels = [col["label"] for col in columns[4:-1]]
    datasets = []

    for row in data:
        dataset = {
            "name": row.get("project_name"),
            "values": [flt(row.get(scrub(label), 0)) for label in labels],
            "fill": False,
        }
        datasets.append(dataset)

    chart = {
        "data": {"labels": labels, "datasets": datasets},
        "type": "line",
        "fieldtype": "Currency",
    }

    return chart


def get_columns(filters):
    columns = [
        {
            "label": _("Project Code"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 150,
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Client Code"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Client Name"),
            "fieldname": "client_name",
            "fieldtype": "Data",
            "width": 150,
        },
    ]

    from_date, to_date = getdate(filters.get("from_date")), getdate(
        filters.get("to_date")
    )
    date_ranges = get_period_date_ranges(from_date, to_date, filters.get("range"))

    for period_end_date in date_ranges:
        period = get_period(
            period_end_date, filters.get("range"), filters.get("company")
        )
        columns.append(
            {
                "label": _(period),
                "fieldname": scrub(period),
                "fieldtype": "Currency",
                "width": 120,
            }
        )

    columns.append(
        {
            "label": _("Total"),
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 120,
        }
    )
    return columns


def get_data(filters):
    from_date, to_date = getdate(filters.get("from_date")), getdate(
        filters.get("to_date")
    )
    project_data = {}
    data = []

    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += (
            f"date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"
        )

    if filters.get("customer"):
        conditions += f" AND customer = '{filters.get('customer')}'"
    if filters.get("project"):
        conditions += f" AND parent = '{filters.get('project')}'"
    if filters.get("cost_center"):
     conditions += f" AND `tabProject`.cost_center = '{filters.get('cost_center')}'"

    project_revenue_records = frappe.db.sql(
        f"""
            SELECT 
                parent AS project,
                customer,
                date,
                amount
            FROM 
                `tabProject Contracts` 
            JOIN 
                `tabProject` ON `tabProject Contracts`.parent = `tabProject`.name
            JOIN 
                `tabCustomer` ON `tabProject`.customer = `tabCustomer`.name

            WHERE 
                {conditions}
        """,
        as_dict=True,
    )

    for record in project_revenue_records:
        project = record.project
        if project not in project_data:
            project_doc = frappe.get_doc(
                "Project", project
            )  # fetch project name and customer name
            project_data[project] = {
                "project_name": project_doc.project_name,
                "customer": record.customer,
                "client_name": (
                    frappe.get_doc("Customer", record.customer).customer_name
                    if record.customer
                    else None
                ),
                "data": {},  # Initialize data dictionary for each project
            }

        period_end_date = get_period_end_date(record.date, filters.get("range"))
        period = get_period(
            period_end_date, filters.get("range"), filters.get("company")
        )

        if (
            period not in project_data[project]["data"]
        ):  # period data against each project
            project_data[project]["data"][period] = 0

        project_data[project]["data"][period] += flt(record.amount)

    for (
        project,
        details,
    ) in project_data.items():  # project name, customer code, customer name
        row = {
            "project": project,
            "project_name": details.get("project_name"),
            "customer": details.get("customer"),
            "client_name": details.get("client_name"),
        }
        period_data = details.get("data", {})  # amounts against periods

        total = 0
        date_ranges = get_period_date_ranges(from_date, to_date, filters.get("range"))

        for end_date in date_ranges:
            period = get_period(end_date, filters.get("range"), filters.get("company"))
            row[scrub(period)] = period_data.get(period, 0)
            total += row[scrub(period)]

        row["total"] = total
        data.append(row)

    return data


def get_period(posting_date, date_range, company):
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    if date_range == "Weekly":
        period = _("Week {0} {1}").format(
            str(posting_date.isocalendar()[1]), str(posting_date.year)
        )
    elif date_range == "Monthly":
        period = _(str(months[posting_date.month - 1])) + " " + str(posting_date.year)
    elif date_range == "Quarterly":
        period = _("Quarter {0} {1}").format(
            str(((posting_date.month - 1) // 3) + 1), str(posting_date.year)
        )
    else:  # Yearly
        year = get_fiscal_year(posting_date, company=company)
        period = str(year[0])
    return period


def get_period_end_date(date, date_range):

    if date_range == "Weekly":
        period_end_date = date + relativedelta(weekday=MO)

    elif date_range == "Monthly":
        period_end_date = date + relativedelta(day=1, months=+1, days=-1)

    elif date_range == "Quarterly":

        period_end_date = date + relativedelta(day=1, months=+3, days=-1)

    else:  # Yearly
        period_end_date = get_fiscal_year(date)[2]

    return period_end_date


def get_period_date_ranges(from_date, to_date, date_range):
    date_ranges = []
    current_date = from_date

    while current_date <= to_date:
        period_end_date = get_period_end_date(current_date, date_range)

        if period_end_date > to_date:
            period_end_date = to_date

        date_ranges.append(period_end_date)

        if date_range == "Weekly":
            current_date = period_end_date + relativedelta(days=+1)

        elif date_range == "Monthly":
            current_date = period_end_date + relativedelta(days=+1)

        elif date_range == "Quarterly":
            current_date = period_end_date + relativedelta(days=+1)

        else:  # Yearly
            current_date = period_end_date + relativedelta(days=+1)

    return date_ranges
