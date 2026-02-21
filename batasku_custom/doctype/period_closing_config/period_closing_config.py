# -*- coding: utf-8 -*-
# Copyright (c) 2024, Batasku and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PeriodClosingConfig(Document):
	def validate(self):
		"""Validate period closing config before saving"""
		self.validate_retained_earnings_account()
		self.validate_roles()
		self.validate_notification_days()
	
	def validate_retained_earnings_account(self):
		"""Validate that retained earnings account is an equity account"""
		if self.retained_earnings_account:
			account = frappe.get_doc("Account", self.retained_earnings_account)
			if account.root_type != "Equity":
				frappe.throw("Retained Earnings Account must be an Equity account")
	
	def validate_roles(self):
		"""Validate that roles exist"""
		if self.closing_role and not frappe.db.exists("Role", self.closing_role):
			frappe.throw(f"Role {self.closing_role} does not exist")
		
		if self.reopen_role and not frappe.db.exists("Role", self.reopen_role):
			frappe.throw(f"Role {self.reopen_role} does not exist")
	
	def validate_notification_days(self):
		"""Validate notification day settings"""
		if self.reminder_days_before_end and self.reminder_days_before_end < 0:
			frappe.throw("Reminder Days Before End must be a positive number")
		
		if self.escalation_days_after_end and self.escalation_days_after_end < 0:
			frappe.throw("Escalation Days After End must be a positive number")
	
	def on_update(self):
		"""Create audit log when config is updated"""
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc:
				# Create audit log for config changes
				log = frappe.get_doc({
					"doctype": "Period Closing Log",
					"accounting_period": "Config Change",
					"action_type": "Transaction Modified",
					"action_by": frappe.session.user,
					"action_date": frappe.utils.now(),
					"reason": "Period Closing Configuration Updated",
					"before_snapshot": frappe.as_json(old_doc.as_dict()),
					"after_snapshot": frappe.as_json(self.as_dict())
				})
				log.insert(ignore_permissions=True)
