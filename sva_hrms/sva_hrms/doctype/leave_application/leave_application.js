frappe.ui.form.on('Leave Application', {
    
    refresh(frm) {
        validate_dates(frm);
    },

    from_date(frm) {
        validate_dates(frm);
    },
    
    to_date(frm) {
        validate_dates(frm);
    },

    posting_date(frm) {
        validate_dates(frm);
    },

    // onload: function(frm) {
    //     if (!frm.doc.employee) {
    //         frm.set_value('employee', frappe.session.user_fullname);
    //     }
    // }
});

function validate_dates(frm) {
    if (!frm.doc.from_date || !frm.doc.to_date || !frm.doc.posting_date) return;

    const from_date = frappe.datetime.str_to_obj(frm.doc.from_date);
    const to_date = frappe.datetime.str_to_obj(frm.doc.to_date);
    const posting_date = frappe.datetime.str_to_obj(frm.doc.posting_date);

    if (from_date < posting_date) {
        frm.set_value('from_date', frm.doc.posting_date);
        frappe.show_alert({
            message: __("'{0}' cannot be before posting date. Changing to {1}.", [
                __(frm.fields_dict["from_date"].df.label),
                frappe.datetime.str_to_user(frm.doc.posting_date),
            ]),
            indicator: "orange",
        });
        return; 
    }

    
    if (to_date < from_date) {
        frm.set_value('to_date', frm.doc.from_date);
        frappe.show_alert({
            message: __("'{0}' cannot be before '{1}'. Changing to {2}.", [
                __(frm.fields_dict["to_date"].df.label),
                __(frm.fields_dict["from_date"].df.label),
                frappe.datetime.str_to_user(frm.doc.from_date),
            ]),
            indicator: "green",
        });
    }
    
    
};



