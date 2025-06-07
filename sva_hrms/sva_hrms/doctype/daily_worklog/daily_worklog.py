# Copyright (c) 2025, Vivek Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DailyWorklog(Document):
    def after_insert(self):
        self.create_or_update_timesheet()

    def on_update(self):
        self.create_or_update_timesheet()

    def create_or_update_timesheet(self):
        # Check if a Timesheet already exists for this DailyWorklog
        existing_timesheet = frappe.db.exists(
            'Timesheet', {'employee': self.employee, 'custom_timesheet_date': self.date}
        )
        
        if existing_timesheet:
            # Fetch the existing Timesheet document
            time_sheet_doc = frappe.get_doc('Timesheet', existing_timesheet)
            time_sheet_doc.time_logs = []  # Clear existing time logs
        else:
            # Create a new Timesheet document
            time_sheet_doc = frappe.new_doc('Timesheet')
            time_sheet_doc.employee = self.employee
            time_sheet_doc.custom_timesheet_date = self.date
        
        # Populate the time logs from the DailyWorklog
        if self.timesheet_detail:
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

        # Save or update the Timesheet document
        time_sheet_doc.save(ignore_permissions=True)
