frappe.query_reports["Employee Birthdays and Work Anniversary"] = {
    "filters": [
        {
            fieldname: "date_range",
            label: __("Date Range"),
            fieldtype: "Select",
            options: [
                { "value": "this_week", "label": __("This Week") },
                { "value": "this_month", "label": __("This Month") },
                { "value": "next_week", "label": __("Next Week") },
                { "value": "next_month", "label": __("Next Month") },
            ],
            default: "this_week",  // Default to this week
        },
        {
            fieldname: "event",
            label: __("Event"),
            fieldtype: "Select",
            options: ["", "Birthday", "Work Anniversary"], // Add a blank option for "All"
            default: "", // Default to show both
        }
    ],

    onload: function(report) {
        report.set_filter_value('date_range', 'this_week'); //Keep the date filter default
    },

    onrender: function(report) {
        const chart_data = report.data.chart; // Use "chart" key as returned by Python code

        if (chart_data && chart_data.labels && chart_data.labels.length > 0) {  // Check chart data properly
            const chart = new frappe.chart.Chart({
                parent: report.page.wrapper.find('.report-chart-container')[0],
                type: chart_data.type,  // Use chart type from data
                title: 'Employee Birthdays/Anniversaries', // More general title
                data: chart_data.data,  // Use data directly
                height: 300,
                colors: chart_data.colors || ['#7cd6fd', '#FF6384'], // Provide default colors, use from data if available
                yAxisPosition: 'right',
            });
        } else {
            report.page.wrapper.find('.report-chart-container').html('No data to display.');
        }
    },


    "onload_post_render": function(report) {
       $('<div class="report-chart-container"></div>').appendTo(report.page.wrapper);
    }
};

