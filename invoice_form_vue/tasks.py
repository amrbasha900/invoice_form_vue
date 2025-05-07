import frappe
from frappe.utils import get_time, now_datetime
from datetime import datetime, time, timedelta

def check_lock_update_invoice_form():
    # Get the reference time from single DocType
    reference_time = frappe.db.get_single_value("Invoice Form Permission", "can_not_edit_after")
    
    # Debug the type of reference_time
    frappe.logger().info(f"Reference time: {reference_time}, Type: {type(reference_time)}")
    
    # Exit if no reference time is set
    if not reference_time:
        return
    
    # Get current datetime and extract time component
    current_datetime = now_datetime()
    current_time = current_datetime.time()
    
    # Parse the reference time - THIS IS THE CRITICAL PART
    # Based on the error, it seems reference_time is coming in as a timedelta
    if isinstance(reference_time, timedelta):
        # Convert timedelta to time of day
        # Assuming the timedelta represents seconds from midnight
        seconds = reference_time.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        ref_time = time(hours, minutes, seconds)
        
        frappe.logger().info(f"Converted timedelta {reference_time} to time {ref_time}")
    elif isinstance(reference_time, str):
        # If it's a string like "13:00:00"
        ref_time = get_time(reference_time)
    else:
        # If it's already a time object
        ref_time = reference_time
    
    frappe.logger().info(f"Current time: {current_time}, Reference time: {ref_time}")
    
    # Compare only the time part
    if current_time >= ref_time:
        # Get all unlocked invoice forms
        invoices = frappe.get_all("Invoice Form", {"lock_update": 0}, "name")
        
        # Format invoice names for logging
        invoice_names = [inv.name for inv in invoices] if invoices else []
        invoice_str = ", ".join(invoice_names)
        
        frappe.log_error(title="Invoice Form Permission", 
                         message=f"Invoice Form Permission expired at {ref_time}. Locking invoices: {invoice_str}")
        
        # Lock all the invoices
        for invoice in invoices:
            frappe.db.set_value("Invoice Form", invoice.name, "lock_update", 1)
        
        # Commit the transaction
        frappe.db.commit()