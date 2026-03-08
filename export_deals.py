"""
Export real deals from database to JSON for web display
"""
import sys
import io
import json
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from core.database import db

def export_deals_to_json():
    """Export current deals to JSON for web display (assumes db is already connected)"""
    
    # Get all products
    products = db.get_all_products(active_only=True)
    
    deals = []
    for product in products:
        # Get latest prices for each platform
        for platform in ['Amazon', 'Flipkart', 'Meesho']:
            latest = db.get_latest_price(product['id'], platform)
            
            if latest and latest.get('price'):
                price = latest['price']
                threshold = product['threshold']
                
                # Determine category based on product name
                name_lower = product['name'].lower()
                if any(word in name_lower for word in ['phone', 'iphone', 'samsung', 'mobile']):
                    category = 'Electronics'
                elif any(word in name_lower for word in ['tv', 'laptop', 'tablet', 'watch']):
                    category = 'Electronics'
                elif any(word in name_lower for word in ['shirt', 'jeans', 'shoe', 'dress']):
                    category = 'Fashion'
                elif any(word in name_lower for word in ['sofa', 'chair', 'table', 'bed']):
                    category = 'Home'
                else:
                    category = 'Electronics'
                
                # Calculate discount
                if latest.get('original_price'):
                    original = latest['original_price']
                    discount = int(((original - price) / original) * 100)
                else:
                    original = threshold
                    discount = int(((original - price) / original) * 100) if original > price else 0
                
                deal = {
                    'title': product['name'],
                    'platform': platform,
                    'category': category,
                    'price': int(price),
                    'originalPrice': int(original),
                    'discount': discount,
                    'url': product.get(f'{platform.lower()}_url', '#'),
                    'image': f'https://via.placeholder.com/200x200?text={category}',
                    'timestamp': latest.get('timestamp', datetime.now().isoformat())
                }
                
                deals.append(deal)
    
    # Write to JSON file
    output_file = Path('docs/deals_data.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(deals, f, indent=2, ensure_ascii=False)
    
    return len(deals)

if __name__ == '__main__':
    export_deals_to_json()
