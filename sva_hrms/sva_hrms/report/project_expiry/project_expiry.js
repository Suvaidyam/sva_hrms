frappe.query_reports["Project Expiry"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), 365)
        }
    ],
    
    onload: function(report) {
        // Hook into chart rendering after data is loaded
        report.refresh_chart = function() {
            frappe.query_report.load_chart = () => {
                let chart_data = frappe.query_report.chart_args;

                const tooltips = chart_data.custom?.tooltips || [];

                chart_data.tooltipOptions = {
                    formatTooltipY: function (value, index, label) {
                        return tooltips[index] || value;
                    }
                };

                frappe.query_report.render_chart(chart_data);
            };

            frappe.query_report.load_chart();
        };
    }
};
