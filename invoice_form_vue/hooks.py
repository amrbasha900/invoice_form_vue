app_name = "invoice_form_vue"
app_title = "Invoice Form Vue"
app_publisher = "Amr Basha"
app_description = "this app build in vue3 js in frappe to change invoice form interface "
app_email = "amrbasha9000@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "invoice_form_vue",
# 		"logo": "/assets/invoice_form_vue/logo.png",
# 		"title": "Invoice Form Vue",
# 		"route": "/invoice_form_vue",
# 		"has_permission": "invoice_form_vue.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/invoice_form_vue/css/invoice_form_vue.css"
# app_include_js = "/assets/invoice_form_vue/js/invoice_form_vue.js"

# include js, css files in header of web template
# web_include_css = "/assets/invoice_form_vue/css/invoice_form_vue.css"
# web_include_js = "/assets/invoice_form_vue/js/invoice_form_vue.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "invoice_form_vue/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "invoice_form_vue/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "invoice_form_vue.utils.jinja_methods",
# 	"filters": "invoice_form_vue.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "invoice_form_vue.install.before_install"
# after_install = "invoice_form_vue.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "invoice_form_vue.uninstall.before_uninstall"
# after_uninstall = "invoice_form_vue.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "invoice_form_vue.utils.before_app_install"
# after_app_install = "invoice_form_vue.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "invoice_form_vue.utils.before_app_uninstall"
# after_app_uninstall = "invoice_form_vue.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "invoice_form_vue.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
 	"all": [
 		"invoice_form_vue.tasks.check_lock_update_invoice_form"
 	],
# 	"daily": [
# 		"invoice_form_vue.tasks.daily"
# 	],
# 	"hourly": [
# 		"invoice_form_vue.tasks.hourly"
# 	],
# 	"weekly": [
# 		"invoice_form_vue.tasks.weekly"
# 	],
# 	"monthly": [
# 		"invoice_form_vue.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "invoice_form_vue.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "invoice_form_vue.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "invoice_form_vue.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["invoice_form_vue.utils.before_request"]
# after_request = ["invoice_form_vue.utils.after_request"]

# Job Events
# ----------
# before_job = ["invoice_form_vue.utils.before_job"]
# after_job = ["invoice_form_vue.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"invoice_form_vue.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


website_route_rules = [{'from_route': '/invoice_form/<path:app_path>', 'to_route': 'invoice_form'},]

fixtures = [
    {"dt": "Custom Field", "filters": [["name", "in", [
        "Invoice Form-custom_is_draft","Customer-custom_pamper_user",
        "Invoice Form-custom_lock_update"
        ]]]},
]
