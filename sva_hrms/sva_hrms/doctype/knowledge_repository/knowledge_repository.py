# Copyright (c) 2025, Alok Shukla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class KnowledgeRepository(Document):
    def after_insert(self):
        project_doc = frappe.get_doc("Project", {"name": self.name})
        project_doc.custom_project_revenue = self.name
        project_doc.save(ignore_permissions=True)

    def on_trash(self):
        project_doc = frappe.get_doc("Project", {"name": self.name})
        project_doc.custom_project_revenue = ""
        project_doc.save(ignore_permissions=True)
