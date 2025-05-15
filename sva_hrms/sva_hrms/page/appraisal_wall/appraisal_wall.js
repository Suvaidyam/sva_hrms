frappe.pages['Appraisal Wall'].on_page_load = function (wrapper) {
	// var page = frappe.ui.make_app_page({
	// 	parent: wrapper,
	// 	title: 'Appraisal Wall',
	// 	single_column: true
	// });
	frappe.require("appriasalwall.bundle.js").then(() => {
		frappe.appraisal_wall = new frappe.ui.AppriasalWall({
			wrapper: wrapper
		});
	})
}