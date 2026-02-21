#!/bin/bash

# Deployment script for Accounting Period Closing transaction restrictions
# This script deploys the Python hooks to ERPNext

set -e  # Exit on error

echo "========================================="
echo "Accounting Period Closing - Hook Deployment"
echo "========================================="
echo ""

# Check if we're in the correct directory
if [ ! -f "apps/batasku_custom/batasku_custom/hooks.py" ]; then
    echo "ERROR: Must run this script from the erpnext-dev directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "Step 1: Verifying files exist..."
if [ ! -f "apps/batasku_custom/batasku_custom/accounting_period_restrictions.py" ]; then
    echo "ERROR: accounting_period_restrictions.py not found"
    exit 1
fi
echo "✓ accounting_period_restrictions.py found"

if [ ! -f "apps/batasku_custom/batasku_custom/hooks.py" ]; then
    echo "ERROR: hooks.py not found"
    exit 1
fi
echo "✓ hooks.py found"
echo ""

echo "Step 2: Checking if hooks.py contains doc_events..."
if grep -q "accounting_period_restrictions" apps/batasku_custom/batasku_custom/hooks.py; then
    echo "✓ hooks.py already contains accounting_period_restrictions"
else
    echo "WARNING: hooks.py does not contain accounting_period_restrictions"
    echo "Please verify hooks.py has been updated correctly"
fi
echo ""

echo "Step 3: Running bench migrate..."
bench --site batasku.local migrate
echo "✓ Migration complete"
echo ""

echo "Step 4: Clearing cache..."
bench --site batasku.local clear-cache
echo "✓ Cache cleared"
echo ""

echo "Step 5: Restarting bench..."
bench restart
echo "✓ Bench restarted"
echo ""

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Test transaction restrictions:"
echo "   - Close a test period"
echo "   - Try to create a Sales Invoice in the closed period"
echo "   - Should be rejected with error message"
echo ""
echo "2. Test admin override:"
echo "   - Login as System Manager"
echo "   - Try to create a transaction in closed period"
echo "   - Should show warning but allow with audit log"
echo ""
echo "3. Verify audit logs:"
echo "   - Check Period Closing Log doctype"
echo "   - Verify entries are created for overrides"
echo ""
echo "========================================="
