# 📱 Telegram Bot Setup Guide

Complete guide to set up Telegram notifications for price alerts.

---

## Step 1: Create Telegram Bot

1. Open Telegram app
2. Search for **@BotFather**
3. Send `/newbot` command
4. Follow prompts:
   - Bot name: `Indian Price Tracker Bot` (or any name)
   - Username: `your_price_tracker_bot` (must end with 'bot')
5. **Copy the token** - looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

---

## Step 2: Get Your Chat ID

1. Search for **@userinfobot** on Telegram
2. Send `/start` command
3. Bot replies with your **Chat ID** - looks like: `123456789`
4. **Copy this number**

---

## Step 3: Start Your Bot

1. Search for your bot username
2. Send `/start` command
3. This activates the bot

---

## Step 4: Add to GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**

Add these two secrets:

### Secret 1: TELEGRAM_BOT_TOKEN
```
Name: TELEGRAM_BOT_TOKEN
Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Secret 2: TELEGRAM_CHAT_IDS
```
Name: TELEGRAM_CHAT_IDS
Value: 123456789
```

**For multiple users**, comma-separate:
```
Value: 123456789,987654321,555555555
```

---

## Step 5: Test

1. Go to **Actions** tab in your repo
2. Click **"Run workflow"**
3. Wait for completion
4. Check if you receive test message on Telegram!

---

## 📱 Notification Example

When a deal is found, you'll receive:

```
🔥 Price Drop Alert!

iPhone 15 Pro Max (256GB)
Platform: Amazon

Old Price: ₹1,59,900
New Price: ₹1,34,900
You Save: ₹25,000 (16% OFF)

Your Threshold: ₹1,40,000
Below Threshold: ✅

View Product → [link]
```

---

## 🔧 Troubleshooting

### Not Receiving Messages?

1. **Check bot token** - Make sure it's correct
2. **Start the bot** - Send `/start` to your bot
3. **Verify chat ID** - Use @userinfobot again
4. **Check secrets** - Ensure they're added in GitHub
5. **Test manually** - Run workflow manually from Actions tab

### Multiple Recipients?

Add multiple chat IDs separated by commas:
```
TELEGRAM_CHAT_IDS: 123456789,987654321,111111111
```

Everyone will receive alerts!

---

## ⚙️ Advanced: Bot Commands (Optional)

If you want interactive commands, extend `integrations/telegram_bot.py`:

```python
# Future features:
/start - Welcome message
/add <url> <threshold> - Add product
/list - Show tracked products
/deals - Show current deals
/stop <id> - Stop tracking product
```

---

## 🔐 Security

- **Never share your bot token publicly**
- Store only in GitHub Secrets
- If compromised, use @BotFather to revoke and generate new token

---

✅ **Done! You'll now receive instant Telegram alerts on price drops!**
