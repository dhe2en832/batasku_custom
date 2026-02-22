# Quick Start Guide - Delivery Note Return

## 5-Minute Setup

### Step 1: Install Custom Fields (2 minutes)

```bash
cd /path/to/frappe-bench
bench --site [your-site-name] console
```

```python
>>> from batasku_custom.install_delivery_note_return import install
>>> install()
```

Expected output:
```
Installing Delivery Note Return custom fields...
Custom fields added to Delivery Note for return tracking
✓ Custom fields installed successfully

Verifying installation...
✓ Delivery Note.return_section - OK
✓ Delivery Note.return_processed_date - OK
✓ Delivery Note.return_processed_by - OK
✓ Delivery Note.return_notes - OK
✓ Delivery Note Item.return_reason - OK
✓ Delivery Note Item.return_item_notes - OK

Installation verification complete!
```

### Step 2: Restart Bench (1 minute)

```bash
bench restart
bench --site [your-site-name] clear-cache
```

### Step 3: Test in ERPNext UI (2 minutes)

1. **Create Test Delivery Note**
   ```
   Go to: Stock > Delivery Note > New
   - Customer: Select any customer
   - Items: Add 1-2 items with quantities
   - Warehouse: Select warehouse
   - Submit
   ```

2. **Create Return from Delivery Note**
   ```
   From the submitted Delivery Note:
   - Click "Create" button
   - Select "Return / Credit Note"
   - ERPNext will create return with is_return=1
   - Add return reasons in custom fields
   - Save and Submit
   ```

3. **Verify Custom Fields**
   ```
   In the return document, you should see:
   - Return Information section
   - Return Reason dropdown per item
   - Return Item Notes field
   - Return Processed Date (after submit)
   - Return Processed By (after submit)
   ```

### Step 4: Test via Frontend (Optional)

If using Next.js frontend:

```bash
cd erp-next-system
pnpm dev
```

Navigate to: http://localhost:3000/sales-return

## Verification Commands

### Check Custom Fields

```bash
bench --site [your-site-name] console
```

```python
>>> import frappe
>>> 
>>> # Check Delivery Note fields
>>> dn_fields = frappe.get_all('Custom Field',
...     filters={'dt': 'Delivery Note', 'fieldname': ['in', ['return_section', 'return_processed_date', 'return_processed_by', 'return_notes']]},
...     fields=['fieldname', 'label'])
>>> print(dn_fields)
>>> 
>>> # Check Delivery Note Item fields
>>> dni_fields = frappe.get_all('Custom Field',
...     filters={'dt': 'Delivery Note Item', 'fieldname': ['in', ['return_reason', 'return_item_notes']]},
...     fields=['fieldname', 'label'])
>>> print(dni_fields)
```

### Check Hooks

```python
>>> import batasku_custom.hooks
>>> print(batasku_custom.hooks.doc_events.get('Delivery Note'))
```

Expected output:
```python
{
    'validate': 'batasku_custom.overrides.delivery_note_return.validate_delivery_note_return',
    'on_submit': 'batasku_custom.overrides.delivery_note_return.on_submit_delivery_note_return',
    'on_cancel': 'batasku_custom.overrides.delivery_note_return.on_cancel_delivery_note_return'
}
```

### Test Validation

```python
>>> import frappe
>>> 
>>> # Create test return
>>> dn = frappe.new_doc('Delivery Note')
>>> dn.is_return = 1
>>> dn.return_against = 'DN-2024-00001'  # Use existing DN
>>> dn.customer = 'CUST-001'
>>> dn.posting_date = '2024-01-15'
>>> dn.company = 'PT Batasku'
>>> 
>>> # Add item without return reason (should fail)
>>> dn.append('items', {
...     'item_code': 'ITEM-001',
...     'qty': -5,
...     'rate': 100000,
...     'uom': 'Nos',
...     'warehouse': 'Stores - B'
... })
>>> 
>>> try:
...     dn.save()
... except Exception as e:
...     print(f"Validation working: {str(e)}")
```

## Common Issues

### Issue: "Module batasku_custom not found"

**Solution:**
```bash
# Check app is installed
bench --site [your-site-name] list-apps

# If not listed, install it
cd /path/to/frappe-bench/apps/batasku_custom
bench --site [your-site-name] install-app batasku_custom
```

### Issue: Custom fields not showing

**Solution:**
```bash
bench --site [your-site-name] clear-cache
bench restart
# Reload ERPNext page in browser (Ctrl+Shift+R)
```

