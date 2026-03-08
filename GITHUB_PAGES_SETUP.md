# 🌐 GitHub Pages Setup Guide

## Current Status
✅ All web files are ready in the `web/` folder  
⏳ GitHub Pages needs to be enabled manually

---

## 📋 Step-by-Step Setup

### Option 1: Using GitHub Web Interface (Recommended)

1. **Go to Repository Settings**
   - Visit: https://github.com/aispiringcoder4302/indian-price-tracker/settings/pages

2. **Configure GitHub Pages**
   - Under **"Source"**: Select `Deploy from a branch`
   - Under **"Branch"**: 
     - Select: `main`
     - Folder: `/web`
   - Click **"Save"**

3. **Wait for Deployment (2-3 minutes)**
   - GitHub will show: "Your site is live at..."
   - You'll see a green checkmark when ready

4. **Access Your Sites**
   Once deployed, you'll have:
   - **Main Dashboard:** https://aispiringcoder4302.github.io/indian-price-tracker/
   - **Monitoring:** https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/monitoring.html
   - **Live Deals:** https://aispiringcoder4302.github.io/indian-price-tracker/live-deals.html
   - **Test Access:** https://aispiringcoder4302.github.io/indian-price-tracker/test-access.html

---

### Option 2: Using GitHub CLI (If Installed)

```bash
# Enable GitHub Pages
gh api repos/aispiringcoder4302/indian-price-tracker/pages -X POST -f source[branch]=main -f source[path]=/web
```

---

### Option 3: Using API with Your PAT

```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/aispiringcoder4302/indian-price-tracker/pages \
  -d '{"source":{"branch":"main","path":"/docs"}}'
```

---

## ✅ Verification

After enabling, verify it's working:

1. **Check Deployment Status**
   - Go to: https://github.com/aispiringcoder4302/indian-price-tracker/actions
   - Look for "pages-build-deployment" workflow
   - Should show green checkmark

2. **Test Access**
   - Visit: https://aispiringcoder4302.github.io/indian-price-tracker/
   - Should load the product manager dashboard

3. **Test Monitoring Dashboard**
   - Visit: https://aispiringcoder4302.github.io/indian-price-tracker/monitoring/monitoring.html
   - Should load with Status/Metrics/Logs tabs

---

## 🔧 Troubleshooting

### Pages Not Loading?
- Wait 2-3 minutes after enabling
- Check Actions tab for deployment errors
- Clear browser cache (Ctrl+Shift+R)

### 404 Error?
- Verify branch is `main` not `master`
- Verify path is `/web` not `/` or `/docs`
- Check files exist in `web/` folder

### Monitoring Data Empty?
- Run GitHub Actions workflow first
- Wait for workflow to complete
- Check that `web/monitoring/*.md` files are committed

---

## 🚀 Next Steps

After GitHub Pages is enabled:

1. **Run First Job**
   - Go to: https://github.com/aispiringcoder4302/indian-price-tracker/actions
   - Click "Indian Price Tracker - Layer 4 Production"
   - Click "Run workflow"

2. **Add Products**
   - Visit your dashboard
   - Add product details
   - Commit `products.json` to repo

3. **Configure Secrets** (if not done)
   - Go to: https://github.com/aispiringcoder4302/indian-price-tracker/settings/secrets/actions
   - Add: `SENDER_EMAIL`, `SENDER_PASSWORD`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_IDS`

---

## 📞 Quick Links

- **Repository:** https://github.com/aispiringcoder4302/indian-price-tracker
- **Pages Settings:** https://github.com/aispiringcoder4302/indian-price-tracker/settings/pages
- **Actions:** https://github.com/aispiringcoder4302/indian-price-tracker/actions
- **Secrets:** https://github.com/aispiringcoder4302/indian-price-tracker/settings/secrets/actions

---

**Choose Option 1 (Web Interface) - it's the easiest!**
