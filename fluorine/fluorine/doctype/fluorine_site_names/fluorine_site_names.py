# -*- coding: utf-8 -*-
# Copyright (c) 2015, Luis Fernandes and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FluorineSiteNames(Document):

	def on_update(self, method=None):
		from fluorine.utils import meteor_config
		from fluorine.utils.meteor.utils import update_common_config

		sites = meteor_config.get("sites")
		if not sites:
			meteor_config["sites"] = {}
			sites = meteor_config.get("sites")
		sites[self.fluorine_site_name] = site = {}

		site["type"] = self.fluorine_site_type
		site["desk_prefix"] = self.fluorine_desk_site_root_prefix
		site["ddp_desk"] = self.fluorine_desk_ddp_conn_url
		site["web_integration"] = self.fluorine_frappe_web_integration
		if self.fluorine_frappe_web_integration:
			site["web_prefix"] = self.fluorine_web_site_root_prefix
			site["ddp_web"] = self.fluorine_web_ddp_conn_url
		site["parent_site"] = self.fluorine_site_depends_of_name

		site["addresses"] = addrs = []
		for app in self.fluorine_table_site_addr:
			addrs.append({"type": app.fluorine_site_ip_type, "root_url": app.fluorine_site_ip, "port": app.fluorine_site_port})

		site["dependents"] = depend = []
		for site in self.fluorine_table_site_dependents:
			depend.append(site.fluorine_site_name)

		update_common_config(meteor_config)


	def validate(self, method=None):
		from fluorine.utils import is_valid_site, update_file_map_site


		if not is_valid_site(self.fluorine_site_name):
			return frappe.throw("The site %s is not a valid site. Please create the site first." % self.fluorine_site_name)

		if self.fluorine_site_type == "Dedicated":

			if not self.fluorine_desk_ddp_conn_url or self.fluorine_desk_ddp_conn_url.strip() == "":
				return frappe.throw("For Dedicated site you must provide a valid DDP ip/url for desk app.")
			elif not self.fluorine_desk_site_root_prefix or self.fluorine_desk_site_root_prefix.strip() == "":
				return frappe.throw("For Dedicated site you must provide a valid root url path prefix for desk app.")

			len_tables_ips = len(self.fluorine_table_site_addr)
			if len_tables_ips == 0 or len_tables_ips == 1:
				return frappe.throw("For Dedicated site you must provide ip and port for web and desk app.")
			elif len_tables_ips > 1:
				cw = 0
				cd = 0
				for app in self.fluorine_table_site_addr:
					if app.fluorine_site_ip_type == "Web":
						cw = cw + 1
					else:
						cd = cd + 1
				if cw < 1 or cd < 1:
					return frappe.throw("For Dedicated site you must provide ip and port for web and desk app. You have 0 %s" % ("Web" if cw==0 else "Desk"))

			len_table_site_dependents = len(self.fluorine_table_site_dependents)
			if len_table_site_dependents > 0:
				for site in self.fluorine_table_site_dependents:
					if site.fluorine_site_name == self.name:
						frappe.throw("It is not permited to have itself as depend.")

					#frappe.cache().set_value("fluorine:site:%s" % site.fluorine_site_name, self.name)
					update_file_map_site({site.fluorine_site_name: self.name})

			#frappe.cache().set_value("fluorine:site:%s" % self.name, self.name)
			update_file_map_site({self.name: self.name})

		else:
			if not self.fluorine_site_depends_of_name or self.fluorine_site_depends_of_name.strip() == "":
				return frappe.throw("For integrated site you must provide a valid depend of site.")
			elif self.fluorine_site_depends_of_name.strip() == self.name:
				return frappe.throw("For integrated site you must provide a valid depend of site. It is not permited to depend of itself.")
			else:
				depend_of = self.fluorine_site_depends_of_name.strip()
				doc = frappe.get_doc("Fluorine Site Names", depend_of)
				if doc.fluorine_site_type == "Integrated":
					return frappe.throw("Sorry, but you must depend only of Dedicated sites.")


