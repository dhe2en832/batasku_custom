#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if hooks are properly registered
Run with: bench --site batasku.local execute batasku_custom.check_hooks.check
"""

import frappe

def check():
    """Check if delivery note return hooks are registered"""
    
    print("\n" + "="*80)
    print("CHECKING DELIVERY NOTE RETURN HOOKS")
    print("="*80 + "\n")
    
    # Get all hooks
    hooks = frappe.get_hooks("doc_events")
    
    # Check Delivery Note hooks
    dn_hooks = hooks.get("Delivery Note", {})
    
    print("Delivery Note Hooks:")
    print("-" * 80)
    
    if not dn_hooks:
        print("❌ NO HOOKS REGISTERED FOR DELIVERY NOTE!")
        return
    
    # Check validate hooks
    validate_hooks = dn_hooks.get("validate", [])
    if isinstance(validate_hooks, str):
        validate_hooks = [validate_hooks]
    
    print(f"\n✓ Validate hooks ({len(validate_hooks)}):")
    for hook in validate_hooks:
        print(f"  - {hook}")
        if "delivery_note_return" in hook:
            print(f"    ✅ Delivery Note Return hook found!")
    
    # Check on_submit hooks
    submit_hooks = dn_hooks.get("on_submit", [])
    if isinstance(submit_hooks, str):
        submit_hooks = [submit_hooks]
    
    if submit_hooks:
        print(f"\n✓ On Submit hooks ({len(submit_hooks)}):")
        for hook in submit_hooks:
            print(f"  - {hook}")
    
    # Check on_cancel hooks
    cancel_hooks = dn_hooks.get("on_cancel", [])
    if isinstance(cancel_hooks, str):
        cancel_hooks = [cancel_hooks]
    
    if cancel_hooks:
        print(f"\n✓ On Cancel hooks ({len(cancel_hooks)}):")
        for hook in cancel_hooks:
            print(f"  - {hook}")
    
    print("\n" + "="*80)
    
    # Try to import the function
    print("\nTrying to import validation function...")
    print("-" * 80)
    try:
        from batasku_custom.overrides.delivery_note_return import validate_delivery_note_return
        print("✅ Function imported successfully!")
        print(f"   Function: {validate_delivery_note_return}")
    except Exception as e:
        print(f"❌ Failed to import function: {str(e)}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    check()
