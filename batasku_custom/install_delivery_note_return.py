# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

"""
Installation script for Delivery Note Return custom fields
Run this after installing batasku_custom app
"""

from __future__ import unicode_literals
import frappe
from batasku_custom.custom_fields.delivery_note_return_fields import add_delivery_note_return_fields

def install():
    """
    Install custom fields for Delivery Note Return tracking
    
    Usage:
        bench --site [site-name] console
        >>> from batasku_custom.install_delivery_note_return import install
        >>> install()
    """
    
    print("Installing Delivery Note Return custom fields...")
    
    try:
        add_delivery_note_return_fields()
        print("✓ Custom fields installed successfully")
        
        # Verify installation
        verify_installation()
        
    except Exception as e:
        print(f"✗ Installation failed: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Delivery Note Return Installation Failed")
        raise

def verify_installation():
    """Verify that custom fields were installed correctly"""
    
    print("\nVerifying installation...")
    
    # Check Delivery Note fields
    dn_fields = [
        'return_section',
        'return_processed_date',
        'return_processed_by',
        'return_notes'
    ]
    
    for fieldname in dn_fields:
        exists = frappe.db.exists('Custom Field', {
            'dt': 'Delivery Note',
            'fieldname': fieldname
        })
        
        if exists:
            print(f"✓ Delivery Note.{fieldname} - OK")
        else:
            print(f"✗ Delivery Note.{fieldname} - MISSING")
    
    # Check Delivery Note Item fields
    dni_fields = [
        'return_reason',
        'return_item_notes'
    ]
    
    for fieldname in dni_fields:
        exists = frappe.db.exists('Custom Field', {
            'dt': 'Delivery Note Item',
            'fieldname': fieldname
        })
        
        if exists:
            print(f"✓ Delivery Note Item.{fieldname} - OK")
        else:
            print(f"✗ Delivery Note Item.{fieldname} - MISSING")
    
    print("\nInstallation verification complete!")

def uninstall():
    """
    Remove custom fields for Delivery Note Return tracking
    
    Usage:
        bench --site [site-name] console
        >>> from batasku_custom.install_delivery_note_return import uninstall
        >>> uninstall()
    """
    
    print("Uninstalling Delivery Note Return custom fields...")
    
    try:
        # Remove Delivery Note fields
        dn_fields = [
            'return_section',
            'return_processed_date',
            'return_processed_by',
            'column_break_return_1',
            'return_notes'
        ]
        
        for fieldname in dn_fields:
            if frappe.db.exists('Custom Field', {'dt': 'Delivery Note', 'fieldname': fieldname}):
                frappe.delete_doc('Custom Field', f'Delivery Note-{fieldname}')
                print(f"✓ Removed Delivery Note.{fieldname}")
        
        # Remove Delivery Note Item fields
        dni_fields = [
            'return_reason',
            'return_item_notes'
        ]
        
        for fieldname in dni_fields:
            if frappe.db.exists('Custom Field', {'dt': 'Delivery Note Item', 'fieldname': fieldname}):
                frappe.delete_doc('Custom Field', f'Delivery Note Item-{fieldname}')
                print(f"✓ Removed Delivery Note Item.{fieldname}")
        
        frappe.db.commit()
        print("\n✓ Uninstallation complete!")
        
    except Exception as e:
        print(f"✗ Uninstallation failed: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Delivery Note Return Uninstallation Failed")
        raise

if __name__ == "__main__":
    install()

