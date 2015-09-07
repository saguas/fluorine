from __future__ import unicode_literals
__author__ = 'luissaguas'

import os
from . import meteor_config
import frappe

start_db = False

def check_mongodb(conf):
	if not conf.get("meteor_mongo"):
		return False

def start_meteor():
	from fluorine.commands_helpers import get_default_site

	frappesite = get_default_site()

	make_meteor_ignor_files()
	extras_context_methods.update(get_extras_context_method(frappesite))

	global start_db

	if frappe.db and start_db:
		frappe.set_user("guest")
		frappe.db.commit()
		frappe.destroy()
		start_db = False

extras_context_methods = set([])

def get_extras_context_method(site):
	from fluorine.utils.fhooks import get_extras_context

	if not frappe.db:
		user = "Administrator"
		frappe.init(site=site)
		frappe.connect()
		frappe.set_user(user)
		global start_db
		start_db = True

	hooks = get_extras_context()

	return hooks

list_ignores = None

def _process_permission_apps(apps):

	list_apps_add = []
	list_apps_remove = []

	for k, v in apps.iteritems():
		if v.get("remove", 0):
			if k not in list_apps_add:
				list_apps_remove.append(k)
		elif v.get("add", 0):
			if k not in list_apps_remove:
				list_apps_add.append(k)

	return list_apps_remove


def _process_permission_files_folders(ff):
	"""
	below app_name is a valid fluorine app and pattern is any valid regular expression.
	See make_meteor_ignor_files below for more information.

	Structure:

	IN:
		ff = {
			"app_name":{
				remove:[{"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}],
				add:[{"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}]
			},
			"all": {
				remove: [{"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}],
				add:[{"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}]
			}
		}
		Use `all` to apply to any folder or file of any valid fluorine app.
		You can provide pattern or folder. Pattern takes precedence over folder.
		If you provide folder then it will be converted in pattern by "^%s/?.*" % folder_name, and will ignore any file and/or folder with that name.

	OUT:
		list_ff_add and list_ff_remove = {
			"app_name":set(["pattern_1", "pattern_2"])
		}

	"""
	from fluorine.utils.fjinja2.utils import c

	list_ff_add = frappe._dict()
	list_ff_remove = frappe._dict()

	for k, v in ff.iteritems():
		remove = v.get("remove") or []
		for r in remove:
			if not list_ff_remove.get(k):
				list_ff_remove[k] = []
			pattern = r.get("pattern")
			if not pattern:
				pattern = "^%s/?.*" % r.get("folder")
			cpattern = c(pattern)
			list_ff_remove[k].append(cpattern)

		add = v.get("add") or []
		for a in add:
			if not list_ff_add.get(k):
				list_ff_add[k] = []
			pattern = a.get("pattern")
			if not pattern:
				pattern = "^%s/?.*" % a.get("folder")
			cpattern = c(pattern)
			list_ff_add[k].append(cpattern)

	return list_ff_add, list_ff_remove


def _make_meteor_ignor_files():
	"""
	This list of permissions is used only by read_client_xhtml_files function.
	This permission file reflect a list of apps and the list of files and folders to ignore when read xhtml files.
	If the function don't read some xhtml (with their folder) files then they don't appears in output files to meteor app.
	As an example take highlight: "highlight/?.*".
	This regular expression will ignore everything inside folder highlight and also any file with name highlight and with any extension.
	"""
	from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app
	from fluorine.utils import get_attr_from_json
	from fluorine.utils.fjinja2.utils import c

	global list_ignores

	list_ignores = frappe._dict({meteor_web_app:{}, meteor_desk_app:{}})

	logger = logging.getLogger("frappe")

	for whatfor in whatfor_all:
		conf = get_permission_files_json(whatfor)
		list_apps_remove = process_permission_apps(conf.get("apps") or {})
		list_meteor_files_folders_add, list_meteor_files_folders_remove = process_permission_files_folders(conf.get("files_folders") or {})

		list_ignores.get(whatfor).update({
			"remove":{
				"apps": list_apps_remove,
				"files_folders": list_meteor_files_folders_remove
			},
			"add":{
				"apps": [],
				"files_folders": list_meteor_files_folders_add
			}
		})

		if meteor_config.get("production_mode") or frappe.local.making_production:
			l = get_attr_from_json([whatfor, "remove", "files_folders"], list_ignores)
			l.update({
				"all":[c("^highlight/?.*")]
				#"all":{
					#"remove": [{"pattern": c("highlight/?.*")}]
				#	"remove": [c("highlight/?.*")]
				#}
			})
			#logger.error("list_ignores inside highlight 4 {}".format(list_ignores))


	return list_ignores


