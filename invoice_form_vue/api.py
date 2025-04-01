# apps/invoice_form_vue/api.py
import frappe
import json
from frappe import _

@frappe.whitelist()
def get_suppliers_and_customers():
    suppliers = frappe.get_all("Supplier", fields=["name", "supplier_name"])
    customers = frappe.get_all("Customer", fields=["name", "customer_name"])
    items = frappe.get_all("Item", fields=["name", "item_name"])
    return {
        "suppliers": suppliers,
        "customers": customers,
        "items": items,
    }

@frappe.whitelist()
def create_invoice(invoice_data):
    data = json.loads(invoice_data)

    if not data.get("supplier") or not data.get("customer"):
        frappe.throw(_("Supplier and Customer are required"))

    doc = frappe.new_doc("Sales Invoice") if not data.get("invoice_id") else frappe.get_doc("Sales Invoice", data["invoice_id"])
    
    doc.customer = data["customer"]["code"] if isinstance(data["customer"], dict) else data["customer"]
    doc.set_posting_time = 1
    doc.posting_date = data.get("posting_date")

    # Optional: link supplier in custom field if you're storing supplier info
    if "supplier" in data:
        doc.supplier = data["supplier"]["code"] if isinstance(data["supplier"], dict) else data["supplier"]

    # Clear existing items before update
    doc.items = []

    for item in data.get("items", []):
        doc.append("items", {
            "item_code": item["item"],
            "qty": item["qty"],
            "rate": item["rate"],
            "customer": item.get("customer", {}).get("code") if isinstance(item.get("customer"), dict) else item.get("customer"),
            "has_commission": item.get("has_commission", 0),
        })

    doc.save()
    frappe.db.commit()

    return {
        "invoice_name": doc.name,
        "supplier": doc.supplier,
        "customer": doc.customer
    }

@frappe.whitelist()
def get_invoice(invoice_name):
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    doc_data = {
        "name": doc.name,
        "supplier": doc.get("supplier"),
        "supplier_name": frappe.db.get_value("Supplier", doc.get("supplier"), "supplier_name"),
        "customer": doc.customer,
        "customer_name": frappe.db.get_value("Customer", doc.customer, "customer_name"),
        "items": []
    }

    for item in doc.items:
        doc_data["items"].append({
            "item_code": item.item_code,
            "qty": item.qty,
            "price": item.rate,
            "total": item.amount,
            "customer": item.get("customer"),
            "customer_name": frappe.db.get_value("Customer", item.get("customer"), "customer_name") if item.get("customer") else "",
            "has_commission": item.get("has_commission", 0)
        })

    return doc_data

@frappe.whitelist()
def delete_invoice(invoice_name):
    frappe.delete_doc("Sales Invoice", invoice_name)
    frappe.db.commit()
    return {"status": "deleted"}

@frappe.whitelist()
def remove_from_invoice(invoice_name):
    # Example logic to submit the invoice
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    if doc.docstatus == 0:
        doc.submit()
        frappe.db.commit()
        return {"status": "submitted"}
    else:
        frappe.throw(_("Invoice is already submitted."))
