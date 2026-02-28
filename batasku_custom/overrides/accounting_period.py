# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.accounting_period.accounting_period import AccountingPeriod

class CustomAccountingPeriod(AccountingPeriod):
    """Custom Accounting Period with bug fixes and enhancements"""
    
    def bootstrap_doctypes_for_closing(self):
        """Override to fix dict/object attribute error and respect period status"""
        if len(self.closed_documents) == 0:
            # Determine if documents should be closed based on period status
            # Only set closed=1 if period status is 'Closed' or 'Permanently Closed'
            should_close = self.get('status') in ['Closed', 'Permanently Closed']
            
            for doctype_for_closing in self.get_doctypes_for_closing():
                # Fix: doctype_for_closing is a dict, not an object
                self.append(
                    "closed_documents",
                    {
                        "document_type": doctype_for_closing.get("document_type"),
                        "closed": 1 if should_close else 0,
                    },
                )
    
    def on_update(self):
        """Update closed status of all documents when period status changes"""
        # Sync closed_documents with period status
        if self.get('status'):
            should_close = self.get('status') in ['Closed', 'Permanently Closed']
            
            for doc in self.closed_documents:
                doc.closed = 1 if should_close else 0
