---
name: ceo_briefing_generator
description: |
  Generates weekly CEO briefings by aggregating business data from multiple sources including Business_Goals.md,
  Odoo accounting data, social media summaries, and system logs. Creates comprehensive Monday morning
  briefings with revenue tracking, bottleneck identification, proactive suggestions, and upcoming deadlines.
---

# CEO Briefing Generator

This skill should be used when generating weekly CEO briefings that aggregate data from multiple business sources. It creates comprehensive Monday morning briefings with key business metrics and insights.

## Purpose

Automatically generates weekly CEO briefings by aggregating data from:
- Business_Goals.md for strategic objectives
- Odoo accounting system for revenue data
- Social media summaries for engagement metrics
- System logs for process analysis

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, skill patterns, data source locations |
| **Conversation** | User's specific requirements for briefing content, scheduling needs |
| **Skill References** | Business intelligence patterns, data aggregation techniques |
| **User Guidelines** | Project-specific conventions, data access protocols |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:
1. Collects data from Business_Goals.md, Odoo accounting, social summaries, and system logs
2. Analyzes revenue trends, identifies bottlenecks, and tracks progress toward goals
3. Generates proactive suggestions for business improvements
4. Lists upcoming deadlines and priorities
5. Formats the briefing in Markdown and saves to Briefings folder

## Data Sources Integration

### Business_Goals.md
- Extracts strategic objectives and progress tracking
- Identifies goals approaching deadlines
- Measures completion percentage of key initiatives

### Odoo Accounting Data
- Retrieves current week's revenue figures
- Compares to previous week and budget targets
- Highlights revenue trends and anomalies

### Social Media Summaries
- Aggregates engagement metrics from LinkedIn posts
- Tracks follower growth and interaction rates
- Identifies high-performing content themes

### System Logs
- Analyzes processing patterns for bottlenecks
- Identifies recurring issues or delays
- Tracks task completion rates and system health

## Output Format

The generated briefing follows this structure:

```markdown
# Weekly CEO Briefing - Week of [Date]

## Revenue This Week
- Total revenue: [amount]
- Comparison to previous week: [change]
- Comparison to budget target: [change]
- Revenue by category: [breakdown if available]

## Current Bottlenecks
- [List of identified bottlenecks with impact assessment]
- [Process delays or resource constraints]
- [System or workflow issues]

## Proactive Suggestions
- [Actionable recommendations based on data analysis]
- [Process improvements]
- [Growth opportunities]

## Upcoming Deadlines
- [Important dates within next 2 weeks]
- [Priority ranking: High/Medium/Low]
- [Dependencies and resources required]
```

## Scheduling

The skill is designed to run automatically on Sunday nights at 11:59 PM via the orchestrator system.

## Error Handling

- If Odoo unavailable: Generates briefing with "Revenue data unavailable" notice
- If Business_Goals.md missing: Uses template with "No goals defined" notice
- If logs inaccessible: Skips bottleneck analysis section
- If social data unavailable: Skips engagement metrics section

## Configuration

The skill requires the following hooks for proper operation:
- `odoo_credentials` for accounting data access
- `linkedin_credentials` for social media data access

Approval is not required as this is an informational report generation task.