### Issue: Validation not working

**Solution:**
```bash
# Restart bench to reload hooks
bench restart

# Check hooks are loaded
bench --site [your-site-name] console
>>> import batasku_custom.hooks
>>> print(batasku_custom.hooks.doc_events)
```

### Issue: Permission denied

**Solution:**
```bash
# Grant permissions via ERPNext UI
1. Go to: Role Permission Manager
2. Select "Delivery Note"
3. Grant permissions to Sales User / Sales Manager
4. Enable: Create, Read, Write, Submit, Cancel, Amend
```

## Quick Test Script

Save this as `test_return.py`:

```python
import frappe

def test_delivery_note_return():
    """Quick test for delivery note return"""
    
    print("=== Testing Delivery Note Return ===\n")
    
    # 1. Check custom fields
    print("1. Checking custom fields...")
    dn_fields = frappe.db.count('Custom Field', {
        'dt': 'Delivery Note',
        'fieldname': ['in', ['return_section', 'return_processed_date', 'return_processed_by', 'return_notes']]
    })
    dni_fields = frappe.db.count('Custom Field', {
        'dt': 'Delivery Note Item',
        'fieldname': ['in', ['return_reason', 'return_item_notes']]
    })
    
    if dn_fields == 4 and dni_fields == 2:
        print("✓ Custom fields installed correctly\n")
    else:
        print(f"✗ Custom fields missing (DN: {dn_fields}/4, DNI: {dni_fields}/2)\n")
        return
    
    # 2. Check hooks
    print("2. Checking hooks...")
    import batasku_custom.hooks
    dn_hooks = batasku_custom.hooks.doc_events.get('Delivery Note', {})
    
    if 'validate' in dn_hooks and 'on_submit' in dn_hooks and 'on_cancel' in dn_hooks:
        print("✓ Hooks registered correctly\n")
    else:
        print("✗ Hooks not registered\n")
        return
    
    # 3. Test validation
    print("3. Testing validation...")
    try:
        dn = frappe.new_doc('Delivery Note')
        dn.is_return = 1
        dn.return_against = 'TEST-DN'
        dn.customer = 'TEST-CUST'
        dn.posting_date = frappe.utils.today()
        dn.company = frappe.defaults.get_defaults().company
        
        dn.append('items', {
            'item_code': 'TEST-ITEM',
            'qty': -5,
            'rate': 100000,
            'uom': 'Nos',
            'warehouse': 'Stores - B'
        })
        
        # This should fail (no return reason)
        dn.save()
        print("✗ Validation not working (should have failed)\n")
    except Exception as e:
        if 'return reason' in str(e).lower():
            print("✓ Validation working correctly\n")
        else:
            print(f"✗ Unexpected error: {str(e)}\n")
    
    print("=== Test Complete ===")

# Run test
test_delivery_note_return()
```

Run it:
```bash
bench --site [your-site-name] execute batasku_custom.test_return.test_delivery_note_return
```

## Next Steps

After successful installation:

1. **Read Full Documentation**
   - `DELIVERY_NOTE_RETURN_README.md` - Complete backend guide
   - `SALES_RETURN_MIGRATION_GUIDE.md` - Frontend migration
   - `SALES_RETURN_HYBRID_SUMMARY.md` - Architecture overview

2. **Update Frontend** (if using Next.js)
   - Change API endpoints from `/api/sales/sales-return` to `/api/sales/delivery-note-return`
   - See migration guide for details

3. **Migrate Existing Data** (if applicable)
   - Follow migration script in `SALES_RETURN_MIGRATION_GUIDE.md`

4. **Configure Permissions**
   - Set up role permissions for Delivery Note
   - Configure workflow if needed

5. **Train Users**
   - Show how to create returns
   - Explain return reasons
   - Demonstrate validation

## Support

For issues:
- Check logs: `bench --site [your-site-name] console`
- Review error logs in ERPNext
- Contact development team

## Quick Reference

### Installation
```bash
bench --site [site] console
>>> from batasku_custom.install_delivery_note_return import install
>>> install()
```

### Verification
```bash
>>> from batasku_custom.install_delivery_note_return import verify_installation
>>> verify_installation()
```

### Uninstall
```bash
>>> from batasku_custom.install_delivery_note_return import uninstall
>>> uninstall()
```

### Restart
```bash
bench restart
bench --site [site] clear-cache
```

