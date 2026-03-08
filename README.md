# 🛒 Indian Price Tracker - Layer 4 Production Service

**24/7 Automated Price Tracking with Playwright Scraping & Real-Time Monitoring**

Track prices from Amazon.in, Flipkart & Meesho with advanced anti-bot measures, instant notifications, and a live monitoring dashboard - all running FREE on GitHub!

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-Enabled-45ba4b.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

### Core Features
- 🎭 **Playwright Scraping** - Advanced headless browser scraping (70-90% success rate)
- 🔄 **24/7 Automated Tracking** - Runs every 6 hours on GitHub Actions
- 📊 **Real-Time Monitoring** - Live dashboard showing status, metrics, and errors
- 🗄️ **SQLite Database** - Proper data storage with job tracking
- 🛍️ **Multi-Platform** - Amazon.in, Flipkart, Meesho

### Notifications
- 📱 **Telegram Bot** - Instant notifications on price drops
- 📧 **Email Alerts** - Enhanced HTML emails with deal summaries

### Integrations
- 📈 **Google Sheets Export** - Track price history in spreadsheets
- 🌐 **Web Dashboard** - Manage products via beautiful UI
- 🔍 **Live Deals Page** - Browse current deals across categories

### Monitoring & Analytics
- ✅ **Job Status Tracking** - Monitor every scraping run
- 📊 **Success Rate Metrics** - Track performance by platform
- 📝 **Error Logging** - Detailed error tracking with retry results
- 🌐 **External API Access** - All monitoring data accessible via HTTP

### Zero Cost
- 💰 **100% FREE** - No hosting costs, runs entirely on GitHub

---

## 🌐 Live Monitoring

View real-time tracker status and metrics:

**🔴 Monitoring Dashboard:**
- **URL:** `https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/monitoring.html`
- Auto-refreshes every 30 seconds
- Shows current job status, platform health, recent runs

**📊 Raw Data Endpoints (Markdown):**
- **Status:** `https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/status.md`
- **Metrics:** `https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/metrics.md`
- **Logs:** `https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/logs.md`

**🧪 Test Access:**
- **URL:** `https://aispiringcoder4302.github.io/indian-price-tracker/test-access.html`
- Verify all monitoring files are accessible externally

---

## 🚀 Quick Start

### 1. Fork/Clone Repository

```bash
git clone https://github.com/aispiringcoder4302/indian-price-tracker.git
cd indian-price-tracker
```

### 2. Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Source: `Deploy from a branch`
3. Branch: `main` → `/web` folder
4. Click **Save**
5. Your dashboard will be live at: `https://aispiringcoder4302.github.io/indian-price-tracker/`

