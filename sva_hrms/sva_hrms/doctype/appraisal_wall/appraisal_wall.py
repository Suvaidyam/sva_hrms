# Copyright (c) 2025, Alok Shukla and contributors
# For license information, please see license.txt
from frappe.utils import cint

# import frappe
from frappe.model.document import Document
import json
import frappe
from frappe import _
import base64
from frappe.utils.file_manager import save_file
from frappe.utils import today
from frappe.utils import now_datetime



class AppraisalWall(Document):
	pass


def save_base64_image(dt,docname, base64_string, filename):
    # Remove the data:image/png;base64, or similar prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    # Decode base64 string
    file_content = base64.b64decode(base64_string)
    # Save file using Frappe's file manager
    saved_file = save_file(
        fname=filename,
        content=file_content,
        dt=dt,       # e.g. "Employee", "Item", etc.
        dn=docname,
        decode=False             # Already decoded
    )

    return saved_file.file_url


@frappe.whitelist(allow_guest=True)
def create_appraisal(employee_list, project_list, reason,attachment=None,add_badge=None):
	
    try:
        employee_list = json.loads(employee_list)
        project_list = json.loads(project_list)
        doc = frappe.new_doc('Appraisal Wall')
        for employee in employee_list:
            doc.append("name_of_the_team_member", {
                "employee": employee.get("employee"),
            })
        for project in project_list:
            doc.append("project", {
                "project": project.get("project"),
            })
        doc.reason = reason
        doc.insert(ignore_permissions=True)
        if attachment:
            file_url = save_base64_image("Appraisal Wall", doc.name, attachment, f"appraisal_attachment_{today()}_{now_datetime().strftime('%H%M%S')}.png")
            doc.add_attachment = file_url
            doc.save(ignore_permissions=True)
        if add_badge:   
            file_url_badge = save_base64_image("Appraisal Wall", doc.name, add_badge, f"add_badge{today()}_{now_datetime().strftime('%H%M%S')}.png")
            doc.add_badge = file_url_badge
            doc.save(ignore_permissions=True)
        return {"status": "success", "message": "Appraisal submitted", "name": doc.name}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Appraisal API Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_appraisal_employees_list():
	try:
		employees = frappe.get_all("Employee", fields=["name", "employee_name"])
		return {"status": "success", "employees": employees}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Employees API Error")
		return {"status": "error", "message": str(e)}
	
@frappe.whitelist(allow_guest=True)
def get_appraisal_projects_list():
	try:
		projects = frappe.get_all("Project", fields=["name", "project_name"])
		
		return {"status": "success", "projects": projects}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Projects API Error")
		return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def get_appraisal_wall_list():
    try:
        appraisal_wall_list = frappe.get_all("Appraisal Wall", pluck='name')
        if not appraisal_wall_list:
            return {"status": "success", "message": "No appraisal wall found"}

        appraisal_wall = []

        for aw in appraisal_wall_list:
            appraisal = frappe.get_doc("Appraisal Wall", aw)

            # Fetch all fields from each child row in 'name_of_the_team_member'
            team_members = [
                {
                    "name": member.name,
                    "employee": member.employee,
                    "employee_name": frappe.get_value("Employee", member.employee, "employee_name"),
                }
                for member in appraisal.name_of_the_team_member
            ]

            # Fetch all fields from each child row in 'project'
            projects = [
                {
                    "name": proj.name,
                    "project": proj.project,
                    "project_name": frappe.get_value("Project", proj.project, "project_name"),
                }
                for proj in appraisal.project
            ]

            # Fetch comments
            comments = frappe.get_all(
                "Comment",
                filters={
                    "reference_doctype": "Appraisal Wall",
                    "reference_name": appraisal.name,
                    "comment_type": "Comment"  # Only user comments, skip automatic logs
                },
                fields=["name", "content", "owner", "creation"]
            )

            # Add comment author full names
            for comment in comments:
                comment["full_name"] = frappe.get_value("User", comment["owner"], "full_name")

            appraisal_wall.append({
                "name": appraisal.name,
                "reason": appraisal.reason,
                "user_details": frappe.get_value(
                    'User',
                    appraisal.owner,
                    ['full_name', 'user_image', 'email'],
                    as_dict=True
                ),
                '_liked_by': appraisal._liked_by,
                "creation": appraisal.creation,
                "attachment": appraisal.add_attachment,
                'add_badge':appraisal.add_badge,
                "appraisal_team_member": team_members,
                "appraisal_project": projects,
                "comments": comments
            })

        return {"status": "success", "appraisal_wall": appraisal_wall}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Appraisal Wall API Error")
        return {"status": "error", "message": str(e)}


import json
@frappe.whitelist(allow_guest=True)
def create_poll(title, options, expiry_date=None, notify=False, anonymous=False):
    try:
        if isinstance(options, str):
            options = json.loads(options)
        notify = 1 if notify == 'true' else 0
        anonymous = 1 if anonymous == 'true' else 0
        doc = frappe.new_doc("Appriasal Poll")
        doc.title = title
        doc.expiry_date = expiry_date
        doc.notify_employees = notify
        doc.anonymous_poll = anonymous
        for option_text in options:
            doc.append("options", {"option": option_text})

        doc.insert()
        frappe.db.commit()
        return {"status": "success", "name": doc.name}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Poll Creation Failed")
        return {"status": "error", "message": str(e)}
    

@frappe.whitelist(allow_guest=True)
def get_poll_list():
    try:
        polls = frappe.get_all("Appriasal Poll", fields=["name", "title", "expiry_date", "notify_employees", "anonymous_poll"])
        for poll in polls:
            poll["options"] = frappe.get_all("Poll Option Child", filters={"parent": poll.name}, pluck="option")
        # Convert expiry_date to a more readable format if needed
        # for poll in polls:
        #     if poll.expiry_date:
        #         poll.expiry_date = frappe.utils.get_datetime(poll.expiry_date).strftime("%Y-%m-%d %H:%M:%S")
        # Return the list of polls
        if not polls:
            return {"status": "success", "message": "No polls found"}
        # Return the list of polls
        
        return {"status": "success", "polls": polls}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Poll List API Error")
        return {"status": "error", "message": str(e)}
    


@frappe.whitelist(allow_guest=True)
def create_post(post):
    try:
        doc = frappe.new_doc("Appraisal Posts")
        doc.post = post
        # print("doc===================================",doc)
        doc.insert()
        frappe.db.commit()
        return {"status": "success", "message": "Post created successfully","post": doc.post}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Post API Error")
        return {"status": "error", "message": str(e)}
    
    
    
    
    
    
    
    
    
    
    
    
    