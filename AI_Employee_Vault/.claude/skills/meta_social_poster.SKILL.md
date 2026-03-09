---
name: meta-social-poster
description: |
  Posts to Facebook Page and Instagram Business Account using Meta Graph API.
  This skill should be used when content needs to be posted to Meta platforms
  for business marketing, announcements, or engagement.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# MetaSocialPoster Skill

## Purpose
Posts to Facebook Page and Instagram Business Account via Meta Graph API with engagement tracking.

## When to Use This Skill
- When business content needs to be posted to Facebook for marketing
- When Instagram posts are needed (requires image URL)
- When cross-platform posting is required (both FB + IG)
- When engagement insights are needed after posting
- When automated social media management is required

## Inputs
- **message**: Post message/caption (required)
- **platform**: Target platform - 'facebook', 'instagram', or 'both' (default: 'both')
- **image_url**: Image URL for Instagram posts (required for Instagram)
- **link**: Optional link to share on Facebook
- **auto_post**: Whether to auto-post without approval (default: true for business content)

## Outputs
- Posts to Facebook Page and/or Instagram
- Returns post IDs, URLs, and status
- Generates engagement summary
- Creates audit file in `/Done/META_POST_{id}.md`
- Logs all actions to `/Logs/meta_mcp.log`

## Hook Dependencies
- `.claude/hook/meta_credentials.hook` - Contains Meta/Facebook API credentials
- MCP Server: `meta` - Registered in mcp.json

## Approval Required
**Conditional:**
- ✅ **Auto-post allowed** for: Business promotions, product updates, value posts
- ❌ **Requires approval** for: Sensitive topics, political content, personal data

## DRY_RUN Support
Yes - Logs intent to post but doesn't call Meta API

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, MCP integration, log formats |
| **Conversation** | User's specific content requirements, posting guidelines |
| **Skill References** | Meta Graph API docs, Facebook/Instagram best practices |
| **User Guidelines** | Project-specific social media rules, brand voice |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Receive post content and platform preferences
2. Validate content (length, appropriateness, image for IG)
3. Check if auto-post criteria met OR requires approval
4a. If auto-post: Call meta_post_to_both via MCP
4b. If approval needed: Create file in /Pending_Approval/
5. Wait for human to move file to /Approved/ or /Rejected/
6. If approved: Execute posting via MCP
7. Log posting activity and generate engagement summary
8. Return post URLs and status
```

### Post Content Schema
The skill processes content with this structure:

```yaml
---
type: meta_post
priority: {high|medium|low}
status: pending
created: {ISO-8601}
platform: {facebook|instagram|both}
message: |
  Your post message here
image_url: https://example.com/image.jpg  # Required for Instagram
link: https://example.com  # Optional for Facebook
auto_post: true
---

## Post Details
**Business Category:** Product Announcement / Value Post / News
**Character Count:** 150
**Target Platforms:** Facebook, Instagram
**Target Audience:** Customers, Followers

## Action Required
This post is ready for automatic posting.
```

### MCP Tool Calls
The skill calls these MCP tools:

```python
# Post to Facebook only
meta_post_to_facebook(
    message="Your message here",
    link="https://example.com"  # optional
)

# Post to Instagram only
meta_post_to_instagram(
    caption="Your caption here",
    image_url="https://example.com/image.jpg"
)

# Post to both platforms
meta_post_to_both(
    message="Your message here",
    image_url="https://example.com/image.jpg"  # optional
)

# Get engagement insights
meta_get_insights(metric="page_impressions_unique")
```

### Response Format
```json
{
  "facebook": {
    "post_id": "123456789_987654321",
    "platform": "facebook",
    "status": "posted",
    "url": "https://facebook.com/123456789_987654321",
    "created_at": "2026-03-07T00:00:00"
  },
  "instagram": {
    "post_id": "123456789",
    "platform": "instagram",
    "status": "posted",
    "url": "https://instagram.com/p/123456789",
    "created_at": "2026-03-07T00:00:00"
  },
  "summary": {
    "total_posts": 2,
    "successful_posts": 2,
    "failed_posts": 0,
    "platforms": ["Facebook", "Instagram"],
    "generated_at": "2026-03-07T00:00:00"
  }
}
```

### Error Handling
- If Meta API is unreachable: Log error, return error message, suggest retry
- If Instagram post without image: Return error (Instagram requires media)
- If authentication fails: Log error, check credentials in .env
- If rate limited: Log error, wait and retry, inform user of limit

### Logging
All actions are logged to:
- Console: Real-time status updates
- File: `AI_Employee_Vault/Logs/meta_mcp.log`
- Audit: `AI_Employee_Vault/Done/META_POST_{id}.md`

### Example Usage

#### Example 1: Post to Facebook Only
```
Input:
---
type: meta_post
platform: facebook
message: |
  Exciting news! Our Gold Tier AI Employee is now complete!
  
  Features:
  ✅ Odoo ERP Integration
  ✅ LinkedIn Auto-Posting
  ✅ Twitter API Integration
  ✅ Facebook + Instagram Posting
  
  #AIAutomation #GoldTier #PersonalAI
auto_post: true
---

Action:
1. Validate content
2. Call: meta_post_to_facebook(message)
3. Return: Facebook post URL and ID
```

#### Example 2: Post to Both Platforms
```
Input:
---
type: meta_post
platform: both
message: Check out our latest AI features!
image_url: https://example.com/ai-features.jpg
auto_post: true
---

Action:
1. Validate content and image URL
2. Call: meta_post_to_both(message, image_url)
3. Generate engagement summary
4. Return: Results from both platforms
```

#### Example 3: Get Engagement Insights
```
Input: Get Facebook page insights

Action:
1. Call: meta_get_insights(metric="page_impressions_unique")
2. Return: Insights data with impressions, reach, engagement
```

### Security Considerations
- Never post personal information or credentials
- Respect Meta's Terms of Service
- Implement rate limiting (max 50 posts/day per platform)
- Log all posting activity for audit trail
- Use secure credential storage (.env, never commit)

### Integration Points
- **Orchestrator**: Monitors /Needs_Action for meta_post type files
- **MCP Server**: meta_mcp.py handles Meta Graph API communication
- **Audit Logger**: Maintains audit trail of all posts
- **Approval Workflow**: Routes sensitive content for human approval

### Best Practices

**Content Guidelines:**
- Facebook: 1-2 paragraphs optimal, can be longer
- Instagram: Short captions (125-150 chars), focus on visuals
- Use 3-5 relevant hashtags per platform
- Include call-to-action when appropriate
- Post consistently (1-2 times per day)

**Image Requirements (Instagram):**
- Format: JPG or PNG
- Size: 1080x1080px (square) or 1080x1350px (portrait)
- URL must be publicly accessible
- HTTPS required

**Posting Schedule:**
- Facebook: 9 AM - 3 PM (best engagement)
- Instagram: 11 AM - 1 PM, 7 PM - 9 PM
- Avoid posting too frequently (max 1 post/hour)
- Monitor insights for optimal timing

**Engagement Tracking:**
- Check insights weekly
- Track post reach and impressions
- Monitor engagement rate
- Adjust content strategy based on data
