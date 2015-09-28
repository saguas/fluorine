__author__ = 'luissaguas'


import frappe, os, logging


list_ignores = None


def make_ignor_apps_list():
	from fluorine.utils import APPS as apps, whatfor_all, meteor_desk_app, meteor_web_app
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils import meteor_config


	global list_ignores

	if list_ignores != None:
		return list_ignores

	list_ignores = frappe._dict({meteor_web_app:{}, meteor_desk_app:{}})

	logger = logging.getLogger("frappe")

	current_site = get_default_site()

	curr_app = meteor_config.get("current_dev_app", "").strip()
	know_apps = apps[::]
	if curr_app != know_apps[-1]:
		#set current dev app in last
		apps.remove(curr_app)
		apps.append(curr_app)

	for whatfor in whatfor_all:
		pfs_in = ProcessFileSystem(whatfor, curr_app)
		##keys are the sites and value is a list of dicts of apps and server_writes to use in the site
		#list_only_for_sites = {}
		only_for_sites = {current_site: []}
		list_know_apps = know_apps[::]
		# Apps removed by current dev app does not remove anything.
		# The same is true for first installed apps that do not removed anything if they are removed by last installed apps.
		while list_know_apps:
			app = list_know_apps.pop()
			app_path = frappe.get_app_path(app)
			meteor_app = os.path.join(app_path, "templates", "react", whatfor)

			if not os.path.exists(meteor_app):
				try:
					list_know_apps.remove(app)
				except:
					pass
				continue

			perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
			if os.path.exists(perm_path):
				conf_file = frappe.get_file_json(perm_path)
				conf_apps = conf_file.get("apps") or {}
				list_only_for_sites = get_list_only_apps_for_site(app, whatfor, conf_in=conf_apps)
				only_for_sites.update(list_only_for_sites)
				pfs_in.feed_apps(conf_apps)
				apps_remove = pfs_in.get_apps_remove()
				if not is_app_for_site(app, list_only_for_sites):
					apps_remove.add(app)
				for r in apps_remove:
					try:
						list_know_apps.remove(r)
					except:
						pass
			else:
				only_for_sites.get(current_site).append(app)

		list_apps_remove = pfs_in.get_apps_remove()#get_permission_files_json(whatfor)

		list_ignores.get(whatfor).update({
			"remove":{
				"apps": list_apps_remove,
			},
			"only_for_sites": only_for_sites#,
		})

		#logger.error("list_ignores inside highlight {} w {} apps {}".format(list_ignores.get(whatfor), whatfor, know_apps))

	return list_ignores


def is_app_for_site(app, list_only_for_sites, site=None):
	from fluorine.commands_helpers import get_default_site

	current_site = site
	if not current_site:
		current_site = get_default_site()

	logger = logging.getLogger("frappe")
	#logger.error("current site {} app {} list {}".format(current_site, app, list_only_for_sites))
	if app in list_only_for_sites.get(current_site):
		return True
	#app_only_for = list_only_for_sites.get(app) or []
	#for obj in list_only_for_sites.get(app, []):
	#	if obj.get("site") == current_site:
	#		return obj.get("server_writes")

	return False


def get_list_only_apps_for_site(app, whatfor, conf_in=None):
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils import is_valid_site

	list_only_for_sites = {}
	current_site = get_default_site()

	if not conf_in:
		app_path = frappe.get_app_path(app)
		perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
		if os.path.exists(perm_path):
			conf_file = frappe.get_file_json(perm_path)
			conf_in = conf_file.get("IN") or conf_file.get("in") or {}
		else:
			return list_only_for_sites

	sites = conf_in.get("only_for_sites") or []
	if not sites:
		#if get nothing for app it is because this app is for all sites
		if not list_only_for_sites.get(current_site):
			list_only_for_sites[current_site] = []
		#list_only_for_sites[app] = [{"site": current_site, "server_writes": True}]
		list_only_for_sites.get(current_site).append(app)

	for site in sites:
		if not is_valid_site(site):
			continue

		if not list_only_for_sites.get(site):
			#list_only_for_sites[app] = []
			list_only_for_sites[site] = []
		#list_only_for_sites.get(app).append(site)
		list_only_for_sites.get(site).append(app)
	#else:
		#if there is no permission file this is because this app is for all sites
		#list_only_for_sites[app] = [{"site": current_site, "server_writes": True}]
	#	if not list_only_for_sites.get(current_site):
	#		list_only_for_sites[current_site] = []
	#	list_only_for_sites.get(current_site).append(app)

	return list_only_for_sites

