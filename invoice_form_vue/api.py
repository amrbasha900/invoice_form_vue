# apps/invoice_form_vue/api.py
import frappe
import json
from frappe import _
import frappe.translate
import datetime


@frappe.whitelist()
def get_suppliers_and_customers():
    suppliers = frappe.get_list("Supplier", fields=["name", "supplier_name"])
    customers = frappe.get_list("Customer", filters={'is_customer':1, 'is_frozen':0},fields=["name", "customer_name"])
    items = frappe.get_list("Item", filters={'commission_item':0},fields=["name", "item_name"])
    return {
        "suppliers": suppliers,
        "customers": customers,
        "items": items,
    }

@frappe.whitelist()
def create_invoice(invoice_data):
    try:
        data = json.loads(invoice_data)
        frappe.logger().info(f"📥 Incoming invoice data: {data}")

        if not data.get("supplier"):
            frappe.throw(_("Supplier and Customer are required"))

        # Create or fetch doc
        doc = (
            frappe.new_doc("Invoice Form")
            if not data.get("invoice_id")
            else frappe.get_doc("Invoice Form", data["invoice_id"])
        )
        pamper = None
        if not data.get("invoice_id"):
            pamper = frappe.db.get_value("Customer", {'pamper_user': frappe.session.user}, "name")
            if pamper:
                doc.pamper = pamper
        doc.customer = data["customer"]["code"] if isinstance(data["customer"], dict) else data["customer"]
        doc.posting_date = data.get("posting_date")

        if "supplier" in data:
            doc.supplier = data["supplier"]["code"] if isinstance(data["supplier"], dict) else data["supplier"]

        # Clear & append items
        doc.items = []

        for item in data.get("items", []):
            doc.append("items", {
                "item_code": item["item"],
                "qty": item["qty"],
                "price": item["rate"],
                "total":item["rate"] * item["qty"],
                "customer": item.get("customer", {}).get("code") if isinstance(item.get("customer"), dict) else item.get("customer"),
                "has_commission": item.get("has_commission", 0),  # optional cleanup if field still exists
                "pamper": pamper
            })

        doc.save()
        
        frappe.db.commit()

        frappe.logger().info(f"✅ Invoice saved: {doc.name}")

        return {
            "invoice_name": doc.name,
            "supplier": doc.supplier,
            "customer": doc.customer
        }

    except Exception as e:
        error_message = frappe.get_traceback()
        frappe.log_error(title="❌ Invoice Creation Failed", message=error_message)
        frappe.db.rollback()
        frappe.throw(_("Something went wrong while saving the invoice. Please contact support."))

@frappe.whitelist()
def get_invoice(invoice_name):
    doc = frappe.get_doc("Invoice Form", invoice_name)
    doc_data = {
        "name": doc.name,
        "supplier": doc.get("supplier"),
        "supplier_name": frappe.db.get_value("Supplier", doc.get("supplier"), "supplier_name"),
        "customer": doc.customer,
        "customer_name": frappe.db.get_value("Customer", doc.customer, "customer_name") or '',
        "is_draft": doc.is_draft,
        "lock_update": doc.lock_update,
        "items": []
    }

    for item in doc.items:
        doc_data["items"].append({
            "item_code": item.item_code,
            "qty": item.qty,
            "price": item.price,
            "total": item.total,
            "customer": item.get("customer"),
            "customer_name": frappe.db.get_value("Customer", item.get("customer"), "customer_name") if item.get("customer") else "",
            "has_commission": item.get("has_commission", 0)
        })

    return doc_data

@frappe.whitelist()
def delete_invoice(invoice_name):
    frappe.delete_doc("Invoice Form", invoice_name, ignore_permissions=False)
    frappe.db.commit()
    return {"status": "deleted"}

@frappe.whitelist()
def remove_from_invoice(invoice_name):
    # Example logic to submit the invoice
    doc = frappe.get_doc("Invoice Form", invoice_name)
    if doc.docstatus == 0:
        doc.is_draft = 0
        doc.save(ignore_permissions=False)
        frappe.db.commit()
        return {"status": "submitted"}
    else:
        frappe.throw(_("Invoice is already submitted."))

