---
name: ceo_briefing_generator
description: |
  Generates advanced business reports with financial insights, creates custom reports based on user preferences,
  builds executive dashboards with key metrics, provides predictive analytics and recommendations,
  schedules various types of reports (daily, weekly, monthly), and exports reports in multiple formats
  (PDF, Excel, HTML).
---

# Enhanced CEO Briefing Generator

This skill should be used when generating advanced business reports and executive dashboards for the Personal AI Employee system. It provides enhanced reporting capabilities beyond basic CEO briefings.

## Purpose

Implements comprehensive business intelligence reporting with the following capabilities:
- Generate advanced business reports with financial insights
- Create custom reports based on user preferences
- Build executive dashboards with key metrics
- Provide predictive analytics and recommendations
- Schedule various types of reports (daily, weekly, monthly)
- Export reports in multiple formats (PDF, Excel, HTML)

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing CEO briefing system, report generation patterns |
| **Conversation** | User's specific requirements for report types, dashboard metrics |
| **Skill References** | Business intelligence patterns, report generation libraries |
| **User Guidelines** | Report format preferences, metric definitions |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Advanced Report Generation
- Generate business reports with financial insights and trend analysis
- Create custom reports based on user-defined parameters
- Include predictive analytics and business recommendations
- Support for various report types (financial, operational, strategic)

### Executive Dashboard Creation
- Build executive dashboards with key performance indicators
- Visualize critical business metrics and trends
- Provide real-time updates to dashboard metrics
- Support for customizable dashboard layouts

### Predictive Analytics
- Analyze historical data for trend identification
- Generate predictive models for business outcomes
- Provide recommendations based on data analysis
- Identify potential business opportunities and risks

### Report Scheduling
- Schedule reports on various frequencies (daily, weekly, monthly)
- Support for custom scheduling patterns
- Automated report generation and distribution
- Schedule management and modification capabilities

### Format Export
- Export reports in multiple formats (PDF, Excel, HTML)
- Support for custom report templates
- Format-specific styling and layout options
- Batch export for multiple reports

## Data Sources Integration

### Report Data Sources
- Business_Goals.md for strategic objectives
- Odoo accounting data for financial metrics
- Social media summaries for engagement metrics
- System logs for operational metrics
- Financial transaction data for detailed analysis

### Dashboard Data Sources
- Real-time metrics from system components
- Historical trend data
- Predictive analytics results
- Custom user-defined metrics

## Output Format

The skill generates:
- Advanced reports to `/Platinum/Advanced_Reports/`
- Executive dashboards to `/Platinum/Advanced_Reports/`
- Scheduled report logs to `/Logs/`
- Predictive analytics reports to `/Platinum/Advanced_Reports/`

## Error Handling

- If data source unavailable: generates report with "Data unavailable" notice
- If predictive model fails: uses historical averages as backup
- If export format fails: attempts alternative format or text-based report
- If scheduling fails: logs error and attempts to reschedule

## Configuration

The skill requires:
- Access to all data sources mentioned above
- Report template configuration
- Dashboard layout preferences
- Scheduling parameters and preferences
- Export format preferences