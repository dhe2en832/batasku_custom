# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

"""
Custom Fields for Delivery Note Return Tracking
Adds return reason and notes fields to Delivery Note and Delivery Note Item
"""

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_delivery_note_return_fields():
    """
    Add custom fields to Delivery Note and Delivery Note Item for return tracking
    
    This enables tracking return reasons without creating a separate DocType,
    leveraging ERPNext's native return mechanism (is_return=1)
    """
    
    custom_fields = {
        'Delivery Note': [
            {
                'fieldname': 'return_section',
                'label': 'Return Information',
                'fieldtype': 'Section Break',
                'insert_after': 'return_against',
                'depends_on': 'eval:doc.is_return==1',
                'collapsible': 0
            },
            {
                'fieldname': 'return_processed_date',
                'label': 'Return Processed Date',
                'fieldtype': 'Date',
                'insert_after': 'return_section',
                'read_only': 1,
                'depends_on': 'eval:doc.is_return==1'
            },
            {
                'fieldname': 'return_processed_by',
                'label': 'Return Processed By',
                'fieldtype': 'Link',
                'options': 'User',
                'insert_after': 'return_processed_date',
                'read_only': 1,
                'depends_on': 'eval:doc.is_return==1'
            },
            {
                'fieldname': 'column_break_return_1',
                'fieldtype': 'Column Break',
                'insert_after': 'return_processed_by'
            },
            {
                'fieldname': 'return_notes',
                'label': 'Return Notes',
                'fieldtype': 'Text',
                'insert_after': 'column_break_return_1',
                'depends_on': 'eval:doc.is_return==1'
            }
        ],
        'Delivery Note Item': [
            {
                'fieldname': 'company_total_stock',
                'label': 'Company Total Stock',
                'fieldtype': 'Float',
                'insert_after': 'warehouse',
                'read_only': 1,
                'in_list_view': 0,
                'precision': 2,
                'description': 'Total stock available in the warehouse at the time of return'
            },
            {
                'fieldname': 'return_reason',
                'label': 'Return Reason',
                'fieldtype': 'Select',
                'options': '\nDamaged\nWrong Item\nQuality Issue\nCustomer Request\nExpired\nOther',
                'insert_after': 'company_total_stock',
                'depends_on': 'eval:parent.is_return==1',
                'in_list_view': 0,
                'mandatory_depends_on': 'eval:parent.is_return==1'
            },
            {
                'fieldname': 'return_item_notes',
                'label': 'Return Item Notes',
                'fieldtype': 'Small Text',
                'insert_after': 'return_reason',
                'depends_on': 'eval:parent.is_return==1 && doc.return_reason=="Other"',
                'mandatory_depends_on': 'eval:parent.is_return==1 && doc.return_reason=="Other"'
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    print("Custom fields added to Delivery Note for return tracking")

def execute():
    """Execute function for patches"""
    add_delivery_note_return_fields()

