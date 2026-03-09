# Odoo API Key Generation Guide

**Gold Tier - Personal AI Employee**  
**Date:** 2026-03-05

---

## Method 1: Automatic Generation (Recommended)

### Prerequisites

- Odoo container must be running
- Database must be created
- Admin user must exist

### Steps

```bash
# 1. Navigate to odoo directory
cd "E:\Hackathon 0\Bronze\Personal-AI-Employee\odoo"

# 2. Run the API key generator
python generate_api_key.py
```

### Expected Output

```
======================================================================
                    ODOO API KEY GENERATOR
======================================================================

[INFO] Gold Tier - Personal AI Employee
[INFO] Target: http://localhost:8069
[INFO] Database: ai_employee_business
[INFO] Username: admin

======================================================================
                 STEP 1: Checking Odoo Connection
======================================================================

[OK] Odoo is running at http://localhost:8069

======================================================================
                STEP 2: Testing Database Connection
======================================================================

[OK] Database connection successful
[OK] Admin user UID: 2

======================================================================
          STEP 3: Generating API Key via JSON-RPC
======================================================================

[OK] Authenticated successfully
[OK] API key created with ID: 5
[OK] API Key retrieved successfully

======================================================================
                  STEP 4: Updating .env File
======================================================================

[OK] .env file updated with new API key
[INFO] API Key: odoo_api_7f3e9a2b5c8d...

======================================================================
                          SUMMARY
======================================================================

If API key was generated successfully:
  1. Check odoo/.env file
  2. Verify ODOO_API_KEY is set
  3. Run: python mcp_servers/odoo_mcp.py --test
```

---

## Method 2: Manual Generation via UI

### Step-by-Step Instructions

#### 1. Login to Odoo

```
URL: http://localhost:8069
Username: admin
Password: Admin_S3cur3P@ss_4h6J9kL2nR5t
```

#### 2. Enable Developer Mode

1. Click on **Settings** (gear icon in top-right)
2. Scroll to the **bottom** of the page
3. Click **"Activate the developer mode"**
4. Wait for the page to reload (you'll see bug icons appear)

#### 3. Navigate to User Settings

1. Go to **Settings** (main menu)
2. Click **"Users & Companies"** → **"Users"**
3. Click on **"Admin"** user

#### 4. Generate API Key

1. Go to **"User Preferences"** tab
2. Click **"New API Key"** button
3. Enter Description: **"AI Employee Integration"**
4. Click **"Generate"**
5. **COPY THE API KEY IMMEDIATELY** (shown only once!)

Example API Key:
```
odoo_api_7f3e9a2b5c8d1f4e6a9c2b5d8e1f4a7c9b2e5d8f
```

#### 5. Save to .env File

1. Open: `odoo/.env`
2. Find the line: `ODOO_API_KEY=<paste_your_key_here>`
3. Replace with your copied key:
   ```
   ODOO_API_KEY=odoo_api_7f3e9a2b5c8d1f4e6a9c2b5d8e1f4a7c9b2e5d8f
   ```
4. Save the file

#### 6. Test Connection

```bash
cd "E:\Hackathon 0\Bronze\Personal-AI-Employee"
python mcp_servers/odoo_mcp.py --test
```

---

## Verification

After generating the API key, verify it works:

```bash
python mcp_servers/odoo_mcp.py --test
```

**Expected Output:**
```
============================================================
ODOO MCP SERVER - Gold Tier Test
============================================================

Testing Odoo connection...

[OK] CONNECTED to Odoo!
   URL: http://localhost:8069
   Database: ai_employee_business
   User ID: 2

[OK] Odoo MCP Server is ready!

============================================================
```

---

## Troubleshooting

### Issue: "Cannot connect to Odoo"

**Solution:**
```bash
# Check if container is running
docker-compose ps

# Start Odoo if not running
docker-compose up -d

# Check logs
docker-compose logs -f odoo
```

### Issue: "Authentication failed"

**Solution:**
1. Verify password in .env matches docker-compose.yml
2. Check database name is correct
3. Ensure database exists

### Issue: "API key not shown"

Some Odoo versions don't expose the API key value via RPC. In this case:
- Use the **Manual UI Method** (Method 2 above)
- The UI will show the key once after generation

### Issue: "res.api.key model not found"

This means your Odoo version doesn't have the API key module installed.

**Solution:**
- Use the **Manual UI Method** (Method 2 above)
- Or install the API key module in Odoo

---

## Security Best Practices

1. **Never commit .env to git**
   ```bash
   # Already in .gitignore
   odoo/.env
   ```

2. **Store API key securely**
   - Use a password manager
   - Don't share via email/chat
   - Rotate periodically

3. **Use HTTPS in production**
   - Set up reverse proxy with SSL
   - Never expose Odoo directly to internet

4. **Monitor API key usage**
   - Check Odoo logs regularly
   - Revoke if suspicious activity detected

---

## API Key Format

```
odoo_api_<64_character_hex_string>

Example:
odoo_api_7f3e9a2b5c8d1f4e6a9c2b5d8e1f4a7c9b2e5d8f1a2b3c4d5e6f7a8b9c0d1e2
```

**Characteristics:**
- Prefix: `odoo_api_`
- Length: 64 hexadecimal characters (0-9, a-f)
- Case: lowercase
- Total length: 73 characters

---

## Quick Reference

| Action | Command |
|--------|---------|
| Generate API Key (Auto) | `python generate_api_key.py` |
| Generate API Key (UI) | Settings → Users → Admin → New API Key |
| Test Connection | `python mcp_servers/odoo_mcp.py --test` |
| View Current Key | Check `odoo/.env` file |
| Rotate Key | Generate new key (old one auto-revoked) |

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-05  
**Tier:** Gold
