# 📊 Google Sheets Setup Guide

Complete guide to export price data to Google Sheets.

---

## Overview

Export your tracked prices to Google Sheets for:
- Easy sharing with family/friends
- Visual charts and analysis
- Historical price tracking
- LLM-ready data format

---

## Step 1: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Click **"Enable APIs and Services"**
4. Search for **"Google Sheets API"**
5. Click **Enable**

---

## Step 2: Create Service Account

1. In Google Cloud Console, go to **"IAM & Admin"** → **"Service Accounts"**
2. Click **"Create Service Account"**
3. Name it: `price-tracker-bot`
4. Click **"Create and Continue"**
5. Skip optional steps, click **"Done"**

---

## Step 3: Generate Credentials

1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Select **JSON** format
5. Click **"Create"**
6. **Download the JSON file** - keep it safe!

---

## Step 4: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it: `Indian Price Tracker`
4. **Important**: Share this sheet with your service account:
   - Click **Share** button
   - Paste the `client_email` from your JSON file
   - Example: `price-tracker-bot@project-id.iam.gserviceaccount.com`
   - Give **Editor** permissions
   - Click **Done**

---

## Step 5: Add to GitHub Secrets

1. Open the downloaded JSON file in text editor
2. **Copy the ENTIRE contents** - all the JSON
3. Go to your GitHub repo → **Settings** → **Secrets** → **Actions**
4. Click **"New repository secret"**

### Secret 1: SHEETS_CREDENTIALS
```
Name: SHEETS_CREDENTIALS
Value: (paste entire JSON content)
```

Example JSON structure:
```json
{
  "type": "service_account",
  "project_id": "your-project-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "price-tracker-bot@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

### Secret 2: SHEETS_ENABLED
```
Name: SHEETS_ENABLED
Value: true
```

---

## Step 6: (Optional) Customize Sheet Name

If you want a different spreadsheet name:

```
Name: SHEETS_NAME
Value: My Custom Price Tracker
```

---

## Step 7: Test

1. Go to **Actions** tab
2. Run workflow manually
3. Check your Google Sheet - it should have 3 sheets:
   - **Products** - All tracked items
   - **Price History** - Historical data
   - **Hot Deals** - Current deals

---

## 📊 Sheet Structure

### Sheet 1: Products
| ID | Name | Threshold | Amazon URL | Flipkart URL | Meesho URL | Active |
|----|------|-----------|------------|--------------|------------|--------|
| 1 | iPhone 15 Pro | 120000 | url | url | | Yes |

### Sheet 2: Price History
| Product ID | Platform | Price | Original | Discount % | Below Threshold | Timestamp |
|------------|----------|-------|----------|------------|-----------------|-----------|
| 1 | Amazon | 134900 | 159900 | 16% | Yes | 2026-03-08 |

### Sheet 3: Hot Deals
| Product | Platform | Price | Original | Discount % | Threshold | Saved | Timestamp |
|---------|----------|-------|----------|------------|-----------|-------|-----------|
| iPhone 15 | Amazon | 134900 | 159900 | 16% | 140000 | 25000 | 2026-03-08 |

---

## 🎨 Formatting

Sheets are auto-formatted with:
- **Header row**: Blue background, white text
- **Hot Deals discount column**: Light green background
- **Formula in Saved column**: Auto-calculates savings
- **Auto-resized columns**: For better readability

---

## 🔧 Troubleshooting

### Error: "Unable to parse range"
- Make sure sheet name matches `SHEETS_NAME` in config
- Default is "Indian Price Tracker"

### Error: "Insufficient permissions"
- Verify you shared the sheet with service account email
- Give **Editor** permissions, not just Viewer

### Error: "API not enabled"
- Go back to Google Cloud Console
- Enable Google Sheets API

### JSON parsing error
- Make sure you copied the ENTIRE JSON file
- Don't add or remove any characters
- Keep all quotes and brackets intact

---

## 📈 Using the Data

### For Analysis:
- Create pivot tables
- Add charts and graphs
- Calculate average prices
- Track price trends

### For Sharing:
- Share sheet with family/friends
- They can see real-time deals
- No login needed (if public)

### For LLMs:
- Copy data to feed into ChatGPT/Claude
- Ask: "Analyze these price trends..."
- Get recommendations

---

## 🔐 Security

- **Never share your credentials JSON publicly**
- Store only in GitHub Secrets
- If compromised, delete service account and create new one
- Keep spreadsheet private or read-only for others

---

## ⚙️ Advanced

### Multiple Spreadsheets:
To export to multiple sheets, modify `integrations/sheets_export.py`:

```python
def export_to_multiple_sheets(self):
    sheets = [
        "Indian Price Tracker",
        "Family Price Tracker",
        "Friends Price Tracker"
    ]
    for sheet_name in sheets:
        # Export logic
```

### Custom Formatting:
Edit `integrations/sheets_export.py` to customize colors, formulas, etc.

---

✅ **Done! Your price data now syncs to Google Sheets every 6 hours!**
