# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

"""
Delivery Note Return Hooks
Handles validation and processing for delivery note returns
"""

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, nowdate

def validate_delivery_note_return(doc, method=None):
    """
    Validate Delivery Note Return before saving
    
    Validates:
    - Return reason is selected for all items when is_return=1
    - Notes are provided when reason is "Other"
    - Return quantities don't exceed original delivered quantities
    - Populates company_total_stock for each item
    """
    
    if not doc.is_return:
        return
    
    print("\n" + "="*80)
    print(f"=== VALIDATE DELIVERY NOTE RETURN: {doc.name} ===")
    print("="*80)
    
    frappe.logger().info(f"=== VALIDATE DELIVERY NOTE RETURN: {doc.name} ===")
    
    # Validate return against exists
    if not doc.return_against:
        frappe.throw(_("Return Against is required for return documents"))
    
    # Get original delivery note
    original_dn = frappe.get_doc("Delivery Note", doc.return_against)
    
    # Build map of original items
    original_items = {}
    for item in original_dn.items:
        original_items[item.item_code] = {
            'qty': item.qty,
            'warehouse': item.warehouse,
            'rate': item.rate
        }
    
    # Validate return items and populate company_total_stock
    print(f"\nProcessing {len(doc.items)} items...")
    for item in doc.items:
        print(f"\n  Item: {item.item_code}")
        print(f"    Warehouse: {item.warehouse}")
        print(f"    Current company_total_stock: {item.company_total_stock or 0}")
        
        frappe.logger().info(f"Processing item {item.item_code} at warehouse {item.warehouse}")
        
        # Populate company_total_stock from Bin
        if item.item_code and item.warehouse:
            try:
                # Use frappe.db.sql for more reliable query
                bin_data = frappe.db.sql("""
                    SELECT actual_qty, projected_qty
                    FROM `tabBin`
                    WHERE item_code = %s AND warehouse = %s
                    LIMIT 1
                """, (item.item_code, item.warehouse), as_dict=True)
                
                if bin_data and len(bin_data) > 0:
                    item.company_total_stock = bin_data[0].actual_qty or 0
                    print(f"    ✓ Set company_total_stock: {item.company_total_stock}")
                    frappe.logger().info(f"✓ Set company_total_stock for {item.item_code}: {item.company_total_stock}")
                else:
                    item.company_total_stock = 0
                    print(f"    ⚠ No Bin record found, set to 0")
                    frappe.logger().warning(f"⚠ No Bin record found for {item.item_code} at {item.warehouse}, setting to 0")
            except Exception as e:
                item.company_total_stock = 0
                print(f"    ✗ Error: {str(e)}")
                frappe.logger().error(f"✗ Failed to get stock for {item.item_code}: {str(e)}")
        else:
            print(f"    ⚠ Missing item_code or warehouse")
            frappe.logger().warning(f"⚠ Missing item_code or warehouse for row {item.idx}")
        
        # Validate return reason is selected
        if not item.return_reason:
            frappe.throw(_(
                "Row {0}: Please select a return reason for item {1}"
            ).format(item.idx, item.item_code))
        
        # Validate notes when reason is "Other"
        if item.return_reason == "Other" and not item.return_item_notes:
            frappe.throw(_(
                "Row {0}: Please provide additional notes for return reason 'Other' for item {1}"
            ).format(item.idx, item.item_code))
        
        # Validate return quantity doesn't exceed delivered quantity
        if item.item_code in original_items:
            original_qty = abs(original_items[item.item_code]['qty'])
            return_qty = abs(item.qty)
            
            # Check for previous returns
            previous_returns = frappe.db.sql("""
                SELECT SUM(ABS(dni.qty)) as total_returned
                FROM `tabDelivery Note Item` dni
                INNER JOIN `tabDelivery Note` dn ON dni.parent = dn.name
                WHERE dn.docstatus = 1
                AND dn.is_return = 1
                AND dn.return_against = %s
                AND dni.item_code = %s
                AND dn.name != %s
            """, (doc.return_against, item.item_code, doc.name), as_dict=True)
            
            total_returned = previous_returns[0].total_returned or 0
            remaining_qty = original_qty - total_returned
            
            if return_qty > remaining_qty:
                frappe.throw(_(
                    "Row {0}: Return quantity ({1}) exceeds remaining returnable quantity ({2}) for item {3}. "
                    "Delivered: {4}, Previously returned: {5}"
                ).format(item.idx, return_qty, remaining_qty, item.item_code, 
                        original_qty, total_returned))
    
    print("\n" + "="*80)
    print(f"=== VALIDATION COMPLETE FOR: {doc.name} ===")
    print("="*80 + "\n")
    frappe.logger().info(f"=== VALIDATION COMPLETE FOR: {doc.name} ===")

def on_submit_delivery_note_return(doc, method=None):
    """
    Handle Delivery Note Return submission
    Sets return processed date and user
    """
    
    if not doc.is_return:
        return
    
    # Set return processed information
    doc.db_set('return_processed_date', nowdate())
    doc.db_set('return_processed_by', frappe.session.user)
    
    frappe.msgprint(_("Return processed successfully. Stock has been updated."))

def on_cancel_delivery_note_return(doc, method=None):
    """
    Handle Delivery Note Return cancellation
    Clears return processed information
    """
    
    if not doc.is_return:
        return
    
    # Clear return processed information
    doc.db_set('return_processed_date', None)
    doc.db_set('return_processed_by', None)
    
    frappe.msgprint(_("Return cancelled. Stock adjustments have been reversed."))

