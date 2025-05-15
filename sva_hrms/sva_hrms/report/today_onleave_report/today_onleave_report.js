frappe.query_reports["Today OnLeave Report"] = {
    "filters": [
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
        {
            fieldname: "leave_type",
            label: __("Leave Type"),
            fieldtype: "Select",
            options: [],
            default: "",
        }
    ],
    onload: function (report) {
        customBreadCrumbs.add(report.report_name, "Report")
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Leave Type",
                fields: ["name"],
            },
            callback: function (response) {
                if (response.message) {
                    let leave_type_options = [""].concat(
                        response.message.map((lt) => lt.name)
                    );

                    report.page.fields_dict.leave_type.df.options = leave_type_options;
                    report.page.fields_dict.leave_type.refresh();
                }
            },
        });
    },
}