### 3. Configure Secrets

Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**Required Secrets:**

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `SENDER_EMAIL` | Gmail address | Your Gmail |
| `SENDER_PASSWORD` | Gmail app password | [Generate here](https://myaccount.google.com/apppasswords) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Chat with [@BotFather](https://t.me/botfather) |
| `TELEGRAM_CHAT_IDS` | Your Telegram chat ID | Chat with [@userinfobot](https://t.me/userinfobot) |

**Optional Secrets:**

| Secret Name | Description |
|------------|-------------|
| `RECEIVER_EMAIL` | Different email for alerts (defaults to SENDER_EMAIL) |
| `SHEETS_CREDENTIALS` | Google service account JSON (see [Sheets Setup](docs/SHEETS_SETUP.md)) |
| `SHEETS_ENABLED` | Set to `true` to enable Sheets export |

### 4. Add Products

Open your dashboard: `https://aispiringcoder4302.github.io/indian-price-tracker/`

1. Fill in product details
2. Add URLs for Amazon/Flipkart/Meesho
3. Set price threshold
4. Click "Add Product"
5. Copy generated JSON
6. Edit `products.json` in your repo
7. Paste and commit

### 5. Run!

- **Automatic**: Runs every 6 hours via GitHub Actions
- **Manual**: Go to **Actions** tab → **Run workflow**

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│           GitHub Repository (FREE - Layer 4)             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🌐 Web Dashboard (GitHub Pages)                        │
│     https://aispiringcoder4302.github.io/...            │
│     ├─ Product Manager                                  │
│     ├─ Live Deals Viewer                                │
│     ├─ Monitoring Dashboard                             │
│     └─ External API Access                              │
│                                                         │
│  🤖 Backend (GitHub Actions)                            │
│     Runs every 6 hours automatically                    │
│     ├─ Playwright scraping (headless Chrome)            │
│     ├─ Job tracking & monitoring                        │
│     ├─ Database updates (SQLite)                        │
│     ├─ Notifications (Telegram/Email)                   │
│     ├─ Google Sheets export                             │
│     └─ Monitoring markdown updates                      │
│                                                         │
│  🗄️  Data Storage                                       │
│     ├─ tracker.db (SQLite)                              │
│     │  ├─ products                                      │
│     │  ├─ price_history                                 │
│     │  ├─ notifications                                 │
│     │  ├─ job_runs                                      │
│     │  └─ error_log                                     │
│     └─ web/monitoring/ (Markdown files)                 │
│        ├─ status.md                                     │
│        ├─ metrics.md                                    │
│        └─ logs.md                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---
│     └─ tracker.db (SQLite in repo)          │
│                                             │
└─────────────────────────────────────────────┘
         ↓↓↓ Notifications ↓↓↓
┌──────────────┬──────────────┬──────────────┐
│   Telegram   │    Email     │ Google Sheets│
└──────────────┴──────────────┴──────────────┘
```

---

## 📁 Project Structure

```
indian-price-tracker/
├── core/
│   ├── database.py           # SQLite database operations
│   ├── price_tracker.py      # Enhanced scraping with retry logic
│   └── notifications.py      # Unified notification system
├── integrations/
│   ├── telegram_bot.py       # Telegram Bot API integration
│   └── sheets_export.py      # Google Sheets export
├── web/
│   ├── index.html            # Product management dashboard
│   ├── live-deals.html       # Browse 111+ live deals
│   └── deals_data.json       # Deal data for live page
├── docs/
│   ├── TELEGRAM_SETUP.md     # Telegram bot setup guide
│   └── SHEETS_SETUP.md       # Google Sheets setup guide
├── .github/workflows/
│   └── price-tracker.yml     # GitHub Actions automation
├── config.py                 # Configuration management
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🔧 Configuration

All settings via environment variables (GitHub Secrets):

```python
# Email Settings
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
RECEIVER_EMAIL = "alerts@gmail.com"  # Optional

# Telegram Settings
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_IDS = "123456789,987654321"  # Comma-separated

# Google Sheets Settings (Optional)
SHEETS_CREDENTIALS = '{"type":"service_account",...}'
SHEETS_ENABLED = "true"
SHEETS_NAME = "Indian Price Tracker"

# Scraping Settings
SCRAPE_INTERVAL = 6  # Hours (set in workflow file)
MAX_RETRIES = 3
TIMEOUT = 15  # Seconds
```

---

## 📖 Setup Guides

- **[Telegram Bot Setup](docs/TELEGRAM_SETUP.md)** - Create bot, get token & chat ID
- **[Google Sheets Setup](docs/SHEETS_SETUP.md)** - Enable API, create service account

---

## 💡 Usage Examples

### Track a Product

```python
# Via web dashboard (easiest)
1. Open https://intrpik.github.io/indian-price-tracker/
2. Fill form
3. Copy JSON
4. Update products.json

# Via database directly
from core.database import db
db.add_product(
    name="iPhone 15 Pro Max",
    threshold=120000,
    amazon_url="https://amazon.in/dp/...",
    flipkart_url="https://flipkart.com/..."
)
```

### Get Deals

```python
from core.database import db
deals = db.get_deals(limit=10)
for deal in deals:
    print(f"{deal['name']}: ₹{deal['price']} ({deal['platform']})")
```

### Send Custom Notification

```python
from core.notifications import notifier
notifier.send_price_drop_alert(
    product={'name': 'Product', 'threshold': 5000},
    platform='Amazon',
    old_price=6000,
    new_price=4500,
    url='https://...'
)
```

---

## 🔄 How It Works

1. **GitHub Actions triggers** every 6 hours (configurable)
2. **Scraper runs** - Checks all products across platforms
3. **Database updates** - Stores prices in SQLite
4. **Notifications sent** - If price < threshold:
   - Telegram message to your phone
   - Email with deal details
   - Google Sheets updated (if enabled)
5. **Database committed** - Changes pushed back to repo
6. **Repeat!** - Cycle continues automatically

---

## 📱 Notifications

### Telegram Notification Example:
```
🔥 Price Drop Alert!

iPhone 15 Pro Max (256GB)
Platform: Amazon

Old Price: ₹1,59,900
New Price: ₹1,34,900
You Save: ₹25,000 (16% OFF)

Your Threshold: ₹1,40,000
Below Threshold: ✅

[View Product →]
```

### Email Example:
Beautiful HTML email with:
- Product details
- Price comparison
- Discount percentage
- Direct product link
- Threshold info

---

## 📊 Google Sheets Export

When enabled, creates 3 sheets:

**Sheet 1: Products**
- All tracked products
- Current prices
- Status

**Sheet 2: Price History**
- Historical price data
- Timestamp tracking
- Platform comparison

**Sheet 3: Hot Deals**
- Deals below threshold
- Auto-calculated savings
- Sorted by discount %

---

## 🛠️ Advanced Configuration

### Change Tracking Frequency

Edit `.github/workflows/price-tracker.yml`:

```yaml
schedule:
  # Every 6 hours (default)
  - cron: '0 */6 * * *'
  
  # Every 3 hours (more frequent)
  # - cron: '0 */3 * * *'
  
  # Every 12 hours (less frequent)
  # - cron: '0 */12 * * *'
  
  # Daily at 9 AM IST (3:30 AM UTC)
  # - cron: '30 3 * * *'
```

### Add More Platforms

Extend `core/price_tracker.py`:

```python
def scrape_snapdeal(self, url, product_name):
    # Add scraping logic
    pass
```

### Custom Notifications

Create new notification channels in `core/notifications.py`

---

## 🐛 Troubleshooting

### Prices Not Fetching?
- Websites block scrapers - this is normal
- Check GitHub Actions logs for errors
- Verify URLs are correct and complete
- Some products work better than others

### Telegram Not Working?
- Verify bot token is correct
- Check chat ID format (numbers only)
- Make sure you've messaged the bot first (

/start)

### Email Not Sending?
- Use Gmail App Password, not regular password
- Enable 2FA on Gmail first
- Check spam folder

### GitHub Actions Failing?
- Check secrets are added correctly
- Verify requirements.txt dependencies
- Review Actions logs for specific error

---

## 💰 Cost Breakdown

| Service | Cost | Usage |
|---------|------|-------|
| GitHub Actions | FREE | 2000 min/month (uses ~60) |
| GitHub Pages | FREE | Unlimited bandwidth |
| Database Storage | FREE | In repo (<100MB limit) |
| Telegram API | FREE | Unlimited messages |
| Gmail SMTP | FREE | Built-in |
| Google Sheets API | FREE | 100 requests/100sec |
| **TOTAL** | **₹0** | **Forever!** |

---

## 🎯 Pro Tips

1. **During Sales**: Increase frequency to every 1-2 hours
2. **Smart Thresholds**: Set 5-10% below current price
3. **Multiple Variants**: Track different colors/sizes separately
4. **Backup Data**: Download `tracker.db` periodically
5. **Share Deals**: Forward Telegram alerts to family group

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 📄 License

MIT License - Free to use and modify

---

## 🙏 Credits

Built with inspiration from international price trackers:
- Italian Amazon Tracker (Telegram integration)
- Russian Wildberries Monitor (Google Sheets)
- Chinese MarketSpider (Multi-platform)
- Spanish Mercado Libre Tracker (Architecture)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/intrpik/indian-price-tracker/issues)
- **Telegram**: [@intrpik](https://t.me/intrpik)

---

## ⭐ Star This Repo!

If this project helps you save money, give it a star! ⭐

---

**Made with ❤️ for Indian shoppers | Never miss a deal again! 🛒💰**
