// Copyright (c) 2025, Alok Shukla and contributors
// For license information, please see license.txt

frappe.query_reports["Project Profitability Via Timesheet"] = {
	filters: [
		{
			"fieldname": "financial_year",
			"label": __("Financial Year"),
			"fieldtype": "MultiSelectList",
			"options": "Fiscal Year",
			"get_data": function (txt) {
				return frappe.db.get_link_options('Fiscal Year', txt).then(function (data) {
					return data.map(function (fiscalYear) {
						return fiscalYear;
					});
				});
			}
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project"
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer"
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center"
		}
	],
};