#TODO to remove
def make_meteor_ignor_files():
	"""
	This list of permissions is used only by read_client_xhtml_files function.
	This permission file reflect a list of apps and the list of files and folders to ignore when read xhtml files.
	If the function don't read some xhtml (with their folder) files then they don't appears in output files to meteor app.
	As an example take highlight: "highlight/?.*".
	This regular expression will ignore everything inside folder highlight and also any file with name highlight and with any extension.
	"""
	from fluorine.utils import APPS as apps, whatfor_all, meteor_desk_app, meteor_web_app#, get_attr_from_json
	from fluorine.commands_helpers import get_default_site
	from fluorine.utils import meteor_config

	global list_ignores

	if list_ignores != None:
		return list_ignores

	list_ignores = frappe._dict({meteor_web_app:{}, meteor_desk_app:{}})

	logger = logging.getLogger("frappe")

	current_site = get_default_site()

	curr_app = meteor_config.get("current_dev_app", "").strip()
	know_apps = apps[::]
	if curr_app != know_apps[-1]:
		#set current dev app in last
		apps.remove(curr_app)
		apps.append(curr_app)

	for whatfor in whatfor_all:
		pfs_in = ProcessFileSystem(whatfor, curr_app)
		##keys are the sites and value is a list of dicts of apps and server_writes to use in the site
		#list_only_for_sites = {}
		only_for_sites = {current_site: []}
		list_know_apps = know_apps[::]
		# Apps removed by current dev app does not remove anything.
		# The same is true for first installed apps that do not removed anything if they are removed by last installed apps.
		while list_know_apps:
			app = list_know_apps.pop()
			app_path = frappe.get_app_path(app)
			meteor_app = os.path.join(app_path, "templates", "react", whatfor)

			if not os.path.exists(meteor_app):
				try:
					list_know_apps.remove(app)
				except:
					pass
				continue

			perm_path = os.path.join(app_path, "templates", "react", whatfor, "permissions.json")
			if os.path.exists(perm_path):
				conf_file = frappe.get_file_json(perm_path)
				conf_in = conf_file.get("IN") or conf_file.get("in") or {}
				list_only_for_sites = get_list_only_apps_for_site(app, whatfor, conf_in=conf_in)
				only_for_sites.update(list_only_for_sites)
				pfs_in.feed_apps(conf_in)
				apps_remove = pfs_in.get_apps_remove()
				if not is_app_for_site(app, list_only_for_sites):
					apps_remove.add(app)
				for r in apps_remove:
					try:
						list_know_apps.remove(r)
					except:
						pass
			else:
				only_for_sites.get(current_site).append(app)

		list_apps_remove = pfs_in.get_apps_remove()#get_permission_files_json(whatfor)

		list_ignores.get(whatfor).update({
			"remove":{
				"apps": list_apps_remove,
			},
			"only_for_sites": only_for_sites#,
		})

		#logger.error("list_ignores inside highlight {} w {} apps {}".format(list_ignores.get(whatfor), whatfor, know_apps))

	return list_ignores


class ProcessFileSystem(object):

	def __init__(self, whatfor, curr_dev_app):
		self.whatfor = whatfor
		self.curr_dev_app = curr_dev_app

		self.list_apps_add = set([])
		self.list_apps_remove = set([])

		self.logger = logging.getLogger("frappe")

	def feed_apps(self, conf_file):
		self.process_permission_apps(conf_file)

	def get_apps_add(self):
		return self.list_apps_add

	def get_apps_remove(self):
		return self.list_apps_remove

	def process_permission_apps(self, conf_file):
		from fluorine.utils import meteor_config, is_making_production

		devmode = meteor_config.get("developer_mode")
		prodmode = meteor_config.get("production_mode") or is_making_production()

		apps = conf_file.get("apps") or {}
		if self.curr_dev_app in apps:
			apps.remove(self.curr_dev_app)


		for k, v in apps.iteritems():
			constrains = v.get("constrains")
			if v.get("remove", 0):
				if k not in self.list_apps_add:
					if constrains == "dm" and not devmode or constrains == "pm" and not prodmode:
						continue
					self.list_apps_remove.add(k)
			elif v.get("add", 0):
				if k not in self.list_apps_remove:
					self.list_apps_add.add(k)