@frappe.whitelist()
def get_draft_invoice_form():
    """
    Retrieve invoices for the current user based on permission settings.
    Returns a list of invoice objects with basic information.
    """
    try:
        # Check user permission from Invoice Form Permission Details
        user_permissions = frappe.get_all(
            "Invoice Form Permission Details",
            filters={"user": frappe.session.user},
            fields=["parent", "show_drafts", "show_submitted", "update_draft_invoice", "view_draft_hour"]
        )
        
        # Default filters
        filters = {"owner": frappe.session.user, "docstatus":0}
        
        # Process permissions
        show_drafts = False
        show_submitted = False
        view_draft_hour = 0
        
        if user_permissions:
            permission = user_permissions[0]
            show_drafts = permission.get("show_drafts", 0)
            show_submitted = permission.get("show_submitted", 0)
            view_draft_hour = permission.get("view_draft_hour", 0)
        
        # If user has no permissions to see any invoices, return empty list
        if not show_drafts and not show_submitted:
            return {"invoices": []}
        
        # Build docstatus filter based on permissions
        docstatus_filter = []
        if show_drafts:
            docstatus_filter.append(1)  # Include drafts
        if show_submitted:
            docstatus_filter.append(0)  # Include submitted
        
        filters["is_draft"] = ["in", docstatus_filter]
        
        # Add time filter based on view_draft_hour if applicable
        if view_draft_hour > 0:
            hours_ago = datetime.datetime.now() - datetime.timedelta(hours=view_draft_hour)
            filters["creation"] = [">", hours_ago]
        
        # Get invoices based on filters
        invoices = frappe.get_all(
            "Invoice Form",
            filters=filters,
            fields=[
                "name", 
                "posting_date", 
                "customer", 
                "customer_name", 
                "supplier", 
                "supplier_name",
                "modified",
                "docstatus",
                "is_draft"
            ],
            order_by="modified desc",
            ignore_permissions=False
        )

        # For each invoice, get the items to show the count
        for invoice in invoices:
            # Convert date format if needed
            if invoice.get("posting_date"):
                invoice["posting_date"] = invoice["posting_date"].strftime("%Y-%m-%d")
            
            # Get items count
            items = frappe.get_all(
                "Invoice Form Item",
                filters={"parent": invoice.name},
                fields=["name"]
            )
            invoice["items"] = items
        
        return {"invoices": invoices}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Failed to fetch invoices"))
        return {"error": str(e), "invoices": []}

@frappe.whitelist()
def get_dashboard_data():
    """
    Get dashboard data including counts and recent invoices.
    
    Returns:
        dict: Dashboard statistics and recent invoice list
    """
    try:
        # Get draft invoice count
        draft_count = frappe.db.count(
            "Invoice Form",  # Use your actual doctype name
            {"docstatus": 0, 'is_draft':1}  # docstatus 0 means draft
        )
        
        # Get submitted invoice count
        submitted_count = frappe.db.count(
            "Invoice Form",  # Use your actual doctype name
            {"docstatus": 1}  # docstatus 1 means submitted
        )
        
        # Get recent invoices (both draft and submitted)
        recent_invoices = frappe.get_all(
            "Invoice Form",
            filters={ 'owner': frappe.session.user}  ,  # Use your actual doctype name
            fields=[
                "name", 
                "posting_date", 
                "customer", 
                "customer_name", 
                "supplier", 
                "supplier_name",
                "docstatus",
                "modified"
            ],
            order_by="modified desc",
            limit=10,
            ignore_permissions=False
        )
        
        # Add status text and format dates
        for invoice in recent_invoices:
            invoice["status"] = "Submitted" if invoice.get("docstatus") == 1 else "Draft"
            if invoice.get("posting_date"):
                invoice["posting_date"] = invoice["posting_date"].strftime("%Y-%m-%d")
        
        return {
            "message": {
                "draft_count": draft_count,
                "submitted_count": submitted_count,
                "recent_invoices": recent_invoices
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Failed to fetch dashboard data"))
        frappe.throw(_("Failed to fetch dashboard data: {0}").format(str(e)))

@frappe.whitelist(allow_guest=True)
def get_app_translations():
	if frappe.session.user != "Guest":
		language = frappe.db.get_value("User", frappe.session.user, "language")
	else:
		language = frappe.db.get_single_value("System Settings", "language")

	return language


@frappe.whitelist()
def set_user_language(language):
    user = frappe.session.user
    if not language:
        frappe.throw("Language not specified")

    frappe.db.set_value("User", user, "language", language)
    frappe.clear_cache(user=user)
    return {"status": "success", "language": language}




@frappe.whitelist()
def check_user_permission(user):
    """Check user permissions for Invoice Form app"""
    if not user:
        return {
            "can_login": False,
            "can_delete_invoice": False,
            "can_submit_invoice": False,
            "can_update_draft": False,
            "can_update_submitted": False,
            "can_show_drafts": False,
            "can_show_submitted": False
        }
    
    # Query the Invoice Form Permission Details for this user
    permission_record = frappe.db.sql("""
        SELECT 
            login,
            delete_invoice,
            submit_invoice,
            update_draft_invoice,
            update_submitted_invoice,
            show_drafts,
            show_submitted
        FROM `tabInvoice Form Permission Details` 
        WHERE user = %s
    """, (user,), as_dict=1)
    
    # Default permissions if no record found
    permissions = {
        "can_login": False,
        "can_delete_invoice": False,
        "can_submit_invoice": False,
        "can_update_draft": False,
        "can_update_submitted": False,
        "can_show_drafts": False,
        "can_show_submitted": False
    }
    
    # Update with actual permissions if record exists
    if permission_record:
        record = permission_record[0]
        permissions = {
            "can_login": record.login == 1,
            "can_delete_invoice": record.delete_invoice == 1,
            "can_submit_invoice": record.submit_invoice == 1,
            "can_update_draft": record.update_draft_invoice == 1,
            "can_update_submitted": record.update_submitted_invoice == 1,
            "can_show_drafts": record.show_drafts == 1,
            "can_show_submitted": record.show_submitted == 1
        }
    
    return permissions