

# Copyright (c) 2025, Alok Shukla and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import flt
from collections import defaultdict



def execute(filters=None):
    filters = filters or {}
    financial_years = filters.get("financial_year") or []
    if not financial_years:
        # If no financial_year filter is provided, return no data or show a message.
        return [], [], _("Please select a filter"), None
    if isinstance(financial_years, str):
        financial_years = [financial_years]

    fy_placeholders = ','.join(['%s'] * len(financial_years)) if financial_years else ''
    fy_condition = f" AND r.financial_year IN ({fy_placeholders})" if financial_years else ''
    conditions = ""
    if filters.get("project"):
        conditions += f" AND r.project = '{filters['project']}'"
    if filters.get("customer"):
        conditions += f" AND r.customer = '{filters['customer']}'"
    if filters.get("cost_center"):
        conditions += f" AND r.cost_center = '{filters['cost_center']}'"
    base_query = f"""
        WITH 
        revenue AS (
            SELECT 
                `tabProject Contracts`.parent AS project,
                `tabCustomer`.customer_name AS customer,
                p.cost_center,
                CASE 
                    WHEN MONTH(`tabProject Contracts`.date) >= 4 
                        THEN CONCAT(YEAR(`tabProject Contracts`.date), '-', YEAR(`tabProject Contracts`.date) + 1)
                    ELSE CONCAT(YEAR(`tabProject Contracts`.date) - 1, '-', YEAR(`tabProject Contracts`.date))
                END AS financial_year,
                SUM(`tabProject Contracts`.amount) AS total_amount
            FROM 
                `tabProject Contracts` 
            JOIN 
                `tabProject` p ON `tabProject Contracts`.parent = p.name
            JOIN 
                `tabCustomer` ON p.customer = `tabCustomer`.name
            GROUP BY 
                `tabProject Contracts`.parent,
                `tabCustomer`.customer_name,
                p.cost_center,
                financial_year              
        ),
        total_expense AS (
            SELECT 
                tsd.project,
                CASE 
                    WHEN MONTH(tsd.from_time) >= 4 
                        THEN CONCAT(YEAR(tsd.from_time), '-', YEAR(tsd.from_time) + 1)
                    ELSE CONCAT(YEAR(tsd.from_time) - 1, '-', YEAR(tsd.from_time))
                END AS financial_year,
                SUM(tsd.hours) AS total_hours,
                (SUM(tsd.hours)/8) AS days
            FROM
                `tabTimesheet` ts
            INNER JOIN 
                `tabTimesheet Detail` tsd 
                ON tsd.parent = ts.name AND tsd.parenttype = 'Timesheet'
            WHERE 
                ts.docstatus = 1 AND workflow_state = "Approved"
            GROUP BY 
                tsd.project,
                financial_year
        ),
        project_rate_card AS (
            SELECT
                parent as project,
                fiscal_year as financial_year,
                rate
            FROM
                `tabRate Card`
        )
        SELECT 
            r.project,
            r.customer,
            r.cost_center,
            r.financial_year,
            r.total_amount,
            te.total_hours,
            te.days,
            prc.rate,
            (te.days * (CASE WHEN prc.rate IS NULL THEN 7000 ELSE prc.rate END)) as total_expense,
            (r.total_amount - (te.days * (CASE WHEN prc.rate IS NULL THEN 7000 ELSE prc.rate END))) AS profit_loss
        FROM 
            revenue AS r
        LEFT JOIN 
            total_expense AS te 
            ON te.project = r.project AND te.financial_year = r.financial_year
        LEFT JOIN 
            project_rate_card AS prc 
            ON prc.project = r.project AND prc.financial_year = r.financial_year
        WHERE 
            1=1
            {fy_condition} {conditions}
        ORDER BY 
    			r.financial_year, r.project
    """

    data = frappe.db.sql(base_query, tuple(financial_years), as_dict=1)

    # Pivot data 
    pivot = {}
    for row in data:
        key = (row["project"], row["customer"], row["cost_center"])
        fy = row["financial_year"]
        if key not in pivot:
            pivot[key] = {}

        pivot[key][fy] = row

    # Final data + dynamic columns
    columns = [
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": _("Client"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
    ]

    for fy in financial_years:
        columns.extend([
            {"label": f"Revenue ({fy})", "fieldname": f"revenue_{fy}", "fieldtype": "Currency", "width": 200},
            {"label": f"Rate ({fy})", "fieldname": f"rate_{fy}", "fieldtype": "Currency", "width": 180},
            {"label": f"Total Hours ({fy})", "fieldname": f"total_hours_{fy}", "fieldtype": "Float", "width": 180},
            {"label": f"Total Days ({fy})", "fieldname": f"days_{fy}", "fieldtype": "Float", "width": 180},
            {"label": f"Expense ({fy})", "fieldname": f"expense_{fy}", "fieldtype": "Currency", "width": 200},
            {"label": f"Profit / Loss ({fy})", "fieldname": f"profit_{fy}", "fieldtype": "Currency", "width": 200},
        ])

    result = []
    for key, fy_data in pivot.items():
        row = {
            "project": key[0],
            "customer": key[1],
            "cost_center": key[2]
        }
        for fy in financial_years:
            fy_row = fy_data.get(fy)
            if fy_row:
                row[f"revenue_{fy}"] = fy_row["total_amount"]
                row[f"expense_{fy}"] = fy_row["total_expense"]
                row[f"profit_{fy}"] = fy_row["profit_loss"]
                row[f"rate_{fy}"] = fy_row["rate"]
                row[f"days_{fy}"] = fy_row["days"]
                row[f"total_hours_{fy}"] = fy_row["total_hours"]
        result.append(row)

    # Chart generation (dynamically adjusting based on selected financial years)
    chart = get_chart(result, financial_years)

    return columns, result, None, chart

def get_chart(data, financial_years):
    labels = [row["project"] for row in data]
    
    # Initialize data for chart
    datasets = []
    for fy in financial_years:
        revenue = [row.get(f"revenue_{fy}", 0) for row in data]
        expense = [row.get(f"expense_{fy}", 0) for row in data]
        profit = [row.get(f"profit_{fy}", 0) for row in data]

        datasets.append({"name": f"Revenue ({fy})", "values": revenue})
        datasets.append({"name": f"Expense ({fy})", "values": expense})
        datasets.append({"name": f"Profit/Loss ({fy})", "values": profit})

    return {
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "type": "bar",
        "colors": ["#5E64FF", "#FFB822", "#28A745"],
    }
