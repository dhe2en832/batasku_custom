# Delivery Note Return - Hybrid Approach

## Overview

Implementasi Sales Return Management menggunakan **Hybrid Approach**:
- **Backend**: Native ERPNext Delivery Note dengan `is_return=1`
- **Frontend**: Custom Next.js UI yang sudah dibuat

## Keuntungan Hybrid Approach

### ✅ Menggunakan Native ERPNext Backend

1. **Inventory Management Otomatis**
   - Stock updates sudah terintegrasi
   - Stock ledger entries otomatis
   - Valuation rate calculation built-in

2. **Accounting Integration**
   - GL entries otomatis untuk return
   - Terintegrasi dengan Sales Invoice return
   - Credit note generation support

3. **Upgrade Compatibility**
   - Tidak perlu maintain custom DocType
   - Compatible dengan ERPNext upgrades
   - Mengikuti best practices ERPNext

4. **Existing Features**
   - Print formats tersedia
   - Email notifications
   - Workflow support
   - Permission system

### ✅ Custom Frontend UI

1. **Better UX**
   - Dedicated return interface
   - Simplified workflow
   - Return reason tracking
   - Better validation

2. **Custom Fields**
   - Return reason per item
   - Return notes
   - Return processed tracking
   - Additional metadata

## Struktur File

```
erpnext-dev/apps/batasku_custom/batasku_custom/
├── custom_fields/
│   └── delivery_note_return_fields.py    # Custom fields definition
├── overrides/
│   └── delivery_note_return.py           # Validation & hooks
├── install_delivery_note_return.py       # Installation script
└── DELIVERY_NOTE_RETURN_README.md        # This file

erp-next-system/
├── app/
│   ├── api/sales/delivery-note-return/   # API routes (NEW)
│   │   ├── route.ts                      # GET (list) + POST (create)
│   │   └── [name]/
│   │       ├── route.ts                  # GET (detail) + PUT (update)
│   │       ├── submit/route.ts           # POST (submit)
│   │       └── cancel/route.ts           # POST (cancel)
│   └── sales-return/                     # Frontend UI (EXISTING)
│       ├── page.tsx
│       ├── srList/component.tsx
│       └── srMain/component.tsx
├── components/
│   └── DeliveryNoteDialog.tsx            # Delivery note selector
└── types/
    └── sales-return.ts                   # Type definitions
```

## Custom Fields

### Delivery Note (Parent)

| Field Name | Type | Label | Depends On | Notes |
|------------|------|-------|------------|-------|
| `return_section` | Section Break | Return Information | `is_return==1` | Section header |
| `return_processed_date` | Date | Return Processed Date | `is_return==1` | Auto-filled on submit |
| `return_processed_by` | Link (User) | Return Processed By | `is_return==1` | Auto-filled on submit |
| `return_notes` | Text | Return Notes | `is_return==1` | General return notes |

### Delivery Note Item (Child)

| Field Name | Type | Label | Depends On | Mandatory |
|------------|------|-------|------------|-----------|
| `return_reason` | Select | Return Reason | `parent.is_return==1` | Yes |
| `return_item_notes` | Small Text | Return Item Notes | `return_reason=="Other"` | Yes (if Other) |

**Return Reason Options:**
- Damaged
- Wrong Item
- Quality Issue
- Customer Request
- Expired
- Other

## Installation

### 1. Install Custom Fields

```bash
# Method 1: Via bench console
cd /path/to/frappe-bench
bench --site [site-name] console

>>> from batasku_custom.install_delivery_note_return import install
>>> install()
```

```bash
# Method 2: Via Python script
cd /path/to/frappe-bench
bench --site [site-name] execute batasku_custom.install_delivery_note_return.install
```

### 2. Verify Installation

```bash
bench --site [site-name] console

>>> from batasku_custom.install_delivery_note_return import verify_installation
>>> verify_installation()
```

Expected output:
```
✓ Delivery Note.return_section - OK
✓ Delivery Note.return_processed_date - OK
✓ Delivery Note.return_processed_by - OK
✓ Delivery Note.return_notes - OK
✓ Delivery Note Item.return_reason - OK
✓ Delivery Note Item.return_item_notes - OK
```

### 3. Restart Bench

```bash
bench restart
```

### 4. Clear Cache

```bash
bench --site [site-name] clear-cache
```

## Validation Hooks

File: `batasku_custom/overrides/delivery_note_return.py`

### 1. `validate_delivery_note_return(doc, method=None)`

Dipanggil saat: **Before Save**

