// Copyright (c) 2025, Alok Shukla and contributors
// For license information, please see license.txt

frappe.query_reports["On WFH Today"] = {
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(), // Set default as today's date
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(), // Set default as today's date
		},
	],
};
