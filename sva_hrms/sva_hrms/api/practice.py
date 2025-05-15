import frappe


 #api/method/dhwani_hrms.dhwani_hrms.api.practice.create_timesheet
@frappe.whitelist(allow_guest=True)
def create_timesheet(**kwargs):
    print("hello")
    doc = frappe.get_doc('Employee', '496')
    return {"message": "Employee data", "name": doc}



@frappe.whitelist(allow_guest=True)
def create_leaveApplication(**kwargs):
    # create a new document
    doc = frappe.new_doc('Leave Application')
    doc.employee = '719'
    doc.from_date = '2024-01-05'
    doc.to_date = '2024-01-05'
    doc.status = 'Open'
    doc.leave_type = 'leave without pay'
    doc.insert(
            ignore_permissions=True,
        )
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"message":"data inserted db commits"}   


@frappe.whitelist(allow_guest=True)
def enter_timesheet_entry():
    
    import requests

    url = "https://dhwaniris.keka.com/api/v1/psa/projects"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjFBRjQzNjk5RUE0NDlDNkNCRUU3NDZFMjhDODM5NUIyMEE0MUNFMTgiLCJ4NXQiOiJHdlEybWVwRW5HeS01MGJpaklPVnNncEJ6aGciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xvZ2luLmtla2EuY29tIiwibmJmIjoxNzM2MzI4MzczLCJpYXQiOjE3MzYzMjgzNzMsImV4cCI6MTczNjQxNDc3MywiYXVkIjpbImtla2FhcGkiLCJodHRwczovL2xvZ2luLmtla2EuY29tL3Jlc291cmNlcyJdLCJzY29wZSI6WyJrZWthYXBpIl0sImFtciI6WyJrZWthYXBpIl0sImNsaWVudF9pZCI6Ijc2OWJkOTA5LTQzNWMtNDIzNi1hZDc5LTU3MGY2ZGFkZDZmYyIsInN1YiI6IjMwMDgzOGI1LWI3OTEtNDU5NS04MjFhLTE1NTA3M2Q5MzNlMCIsImF1dGhfdGltZSI6MTczNjMyODM3MywiaWRwIjoibG9jYWwiLCJ0ZW5hbnRfaWQiOiI5ZjBiMDVkYi0zNzJlLTQ0YzUtYWFmYS0yNzQ3MWI3MWE4NjgiLCJ0ZW5hbnRpZCI6IjlmMGIwNWRiLTM3MmUtNDRjNS1hYWZhLTI3NDcxYjcxYTg2OCIsImFwcF9uYW1lIjoiRnJhcHBlIC0gU3RhZ2luZyIsInN1YmRvbWFpbiI6ImRod2FuaXJpcy5rZWthLmNvbSIsImp0aSI6IjU2ODMwMEEwQzcyMTBBNjM1QTI0RTcyN0IwM0RBRTlDIn0.RvThXVQUVDKhThCGHjixPXoZmkrQG9e0x1BER9jPQlWoz-61O1LZHD0VhSwT_SZAwWB6LkeZ6O1cUouakcoEGvIZkriAM5a1c-a0lymdwotbxuPQngXWH4780e7LM7wumZyTXctPUD52yollLTABFpdo1ljsjeX_wO-5wh60bTkuAJLYAR5bxdzn_v2aGIu3phpnAoE43kk3MfFQZUi_8OrhzbGlf9ZWWZ3cU5vBV4bxlCeX4kiicLRE3sdUULdSJf1K0zgpzRp2rc3GuoQl1YufQJpCcFoBrls1lKiczxp7CtZuZDSk9aZ8eYqiRbvpXYCmxfwKNBfodkpU-DmKiA"
    }

    response = requests.get(url, headers=headers)
   

    return response.json()