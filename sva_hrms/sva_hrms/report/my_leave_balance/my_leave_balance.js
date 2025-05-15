frappe.query_reports["My Leave Balance"] = {
	"filters": [
		{
			fieldname: "leave_type",
			label: __("Leave Type"),
			fieldtype: "Link",
			options: "Leave Type", // This assumes Leave Type is a DocType
            
		}
	],
	onload: function (report) {
		customBreadCrumbs.add(report.doctype, "Report", "Leave")
	},
};
