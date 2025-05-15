// Copyright (c) 2025, Alok Shukla and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Timesheet"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Employee"
		},

		{
			"fieldname": "month",
			"label": "Month",
			"fieldtype": "Select",
			"options": "\nJanuary\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default": "{{ frappe.utils.formatdate(frappe.utils.nowdate(), 'MMM') }}"
		},
		{
			"fieldname": "year",
			"label": "Year",
			"fieldtype": "Select",
			"options": ""
		},


	],
	onload: function (report) {
		const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
		const currentMonth = today.toLocaleString('default', { month: 'long' });
		const currentYear = today.getFullYear();

		// Set default Month
		if (!report.get_filter_value("month")) {
			report.set_filter_value("month", currentMonth);
		}

		// Set Year options dynamically: [currentYear - 1, currentYear]
		const year_filter = report.get_filter("year");
		if (year_filter) {
			const years = [currentYear - 1, currentYear];  // Only previous and current year
			year_filter.df.options = years.join("\n");
			year_filter.refresh();

			// Set default Year
			if (!report.get_filter_value("year")) {
				report.set_filter_value("year", currentYear);
			}
		}
	}

};
