# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.accounting_period.accounting_period import AccountingPeriod

class CustomAccountingPeriod(AccountingPeriod):
    """Custom Accounting Period with bug fixes and enhancements"""
    
    def bootstrap_doctypes_for_closing(self):
        """Override to fix dict/object attribute error"""
        if len(self.closed_documents) == 0:
            for doctype_for_closing in self.get_doctypes_for_closing():
                # Fix: doctype_for_closing is a dict, not an object
                self.append(
                    "closed_documents",
                    {
                        "document_type": doctype_for_closing.get("document_type"),
                        "closed": doctype_for_closing.get("closed", 1),
                    },
                )
