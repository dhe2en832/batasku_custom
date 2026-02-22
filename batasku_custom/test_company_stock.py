#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify company_total_stock field population
Run with: bench --site batasku.local execute batasku_custom.test_company_stock.test_hook
"""

import frappe
from frappe import _

def test_hook():
    """Test if the validation hook populates company_total_stock"""
    
    print("\n" + "="*80)
    print("TESTING COMPANY_TOTAL_STOCK FIELD POPULATION")
    print("="*80 + "\n")
    
    # Find a recent delivery note return
    returns = frappe.get_all(
        "Delivery Note",
        filters={"is_return": 1, "docstatus": 0},
        fields=["name", "return_against", "posting_date"],
        order_by="creation desc",
        limit=1
    )
    
    if not returns:
        print("❌ No draft delivery note returns found")
        print("   Please create a delivery note return from Next.js first")
        return
    
    return_doc = frappe.get_doc("Delivery Note", returns[0].name)
    
    print(f"📄 Testing with: {return_doc.name}")
    print(f"   Return Against: {return_doc.return_against}")
    print(f"   Items: {len(return_doc.items)}")
    print()
    
    # Check current values
    print("BEFORE VALIDATION:")
    print("-" * 80)
    for item in return_doc.items:
        print(f"  Item: {item.item_code}")
        print(f"    Warehouse: {item.warehouse}")
        print(f"    company_total_stock: {item.company_total_stock or 0}")
        
        # Check Bin
        bin_data = frappe.db.get_value(
            "Bin",
            {"item_code": item.item_code, "warehouse": item.warehouse},
            ["actual_qty"],
            as_dict=True
        )
        if bin_data:
            print(f"    Bin actual_qty: {bin_data.actual_qty}")
        else:
            print(f"    ⚠️  No Bin record found")
        print()
    
    # Run validation
    print("\nRUNNING VALIDATION...")
    print("-" * 80)
    try:
        return_doc.validate()
        print("✅ Validation completed successfully")
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return
    
    # Check after validation
    print("\nAFTER VALIDATION:")
    print("-" * 80)
    for item in return_doc.items:
        print(f"  Item: {item.item_code}")
        print(f"    Warehouse: {item.warehouse}")
        print(f"    company_total_stock: {item.company_total_stock or 0}")
        
        if item.company_total_stock and item.company_total_stock > 0:
            print(f"    ✅ Field populated!")
        else:
            print(f"    ❌ Field still 0")
        print()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_hook()
