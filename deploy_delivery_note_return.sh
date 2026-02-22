#!/bin/bash

# Deployment script for Delivery Note Return custom fields
# Similar to deploy_accounting_period_hooks.sh

set -e  # Exit on error

echo "=========================================="
echo "Delivery Note Return - Deployment Script"
echo "=========================================="
echo ""

# Get site name from command line or use default
SITE_NAME=${1:-erp.batasku.local}

echo "Site: $SITE_NAME"
echo ""

# Check if site exists
if ! bench --site $SITE_NAME list-apps > /dev/null 2>&1; then
    echo "❌ Error: Site '$SITE_NAME' not found"
    echo "Usage: ./deploy_delivery_note_return.sh [site-name]"
    exit 1
fi

# Check if batasku_custom app is installed
if ! bench --site $SITE_NAME list-apps | grep -q "batasku_custom"; then
    echo "❌ Error: batasku_custom app not installed on site '$SITE_NAME'"
    echo "Please install the app first: bench --site $SITE_NAME install-app batasku_custom"
    exit 1
fi

echo "✓ Site and app verified"
echo ""

# Step 1: Install custom fields
echo "Step 1: Installing custom fields..."
bench --site $SITE_NAME execute batasku_custom.install_delivery_note_return.install

if [ $? -eq 0 ]; then
    echo "✓ Custom fields installed successfully"
else
    echo "❌ Failed to install custom fields"
    exit 1
fi
echo ""

# Step 2: Verify installation
echo "Step 2: Verifying installation..."
bench --site $SITE_NAME execute batasku_custom.install_delivery_note_return.verify_installation

if [ $? -eq 0 ]; then
    echo "✓ Installation verified"
else
    echo "⚠️  Verification completed with warnings"
fi
echo ""

# Step 3: Clear cache
echo "Step 3: Clearing cache..."
bench --site $SITE_NAME clear-cache

if [ $? -eq 0 ]; then
    echo "✓ Cache cleared"
else
    echo "⚠️  Failed to clear cache"
fi
echo ""

# Step 4: Restart bench (optional, commented out by default)
# Uncomment if you want automatic restart
# echo "Step 4: Restarting bench..."
# bench restart
# echo "✓ Bench restarted"
# echo ""

echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart bench manually: bench restart"
echo "2. Test in ERPNext UI:"
echo "   - Create a Delivery Note"
echo "   - Submit it"
echo "   - Create Return from it"
echo "   - Verify custom fields appear"
echo ""
echo "3. Or test via Next.js frontend:"
echo "   - Navigate to: http://localhost:3000/sales-return"
echo "   - Create a return"
echo "   - Verify return reasons work"
echo ""
echo "Documentation:"
echo "- Quick Start: apps/batasku_custom/batasku_custom/QUICK_START_DELIVERY_NOTE_RETURN.md"
echo "- Full Guide: apps/batasku_custom/batasku_custom/DELIVERY_NOTE_RETURN_README.md"
echo ""

