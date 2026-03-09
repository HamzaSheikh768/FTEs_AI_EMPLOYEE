---
name: linkedin-poster
description: |
  Creates LinkedIn post drafts for business content and handles posting with human approval.
  This skill should be used when generating business-related content for LinkedIn with approval workflow.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# LinkedInPoster Skill

## Purpose
Creates LinkedIn post drafts for business content and manages the approval workflow before posting to LinkedIn.

## When to Use This Skill
- When business content needs to be posted to LinkedIn for marketing
- As part of the Silver Tier enhancement for the Personal AI Employee
- When implementing automated social media posting with approval

## Inputs
- **content**: The content to post on LinkedIn (required)
- **hashtags**: List of hashtags to include in the post
- **post_type**: Type of post (update, article, image, etc.)
- **approval_required**: Whether human approval is needed before posting (defaults to true)

## Outputs
- Creates approval request file in `/Pending_Approval/LINKEDIN_POST_{id}.md`
- Generates properly formatted LinkedIn post draft
- Updates system logs with posting activity

## Hook Dependencies
- `.claude/hook/linkedin_credentials.hook` - Contains LinkedIn session information or API credentials

## Approval Required
Yes - All LinkedIn posts require human approval

## DRY_RUN Support
Yes - Logs intent to create post but doesn't create approval request

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, approval workflow, post formats |
| **Conversation** | User's specific business content requirements, posting frequency, compliance needs |
| **Skill References** | LinkedIn posting guidelines, content best practices, approval patterns |
| **User Guidelines** | Project-specific social media rules, branding requirements |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Receive content and formatting requirements
2. Format content according to LinkedIn best practices
3. Create approval request in /Pending_Approval/LINKEDIN_POST_{id}.md
4. Wait for human to move file to /Approved/ or /Rejected/
5. If approved, execute LinkedIn posting (via MCP or automation)
6. Log posting activity to system logs
7. Update dashboard if needed
```

### Approval Request Schema
The skill creates approval files in `/Pending_Approval/` with this structure:

```yaml
---
type: linkedin_post_approval
action: post_linkedin
content_type: {update|article|image}
created: {ISO-8601}
status: pending_approval
expires: {ISO-8601}
---
## LinkedIn Post Draft

**Content:**
{formatted_linkedin_content}

**Hashtags:**
#{hashtag1} #{hashtag2} #{hashtag3}

## Action Required
Move this file to:
- `/Approved/` to post to LinkedIn
- `/Rejected/` to skip posting

## Preview
{preview_of_how_post_will_appear}
```

### Error Handling
- If LinkedIn credentials unavailable: create approval request but note authentication issue
- If content formatting fails: log error and create basic approval request
- If approval request creation fails: log error and don't proceed with posting
- If posting fails after approval: log error and notify user

### Compliance Considerations
- Follow LinkedIn's terms of service for automated posting
- Don't spam or post duplicate content
- Respect LinkedIn's rate limits
- Ensure content is appropriate for professional network