#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indian Price Tracker - Main Entry Point
Tracks prices from Amazon.in, Flipkart, and Meesho
Sends notifications via Email and Telegram, exports to Google Sheets
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.database import db
from core.price_tracker import PriceTracker
from core.notifications import notifier
from integrations.sheets_export import SheetsExporter

def main():
    print("=" * 60)
    print("🚀 Indian Price Tracker - Production Version")
    print("=" * 60)
    print()
    
    # Show configuration
    config_summary = config.get_config_summary()
    print("📋 Configuration:")
    for key, value in config_summary.items():
        print(f"   {key}: {value}")
    print()
    
    # Initialize database
    print("🗄️  Initializing database...")
    db.connect()
    
    # Migrate from JSON if exists
    if os.path.exists('products.json'):
        print("📦 Migrating from products.json...")
        db.migrate_from_json('products.json')
    
    # Get database stats
    stats = db.get_stats()
    print(f"   Total products: {stats['total_products']}")
    print(f"   Products with deals: {stats['products_with_deals']}")
    print()
    
    # Run price tracker
    print("🔍 Starting price tracking...")
    tracker = PriceTracker()
    results = tracker.track_all_products()
    
    print()
    print("=" * 60)
    print("📊 Tracking Results:")
    print(f"   Total checks: {results['total_checks']}")
    print(f"   Successful: {results['successful']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Deals found: {results['deals_found']}")
    print()
    
    # Platform summary
    print("📈 Platform Summary:")
    for platform, data in results['platform_summary'].items():
        if data['count'] > 0:
            print(f"   {platform}: {data['count']} products")
            print(f"      Avg: ₹{data['avg_price']:,.2f}")
            if data['min_price']:
                print(f"      Range: ₹{data['min_price']:,.2f} - ₹{data['max_price']:,.2f}")
    print()
    
    # Send notifications for deals
    if results['deals_found'] > 0:
        print("📧 Sending notifications...")
        deals = db.get_deals(limit=50)
        
        # Send individual alerts for price drops
        for deal in deals[:5]:  # Top 5 deals
            if config.EMAIL_ENABLED or config.TELEGRAM_ENABLED:
                product = db.get_product(deal['product_id'])
                notifier.send_price_drop_alert(
                    product=product,
                    platform=deal['platform'],
                    old_price=deal.get('original_price', deal['price'] * 1.2),
                    new_price=deal['price'],
                    url=deal.get('url', '#')
                )
        
        # Send deals digest
        if config.DAILY_DIGEST:
            notifier.send_deals_digest(deals)
        
        print(f"   ✅ Notifications sent for {min(5, len(deals))} deals")
    else:
        print("ℹ️  No deals found below threshold")
    print()
    
    # Export to Google Sheets
    if config.SHEETS_ENABLED and config.SHEETS_CREDENTIALS:
        print("📊 Exporting to Google Sheets...")
        try:
            exporter = SheetsExporter()
            success, message = exporter.authenticate()
            
            if success:
                # Export products
                products = db.get_all_products()
                success, msg = exporter.export_products(products)
                print(f"   Products: {msg}")
                
                # Export deals
                deals = db.get_deals(limit=100)
                success, msg = exporter.export_deals(deals)
                print(f"   Deals: {msg}")
            else:
                print(f"   ❌ Authentication failed: {message}")
        except Exception as e:
            print(f"   ❌ Sheets export error: {e}")
    print()
    
    # Cleanup old data (keep 90 days)
    deleted = db.cleanup_old_data(days=90)
    if deleted > 0:
        print(f"🧹 Cleaned up {deleted} old price records")
    
    # Close database
    db.close()
    
    print()
    print("=" * 60)
    print("✅ Price tracking completed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