Validasi:
- ✅ Return against exists
- ✅ Return reason selected for all items
- ✅ Notes provided when reason is "Other"
- ✅ Return quantity ≤ delivered quantity
- ✅ Check previous returns from same delivery note

### 2. `on_submit_delivery_note_return(doc, method=None)`

Dipanggil saat: **On Submit**

Actions:
- ✅ Set `return_processed_date` = today
- ✅ Set `return_processed_by` = current user
- ✅ Show success message

### 3. `on_cancel_delivery_note_return(doc, method=None)`

Dipanggil saat: **On Cancel**

Actions:
- ✅ Clear `return_processed_date`
- ✅ Clear `return_processed_by`
- ✅ Show cancellation message

## API Routes

### Base URL: `/api/sales/delivery-note-return`

### 1. List Returns

```http
GET /api/sales/delivery-note-return
```

**Query Parameters:**
- `limit_page_length`: number (default: 20)
- `start`: number (default: 0)
- `search`: string (customer name)
- `documentNumber`: string (return document number)
- `status`: string (Draft | Submitted | Cancelled)
- `from_date`: string (YYYY-MM-DD)
- `to_date`: string (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "DN-RET-2024-00001",
      "customer": "CUST-001",
      "customer_name": "PT ABC",
      "posting_date": "2024-01-15",
      "delivery_note": "DN-2024-00123",
      "status": "Submitted",
      "grand_total": 1500000,
      "custom_notes": "Return notes",
      "return_processed_date": "2024-01-15",
      "return_processed_by": "user@example.com"
    }
  ],
  "total_records": 1
}
```

### 2. Create Return

```http
POST /api/sales/delivery-note-return
```

**Request Body:**
```json
{
  "company": "PT Batasku",
  "customer": "CUST-001",
  "posting_date": "2024-01-15",
  "return_against": "DN-2024-00123",
  "items": [
    {
      "item_code": "ITEM-001",
      "item_name": "Product A",
      "qty": 5,
      "rate": 100000,
      "uom": "Nos",
      "warehouse": "Stores - B",
      "return_reason": "Damaged",
      "return_item_notes": ""
    }
  ],
  "return_notes": "Customer reported damage during delivery"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "DN-RET-2024-00001",
    "docstatus": 0,
    "status": "Draft"
  }
}
```

### 3. Get Return Detail

```http
GET /api/sales/delivery-note-return/[name]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "DN-RET-2024-00001",
    "customer": "CUST-001",
    "customer_name": "PT ABC",
    "posting_date": "2024-01-15",
    "return_against": "DN-2024-00123",
    "is_return": 1,
    "docstatus": 0,
    "status": "Draft",
    "items": [...],
    "return_notes": "..."
  }
}
```

### 4. Update Return (Draft only)

```http
PUT /api/sales/delivery-note-return/[name]
```

**Request Body:** Same as Create

### 5. Submit Return

```http
POST /api/sales/delivery-note-return/[name]/submit
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "DN-RET-2024-00001",
    "docstatus": 1,
    "status": "Submitted"
  },
  "message": "Return submitted successfully. Stock has been updated."
}
```

### 6. Cancel Return

```http
POST /api/sales/delivery-note-return/[name]/cancel
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "DN-RET-2024-00001",
    "docstatus": 2,
    "status": "Cancelled"
  },
  "message": "Return cancelled successfully. Stock adjustments have been reversed."
}
```

## Frontend Integration

### Update API Endpoint

File: `app/sales-return/srList/component.tsx`

```typescript
// OLD: const response = await fetch('/api/sales/sales-return');
// NEW:
const response = await fetch('/api/sales/delivery-note-return');
```

File: `app/sales-return/srMain/component.tsx`

```typescript
// OLD: const response = await fetch('/api/sales/sales-return', {...});
// NEW:
const response = await fetch('/api/sales/delivery-note-return', {...});
```

### Data Transformation

API routes sudah handle transformasi:
- `return_against` → `delivery_note`
- `docstatus` → `status` (Draft/Submitted/Cancelled)
- `return_notes` → `custom_notes`
- Negative quantities untuk return items

## Testing

### 1. Create Test Delivery Note

```bash
# Via ERPNext UI
1. Go to: Stock > Delivery Note > New
2. Select customer
3. Add items with quantities
4. Set warehouse
5. Submit delivery note
```

### 2. Create Return via Frontend

```bash
# Via Next.js UI
1. Go to: http://localhost:3000/sales-return
2. Click "Create Return"
3. Select delivery note
4. Select items to return
5. Enter quantities
6. Select return reasons
7. Save as Draft
8. Submit
```

### 3. Verify Stock Updates

```sql
-- Check stock ledger entries
SELECT * FROM `tabStock Ledger Entry`
WHERE voucher_type = 'Delivery Note'
AND voucher_no = 'DN-RET-2024-00001'
ORDER BY posting_date DESC, posting_time DESC;

