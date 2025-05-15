import frappe
# get_project_hours
@frappe.whitelist()
def get_project_hours(project=None):
    filters = {}
    if project:
        filters['project'] = project
    
    data = frappe.db.sql("""
        SELECT 
            tsd.project,
            SUM(tsd.hours) as total_hours
        FROM 
            `tabTimesheet Detail` tsd
        JOIN 
            `tabTimesheet` ts ON ts.name = tsd.parent
        WHERE 
            ts.docstatus = 1
            AND (%(project)s IS NULL OR tsd.project = %(project)s)
        GROUP BY 
            tsd.project
        ORDER BY 
            total_hours DESC
    """, filters, as_dict=True)
    
    return data

# get_project_contract_revenue
@frappe.whitelist()
def get_project_contract_revenue(project=None):
    filters = {}
    if project:
        filters["project"] = project

    query = """
        SELECT
            pr.project,
            SUM(pc.amount) AS total_contract_revenue
        FROM
            `tabProject Revenue` pr
        JOIN
            `tabProject Contracts` pc ON pc.parent = pr.name
        WHERE
            (%(project)s IS NULL OR pr.project = %(project)s)
        GROUP BY
            pr.project
        ORDER BY
            total_contract_revenue DESC
    """

    data = frappe.db.sql(query, filters, as_dict=True)
    return data

# get_project_invoiced_amount
@frappe.whitelist()
def get_project_invoiced_amount(project=None):
    conditions = ""
    values = {}

    if project:
        conditions = "AND pr.project = %(project)s"
        values["project"] = project

    data = frappe.db.sql(f"""
        SELECT
            pr.project,
            SUM(pc.amount) AS total_invoiced_amount
        FROM
            `tabProject Revenue` pr
        JOIN
            `tabProject Contracts` pc ON pc.parent = pr.name
        WHERE
            pc.invoiced = 'Yes'
            {conditions}
        GROUP BY
            pr.project
        ORDER BY
            total_invoiced_amount DESC
    """, values, as_dict=True)

    return data

# get_overdue_tasks
@frappe.whitelist()
def get_overdue_tasks(project=None):
    conditions = ""
    values = {}

    if project:
        conditions = "AND project = %(project)s"
        values["project"] = project

    data = frappe.db.sql(f"""
        SELECT 
            project,
            COUNT(name) AS overdue_tasks
        FROM 
            `tabTask`
        WHERE 
            status = 'Overdue'
            {conditions}
        GROUP BY 
            project
        ORDER BY 
            overdue_tasks DESC
    """, values, as_dict=True)

    return data