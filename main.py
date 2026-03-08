#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indian Price Tracker - Main Entry Point
Tracks prices from Amazon.in, Flipkart, and Meesho
Sends notifications via Email and Telegram, exports to Google Sheets
Layer 4 Production: Playwright scraping + Monitoring dashboard
"""

import sys
import io

# Fix Windows console encoding FIRST - before any other imports
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.database import db
from core.price_tracker import PriceTracker
from core.notifications import notifier
from core.monitoring import MonitoringLogger
from core.playwright_scraper import scrape_with_playwright
from integrations.sheets_export import SheetsExporter

def main():
    print("=" * 60)
    print("🚀 Indian Price Tracker - Layer 4 Production Service")
    print("=" * 60)
    print()
    
    # Initialize monitoring
    monitor = MonitoringLogger()
    
    # Show configuration
    config_summary = config.get_config_summary()
    print("📋 Configuration:")
    for key, value in config_summary.items():
        print(f"   {key}: {value}")
    print()
    
    # Initialize database
    print("🗄️  Initializing database...")
    db.connect()
    
    # Start job tracking
    job_id = db.start_job()
    job_start_time = datetime.now()
    
    # Migrate from JSON if exists
    if os.path.exists('products.json'):
        print("📦 Migrating from products.json...")
        db.migrate_from_json('products.json')
    
    # Get database stats
    stats = db.get_stats()
    print(f"   Total products: {stats['total_products']}")
    print(f"   Products with deals: {stats['products_with_deals']}")
    print()
    
    # Run price tracker with Playwright
    print("🎭 Starting Playwright-based price tracking...")
    tracker = PriceTracker()
    
    # Get all products
    products = db.get_all_products()
    total_products = len(products)
    checked_products = 0
    deals_found = 0
    errors_count = 0
    
    # Track status for monitoring
    platforms_status = {'Amazon': 'pending', 'Flipkart': 'pending', 'Meesho': 'pending'}
    
    # Process each product with Playwright
    for product in products:
        product_id = product['id']
        product_name = product['name']
        
        print(f"\n📦 Checking: {product_name}")
        
        # Check each platform
        for platform_name, url_key in [('Amazon', 'amazon_url'), ('Flipkart', 'flipkart_url'), ('Meesho', 'meesho_url')]:
            url = product.get(url_key)
            if not url:
                continue
            
            platforms_status[platform_name] = 'running'
            
            # Update monitoring status
            monitor.update_status(
                current_job={
                    'running': True,
                    'status': 'running',
                    'checked': checked_products,
                    'total': total_products,
                    'platforms': platforms_status,
                    'deals': deals_found,
                    'notifications': 0,
                    'duration': int((datetime.now() - job_start_time).total_seconds())
                },
                recent_runs=[]
            )
            
            try:
                # Use Playwright scraper
                result = scrape_with_playwright(url, platform_name, product_name)
                
                if result and result.get('price'):
                    price = result['price']
                    print(f"   ✅ {platform_name}: ₹{price:,.2f}")
                    
                    # Save to database
                    db.add_price_record(
                        product_id=product_id,
                        platform=platform_name,
                        price=price,
                        available=True
                    )
                    
                    # Check if it's a deal
                    if price <= product['threshold']:
                        deals_found += 1
                        print(f"      🎉 DEAL! Below threshold ₹{product['threshold']:,.2f}")
                    
                    platforms_status[platform_name] = 'success'
                    
                elif result and result.get('error'):
                    error_msg = result['error']
                    print(f"   ⚠️ {platform_name}: {error_msg}")
                    
                    # Log error
                    error_type = 'timeout' if 'timeout' in error_msg.lower() else 'selector' if 'selector' in error_msg.lower() else 'network'
                    db.log_error(
                        job_run_id=job_id,
                        product_id=product_id,
                        platform=platform_name,
                        error_type=error_type,
                        error_message=error_msg,
                        retry_result='Failed'
                    )
                    
                    # Log to monitoring
                    monitor.log_error(
                        product=product_name,
                        platform=platform_name,
                        error={'type': error_type, 'message': error_msg},
                        retry_result='Failed'
                    )
                    
                    errors_count += 1
                    platforms_status[platform_name] = 'error'
                else:
                    print(f"   ⚠️ {platform_name}: Price not found")
                    platforms_status[platform_name] = 'error'
                    
            except Exception as e:
                print(f"   ❌ {platform_name}: {str(e)}")
                db.log_error(
                    job_run_id=job_id,
                    product_id=product_id,
                    platform=platform_name,
                    error_type='exception',
                    error_message=str(e),
                    retry_result='Failed'
                )
                errors_count += 1
                platforms_status[platform_name] = 'error'
        
        checked_products += 1
        
        # Update job progress
        db.update_job(
            job_id=job_id,
            products_checked=checked_products,
            deals_found=deals_found,
            errors_count=errors_count
        )
    
    # End job tracking
    job_status = 'success' if errors_count == 0 else 'partial' if checked_products > 0 else 'failed'
    db.end_job(job_id, status=job_status)
    
    job_duration = int((datetime.now() - job_start_time).total_seconds())
    
    print()
    print("=" * 60)
    print("📊 Tracking Results:")
    print(f"   Total products checked: {checked_products}")
    print(f"   Deals found: {deals_found}")
    print(f"   Errors: {errors_count}")
    print(f"   Duration: {job_duration}s")
    print(f"   Status: {job_status.upper()}")
    print()
    
    # Update monitoring with final status
    recent_runs = db.get_recent_job_runs(limit=10)
    recent_runs_formatted = []
    for run in recent_runs:
        recent_runs_formatted.append({
            'time': run['start_time'].split()[1] if ' ' in run['start_time'] else run['start_time'],
            'status': run['status'],
            'products': run['products_checked'],
            'deals': run['deals_found'],
            'duration': run['duration_seconds'] or 0
        })
    
    monitor.update_status(
        current_job={
            'running': False,
            'status': job_status,
            'checked': checked_products,
            'total': total_products,
            'platforms': platforms_status,
            'deals': deals_found,
            'notifications': 0,
            'duration': job_duration
        },
        recent_runs=recent_runs_formatted
    )
    
    # Update metrics
    metrics = monitor.calculate_metrics(db.conn)
    monitor.update_metrics(metrics)
    
    # Update error summary
    error_summary = db.get_error_summary(hours=24)
    monitor.update_error_summary(error_summary)
    
    print("📊 Monitoring dashboard updated!")
    print()
    
    # Send notifications for deals
    if deals_found > 0:
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
    print("🌐 View monitoring dashboard at:")
    print("   https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/monitoring.html")
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
