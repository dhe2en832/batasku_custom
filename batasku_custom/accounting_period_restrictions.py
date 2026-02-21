"""
Transaction Restrictions for Closed Accounting Periods

This module implements validation hooks to prevent transactions in closed periods.
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5

Restricted Transaction Types:
- Sales Order (SO)
- Sales Invoice (SJ/SI)
- Journal Entry (FJ/JE)
- Purchase Order (PO)
- Purchase Receipt (PR)
- Purchase Invoice (PI)
- Payment Entry (Payment Receive and Payment Pay)
- Stock Entry (Stock Reconciliation)
"""

import frappe
from frappe import _
from frappe.utils import getdate
import json


def validate_transaction_against_closed_period(doc, method):
    """
    Validate that transactions are not created/modified in closed periods.
    
    This function is called via doc_events hooks for various transaction doctypes.
    It checks if the transaction's posting_date falls within a closed period and
    prevents the transaction unless the user has override permissions.
    
    Requirements:
    - 5.1: Reject new transactions in closed periods
    - 5.2: Reject modifications to transactions in closed periods
    - 5.3: Reject deletions of transactions in closed periods
    - 5.4: Allow administrator override with logging
    - 5.5: Record reason for override in audit log
    
    Args:
        doc: The document being validated
        method: The method being called (before_insert, before_save, etc.)
    """
    # Skip if no posting_date
    if not hasattr(doc, 'posting_date') or not doc.posting_date:
        return
    
    # Skip if no company
    if not hasattr(doc, 'company') or not doc.company:
        return
    
    # Get all closed periods for the company that include this posting_date
    closed_periods = frappe.get_all(
        'Accounting Period',
        filters={
            'company': doc.company,
            'status': ['in', ['Closed', 'Permanently Closed']],
            'start_date': ['<=', doc.posting_date],
            'end_date': ['>=', doc.posting_date]
        },
        fields=['name', 'period_name', 'status', 'start_date', 'end_date'],
        limit=1
    )
    
    if not closed_periods:
        # No closed period found, allow transaction
        return
    
    period = closed_periods[0]
    
    # Check if permanently closed - no exceptions allowed
    if period['status'] == 'Permanently Closed':
        frappe.throw(
            _(f"Cannot modify transaction: Period {period['period_name']} is permanently closed. "
              f"No modifications are allowed."),
            title=_("Period Permanently Closed")
        )
    
    # Check if user has override permission
    # System Manager or Accounts Manager can override
    if frappe.has_permission('Accounting Period', 'write') and (
        'System Manager' in frappe.get_roles() or 
        'Accounts Manager' in frappe.get_roles()
    ):
        # Log the override
        try:
            frappe.get_doc({
                'doctype': 'Period Closing Log',
                'accounting_period': period['name'],
                'action_type': 'Transaction Modified',
                'action_by': frappe.session.user,
                'action_date': frappe.utils.now(),
                'affected_transaction': doc.name if doc.name else 'New Document',
                'transaction_doctype': doc.doctype,
                'reason': f"Modified {doc.doctype} in closed period {period['period_name']}",
                'ip_address': frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None,
                'user_agent': frappe.local.request.headers.get('User-Agent') if hasattr(frappe.local, 'request') else None
            }).insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to create audit log: {str(e)}", "Period Closing Audit Log Error")
        
        # Show warning but allow transaction
        frappe.msgprint(
            _(f"Warning: Modifying transaction in closed period {period['period_name']}. "
              f"This action is logged for audit purposes."),
            title=_("Closed Period Override"),
            indicator='orange'
        )
        return
    
    # Deny transaction for regular users
    frappe.throw(
        _(f"Cannot modify transaction: Period {period['period_name']} "
          f"({period['start_date']} to {period['end_date']}) is closed. "
          f"Contact administrator to reopen the period."),
        title=_("Period Closed")
    )


def validate_transaction_deletion(doc, method):
    """
    Validate that transactions are not deleted in closed periods.
    
    Requirements: 5.3, 5.4, 5.5
    
    Args:
        doc: The document being deleted
        method: The method being called (before_cancel, on_trash)
    """
    # Use the same validation logic
    validate_transaction_against_closed_period(doc, method)
