# 🐦 Twitter/X MCP Server - Playwright Automation

**Status:** ✅ COMPLETE  
**Date:** 2026-03-06  
**Method:** Browser Automation (Playwright)

---

## 📋 OVERVIEW

This MCP server uses **Playwright browser automation** to post tweets to X (Twitter), bypassing the API limitations of the free developer plan.

### Why Browser Automation?

- ❌ Twitter API v2 Free Plan: Cannot post tweets (POST /2/tweets blocked)
- ✅ Playwright Automation: Works with any Twitter account
- ✅ Session Persistence: Login once, reuse session
- ✅ No API Rate Limits: Limited only by Twitter's web interface

---

## 🚀 INSTALLATION

### Step 1: Install Python Dependencies

```bash
cd "E:\Hackathon 0\Bronze\Personal-AI-Employee"

# Activate virtual environment (if using)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r mcp_servers/requirements-twitter-playwright.txt
```

### Step 2: Install Playwright Browsers

```bash
# Install Playwright browsers (Chromium, Firefox, WebKit)
playwright install

# Install Chromium specifically (recommended)
playwright install chromium

# Install system dependencies (Windows doesn't need this)
# playwright install-deps  # Only for Linux/Mac
```

### Step 3: Verify Installation

```bash
python -c "from playwright.async_api import async_playwright; print('Playwright installed!')"
```

---

## 🔧 CONFIGURATION

### Environment Variables (.env)

Add these to your `.env` file (optional for manual login):

```bash
# Twitter Account Credentials (optional)
TWITTER_USERNAME=your_username
TWITTER_ACCOUNT_EMAIL=your_email@example.com
TWITTER_ACCOUNT_PASSWORD=your_password
```

### Session Storage

- **Location:** `AI_Employee_Vault/twitter_session.json`
- **Purpose:** Stores login session for reuse
- **First Run:** Manual login required
- **Subsequent Runs:** Automatic session reuse

---

## 📖 USAGE

### Basic Tweet Posting

```bash
python mcp_servers/twitter_mcp_playwright.py --post "Hello world from AI Employee! #GoldTier"
```

### With Headless Mode (No Browser UI)

```bash
python mcp_servers/twitter_mcp_playwright.py --post "Hello world" --headless
```

### Force Login (First Time Setup)

```bash
# With credentials
python mcp_servers/twitter_mcp_playwright.py --login --username "your_user" --password "your_pass"

# Manual login (browser opens, you login manually)
python mcp_servers/twitter_mcp_playwright.py --login
```

### Full Example

```bash
# First time: Login and save session
python mcp_servers/twitter_mcp_playwright.py --login

# Subsequent times: Just post tweets
python mcp_servers/twitter_mcp_playwright.py --post "Gold Tier Test: AI Employee posting via browser automation! #AIAutomation"
```

---

## 🎯 CLI OPTIONS

| Option | Description | Example |
|--------|-------------|---------|
| `--post` | Post a tweet | `--post "Hello world"` |
| `--headless` | Run without browser UI | `--headless` |
| `--login` | Force login | `--login` |
| `--username` | Twitter username | `--username "user"` |
| `--password` | Twitter password | `--password "pass"` |

---

## 📊 OUTPUT FORMAT

### Success Response

```json
{
  "status": "success",
  "tweet": "Hello world from AI Employee! #GoldTier",
  "platform": "X",
  "message": "Tweet posted successfully",
  "timestamp": "2026-03-06T04:30:00.000000"
}
```

### Error Response

```json
{
  "status": "error",
  "tweet": "Hello world",
  "platform": "X",
  "error": "Failed after 3 attempts: Timeout error",
  "timestamp": "2026-03-06T04:30:00.000000"
}
```

---

## 🔐 SECURITY

### Session Management

- Sessions are stored in `AI_Employee_Vault/twitter_session.json`
- **DO NOT** commit this file to git (already in .gitignore)
- Session includes cookies and authentication tokens

### Credentials

