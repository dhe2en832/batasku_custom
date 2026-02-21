# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_accounting_period_custom_fields():
    """Add custom fields to Accounting Period DocType"""
    
    custom_fields = {
        'Accounting Period': [
            {
                'fieldname': 'period_type',
                'label': 'Period Type',
                'fieldtype': 'Select',
                'options': 'Monthly\nQuarterly\nYearly',
                'default': 'Monthly',
                'insert_after': 'end_date',
                'in_list_view': 0,
                'in_standard_filter': 1
            },
            {
                'fieldname': 'status',
                'label': 'Status',
                'fieldtype': 'Select',
                'options': 'Open\nClosed\nPermanently Closed',
                'default': 'Open',
                'insert_after': 'period_type',
                'in_list_view': 1,
                'in_standard_filter': 1,
                'reqd': 1
            },
            {
                'fieldname': 'fiscal_year',
                'label': 'Fiscal Year',
                'fieldtype': 'Link',
                'options': 'Fiscal Year',
                'insert_after': 'status',
                'in_list_view': 0
            },
            {
                'fieldname': 'column_break_custom_1',
                'fieldtype': 'Column Break',
                'insert_after': 'fiscal_year'
            },
            {
                'fieldname': 'closed_by',
                'label': 'Closed By',
                'fieldtype': 'Link',
                'options': 'User',
                'read_only': 1,
                'insert_after': 'column_break_custom_1',
                'in_list_view': 0
            },
            {
                'fieldname': 'closed_on',
                'label': 'Closed On',
                'fieldtype': 'Datetime',
                'read_only': 1,
                'insert_after': 'closed_by',
                'in_list_view': 0
            },
            {
                'fieldname': 'closing_journal_entry',
                'label': 'Closing Journal Entry',
                'fieldtype': 'Link',
                'options': 'Journal Entry',
                'read_only': 1,
                'insert_after': 'closed_on',
                'in_list_view': 0
            },
            {
                'fieldname': 'permanently_closed_by',
                'label': 'Permanently Closed By',
                'fieldtype': 'Link',
                'options': 'User',
                'read_only': 1,
                'insert_after': 'closing_journal_entry',
                'in_list_view': 0
            },
            {
                'fieldname': 'permanently_closed_on',
                'label': 'Permanently Closed On',
                'fieldtype': 'Datetime',
                'read_only': 1,
                'insert_after': 'permanently_closed_by',
                'in_list_view': 0
            },
            {
                'fieldname': 'section_break_custom_remarks',
                'fieldtype': 'Section Break',
                'label': 'Remarks',
                'insert_after': 'permanently_closed_on'
            },
            {
                'fieldname': 'remarks',
                'label': 'Remarks',
                'fieldtype': 'Text Editor',
                'insert_after': 'section_break_custom_remarks',
                'in_list_view': 0
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    print("Custom fields added to Accounting Period")

def execute():
    """Execute function for patches"""
    add_accounting_period_custom_fields()
