"""
SQLite Database Module for Indian Price Tracker
Handles all database operations with proper schema and migrations
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import config

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def init_database(self):
        """Initialize database with schema"""
        self.connect()
        
        # Products table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                threshold REAL NOT NULL,
                amazon_url TEXT,
                flipkart_url TEXT,
                meesho_url TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Price history table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                price REAL,
                original_price REAL,
                discount_percent REAL,
                below_threshold BOOLEAN DEFAULT 0,
                available BOOLEAN DEFAULT 1,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Create indexes
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_product 
            ON price_history(product_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_timestamp 
            ON price_history(timestamp DESC)
        """)
        
        # Notifications log
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                platform TEXT,
                old_price REAL,
                new_price REAL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        self.conn.commit()
        print(f"Database initialized: {self.db_path}")
    
    def migrate_from_json(self, json_file: str = 'products.json'):
        """Migrate data from JSON to SQLite"""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            products = data.get('products', [])
            for product in products:
                self.add_product(
                    name=product['name'],
                    threshold=product['threshold'],
                    amazon_url=product['urls'].get('amazon', ''),
                    flipkart_url=product['urls'].get('flipkart', ''),
                    meesho_url=product['urls'].get('meesho', '')
                )
            
            print(f"Migrated {len(products)} products from {json_file}")
        except Exception as e:
            print(f"Migration error: {e}")
    
    def add_product(self, name: str, threshold: float, 
                   amazon_url: str = '', flipkart_url: str = '', 
                   meesho_url: str = '') -> int:
        """Add a new product to track"""
        self.cursor.execute("""
            INSERT INTO products (name, threshold, amazon_url, flipkart_url, meesho_url)
            VALUES (?, ?, ?, ?, ?)
        """, (name, threshold, amazon_url, flipkart_url, meesho_url))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_products(self, active_only: bool = True) -> List[Dict]:
        """Get all products"""
        query = "SELECT * FROM products"
        if active_only:
            query += " WHERE active = 1"
        
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        """Get a single product by ID"""
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_product(self, product_id: int, **kwargs):
        """Update product fields"""
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'threshold', 'amazon_url', 'flipkart_url', 'meesho_url', 'active']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            values.append(product_id)
            query = f"UPDATE products SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
    
    def delete_product(self, product_id: int):
        """Soft delete product"""
        self.cursor.execute("UPDATE products SET active = 0 WHERE id = ?", (product_id,))
        self.conn.commit()
    
    def add_price_record(self, product_id: int, platform: str, price: Optional[float],
                        original_price: Optional[float] = None, 
                        discount_percent: Optional[float] = None,
                        available: bool = True) -> int:
        """Add a price history record"""
        product = self.get_product(product_id)
        below_threshold = price <= product['threshold'] if price and product else False
        
        self.cursor.execute("""
            INSERT INTO price_history 
            (product_id, platform, price, original_price, discount_percent, below_threshold, available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, platform, price, original_price, discount_percent, below_threshold, available))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_price_history(self, product_id: int, platform: str = None, 
                         limit: int = 100) -> List[Dict]:
        """Get price history for a product"""
        query = "SELECT * FROM price_history WHERE product_id = ?"
        params = [product_id]
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_latest_price(self, product_id: int, platform: str) -> Optional[Dict]:
        """Get latest price for a product on a platform"""
        self.cursor.execute("""
            SELECT * FROM price_history 
            WHERE product_id = ? AND platform = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (product_id, platform))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def add_notification(self, product_id: int, type: str, platform: str,
                        old_price: float = None, new_price: float = None,
                        status: str = 'sent'):
        """Log a notification"""
        self.cursor.execute("""
            INSERT INTO notifications 
            (product_id, type, platform, old_price, new_price, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, type, platform, old_price, new_price, status))
        self.conn.commit()
    
    def get_deals(self, limit: int = 50) -> List[Dict]:
        """Get current deals (below threshold)"""
        self.cursor.execute("""
            SELECT p.*, ph.platform, ph.price, ph.original_price, 
                   ph.discount_percent, ph.timestamp
            FROM products p
            JOIN price_history ph ON p.id = ph.product_id
            WHERE ph.below_threshold = 1 
            AND ph.available = 1
            AND p.active = 1
            AND ph.id IN (
                SELECT MAX(id) FROM price_history 
                GROUP BY product_id, platform
            )
            ORDER BY ph.discount_percent DESC, ph.timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) as count FROM products WHERE active = 1")
        stats['total_products'] = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(*) as count FROM price_history WHERE below_threshold = 1")
        stats['total_deals'] = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(DISTINCT product_id) as count FROM price_history WHERE below_threshold = 1")
        stats['products_with_deals'] = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE date(sent_at) = date('now')")
        stats['notifications_today'] = self.cursor.fetchone()['count']
        
        return stats
    
    def cleanup_old_data(self, days: int = 90):
        """Remove old price history records"""
        self.cursor.execute("""
            DELETE FROM price_history 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """, (days,))
        deleted = self.cursor.rowcount
        self.conn.commit()
        return deleted

# Singleton instance
db = Database()

if __name__ == '__main__':
    db = Database('test_tracker.db')
    print("Database created successfully!")
    print("Stats:", db.get_stats())
    db.close()
