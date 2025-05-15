import frappe
from hrms.hr.doctype.attendance.attendance import Attendance
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from hrms.hr.doctype.attendance_request.attendance_request import AttendanceRequest
from frappe.utils import getdate
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, get_link_to_form, getdate,format_date
from datetime import timedelta
from erpnext.setup.doctype.employee.employee import is_holiday
from hrms.hr.utils import validate_active_employee, validate_dates
from erpnext.setup.doctype.department.department import Department

class CustomAttendance(Attendance):
    def validate_duplicate_records(self):
        pass
    
class CustomleaveApplication(LeaveApplication):
	def validate_attendance(self):
		pass
	def create_or_update_attendance(self, attendance_name, date):
            status = (
                "Half Day" if self.half_day_date and getdate(date) == getdate(self.half_day_date) else "On Leave"
                )

            if attendance_name:
                # update existing attendance, change absent to on leave
                doc = frappe.get_doc("Attendance", attendance_name)
                if doc.status == 'Half Day' and not doc.attendance_request:
                    status = "On Leave"			
                doc.db_set({
                    "status": status, 
                    "custom_custom_leave_type": self.leave_type, 
                    "custom_custom_leave_application_": self.name,
                    "custom_half_day_type_2":self.custom_half
                })
                if doc.status == 'Present' and not doc.attendance_request:
                    status = "Half Day"			
                doc.db_set({
                    "status": status, 
                    "custom_custom_leave_type": self.leave_type, 
                    "custom_custom_leave_application_": self.name,
                    "custom_half_day_type_2":self.custom_half
                })
                if doc.status == "Absent" and not doc.attendance_request:
                    status = "On Leave"
                    doc.db_set({
                        "status": status, 
                        "custom_custom_leave_type": self.leave_type, 
                        "custom_custom_leave_application_": self.name,
                        "custom_half_day_type_2":self.custom_half
                    })
            else:
                # make new attendance and submit it
                doc = frappe.new_doc("Attendance")
                doc.employee = self.employee
                doc.employee_name = self.employee_name
                doc.attendance_date = date
                doc.company = self.company
                doc.leave_type = self.leave_type
                doc.leave_application = self.name
                doc.custom_half_day_type = self.custom_half
                doc.status = status
                doc.flags.ignore_validate = True
                doc.insert(ignore_permissions=True)
                doc.submit()


class CustomAttendaceRequest(AttendanceRequest):
    def validate(self):
        validate_active_employee(self.employee)
        validate_dates(self, self.from_date, self.to_date, False)
        self.validate_half_day()
        self.validate_request_overlap()

    def validate_half_day(self):
        if self.half_day:
            if not getdate(self.from_date) <= getdate(self.half_day_date) <= getdate(self.to_date):
                frappe.throw(_("Half day date should be in between from date and to date"))

    def validate_request_overlap(self):
        overlapping_requests = frappe.get_list(
            "Attendance Request",
            filters={
                "employee": self.employee,
                "docstatus": ("<", 2),
                "name": ("!=", self.name),
                "from_date": ("<=", self.to_date),
                "to_date": (">=", self.from_date),
            },
            fields=["name", "from_date", "to_date"]
        )

        for req in overlapping_requests:
            overlap_days = set(
                getdate(self.from_date) + timedelta(days=i)
                for i in range((getdate(self.to_date) - getdate(self.from_date)).days + 1)
            ) & set(
                getdate(req.from_date) + timedelta(days=i)
                for i in range((getdate(req.to_date) - getdate(req.from_date)).days + 1)
            )
            if len(overlap_days) > 1:
                self.throw_overlap_error(req.name)

    def throw_overlap_error(self, overlapping_request: str):
        msg = _("Employee {0} already has an Attendance Request {1} that overlaps with this period").format(
            frappe.bold(self.employee),
            get_link_to_form("Attendance Request", overlapping_request),
        )
        # frappe.throw(msg, title=_("Overlapping Attendance Request"), exc=OverlappingAttendanceRequestError)

    def on_submit(self):
        self.create_attendance_records()

    def on_cancel(self):
        attendance_list = frappe.get_all(
            "Attendance", {"employee": self.employee, "attendance_request": self.name, "docstatus": 1}
        )
        for attendance in attendance_list:
            doc = frappe.get_doc("Attendance", attendance["name"])
            doc.cancel()

    def create_attendance_records(self):
        for day in range(date_diff(self.to_date, self.from_date) + 1):
            attendance_date = add_days(self.from_date, day)
            if self.should_mark_attendance(attendance_date):
                self.create_or_update_attendance(attendance_date)

    def should_mark_attendance(self, attendance_date: str) -> bool:
        if not self.include_holidays and is_holiday(self.employee, attendance_date):
            return False
        return True

    def get_attendance_status(self, attendance_date: str) -> str:
        if self.half_day and getdate(self.half_day_date) == getdate(attendance_date):
            return "Half Day"
        elif self.reason == "Work From Home":
            return "Work From Home"
        elif self.reason == "On Duty / Regularization":
            return "Present"
        else:
            return "Present"

    def get_attendance_record(self, attendance_date: str) -> str | None:
        return frappe.db.exists(
            "Attendance",
            {
                "employee": self.employee,
                "attendance_date": attendance_date,
                "docstatus": ("!=", 2),
            },
        )

    def create_or_update_attendance(self, date: str):
        existing = self.get_attendance_record(date)
        status = self.get_attendance_status(date)

        if existing:
            doc = frappe.get_doc("Attendance", existing)
            old_status = doc.status
            if doc.status == "Present":
                # print(doc.status,'============================================')
                doc.db_set({"status": status, "attendance_request": self.name})
                text = _("changed the status from {0} to {1} via Attendance Request").format(
					frappe.bold(old_status), frappe.bold(status)
				)
                doc.add_comment(comment_type="Info", text=text)
                frappe.msgprint(
					_("Updated status from {0} to {1} for date {2} in the attendance record {3}").format(
						frappe.bold(old_status),
						frappe.bold(status),
						frappe.bold(format_date(date)),
						get_link_to_form("Attendance", doc.name),
					),
					title=_("Attendance Updated"),
				)
            elif doc.status == 'Half Day':
                doc.db_set({"status": status, "attendance_request": self.name})
            elif doc.status == 1:
                doc.cancel()
                doc.delete()

        else :
            # submit a new attendance record
            doc = frappe.new_doc("Attendance")
            doc.employee = self.employee
            doc.attendance_date = date
            doc.shift = self.shift
            doc.company = self.company
            doc.attendance_request = self.name
            doc.status = status
            doc.insert(ignore_permissions=True)
            doc.submit()

    @frappe.whitelist()
    def get_attendance_warnings(self) -> list:
        # Overriding default to exclude Leave Application warnings
        warnings = []
        for day in range(date_diff(self.to_date, self.from_date) + 1):
            date = add_days(self.from_date, day)
            if not self.include_holidays and is_holiday(self.employee, date):
                warnings.append({"date": date, "reason": "Holiday", "action": "Skip"})
            else:
                existing = self.get_attendance_record(date)
                if existing:
                    warnings.append({
                        "date": date,
                        "reason": "Attendance already marked",
                        "record": existing,
                        "action": "Overwrite",
                    })
        return warnings

class CustomDepartment(Department):
    def autoname(self):
     pass
    def before_rename(self, old, new, merge=False):
        pass
















