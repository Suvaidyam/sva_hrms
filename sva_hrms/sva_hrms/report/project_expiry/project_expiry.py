import frappe
from datetime import datetime


def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select both From Date and To Date")

    query = """
        SELECT 
            DATE_FORMAT(custom_contract_expire_date, '%%M %%Y') AS Month,
            COUNT(*) AS `Total Expiring Contracts`,
            custom_contract_expire_date as `Expiry Date`,
            GROUP_CONCAT(name SEPARATOR ', ') AS Projects
        FROM 
            tabProject
        WHERE 
            custom_contract_expire_date IS NOT NULL
            AND custom_contract_expire_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY 
            Month
        ORDER BY 
            STR_TO_DATE(Month, '%%M %%Y') ASC
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    columns = [
        {"fieldname": "Month", "label": "Month", "fieldtype": "Data", "width": 150},
        {
            "fieldname": "Total Expiring Contracts",
            "label": "Total Expiring Contracts",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "fieldname": "Expiry Date",
            "label": "Expiry Date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "fieldname": "Projects",
            "label": "Projects",
            "fieldtype": "Text",
            "width": 400,
        },
    ]

    chart = get_chart_data(data)

    return columns, data, None, chart


def get_chart_data(data):
    labels = []
    values = []

    for row in data:
        month = row["Month"]
        total = row["Total Expiring Contracts"]
        projects = row.get("Projects", "")
        project_list = projects.split(", ") if projects else []

        preview = project_list[:3]
        more = f" +{len(project_list) - 3} more" if len(project_list) > 3 else ""

        # Label includes month + short project list
        label = f"{month} <br><br> " + ", ".join(preview) + more

        labels.append(label)
        values.append(total)

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Expiring Contracts", "values": values}],
        },
        "type": "bar",
    }


def get_hover_text(row):
    total_contracts = row.get("Total Expiring Contracts")
    projects = row.get("Projects")

    # Clean up project list to avoid overly long strings if needed
    max_projects_to_show = 5
    project_list = projects.split(", ") if projects else []
    shown_projects = project_list[:max_projects_to_show]
    more_count = len(project_list) - max_projects_to_show

    hover_text = f"Total Contracts: {total_contracts}\n"
    if shown_projects:
        hover_text += "Projects:\n" + "\n".join(f"- {p}" for p in shown_projects)
        if more_count > 0:
            hover_text += f"\n+{more_count} more..."
    else:
        hover_text += "Projects: None"

    return hover_text
