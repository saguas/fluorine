app_url=["http://localhost"]
app_version=["0.0.1"]
app_email=["luisfmfernandes@gmail.com"]
app_icon=["icon-beaker"]
app_color=["#336600"]
fluorine_extras_context_method=["sidebar"]
website_clear_cache=["fluorine.utils.fcache.clear_cache"]
app_description=["The most reactive app."]
app_publisher=["Luis Fernandes"]
before_install=["fluorine.utils.install.before_install"]
app_title=["Fluorine"]
#home_page=["fluorine_home"]
after_install=["fluorine.utils.install.after_install"]
#base_template=["templates/fluorine_base.html"]
app_name=["fluorine"]
#app_include_js=["/assets/js/meteor_app.min.js"]
#app_include_css=["/assets/css/meteor_app.css"]
boot_session = "fluorine.utils.boot.boot_session"
app_include_js=["/assets/fluorine/js/fluorine_header_loader.js"]

website_route_rules = [
	{"from_route": "/desk", "to_route": "mdesk"},
]