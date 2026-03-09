"""
Platinum Tier Watchdog - System Health Monitoring

Monitors system health metrics, tracks resource usage, generates alerts for system anomalies,
performs automatic recovery operations, and maintains system health logs.
"""
import psutil
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import subprocess
import os
from typing import Dict, List, Optional, Any


class Watchdog:
    """
    Platinum Tier Watchdog - System Health Monitoring
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Watchdog system"""
        self.config = self._load_config(config_path)
        self.health_metrics_dir = Path(self.config.get('health_metrics_dir', 'AI_Employee_Vault/Platinum/Health_Metrics'))
        self.log_level = self.config.get('log_level', 'INFO')
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'process_count': 1000
        })

        # Setup logging
        self._setup_logging()
        self.health_metrics_dir.mkdir(parents=True, exist_ok=True)

        # Initialize metrics history
        self.metrics_history = []
        self.alert_history = []

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'health_metrics_dir': 'AI_Employee_Vault/Platinum/Health_Metrics',
            'log_level': 'INFO',
            'alert_thresholds': {
                'cpu_percent': 80,
                'memory_percent': 85,
                'disk_percent': 90,
                'process_count': 1000
            },
            'monitoring_interval': 60,  # seconds
            'metric_retention_days': 30
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
        """Setup logging for the Watchdog system"""
        log_file = self.health_metrics_dir / f"watchdog_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system health metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available': psutil.virtual_memory().available,
            'memory_total': psutil.virtual_memory().total,
            'disk_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
            'disk_total': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:\\').total,
            'disk_used': psutil.disk_usage('/').used if os.name != 'nt' else psutil.disk_usage('C:\\').used,
            'process_count': len(list(psutil.process_iter())),
            'boot_time': psutil.boot_time(),
            'network_io': dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {},
            'disk_io': dict(psutil.disk_io_counters()._asdict()) if psutil.disk_io_counters() else {}
        }

        # Add system-specific metrics
        if os.name == 'nt':  # Windows
            metrics['load_average'] = None  # Not available on Windows
        else:  # Unix-like
            try:
                metrics['load_average'] = os.getloadavg()
            except:
                metrics['load_average'] = [0, 0, 0]  # Fallback

        return metrics

    def check_for_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check collected metrics for anomalies and generate alerts"""
        alerts = []

        # Check CPU usage
        if metrics['cpu_percent'] > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning' if metrics['cpu_percent'] < 90 else 'critical',
                'message': f"High CPU usage detected: {metrics['cpu_percent']}%",
                'value': metrics['cpu_percent'],
                'threshold': self.alert_thresholds['cpu_percent'],
                'timestamp': metrics['timestamp']
            })

        # Check memory usage
        if metrics['memory_percent'] > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning' if metrics['memory_percent'] < 95 else 'critical',
                'message': f"High memory usage detected: {metrics['memory_percent']}%",
                'value': metrics['memory_percent'],
                'threshold': self.alert_thresholds['memory_percent'],
                'timestamp': metrics['timestamp']
            })

        # Check disk usage
        if metrics['disk_percent'] > self.alert_thresholds['disk_percent']:
            alerts.append({
                'type': 'disk_high',
                'severity': 'warning' if metrics['disk_percent'] < 95 else 'critical',
                'message': f"High disk usage detected: {metrics['disk_percent']}%",
                'value': metrics['disk_percent'],
                'threshold': self.alert_thresholds['disk_percent'],
                'timestamp': metrics['timestamp']
            })

        # Check process count
        if metrics['process_count'] > self.alert_thresholds['process_count']:
            alerts.append({
                'type': 'process_count_high',
                'severity': 'warning',
                'message': f"High process count detected: {metrics['process_count']}",
                'value': metrics['process_count'],
                'threshold': self.alert_thresholds['process_count'],
                'timestamp': metrics['timestamp']
            })

        # Check for unusual network activity
        if 'network_io' in metrics and metrics['network_io']:
            # Simple check for unusually high network activity (placeholder for more complex logic)
            bytes_sent = metrics['network_io'].get('bytes_sent', 0)
            bytes_recv = metrics['network_io'].get('bytes_recv', 0)
            if bytes_sent > 1000000000 or bytes_recv > 1000000000:  # 1GB threshold
                alerts.append({
                    'type': 'network_activity',
                    'severity': 'info',
                    'message': f"High network activity detected: {bytes_sent} sent, {bytes_recv} received",
                    'value': f"{bytes_sent}/{bytes_recv}",
                    'threshold': "1GB",
                    'timestamp': metrics['timestamp']
                })

        return alerts

    def perform_automatic_recovery(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform automatic recovery operations based on alerts"""
        recovery_actions = []

        for alert in alerts:
            action_taken = None

            if alert['type'] == 'cpu_high' and alert['severity'] == 'critical':
                # For critical CPU usage, check for specific processes
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        if proc.info['cpu_percent'] > 50:  # High CPU consumer
                            recovery_actions.append({
                                'action': 'high_cpu_process_identified',
                                'pid': proc.info['pid'],
                                'process_name': proc.info['name'],
                                'cpu_percent': proc.info['cpu_percent'],
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass  # Ignore errors in process enumeration

            elif alert['type'] == 'memory_high' and alert['severity'] == 'critical':
                # For critical memory usage, suggest cleanup
                recovery_actions.append({
                    'action': 'memory_cleanup_suggested',
                    'message': 'High memory usage detected, consider cleaning up unused processes',
                    'timestamp': datetime.now().isoformat()
                })

            # Add more recovery actions based on alert types
            if action_taken:
                recovery_actions.append(action_taken)

        return recovery_actions

    def save_metrics(self, metrics: Dict[str, Any]):
        """Save collected metrics to file"""
        timestamp = datetime.fromisoformat(metrics['timestamp'])
        filename = self.health_metrics_dir / f"metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2)

        # Keep metrics history limited
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 1000:  # Keep last 1000 metrics
            self.metrics_history = self.metrics_history[-500:]

    def save_alerts(self, alerts: List[Dict[str, Any]]):
        """Save alerts to file"""
        if not alerts:
            return

        timestamp = datetime.now()
        filename = self.health_metrics_dir / f"alerts_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp.isoformat(),
                'alerts': alerts
            }, f, indent=2)

        # Add to alert history
        self.alert_history.extend(alerts)
        if len(self.alert_history) > 1000:  # Keep last 1000 alerts
            self.alert_history = self.alert_history[-500:]

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate a comprehensive health report"""
        if not self.metrics_history:
            return {'error': 'No metrics collected yet'}

        latest_metrics = self.metrics_history[-1]

        # Calculate averages for key metrics
        cpu_sum = sum(m['cpu_percent'] for m in self.metrics_history)
        memory_sum = sum(m['memory_percent'] for m in self.metrics_history)
        disk_sum = sum(m['disk_percent'] for m in self.metrics_history)

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_metrics_collected': len(self.metrics_history),
            'total_alerts_generated': len(self.alert_history),
            'average_cpu_percent': round(cpu_sum / len(self.metrics_history), 2) if self.metrics_history else 0,
            'average_memory_percent': round(memory_sum / len(self.metrics_history), 2) if self.metrics_history else 0,
            'average_disk_percent': round(disk_sum / len(self.metrics_history), 2) if self.metrics_history else 0,
            'current_cpu_percent': latest_metrics['cpu_percent'],
            'current_memory_percent': latest_metrics['memory_percent'],
            'current_disk_percent': latest_metrics['disk_percent'],
            'current_process_count': latest_metrics['process_count']
        }

        report = {
            'summary': summary,
            'trends': self._calculate_trends(),
            'top_processes': self._get_top_processes(),
            'recent_alerts': self.alert_history[-10:] if self.alert_history else []
        }

        # Save report
        timestamp = datetime.now()
        filename = self.health_metrics_dir / f"health_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return report

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends from historical metrics"""
        if len(self.metrics_history) < 2:
            return {'error': 'Insufficient data for trend analysis'}

        # Calculate trends for key metrics
        cpu_trend = self._calculate_simple_trend([m['cpu_percent'] for m in self.metrics_history])
        memory_trend = self._calculate_simple_trend([m['memory_percent'] for m in self.metrics_history])
        disk_trend = self._calculate_simple_trend([m['disk_percent'] for m in self.metrics_history])

        return {
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'disk_trend': disk_trend
        }

    def _calculate_simple_trend(self, values: List[float]) -> str:
        """Calculate a simple trend based on last few values"""
        if len(values) < 3:
            return 'insufficient_data'

        recent_avg = sum(values[-3:]) / 3
        earlier_avg = sum(values[:3]) / 3

        if recent_avg > earlier_avg * 1.1:  # 10% increase
            return 'increasing'
        elif recent_avg < earlier_avg * 0.9:  # 10% decrease
            return 'decreasing'
        else:
            return 'stable'

    def _get_top_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by resource usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by CPU usage first, then memory
            processes.sort(key=lambda x: (x['cpu_percent'], x['memory_percent']), reverse=True)
            return processes[:limit]
        except:
            return []

    def cleanup_old_files(self):
        """Clean up old metric and alert files based on retention policy"""
        retention_days = self.config.get('metric_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        for file_path in self.health_metrics_dir.glob('*.json'):
            if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
                try:
                    file_path.unlink()
                    self.logger.info(f"Deleted old file: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to delete old file {file_path}: {e}")

    def start_monitoring(self, interval: Optional[int] = None):
        """Start continuous monitoring loop"""
        monitoring_interval = interval or self.config.get('monitoring_interval', 60)

        self.logger.info(f"Starting Watchdog monitoring with {monitoring_interval}s interval")

        try:
            while True:
                # Collect system metrics
                metrics = self.collect_system_metrics()
                self.save_metrics(metrics)

                # Check for anomalies
                alerts = self.check_for_anomalies(metrics)
                if alerts:
                    self.logger.warning(f"Detected {len(alerts)} anomalies")
                    self.save_alerts(alerts)

                    # Perform recovery actions if needed
                    recovery_actions = self.perform_automatic_recovery(alerts)
                    if recovery_actions:
                        self.logger.info(f"Performed {len(recovery_actions)} recovery actions")

                # Clean up old files periodically
                if len(self.metrics_history) % 10 == 0:  # Every 10 metrics collected
                    self.cleanup_old_files()

                time.sleep(monitoring_interval)

        except KeyboardInterrupt:
            self.logger.info("Watchdog monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    watchdog = Watchdog()

    # Collect one set of metrics for testing
    metrics = watchdog.collect_system_metrics()
    print("Collected metrics:", json.dumps(metrics, indent=2))

    # Check for anomalies
    alerts = watchdog.check_for_anomalies(metrics)
    if alerts:
        print(f"Detected {len(alerts)} alerts:")
        for alert in alerts:
            print(f"  - {alert['message']} ({alert['severity']})")
    else:
        print("No alerts detected")

    # Generate a health report
    report = watchdog.generate_health_report()
    print("Health report summary:", json.dumps(report.get('summary', {}), indent=2))