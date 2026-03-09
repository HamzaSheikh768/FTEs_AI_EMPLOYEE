---
name: twitter-poster
description: |
  Posts tweets to X (Twitter) and generates tweet summaries automatically.
  This skill should be used when content needs to be posted to X/Twitter for
  business promotion, announcements, or engagement. Supports automatic posting
  from /Needs_Action files with type: twitter_post.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# TwitterPoster Skill

## Purpose
Posts tweets to X (Twitter) and generates summaries automatically via MCP server integration.

## When to Use This Skill
- When business content needs to be posted to X/Twitter for marketing
- When announcing product updates, news, or achievements
- When engaging with trending topics (business-related only)
- When automatic posting from email/WhatsApp content is required
- When tweet summaries and analytics are needed

## Inputs
- **content**: The tweet text (required, max 280 characters)
- **hashtags**: List of hashtags to include (optional)
- **reply_settings**: Who can reply (everyone, mentioned, following) (optional)
- **auto_post**: Whether to auto-post without approval (default: false for sensitive content)

## Outputs
- Posts tweet to X/Twitter via MCP server
- Returns tweet ID, URL, and posting status
- Creates audit file in `/Done/TWITTER_POST_{id}.md`
- Logs all actions to `/Logs/twitter_mcp.log`

## Hook Dependencies
- `.claude/hook/twitter_credentials.hook` - Contains Twitter API credentials
- MCP Server: `twitter` - Registered in mcp.json

## Approval Required
**Conditional:**
- ✅ **Auto-post allowed** for: Business promotions, product updates, value posts (100-280 chars)
- ❌ **Requires approval** for: Replies to individuals, controversial topics, payments, personal data

## DRY_RUN Support
Yes - Logs intent to post tweet but doesn't call Twitter API

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, MCP integration, log formats |
| **Conversation** | User's specific content requirements, posting guidelines |
| **Skill References** | Twitter posting best practices, character limits, hashtag strategies |
| **User Guidelines** | Project-specific social media rules, brand voice |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Receive tweet content and formatting requirements
2. Validate content (length, appropriateness, hashtags)
3. Check if auto-post criteria met OR requires approval
4a. If auto-post: Call twitter_post_tweet via MCP
4b. If approval needed: Create file in /Pending_Approval/
5. Wait for human to move file to /Approved/ or /Rejected/
6. If approved: Execute Twitter posting via MCP
7. Log posting activity and create audit trail
8. Return tweet URL and status
```

### Tweet Content Schema
The skill processes content with this structure:

```yaml
---
type: twitter_post
priority: {high|medium|low}
status: pending
created: {ISO-8601}
content: |
  Tweet text here (max 280 characters)
hashtags:
  - Hashtag1
  - Hashtag2
reply_settings: everyone
auto_post: true
---

## Tweet Details
**Business Category:** Product Announcement / Value Post / News
**Character Count:** 150
**Target Audience:** Developers, Business Owners, Tech Community

## Action Required
This tweet is ready for automatic posting.
```

### MCP Tool Calls
The skill calls these MCP tools:

```python
# Post tweet
twitter_post_tweet(
    text="Your tweet content here #Hashtag",
    reply_settings="everyone"  # optional
)

# Get user info (for verification)
twitter_get_user_info(username="elonmusk")

# Generate tweet summary (for analytics)
twitter_generate_summary(tweet_id="1234567890")
```

### Response Format
```json
{
    "tweet_id": "1234567890123456789",
    "text": "Your tweet content here #Hashtag",
    "status": "posted",
    "url": "https://twitter.com/i/web/status/1234567890123456789",
    "created_at": "2026-03-06T12:00:00.000Z"
}
```

### Error Handling
- If Twitter API is unreachable: Log error, return error message, suggest retry
- If content exceeds 280 chars: Truncate or ask user to shorten
- If authentication fails: Log error, check credentials in .env
- If rate limited: Log error, wait and retry, inform user of limit

### Logging
All actions are logged to:
- Console: Real-time status updates
- File: `AI_Employee_Vault/Logs/twitter_mcp.log`
- Audit: `AI_Employee_Vault/Done/TWITTER_POST_{id}.md`

### Example Usage

#### Example 1: Auto-Post Business Promotion
```
Input File: /Needs_Action/TWITTER_PROMO_001.md

Content:
---
type: twitter_post
auto_post: true
content: |
  🚀 Excited to announce our new AI-powered automation platform!
  
  We've just completed Gold Tier integration with Odoo ERP.
  
  The future of work is automated! 🤖
hashtags:
  - AIAutomation
  - Odoo
  - BusinessAutomation
---

Action:
1. Validate content (280 chars, business-appropriate)
2. Auto-post criteria met → Post directly
3. Call: twitter_post_tweet(text, hashtags)
4. Return: Tweet URL and ID
```

#### Example 2: Generate Tweet Summary
```
Input: Tweet ID "1234567890123456789"

Action:
1. Call: twitter_generate_summary(tweet_id)
2. Retrieve tweet metrics and context
3. Generate summary with engagement stats
4. Return: Summary with likes, retweets, replies
```

### Security Considerations
- Never post personal information or credentials
- Respect Twitter's Terms of Service
- Implement rate limiting (max 10 tweets/hour)
- Log all posting activity for audit trail
- Use secure credential storage (.env, never commit)

### Integration Points
- **Orchestrator**: Monitors /Needs_Action for twitter_post type files
- **MCP Server**: twitter_mcp.py handles Twitter API communication
- **Audit Logger**: Maintains audit trail of all tweet operations
- **Approval Workflow**: Routes sensitive content for human approval

### Best Practices

**Content Guidelines:**
- Keep tweets 100-280 characters for optimal engagement
- Include 2-5 relevant hashtags
- Use emojis sparingly (1-3 per tweet)
- Include call-to-action when appropriate
- Avoid controversial topics unless approved

**Posting Schedule:**
- Business hours: 9 AM - 5 PM local time
- Avoid weekends for B2B content
- Space posts at least 1 hour apart
- Monitor engagement and adjust timing

**Hashtag Strategy:**
- Mix popular and niche hashtags
- Create branded hashtags for campaigns
- Research trending hashtags in your industry
- Don't overuse (max 5 per tweet)