- Store credentials in `.env` file (never commit)
- Or use command-line arguments for one-time login
- Manual login recommended for first-time setup

### Best Practices

1. Keep `.env` file secure
2. Never share session files
3. Use strong passwords
4. Enable 2FA on Twitter account
5. Review Twitter's Terms of Service

---

## 🐛 TROUBLESHOOTING

### Issue: "Timeout waiting for selector"

**Solution:**
- Twitter UI may have changed
- Increase timeout in code
- Try manual login first

### Issue: "Login failed"

**Solution:**
- Check credentials
- Try manual login in browser
- Clear session file and re-login

### Issue: "Browser won't open"

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install chromium

# Check Python version (need 3.8+)
python --version
```

### Issue: "Session expired"

**Solution:**
```bash
# Delete old session
del AI_Employee_Vault\twitter_session.json

# Re-login
python mcp_servers/twitter_mcp_playwright.py --login
```

---

## 📁 FILE STRUCTURE

```
Personal-AI-Employee/
├── mcp_servers/
│   ├── twitter_mcp_playwright.py    # Main script
│   └── requirements-twitter-playwright.txt  # Dependencies
├── AI_Employee_Vault/
│   ├── Logs/
│   │   └── twitter_playwright.log   # Activity logs
│   └── twitter_session.json         # Session storage (auto-created)
└── .env                             # Credentials (optional)
```

---

## 🧪 TESTING

### Test Connection

```bash
# Just initialize browser (no posting)
python -c "import asyncio; from mcp_servers.twitter_mcp_playwright import TwitterPlaywrightClient; asyncio.run(TwitterPlaywrightClient().initialize())"
```

### Test Tweet

```bash
# Post a test tweet
python mcp_servers/twitter_mcp_playwright.py --post "Test tweet from AI Employee #GoldTier"
```

### Test Headless Mode

```bash
# Post without browser UI
python mcp_servers/twitter_mcp_playwright.py --post "Headless test" --headless
```

---

## 🔄 INTEGRATION WITH MCP

### Add to mcp.json

```json
"twitter_playwright": {
    "command": "python",
    "args": [
        "mcp_servers/twitter_mcp_playwright.py"
    ],
    "env": {
        "TWITTER_ACCOUNT_EMAIL": "your_email@example.com",
        "TWITTER_ACCOUNT_PASSWORD": "your_password"
    }
}
```

### Agent Skill Integration

The twitter_poster.SKILL.md can be updated to use this MCP server instead of the API-based approach.

---

## 📝 LOGS

### Log File Location

```
AI_Employee_Vault/Logs/twitter_playwright.log
```

### Log Format

```
2026-03-06 04:30:00,000 - twitter_playwright - INFO - Twitter Playwright client initialized
2026-03-06 04:30:01,000 - twitter_playwright - INFO - Initializing browser...
2026-03-06 04:30:02,000 - twitter_playwright - INFO - Posting tweet: Hello world...
2026-03-06 04:30:05,000 - twitter_playwright - INFO - Tweet posted successfully!
```

---

## ✅ FEATURES

- ✅ Browser-based posting (no API needed)
- ✅ Session persistence (login once)
- ✅ Headless mode support
- ✅ Automatic retry on failure
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ CLI interface
- ✅ MCP-ready architecture

---

## 🎯 NEXT STEPS

1. **Install Dependencies:**
   ```bash
   pip install -r mcp_servers/requirements-twitter-playwright.txt
   playwright install chromium
   ```

2. **First Login:**
   ```bash
   python mcp_servers/twitter_mcp_playwright.py --login
   ```

3. **Post Test Tweet:**
   ```bash
   python mcp_servers/twitter_mcp_playwright.py --post "Hello from AI Employee! #GoldTier"
   ```

4. **Integrate with MCP:**
   - Update mcp.json
   - Update twitter_poster.SKILL.md

---

**Version:** 1.0  
**Last Updated:** 2026-03-06  
**Status:** ✅ READY FOR USE
