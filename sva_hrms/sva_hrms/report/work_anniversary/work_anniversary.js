// Copyright (c) 2025, Alok Shukla and contributors
// For license information, please see license.txt

frappe.query_reports["Work Anniversary"] = {
	"filters": [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: get_today_date(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: get_next_month_date(),
        },
    ],
};
function get_today_date() {
    let today = new Date();
    let year = today.getFullYear();
    let month = String(today.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
    let day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}
 
function get_next_month_date() {
    let today = new Date();
    let nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate());
    let year = nextMonth.getFullYear();
    let month = String(nextMonth.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
    let day = String(nextMonth.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}