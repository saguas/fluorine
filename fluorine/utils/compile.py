__author__ = 'luissaguas'


import frappe

@frappe.whitelist(allow_guest=True)
def meteor_compile():
	from fluorine.fluorine.doctype.fluorine_reactivity.fluorine_reactivity import prepare_make_meteor_file
	from fluorine.utils.reactivity import start_meteor, meteor_config
	from fluorine.commands_helpers import get_doctype

	if meteor_config.get("developer_mode") and not meteor_config.get("stop"):
		frappe.set_user("Administrator")
		start_meteor()
		doc = get_doctype("Fluorine Reactivity", frappe.local.site)
		frappe.local.request = frappe._dict()
		prepare_make_meteor_file(doc.fluor_meteor_port, doc.fluorine_reactivity)
		print "compile_meteor called."