def make_meteor_ignor_files():
	"""
	This list of permissions is used only by read_client_xhtml_files function.
	This permission file reflect a list of apps and the list of files and folders to ignore when read xhtml files.
	If the function don't read some xhtml (with their folder) files then they don't appears in output files to meteor app.
	As an example take highlight: "highlight/?.*".
	This regular expression will ignore everything inside folder highlight and also any file with name highlight and with any extension.
	"""
	from fluorine.utils import whatfor_all, meteor_desk_app, meteor_web_app
	from fluorine.utils import get_attr_from_json
	from fluorine.utils.fjinja2.utils import c

	global list_ignores

	list_ignores = frappe._dict({meteor_web_app:{}, meteor_desk_app:{}})

	logger = logging.getLogger("frappe")

	for whatfor in whatfor_all:
		list_meteor_files_folders_add, list_meteor_files_folders_remove, list_apps_remove = get_permission_files_json(whatfor)
		#list_apps_remove = process_permission_apps(conf.get("apps") or {})
		#list_meteor_files_folders_add, list_meteor_files_folders_remove = process_permission_files_folders(conf.get("files_folders") or {})

		list_ignores.get(whatfor).update({
			"remove":{
				"apps": list_apps_remove,
				"files_folders": list_meteor_files_folders_remove
			},
			"add":{
				"apps": [],
				"files_folders": list_meteor_files_folders_add
			}
		})

		if meteor_config.get("production_mode") or frappe.local.making_production:
			lff = get_attr_from_json([whatfor, "remove", "files_folders"], list_ignores)
			lall = lff.get("all")
			if not lall:
				lff.update({
					"all":set([c("^highlight/?.*")])
					#"all":{
						#"remove": [{"pattern": c("highlight/?.*")}]
					#	"remove": [c("highlight/?.*")]
					#}
				})
			else:
				lall.add(c("^highlights/?.*"))
			#logger.error("list_ignores inside highlight 4 {}".format(list_ignores))


	return list_ignores


def get_permission_files_json(whatfor):
	from fluorine.utils.apps import get_active_apps

	list_ff_add = frappe._dict()
	list_ff_remove = frappe._dict()

	list_apps_add = set([])
	list_apps_remove = set([])

	curr_app = meteor_config.get("current_dev_app", "").strip()
	apps = get_active_apps(whatfor)
	if curr_app != apps[0]:
		#set current dev app in last
		apps.remove(curr_app)
		apps.insert(0, curr_app)

	def process_permission_apps(conf_file):

		apps = conf_file.get("apps") or {}
		for k, v in apps.iteritems():
			if v.get("remove", 0):
				if k not in list_apps_add:
					list_apps_remove.add(k)
			elif v.get("add", 0):
				if k not in list_apps_remove:
					list_apps_add.add(k)

	def add_pattern_to_list(appname, pattern, plist):
		if not plist.get(appname):
			plist[appname] = set([])
		#pattern = obj.get("pattern")
		#if not pattern:
		#	pattern = "^%s/?.*" % obj.get("folder")
		plist[appname].add(pattern)

	def process_permission_files_folders(conf_file):

		ff = conf_file.get("files_folders") or {}
		for k, v in ff.iteritems():
			#k is appname or `all` and v is a dict with remove and/or add
			remove = v.get("remove") or []
			ladd = list_ff_add.get(k)
			for r in remove:
				found = False
				pattern = r.get("pattern") or "^%s/?.*" % r.get("folder")
				#r is an dict with pattern string of folder name
				#if k is all must agains all k
				if k == "all":
					for key, values in list_ff_add.iteritems():
						if pattern in values:
							found = True
							break
					if not found:
						add_pattern_to_list(k, pattern, list_ff_remove)
				else:
					#check if it is already added by any older app if so then don't remove
					if pattern not in ladd.get("add"):
						add_pattern_to_list(k, pattern, list_ff_remove)

			add = v.get("add") or []
			lremove = list_ff_remove.get(k)
			for a in add:
				found = False
				pattern = a.get("pattern") or "^%s/?.*" % a.get("folder")
				#if k is all must agains all k
				if k == "all":
					for key, values in list_ff_remove.iteritems():
						if pattern in values:
							found = True
							break
					if not found:
						add_pattern_to_list(k, pattern, list_ff_add)
				else:
					#a is a pattern string
					#check if it is already removed by any older app if so then don't add
					if pattern not in lremove.get("remove"):
						add_pattern_to_list(k, pattern, list_ff_add)

	def compile_pattern():
		from fluorine.utils.fjinja2.utils import c

		for k,values in list_ff_remove.iteritems():
			#remove = v.get("remove")
			list_ff_remove[k] = set([c(v) for v in values])

		for k,values in list_ff_add.iteritems():
			#add = v.get("add")
			#v["add"] = [c(r) for r in add]
			list_ff_add[k] = set([c(v) for v in values])

	#from current dev app passing by last installed to first installed
	for app in apps:
		app_path = frappe.get_app_path(app)
		perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
		if os.path.exists(perm_path):
			conf_file = frappe.get_file_json(perm_path)
			process_permission_files_folders(conf_file)
			process_permission_apps(conf_file)

	compile_pattern()

	return list_ff_add, list_ff_remove, list_apps_remove


def _get_permission_files_json(whatfor):
	from fluorine.utils.apps import get_active_apps


	curr_app = meteor_config.get("current_dev_app", "").strip()
	apps = get_active_apps(whatfor)
	if curr_app != apps[-1]:
		#set current dev app in last
		apps.remove(curr_app)
		apps.append(curr_app)

	conf_perm = frappe._dict()

	#curr develop app override everything follow by last installed app.
	for app in apps:
		app_path = frappe.get_app_path(app)
		perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
		if os.path.exists(perm_path):
			conf_file = frappe.get_file_json(perm_path)
			for k,v in conf_file.iteritems():
				key = conf_perm.get(k)
				if key:
					key.update(v)
				else:
					conf_perm[k] = v

	return conf_perm


import logging
logger = logging.getLogger("frappe")
if not meteor_config.get("production_mode") and not meteor_config.get("stop"):
	logger.error('starting reactivity...')
	start_meteor()