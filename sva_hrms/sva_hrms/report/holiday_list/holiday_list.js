// Copyright (c) 2025, Alok Shukla and contributors
// For license information, please see license.txt

frappe.query_reports["Holiday List"] = {
	"filters": [
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select", 
            "options": get_years(),
            "default": new Date().getFullYear().toString() // Default to the current year
        },
	]
};

function get_years() {
    let current_year = new Date().getFullYear();
    return [current_year -1, current_year].join('\n'); // Only 2024 and current year
}
