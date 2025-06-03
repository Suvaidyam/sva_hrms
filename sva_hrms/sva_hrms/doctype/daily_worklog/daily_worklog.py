# Copyright (c) 2025, Vivek Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DailyWorklog(Document):
    def after_insert(self):
        time_sheet_doc = frappe.new_doc('Timesheet')
        time_sheet_doc.employee = self.employee
        time_sheet_doc.custom_timesheet_date = self.date
        
        if self.timesheet_detail:  # Check if the child table has data
            for data in self.timesheet_detail:
                time_sheet_doc.append('time_logs', {
                    'project': data.project,
                    'task': data.task,
                    'custom_date': data.date,
                    'description': data.description,
                    'from_time': data.from_time,
                    'to_time': data.to_time,
                    'is_billable': data.is_billable,
                })
	
        time_sheet_doc.insert(ignore_permissions=True)