-- Check stock balance
SELECT item_code, warehouse, actual_qty, stock_value
FROM `tabBin`
WHERE item_code = 'ITEM-001'
AND warehouse = 'Stores - B';
```

### 4. Test Validation

```bash
# Test 1: Return quantity > delivered quantity
- Should show error: "Return quantity exceeds remaining returnable quantity"

# Test 2: Missing return reason
- Should show error: "Please select a return reason"

# Test 3: Reason "Other" without notes
- Should show error: "Please provide additional notes for return reason 'Other'"

# Test 4: Multiple returns from same DN
- Should track previous returns
- Should validate remaining quantity correctly
```

## Migration from Custom DocType

Jika sudah ada data di custom `Sales Return` DocType:

### 1. Export Data

```python
import frappe
import json

# Get all sales returns
returns = frappe.get_all('Sales Return',
    fields=['*'],
    filters={'docstatus': ['<', 2]}
)

# Export to JSON
with open('sales_returns_export.json', 'w') as f:
    json.dump(returns, f, indent=2, default=str)
```

### 2. Transform & Import

```python
import frappe
from frappe.utils import nowdate

def migrate_sales_return_to_delivery_note():
    """Migrate custom Sales Return to native Delivery Note returns"""
    
    returns = frappe.get_all('Sales Return',
        fields=['*'],
        filters={'docstatus': ['<', 2]}
    )
    
    for sr in returns:
        # Create Delivery Note return
        dn = frappe.new_doc('Delivery Note')
        dn.is_return = 1
        dn.return_against = sr.delivery_note
        dn.customer = sr.customer
        dn.posting_date = sr.posting_date
        dn.company = sr.company
        dn.return_notes = sr.custom_notes
        
        # Add items
        for sr_item in frappe.get_all('Sales Return Item',
            filters={'parent': sr.name},
            fields=['*']
        ):
            dn.append('items', {
                'item_code': sr_item.item_code,
                'item_name': sr_item.item_name,
                'qty': -abs(sr_item.qty),  # Negative for return
                'rate': sr_item.rate,
                'uom': sr_item.uom,
                'warehouse': sr_item.warehouse,
                'return_reason': sr_item.return_reason,
                'return_item_notes': sr_item.return_notes
            })
        
        # Save
        dn.insert()
        
        # Submit if original was submitted
        if sr.docstatus == 1:
            dn.submit()
        
        print(f"Migrated {sr.name} -> {dn.name}")
    
    frappe.db.commit()
    print("Migration complete!")

# Run migration
# migrate_sales_return_to_delivery_note()
```

## Troubleshooting

### Issue: Custom fields not showing

**Solution:**
```bash
bench --site [site-name] clear-cache
bench restart
```

### Issue: Validation not working

**Solution:**
```bash
# Check hooks.py is loaded
bench --site [site-name] console
>>> import batasku_custom.hooks
>>> print(batasku_custom.hooks.doc_events)

# Restart bench
bench restart
```

### Issue: Stock not updating

**Solution:**
```bash
# Check stock settings
1. Go to: Stock Settings
2. Enable "Allow Negative Stock" (if needed)
3. Check "Auto Create Serial and Batch Bundle"

# Check item settings
1. Go to: Item Master
2. Check "Maintain Stock" is enabled
3. Check "Has Serial No" / "Has Batch No" if applicable
```

### Issue: Permission denied

**Solution:**
```bash
# Grant permissions to role
1. Go to: Role Permission Manager
2. Select "Delivery Note"
3. Grant permissions to Sales User / Sales Manager
4. Enable "Submit", "Cancel", "Amend"
```

## Uninstallation

```bash
bench --site [site-name] console

>>> from batasku_custom.install_delivery_note_return import uninstall
>>> uninstall()
```

## Support

For issues or questions:
- Check ERPNext documentation: https://docs.erpnext.com
- Review Delivery Note source code
- Contact development team

## Version History

- **v1.0** (2024-01-15) - Initial hybrid implementation
  - Native ERPNext backend with custom fields
  - Custom Next.js frontend
  - Return reason tracking
  - Validation hooks
  - Stock integration

