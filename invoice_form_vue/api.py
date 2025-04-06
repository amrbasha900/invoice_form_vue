# apps/invoice_form_vue/api.py
import frappe
import json
from frappe import _
import frappe.translate

@frappe.whitelist()
def get_suppliers_and_customers():
    suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name"])
    customers = frappe.get_all("Customer", filters={'is_customer':1, 'is_frozen':0},fields=["name", "customer_name"])
    items = frappe.get_all("Item", filters={'commission_item':0},fields=["name", "item_name"])
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
    Retrieve all draft invoices for the current user.
    Returns a list of invoice objects with basic information.
    """
    try:
        # Get all draft invoices
        invoices = frappe.get_all(
            "Invoice Form",  # Use your actual doctype name here
            filters={"docstatus": 0, 'is_draft':1, 'owner': frappe.session.user},  # docstatus 0 means draft
            fields=[
                "name", 
                "posting_date", 
                "customer", 
                "customer_name", 
                "supplier", 
                "supplier_name",
                "modified"
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
                "Invoice Form Item",  # Use your actual child doctype name here
                filters={"parent": invoice.name},
                fields=["name"]
            )
            invoice["items"] = items
        
        return {"invoices": invoices}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Failed to fetch draft invoices"))
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