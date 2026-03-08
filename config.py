"""
Configuration Management for Indian Price Tracker
Handles all environment variables and settings
"""

import os
import json

# Email Configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', SENDER_EMAIL)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_IDS = [id.strip() for id in os.getenv('TELEGRAM_CHAT_IDS', '').split(',') if id.strip()]
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS)

# Google Sheets Configuration
SHEETS_CREDENTIALS_JSON = os.getenv('SHEETS_CREDENTIALS', '')
SHEETS_ENABLED = os.getenv('SHEETS_ENABLED', 'false').lower() == 'true'
SHEETS_NAME = os.getenv('SHEETS_NAME', 'Indian Price Tracker')

try:
    SHEETS_CREDENTIALS = json.loads(SHEETS_CREDENTIALS_JSON) if SHEETS_CREDENTIALS_JSON else {}
except:
    SHEETS_CREDENTIALS = {}

# Scraping Configuration
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', 6))  # Hours
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
TIMEOUT = int(os.getenv('TIMEOUT', 15))  # Seconds
RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', 2))  # Seconds between requests

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'tracker.db')

# Notification Settings
EMAIL_ENABLED = bool(SENDER_EMAIL and SENDER_PASSWORD)
DAILY_DIGEST = os.getenv('DAILY_DIGEST', 'false').lower() == 'true'

# Platform Configuration
PLATFORMS = {
    'amazon': {
        'name': 'Amazon.in',
        'base_url': 'https://www.amazon.in',
        'enabled': True
    },
    'flipkart': {
        'name': 'Flipkart',
        'base_url': 'https://www.flipkart.com',
        'enabled': True
    },
    'meesho': {
        'name': 'Meesho',
        'base_url': 'https://www.meesho.com',
        'enabled': True
    }
}

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_config_summary():
    """Return configuration summary for debugging"""
    return {
        'email_enabled': EMAIL_ENABLED,
        'telegram_enabled': TELEGRAM_ENABLED,
        'sheets_enabled': SHEETS_ENABLED,
        'platforms': len([p for p in PLATFORMS.values() if p['enabled']]),
        'scrape_interval': SCRAPE_INTERVAL,
        'database': DATABASE_PATH
    }

if __name__ == '__main__':
    import json
    print(json.dumps(get_config_summary(), indent=2))
