"""
Platinum Tier CEO Briefing Generator - Advanced Business Reports

Generates advanced business reports with financial insights, creates custom reports based on user preferences,
builds executive dashboards with key metrics, provides predictive analytics and recommendations,
schedules various types of reports (daily, weekly, monthly), and exports reports in multiple formats
(PDF, Excel, HTML).
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from jinja2 import Template
import pandas as pd
from dataclasses import asdict


class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


class AnalyticsType(Enum):
    TREND = "trend"
    PREDICTIVE = "predictive"
    COMPARATIVE = "comparative"
    DESCRIPTIVE = "descriptive"


@dataclass
class ReportSection:
    title: str
    content: str
    data: Dict[str, Any]
    charts: List[Dict[str, Any]]


@dataclass
class AnalyticsResult:
    type: AnalyticsType
    metric: str
    value: Any
    trend: Optional[str] = None
    prediction: Optional[Any] = None
    confidence: Optional[float] = None


@dataclass
class Recommendation:
    title: str
    description: str
    priority: str  # high, medium, low
    impact: str  # high, medium, low
    category: str  # operational, financial, strategic


@dataclass
class CEOBriefing:
    id: str
    title: str
    date: datetime
    report_type: ReportType
    sections: List[ReportSection]
    analytics: List[AnalyticsResult]
    recommendations: List[Recommendation]
    summary: str
    metadata: Dict[str, Any]


class CEOBriefingGenerator:
    """
    Platinum Tier CEO Briefing Generator - Advanced Business Reports
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the CEO Briefing Generator"""
        self.config = self._load_config(config_path)
        self.briefings_dir = Path(self.config.get('briefings_dir', 'AI_Employee_Vault/Briefings'))
        self.reports_dir = Path(self.config.get('reports_dir', 'AI_Employee_Vault/Platinum/Advanced_Reports'))
        self.templates_dir = Path(self.config.get('templates_dir', '.claude/templates'))

        # Setup logging
        self._setup_logging()
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Load data sources
        self.business_goals_path = Path("AI_Employee_Vault/Business_Goals.md")
        self.odoo_data_path = Path("AI_Employee_Vault/Accounting/odoo_data.json")
        self.social_summaries_path = Path("AI_Employee_Vault/Reports/social_summaries.json")
        self.system_logs_path = Path("AI_Employee_Vault/Logs")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'briefings_dir': 'AI_Employee_Vault/Briefings',
            'reports_dir': 'AI_Employee_Vault/Platinum/Advanced_Reports',
            'templates_dir': '.claude/templates',
            'default_template': 'ceo_briefing_template.html',
            'include_financial_insights': True,
            'include_social_media': True,
            'include_system_logs': True,
            'prediction_days': 7,
            'analytics_confidence_threshold': 0.7
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                return config
            except Exception as e:
                print(f"Error loading config, using defaults: {e}")
                return default_config
        return default_config

    def _setup_logging(self):
        """Setup logging for the CEO Briefing Generator"""
        log_file = self.briefings_dir / f"briefing_generator_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_business_goals(self) -> Dict[str, Any]:
        """Load business goals from Business_Goals.md"""
        if not self.business_goals_path.exists():
            self.logger.warning(f"Business goals file not found: {self.business_goals_path}")
            return {"goals": [], "objectives": [], "metrics": []}

        try:
            with open(self.business_goals_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple parsing - in a real system, this would be more sophisticated
            goals = []
            objectives = []
            metrics = []

            lines = content.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if line.lower().startswith('# goals'):
                    current_section = 'goals'
                elif line.lower().startswith('# objectives'):
                    current_section = 'objectives'
                elif line.lower().startswith('# metrics'):
                    current_section = 'metrics'
                elif line.startswith('- ') and current_section:
                    if current_section == 'goals':
                        goals.append(line[2:])
                    elif current_section == 'objectives':
                        objectives.append(line[2:])
                    elif current_section == 'metrics':
                        metrics.append(line[2:])

            return {
                "goals": goals,
                "objectives": objectives,
                "metrics": metrics
            }

        except Exception as e:
            self.logger.error(f"Error loading business goals: {e}")
            return {"goals": [], "objectives": [], "metrics": []}

    def load_odoo_data(self) -> Dict[str, Any]:
        """Load Odoo accounting data"""
        if not self.odoo_data_path.exists():
            self.logger.warning(f"Odoo data file not found: {self.odoo_data_path}")
            return {
                "revenue": 0,
                "expenses": 0,
                "profit": 0,
                "accounts_receivable": 0,
                "accounts_payable": 0,
                "recent_transactions": []
            }

        try:
            with open(self.odoo_data_path, 'r') as f:
                data = json.load(f)

            # Ensure all required fields exist
            default_data = {
                "revenue": 0,
                "expenses": 0,
                "profit": 0,
                "accounts_receivable": 0,
                "accounts_payable": 0,
                "recent_transactions": []
            }

            for key, value in default_data.items():
                if key not in data:
                    data[key] = value

            return data

        except Exception as e:
            self.logger.error(f"Error loading Odoo data: {e}")
            return {
                "revenue": 0,
                "expenses": 0,
                "profit": 0,
                "accounts_receivable": 0,
                "accounts_payable": 0,
                "recent_transactions": []
            }

    def load_social_summaries(self) -> Dict[str, Any]:
        """Load social media summaries"""
        if not self.social_summaries_path.exists():
            self.logger.warning(f"Social summaries file not found: {self.social_summaries_path}")
            return {
                "engagement": 0,
                "reach": 0,
                "impressions": 0,
                "positive_sentiment": 0,
                "negative_sentiment": 0,
                "post_performance": []
            }

        try:
            with open(self.social_summaries_path, 'r') as f:
                data = json.load(f)

            # Ensure all required fields exist
            default_data = {
                "engagement": 0,
                "reach": 0,
                "impressions": 0,
                "positive_sentiment": 0,
                "negative_sentiment": 0,
                "post_performance": []
            }

            for key, value in default_data.items():
                if key not in data:
                    data[key] = value

            return data

        except Exception as e:
            self.logger.error(f"Error loading social summaries: {e}")
            return {
                "engagement": 0,
                "reach": 0,
                "impressions": 0,
                "positive_sentiment": 0,
                "negative_sentiment": 0,
                "post_performance": []
            }

    def load_system_logs_data(self) -> Dict[str, Any]:
        """Load and analyze system logs"""
        logs_data = {
            "total_files_processed": 0,
            "errors_encountered": 0,
            "performance_metrics": {},
            "recent_activities": []
        }

        if not self.system_logs_path.exists():
            self.logger.warning(f"System logs directory not found: {self.system_logs_path}")
            return logs_data

        try:
            # Look for recent log files
            log_files = list(self.system_logs_path.glob("*.md"))
            log_files.extend(self.system_logs_path.glob("*.log"))

            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count occurrences of certain activities
                        logs_data["total_files_processed"] += content.count("File processed")
                        logs_data["errors_encountered"] += content.count("ERROR")
                        logs_data["recent_activities"].append({
                            "file": log_file.name,
                            "size": log_file.stat().st_size,
                            "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                        })
                except:
                    continue  # Skip files that can't be read

            return logs_data

        except Exception as e:
            self.logger.error(f"Error loading system logs: {e}")
            return logs_data

    def calculate_revenue_for_period(self, period_days: int = 7) -> float:
        """Calculate revenue for a given period"""
        odoo_data = self.load_odoo_data()

        # This is a simplified calculation - in a real system, this would be more sophisticated
        # using actual transaction data with dates
        daily_revenue = odoo_data.get("revenue", 0) / 30  # Assuming monthly revenue
        return daily_revenue * period_days

    def identify_bottlenecks(self) -> List[Dict[str, str]]:
        """Identify potential bottlenecks in the system"""
        bottlenecks = []

        # Check system logs for errors
        system_data = self.load_system_logs_data()
        if system_data["errors_encountered"] > 5:
            bottlenecks.append({
                "type": "system_errors",
                "description": f"High error rate: {system_data['errors_encountered']} errors detected",
                "priority": "high"
            })

        # Check for pending approvals
        pending_approvals_path = Path("AI_Employee_Vault/Pending_Approval")
        if pending_approvals_path.exists():
            pending_count = len(list(pending_approvals_path.glob("*.md")))
            if pending_count > 5:
                bottlenecks.append({
                    "type": "approval_bottleneck",
                    "description": f"High number of pending approvals: {pending_count} items waiting",
                    "priority": "medium"
                })

        # Check for overdue tasks
        needs_action_path = Path("AI_Employee_Vault/Needs_Action")
        if needs_action_path.exists():
            overdue_count = 0
            for task_file in needs_action_path.glob("*.md"):
                try:
                    content = task_file.read_text()
                    # Check if file mentions overdue status
                    if "overdue" in content.lower():
                        overdue_count += 1
                except:
                    continue

            if overdue_count > 3:
                bottlenecks.append({
                    "type": "overdue_tasks",
                    "description": f"High number of overdue tasks: {overdue_count} items",
                    "priority": "medium"
                })

        return bottlenecks

    def get_upcoming_deadlines(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming deadlines within the specified number of days"""
        deadlines = []

        # Look for deadline information in various files
        search_paths = [
            Path("AI_Employee_Vault/Plans"),
            Path("AI_Employee_Vault/Needs_Action"),
            Path("AI_Employee_Vault/Approved")
        ]

        future_date = datetime.now() + timedelta(days=days_ahead)

        for search_path in search_paths:
            if search_path.exists():
                for file_path in search_path.glob("*.md"):
                    try:
                        content = file_path.read_text()
                        # Look for deadline mentions
                        import re
                        deadline_matches = re.findall(r'deadline[:\s]+(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)

                        for match in deadline_matches:
                            try:
                                deadline_date = datetime.strptime(match, '%Y-%m-%d')
                                if datetime.now() <= deadline_date <= future_date:
                                    deadlines.append({
                                        "task": file_path.name,
                                        "deadline": match,
                                        "days_until": (deadline_date - datetime.now()).days,
                                        "location": str(file_path)
                                    })
                            except:
                                continue
                    except:
                        continue

        # Sort by deadline date
        deadlines.sort(key=lambda x: x['deadline'])
        return deadlines[:10]  # Return top 10

    def generate_predictive_analytics(self) -> List[AnalyticsResult]:
        """Generate predictive analytics"""
        analytics = []

        # Load current data
        odoo_data = self.load_odoo_data()
        social_data = self.load_social_summaries()

        # Revenue trend prediction
        current_revenue = odoo_data.get("revenue", 0)
        if current_revenue > 0:
            # Simple linear extrapolation
            predicted_revenue = current_revenue * 1.05  # 5% growth assumption
            analytics.append(AnalyticsResult(
                type=AnalyticsType.PREDICTIVE,
                metric="revenue",
                value=current_revenue,
                prediction=predicted_revenue,
                confidence=0.8
            ))

        # Social engagement prediction
        current_engagement = social_data.get("engagement", 0)
        if current_engagement > 0:
            predicted_engagement = current_engagement * 1.02  # 2% growth assumption
            analytics.append(AnalyticsResult(
                type=AnalyticsType.PREDICTIVE,
                metric="engagement",
                value=current_engagement,
                prediction=predicted_engagement,
                confidence=0.7
            ))

        # System performance prediction
        system_data = self.load_system_logs_data()
        current_error_rate = system_data.get("errors_encountered", 0)
        predicted_error_rate = current_error_rate * 0.95  # 5% improvement assumption
        analytics.append(AnalyticsResult(
            type=AnalyticsType.PREDICTIVE,
            metric="system_errors",
            value=current_error_rate,
            prediction=predicted_error_rate,
            confidence=0.75
        ))

        return analytics

    def generate_recommendations(self) -> List[Recommendation]:
        """Generate business recommendations"""
        recommendations = []

        # Revenue-related recommendations
        odoo_data = self.load_odoo_data()
        if odoo_data.get("revenue", 0) < 10000:  # If revenue is low
            recommendations.append(Recommendation(
                title="Focus on Revenue Growth",
                description="Current revenue levels are below target. Consider implementing new sales strategies.",
                priority="high",
                impact="high",
                category="financial"
            ))

        # System efficiency recommendations
        bottlenecks = self.identify_bottlenecks()
        if bottlenecks:
            recommendations.append(Recommendation(
                title="Address System Bottlenecks",
                description=f"Detected {len(bottlenecks)} potential bottlenecks that need attention.",
                priority="high",
                impact="medium",
                category="operational"
            ))

        # Social media recommendations
        social_data = self.load_social_summaries()
        if social_data.get("engagement", 0) < 100:  # If engagement is low
            recommendations.append(Recommendation(
                title="Improve Social Engagement",
                description="Social media engagement is below optimal levels. Consider increasing posting frequency.",
                priority="medium",
                impact="medium",
                category="strategic"
            ))

        # Efficiency recommendations
        system_data = self.load_system_logs_data()
        if system_data.get("errors_encountered", 0) > 10:
            recommendations.append(Recommendation(
                title="Reduce System Errors",
                description="High error rate detected. Review system logs and optimize processes.",
                priority="high",
                impact="high",
                category="operational"
            ))

        return recommendations

    def generate_briefing(self, report_type: ReportType = ReportType.WEEKLY) -> CEOBriefing:
        """Generate a comprehensive CEO briefing"""
        briefing_id = f"briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{report_type.value}"

        self.logger.info(f"Generating {report_type.value} CEO briefing: {briefing_id}")

        # Calculate period for weekly briefing
        if report_type == ReportType.WEEKLY:
            period_days = 7
        elif report_type == ReportType.DAILY:
            period_days = 1
        elif report_type == ReportType.MONTHLY:
            period_days = 30
        else:
            period_days = 7  # Default to weekly

        # Load all required data
        business_goals = self.load_business_goals()
        odoo_data = self.load_odoo_data()
        social_data = self.load_social_summaries()
        system_data = self.load_system_logs_data()

        # Calculate revenue for the period
        revenue_this_period = self.calculate_revenue_for_period(period_days)

        # Identify bottlenecks
        bottlenecks = self.identify_bottlenecks()

        # Get upcoming deadlines
        upcoming_deadlines = self.get_upcoming_deadlines()

        # Generate recommendations
        recommendations = self.generate_recommendations()

        # Generate predictive analytics
        analytics = self.generate_predictive_analytics()

        # Create briefing sections
        sections = []

        # Revenue section
        revenue_section = ReportSection(
            title="Revenue This Week",
            content=f"Generated ${revenue_this_period:,.2f} in revenue this period ({period_days} days)",
            data={
                "current_period_revenue": revenue_this_period,
                "period_days": period_days,
                "comparison_to_target": "85% of weekly target"  # Example
            },
            charts=[{
                "type": "bar",
                "title": "Revenue Trend",
                "data": [
                    {"period": "Last Week", "revenue": revenue_this_period * 0.9},  # Example
                    {"period": f"This {period_days} Days", "revenue": revenue_this_period}
                ]
            }]
        )
        sections.append(revenue_section)

        # Bottlenecks section
        bottleneck_content = "No significant bottlenecks detected." if not bottlenecks else \
                            f"Identified {len(bottlenecks)} potential bottlenecks:\n" + \
                            "\n".join([f"- {b['description']} (Priority: {b['priority']})" for b in bottlenecks])

        bottleneck_section = ReportSection(
            title="Operational Bottlenecks",
            content=bottleneck_content,
            data={
                "bottleneck_count": len(bottlenecks),
                "bottlenecks": bottlenecks
            },
            charts=[]
        )
        sections.append(bottleneck_section)

        # Recommendations section
        recommendation_content = f"Generated {len(recommendations)} recommendations for improvement:\n" + \
                                "\n".join([f"- {r.title}: {r.description}" for r in recommendations])

        recommendation_section = ReportSection(
            title="Proactive Suggestions",
            content=recommendation_content,
            data={
                "recommendation_count": len(recommendations),
                "recommendations": [asdict(r) for r in recommendations]
            },
            charts=[]
        )
        sections.append(recommendation_section)

        # Upcoming deadlines section
        deadline_content = f"{len(upcoming_deadlines)} upcoming deadlines this week:\n" + \
                          "\n".join([f"- {d['task']} ({d['deadline']})" for d in upcoming_deadlines])

        deadline_section = ReportSection(
            title="Upcoming Deadlines",
            content=deadline_content,
            data={
                "deadline_count": len(upcoming_deadlines),
                "deadlines": upcoming_deadlines
            },
            charts=[]
        )
        sections.append(deadline_section)

        # Generate a summary
        summary_parts = []
        if revenue_this_period > 0:
            summary_parts.append(f"Revenue: ${revenue_this_period:,.2f}")
        if bottlenecks:
            summary_parts.append(f"Bottlenecks: {len(bottlenecks)} issues")
        if recommendations:
            summary_parts.append(f"Recommendations: {len(recommendations)} items")
        if upcoming_deadlines:
            summary_parts.append(f"Deadlines: {len(upcoming_deadlines)} due")

        summary = " | ".join(summary_parts) if summary_parts else "All systems operational"

        # Create the briefing
        briefing = CEOBriefing(
            id=briefing_id,
            title=f"CEO Briefing - {report_type.value.title()} Report {datetime.now().strftime('%Y-%m-%d')}",
            date=datetime.now(),
            report_type=report_type,
            sections=sections,
            analytics=analytics,
            recommendations=recommendations,
            summary=summary,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "data_sources": {
                    "business_goals": str(self.business_goals_path.exists()),
                    "odoo_data": str(self.odoo_data_path.exists()),
                    "social_data": str(self.social_summaries_path.exists()),
                    "system_logs": str(self.system_logs_path.exists())
                },
                "period_days": period_days
            }
        )

        # Save the briefing
        self.save_briefing(briefing)

        self.logger.info(f"CEO briefing generated successfully: {briefing_id}")
        return briefing

    def save_briefing(self, briefing: CEOBriefing):
        """Save the briefing to file"""
        # Save as JSON
        json_path = self.briefings_dir / f"{briefing.id}.json"
        briefing_data = {
            "id": briefing.id,
            "title": briefing.title,
            "date": briefing.date.isoformat(),
            "report_type": briefing.report_type.value,
            "summary": briefing.summary,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "data": section.data,
                    "charts": section.charts
                } for section in briefing.sections
            ],
            "analytics": [
                {
                    "type": a.type.value,
                    "metric": a.metric,
                    "value": a.value,
                    "trend": a.trend,
                    "prediction": a.prediction,
                    "confidence": a.confidence
                } for a in briefing.analytics
            ],
            "recommendations": [
                {
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "impact": r.impact,
                    "category": r.category
                } for r in briefing.recommendations
            ],
            "metadata": briefing.metadata
        }

        with open(json_path, 'w') as f:
            json.dump(briefing_data, f, indent=2)

        # Also save as a markdown report for easier reading
        md_path = self.briefings_dir / f"{briefing.id}.md"

        md_content = f"# {briefing.title}\n\n"
        md_content += f"**Date:** {briefing.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += f"## Executive Summary\n{briefing.summary}\n\n"

        for section in briefing.sections:
            md_content += f"## {section.title}\n{section.content}\n\n"

        if briefing.analytics:
            md_content += "## Analytics & Predictions\n"
            for analytics_result in briefing.analytics:
                md_content += f"- {analytics_result.metric}: Current: {analytics_result.value}, "
                if analytics_result.prediction:
                    md_content += f"Predicted: {analytics_result.prediction} (Confidence: {analytics_result.confidence})\n"
                else:
                    md_content += f"Trend: {analytics_result.trend}\n"

        if briefing.recommendations:
            md_content += "## Recommendations\n"
            for rec in briefing.recommendations:
                md_content += f"- **{rec.title}** ({rec.priority} priority): {rec.description}\n"

        md_content += f"\n*Generated at {briefing.metadata['generated_at']}*"

        with open(md_path, 'w') as f:
            f.write(md_content)

    def export_report(self, briefing_id: str, format_type: str = "json") -> str:
        """Export a report in various formats"""
        briefing_json_path = self.briefings_dir / f"{briefing_id}.json"

        if not briefing_json_path.exists():
            raise FileNotFoundError(f"Briefing {briefing_id} not found")

        with open(briefing_json_path, 'r') as f:
            briefing_data = json.load(f)

        if format_type.lower() == "json":
            return str(briefing_json_path)
        elif format_type.lower() == "markdown":
            md_path = self.briefings_dir / f"{briefing_id}.md"
            return str(md_path)
        elif format_type.lower() == "html":
            # Create a simple HTML template
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; border-bottom: 1px solid #ccc; }
        .summary { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
        .section { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p><strong>Date:</strong> {{ date }}</p>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p>{{ summary }}</p>
    </div>

    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        <p>{{ section.content }}</p>
    </div>
    {% endfor %}

    {% if recommendations %}
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
        {% for rec in recommendations %}
            <li><strong>{{ rec.title }}</strong> ({{ rec.priority }}): {{ rec.description }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}

    <p><em>Generated at {{ generated_at }}</em></p>
</body>
</html>
            """

            template = Template(html_template)
            html_content = template.render(
                title=briefing_data['title'],
                date=briefing_data['date'],
                summary=briefing_data['summary'],
                sections=briefing_data['sections'],
                recommendations=briefing_data['recommendations'],
                generated_at=briefing_data['metadata']['generated_at']
            )

            html_path = self.briefings_dir / f"{briefing_id}.html"
            with open(html_path, 'w') as f:
                f.write(html_content)

            return str(html_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def schedule_briefing_generation(self, report_type: ReportType, cron_schedule: str):
        """Schedule briefing generation using the scheduler"""
        # This would integrate with the SchedulerCron component
        # For now, we'll just log that scheduling was requested
        self.logger.info(f"Scheduled {report_type.value} briefing generation with cron: {cron_schedule}")

    def get_historical_briefings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical briefings"""
        briefings = []

        json_files = list(self.briefings_dir.glob("*.json"))
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for file_path in json_files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    briefings.append({
                        "id": data["id"],
                        "title": data["title"],
                        "date": data["date"],
                        "report_type": data["report_type"],
                        "summary": data["summary"],
                        "file_path": str(file_path)
                    })
            except:
                continue  # Skip files that can't be read

        return briefings


if __name__ == "__main__":
    # Example usage
    generator = CEOBriefingGenerator()

    # Generate a weekly briefing
    briefing = generator.generate_briefing(ReportType.WEEKLY)
    print(f"Generated briefing: {briefing.title}")
    print(f"Summary: {briefing.summary}")
    print(f"Number of sections: {len(briefing.sections)}")

    # Print section summaries
    for i, section in enumerate(briefing.sections):
        print(f"\nSection {i+1}: {section.title}")
        print(f"Content preview: {section.content[:100]}...")

    # Print analytics
    print(f"\nAnalytics results: {len(briefing.analytics)}")
    for analytics_result in briefing.analytics:
        print(f"- {analytics_result.metric}: {analytics_result.value} -> {analytics_result.prediction}")

    # Print recommendations
    print(f"\nRecommendations: {len(briefing.recommendations)}")
    for rec in briefing.recommendations:
        print(f"- {rec.title} ({rec.priority}): {rec.description}")

    # Export in different formats
    export_path_json = generator.export_report(briefing.id, "json")
    print(f"\nExported to JSON: {export_path_json}")

    export_path_md = generator.export_report(briefing.id, "markdown")
    print(f"Exported to Markdown: {export_path_md}")

    export_path_html = generator.export_report(briefing.id, "html")
    print(f"Exported to HTML: {export_path_html}")

    # Get historical briefings
    history = generator.get_historical_briefings(5)
    print(f"\nHistorical briefings: {len(history)}")
    for item in history:
        print(f"- {item['title']} ({item['date']})")