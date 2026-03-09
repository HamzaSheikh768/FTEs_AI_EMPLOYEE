# LinkedIn Poster System Documentation

## Overview

The LinkedIn Poster system allows the Personal AI Employee to create and post content to LinkedIn, with an approval workflow to ensure appropriate content control.

## Architecture

The system consists of two main components:

### 1. MCP Server (linkedin_poster.py)
- Exposes LinkedIn posting capabilities as MCP tools
- Allows AI agents to create post drafts through API calls
- Tools available:
  - `create_linkedin_post_draft`: Creates a LinkedIn post draft that requires human approval
  - `approve_linkedin_post`: Moves a LinkedIn post from pending approval to approved status

### 2. LinkedIn Poster Watcher (watcher/linkedin_poster_impl.py)
- Monitors the vault's approval folders
- Automatically posts to LinkedIn when posts are approved
- Handles the actual browser automation to post on LinkedIn

## Approval Workflow

The system follows a 3-stage approval workflow:

1. **Draft Creation**: AI agents call `create_linkedin_post_draft` which creates a file in `AI_Employee_Vault/Pending_Approval/`
2. **Human Approval**: Users move files from `Pending_Approval` to `Approved` (or `Rejected`)
3. **Automatic Posting**: The LinkedIn poster watcher detects approved posts and publishes them to LinkedIn

## Usage

### For AI Agents:
```python
# Create a post draft for approval
response = await linkedin_poster.create_linkedin_post_draft({
  "content": "Your LinkedIn post content here",
  "hashtags": ["ai", "automation", "linkedin"],
  "post_type": "update"
})
```

### For Human Users:
1. Check `AI_Employee_Vault/Pending_Approval/` for new post drafts
2. Review the content
3. Move to `AI_Employee_Vault/Approved/` to approve and post, or `AI_Employee_Vault/Rejected/` to skip

## Configuration

### Environment Variables:
- `LINKEDIN_USERNAME`: LinkedIn account username/email
- `LINKEDIN_PASSWORD`: LinkedIn account password

### Required Directories:
- `AI_Employee_Vault/Pending_Approval/` - Posts awaiting approval
- `AI_Employee_Vault/Approved/` - Approved posts for publishing
- `AI_Employee_Vault/Rejected/` - Rejected posts
- `AI_Employee_Vault/Done/` - Processed posts

## Security Considerations

- LinkedIn credentials should be stored securely in environment variables
- All posts go through approval workflow to prevent inappropriate content
- The system uses browser automation which may be detectable by LinkedIn's anti-bot measures
- Monitor for CAPTCHA challenges or account restrictions

## Error Handling

- If posting fails, the system logs the error and continues monitoring
- Invalid approval files are skipped during monitoring
- Browser automation timeouts are handled gracefully