#TODO to remove
class _ProcessFileSystem(object):

	def __init__(self, whatfor, curr_dev_app):
		self.whatfor = whatfor
		self.curr_dev_app = curr_dev_app

		self.list_ff_add = frappe._dict()
		self.list_ff_remove = frappe._dict()

		self.list_apps_add = set([])
		self.list_apps_remove = set([])

		self.logger = logging.getLogger("frappe")

	def feed_files_folders(self, conf_file):
		self.process_permission_files_folders(conf_file)

	def feed_apps(self, conf_file):
		self.process_permission_apps(conf_file)

	def compile(self):
		self.compile_pattern()

	def get_add_files_folders(self):
		return self.list_ff_add

	def get_remove_files_folders(self):
		return self.list_ff_remove

	def get_apps_add(self):
		return self.list_apps_add

	def get_apps_remove(self):
		return self.list_apps_remove

	"""
	def get_permission_files_json(self):
		from fluorine.utils.apps import get_active_apps

		curr_app = meteor_config.get("current_dev_app", "").strip()
		apps = get_active_apps(self.whatfor)
		if curr_app != apps[0]:
			#set current dev app in last
			apps.remove(curr_app)
			apps.insert(0, curr_app)
	"""
	def process_permission_apps(self, conf_file):
		from fluorine.utils import meteor_config, is_making_production

		devmode = meteor_config.get("developer_mode")
		prodmode = meteor_config.get("production_mode") or is_making_production()

		apps = conf_file.get("apps") or {}
		if self.curr_dev_app in apps:
			apps.remove(self.curr_dev_app)


		for k, v in apps.iteritems():
			constrains = v.get("constrains")
			if v.get("remove", 0):
				if k not in self.list_apps_add:
					if constrains == "dm" and not devmode or constrains == "pm" and not prodmode:
						continue
					self.list_apps_remove.add(k)
			elif v.get("add", 0):
				if k not in self.list_apps_remove:
					self.list_apps_add.add(k)


	def add_pattern_to_list(self, appname, pattern, plist):
		if not pattern:
			return
		if not plist.get(appname):
			plist[appname] = set([])
		plist[appname].add(pattern)

	def process_permission_files_folders(self, conf_file):
		"""
		below app_name is a valid fluorine app and pattern is any valid regular expression.
		See make_meteor_ignor_files below for more information.

		Structure:

		IN:
			ff = {
				"app_name":{
					remove:[{"folder": "folder_name"}, {"file": "file_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}],
					add:[{"file": "file_name"}, {"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}]
				},
				"all": {
					remove: [{"file": "file_name"}, {"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}],
					add:[{"file": "file_name"}, {"folder": "folder_name"}, {"pattern": "pattern_1"}, {"pattern": "pattern_2"}]
				}
			}
			Use `all` to apply to any folder or file of any valid fluorine app.
			You can provide pattern or folder. Pattern takes precedence over folder.
			If you provide folder then it will be converted in pattern by "^%s/.*|^%s$" % (folder_name, folder_name) and will ignore any file and/or folder with that name.
			If you provide a file stay as is.
		OUT:
			list_ff_add and list_ff_remove = {
				"app_name":set(["pattern_1", "pattern_2"])
			}

		"""
		ff = conf_file.get("files_folders") or {}
		#logger.error("list_ignores inside highlight {}".format(ff))
		#logger.error("list_ignores inside highlight {}".format(ff))
		for k, v in ff.iteritems():
			#k is appname or `all` and v is a dict with remove and/or add
			remove = v.get("remove") or []
			ladd = self.list_ff_add.get(k, {})
			for r in remove:
				found = False
				pattern = r.get("pattern")
				if not pattern:
					folder = r.get("folder")
					if folder:
						if folder.endswith("/"):
							folder = folder.rsplit("/",1)[0]
						pattern = "^%s/.*|^%s$" % (folder, folder)
					else:
						pattern = r.get("file")
				#r is an dict with pattern string of folder name
				#if k is all must agains all k
				if k == "all":
					for key, values in self.list_ff_add.iteritems():
						if pattern in values:
							found = True
							break
					if not found:
						self.add_pattern_to_list(k, pattern, self.list_ff_remove)
				else:
					#check if it is already added by any older app if so then don't remove
					if pattern not in ladd.get("add", []):
						self.add_pattern_to_list(k, pattern, self.list_ff_remove)

			add = v.get("add") or []
			lremove = self.list_ff_remove.get(k, {})
			for a in add:
				found = False
				pattern = a.get("pattern")
				if not pattern:
					folder = a.get("folder")
					if folder:
						if folder.endswith("/"):
							folder = folder.rsplit("/",1)[0]
						pattern = "^%s/.*|^%s$" % (folder, folder)
					else:
						pattern = a.get("file")
				#if k is all must be agains all k
				if k == "all":
					for key, values in self.list_ff_remove.iteritems():
						if pattern in values:
							found = True
							break
					if not found:
						self.add_pattern_to_list(k, pattern, self.list_ff_add)
				else:
					#a is a pattern string
					#check if it is already removed by any older app if so then don't add
					if pattern not in lremove.get("remove", []):
						self.add_pattern_to_list(k, pattern, self.list_ff_add)

	def compile_pattern(self):
		from fluorine.utils.fjinja2.utils import c

		for k,values in self.list_ff_remove.iteritems():
			self.list_ff_remove[k] = set([c(v) for v in values])

		for k,values in self.list_ff_add.iteritems():
			self.list_ff_add[k] = set([c(v) for v in values])