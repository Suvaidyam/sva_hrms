// Copyright (c) 2025, Vivek Kumar and contributors
// For license information, please see license.txt

// Daily Worklog Script

frappe.ui.form.on("Daily Worklog", {
    onload: function (frm) {
        if (frm.is_new()) {
            fetch_employee_details(frm);
        }
    },

    setup: function (frm) {
        setup_filters(frm);
    },

    customer: function (frm) {
        frm.set_query("project", "timesheet_detail", function (doc) {
            return {
                filters: { customer: doc.customer },
            };
        });
        frm.refresh();
    },

    currency: function (frm) {
        update_exchange_rate(frm);
    },

    exchange_rate: function (frm) {
        update_billing_and_costing(frm);
    },

    parent_project: function (frm) {
        set_project_in_timelog(frm);
    },
});

// Helper Functions

function fetch_employee_details(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Employee",
            filters: { user_id: frappe.session.user },
            fields: ["name", "employee_name"],
            limit_page_length: 1,
        },
        callback: function (r) {
            if (r.message?.length > 0) {
                const emp = r.message[0];
                frm.set_value("employee", emp.name);
                frm.set_df_property("employee", "read_only", 1);
            }
        },
    });
}

function setup_filters(frm) {
    frm.fields_dict.employee.get_query = () => ({ filters: { status: "Active" } });
    frm.fields_dict["timesheet_detail"].grid.get_field("task").get_query = function (frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        return { filters: { project: child.project, status: ["!=", "Cancelled"] } };
    };
    frm.fields_dict["timesheet_detail"].grid.get_field("project").get_query = () => ({
        filters: { company: frm.doc.company },
    });
}

function update_exchange_rate(frm) {
    const base_currency = frappe.defaults.get_global_default("currency");
    if (frm.doc.currency && base_currency !== frm.doc.currency) {
        frappe.call({
            method: "erpnext.setup.utils.get_exchange_rate",
            args: {
                from_currency: frm.doc.currency,
                to_currency: base_currency,
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value("exchange_rate", flt(r.message));
                    frm.set_df_property(
                        "exchange_rate",
                        "description",
                        `1 ${frm.doc.currency} = [?] ${base_currency}`
                    );
                }
            },
        });
    }
}

function update_billing_and_costing(frm) {
    frm.doc.timesheet_detail.forEach((row) => {
        calculate_billing_costing_amount(frm, row.doctype, row.name);
    });
    calculate_time_and_amount(frm);
}

function set_project_in_timelog(frm) {
    if (frm.doc.parent_project) {
        frm.doc.timesheet_detail.forEach((row) => {
            frappe.model.set_value(row.doctype, row.name, "project", frm.doc.parent_project);
        });
    }
}


