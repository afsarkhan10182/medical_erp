frappe.pages['first-page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Testing',
		single_column: true
	});
}