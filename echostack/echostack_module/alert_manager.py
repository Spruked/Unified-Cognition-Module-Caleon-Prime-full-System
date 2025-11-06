"""
Alert Manager Module - Threshold Breach Detection & Alert Suppression
Provides comprehensive alert management with threshold monitoring and intelligent suppression.
"""

import json
import time
import threading
from typing import Dict, Any, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertState(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertType(Enum):
    THRESHOLD_BREACH = "threshold_breach"
    SYSTEM_FAILURE = "system_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_INCIDENT = "security_incident"
    VAULT_INTEGRITY = "vault_integrity"
    CONNECTION_ISSUE = "connection_issue"


@dataclass
class AlertRule:
    """Represents an alert rule with thresholds and conditions"""
    name: str
    alert_type: AlertType
    metric_path: str  # JSON path to metric in telemetry
    condition: str  # "gt", "lt", "eq", "ne", "contains"
    threshold: Any
    severity: AlertSeverity
    description: str
    cooldown_period: int = 300  # seconds
    auto_resolve: bool = True
    notification_channels: List[str] = None

    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["console"]


@dataclass
class Alert:
    """Represents an active alert"""
    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    state: AlertState
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    suppressed_until: Optional[datetime] = None
    occurrence_count: int = 1


class AlertManager:
    """
    Alert Management System with Threshold Breach Detection and Intelligent Suppression
    """

    def __init__(self, telemetry_path: str = "../telemetry.json", config_path: str = "../config.json"):
        self.telemetry_path = telemetry_path
        self.config_path = config_path
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.suppression_rules: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval = 30  # seconds

        # Notification settings
        self.notification_config = {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": []
            },
            "console": {
                "enabled": True
            },
            "log": {
                "enabled": True,
                "file": "alerts.log"
            }
        }

        # Setup logging
        self.logger = logging.getLogger("AlertManager")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("alerts.log")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        self._initialize_default_rules()

    def start_monitoring(self):
        """Start the alert monitoring system"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[AlertManager] Alert monitoring started")

    def stop_monitoring(self):
        """Stop the alert monitoring system"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        print("[AlertManager] Alert monitoring stopped")

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.name] = rule
        print(f"[AlertManager] Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            print(f"[AlertManager] Removed alert rule: {rule_name}")

    def acknowledge_alert(self, alert_id: str, user: str = "system"):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.updated_at = datetime.now()
            print(f"[AlertManager] Alert {alert_id} acknowledged by {user}")

    def resolve_alert(self, alert_id: str, user: str = "system"):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.now()
            alert.updated_at = datetime.now()

            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]

            print(f"[AlertManager] Alert {alert_id} resolved by {user}")

    def suppress_alerts(self, pattern: str, duration: int = 3600, reason: str = "maintenance"):
        """Suppress alerts matching a pattern for a duration"""
        suppression_id = f"suppression_{int(time.time())}"
        self.suppression_rules[suppression_id] = {
            "pattern": pattern,
            "duration": duration,
            "reason": reason,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=duration)
        }

        # Suppress existing alerts
        for alert_id, alert in self.active_alerts.items():
            if pattern in alert.rule_name or pattern in alert.message:
                alert.state = AlertState.SUPPRESSED
                alert.suppressed_until = datetime.now() + timedelta(seconds=duration)
                alert.updated_at = datetime.now()

        print(f"[AlertManager] Suppressed alerts matching '{pattern}' for {duration}s")

    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        self.alert_rules = {
            "high_cpu_usage": AlertRule(
                name="high_cpu_usage",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                metric_path="performance_indicators.cpu_usage_percent",
                condition="gt",
                threshold=80.0,
                severity=AlertSeverity.HIGH,
                description="CPU usage exceeds 80%",
                cooldown_period=300
            ),
            "critical_memory_usage": AlertRule(
                name="critical_memory_usage",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                metric_path="performance_indicators.memory_usage_percent",
                condition="gt",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                description="Memory usage exceeds 90%",
                cooldown_period=180
            ),
            "system_health_low": AlertRule(
                name="system_health_low",
                alert_type=AlertType.SYSTEM_FAILURE,
                metric_path="system_info.health_score",
                condition="lt",
                threshold=0.7,
                severity=AlertSeverity.CRITICAL,
                description="System health score below 0.7",
                cooldown_period=600
            ),
            "vault_integrity_breach": AlertRule(
                name="vault_integrity_breach",
                alert_type=AlertType.VAULT_INTEGRITY,
                metric_path="vault_telemetry.vault_health_scores",
                condition="contains",
                threshold="failed",
                severity=AlertSeverity.HIGH,
                description="Vault integrity compromised",
                cooldown_period=300
            ),
            "connection_loss": AlertRule(
                name="connection_loss",
                alert_type=AlertType.CONNECTION_ISSUE,
                metric_path="connection_metrics.active_connections",
                condition="lt",
                threshold=1,
                severity=AlertSeverity.MEDIUM,
                description="No active connections detected",
                cooldown_period=300
            ),
            "error_rate_spike": AlertRule(
                name="error_rate_spike",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                metric_path="performance_indicators.error_rate_percent",
                condition="gt",
                threshold=5.0,
                severity=AlertSeverity.HIGH,
                description="Error rate exceeds 5%",
                cooldown_period=180
            )
        }

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_alerts()
                self._cleanup_expired_suppressions()
                self._auto_resolve_alerts()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"[AlertManager] Monitor loop error: {e}")
                time.sleep(10)

    def _check_alerts(self):
        """Check all alert rules against current telemetry"""
        try:
            # Load telemetry
            with open(self.telemetry_path, 'r') as f:
                telemetry = json.load(f)

            current_time = datetime.now()

            for rule_name, rule in self.alert_rules.items():
                # Check if alert is in cooldown
                if self._is_rule_in_cooldown(rule_name, current_time):
                    continue

                # Check if alert is suppressed
                if self._is_rule_suppressed(rule_name):
                    continue

                # Evaluate condition
                if self._evaluate_condition(telemetry, rule):
                    self._trigger_alert(rule, telemetry, current_time)

        except Exception as e:
            print(f"[AlertManager] Alert check error: {e}")

    def _evaluate_condition(self, telemetry: Dict[str, Any], rule: AlertRule) -> bool:
        """Evaluate if an alert condition is met"""
        try:
            # Navigate to metric value
            value = self._get_nested_value(telemetry, rule.metric_path)

            if value is None:
                return False

            # Evaluate condition
            if rule.condition == "gt":
                return float(value) > float(rule.threshold)
            elif rule.condition == "lt":
                return float(value) < float(rule.threshold)
            elif rule.condition == "eq":
                return value == rule.threshold
            elif rule.condition == "ne":
                return value != rule.threshold
            elif rule.condition == "contains":
                if isinstance(value, dict):
                    return rule.threshold in str(value)
                elif isinstance(value, list):
                    return rule.threshold in value
                else:
                    return rule.threshold in str(value)
            else:
                return False

        except (ValueError, TypeError, KeyError):
            return False

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _trigger_alert(self, rule: AlertRule, telemetry: Dict[str, Any], timestamp: datetime):
        """Trigger a new alert"""
        alert_id = f"{rule.name}_{int(timestamp.timestamp())}"

        # Check if similar alert already exists
        existing_alert = self._find_similar_alert(rule.name)
        if existing_alert:
            # Increment occurrence count
            existing_alert.occurrence_count += 1
            existing_alert.updated_at = timestamp
            existing_alert.message = f"{rule.description} (occurred {existing_alert.occurrence_count} times)"
            print(f"[AlertManager] Alert {existing_alert.id} occurrence count increased to {existing_alert.occurrence_count}")
            return

        # Create new alert
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            message=rule.description,
            details={
                "metric_path": rule.metric_path,
                "threshold": rule.threshold,
                "current_value": self._get_nested_value(telemetry, rule.metric_path),
                "condition": rule.condition
            },
            state=AlertState.ACTIVE,
            created_at=timestamp,
            updated_at=timestamp
        )

        self.active_alerts[alert_id] = alert

        # Send notifications
        self._send_notifications(alert)

        print(f"[AlertManager] ALERT TRIGGERED: {alert.message} (Severity: {alert.severity.value})")

    def _find_similar_alert(self, rule_name: str) -> Optional[Alert]:
        """Find similar active alert for the same rule"""
        for alert in self.active_alerts.values():
            if alert.rule_name == rule_name and alert.state == AlertState.ACTIVE:
                return alert
        return None

    def _is_rule_in_cooldown(self, rule_name: str, current_time: datetime) -> bool:
        """Check if a rule is in cooldown period"""
        rule = self.alert_rules.get(rule_name)
        if not rule:
            return False

        # Check recent alerts for this rule
        cooldown_end = current_time - timedelta(seconds=rule.cooldown_period)

        for alert in self.active_alerts.values():
            if alert.rule_name == rule_name and alert.created_at > cooldown_end:
                return True

        return False

    def _is_rule_suppressed(self, rule_name: str) -> bool:
        """Check if a rule is currently suppressed"""
        current_time = datetime.now()

        for suppression in self.suppression_rules.values():
            if current_time < suppression["expires_at"]:
                pattern = suppression["pattern"]
                if pattern in rule_name:
                    return True

        return False

    def _cleanup_expired_suppressions(self):
        """Clean up expired suppression rules"""
        current_time = datetime.now()
        expired = []

        for suppression_id, suppression in self.suppression_rules.items():
            if current_time >= suppression["expires_at"]:
                expired.append(suppression_id)

        for suppression_id in expired:
            del self.suppression_rules[suppression_id]

        # Re-activate suppressed alerts
        for alert in self.active_alerts.values():
            if alert.state == AlertState.SUPPRESSED and alert.suppressed_until and current_time >= alert.suppressed_until:
                alert.state = AlertState.ACTIVE
                alert.suppressed_until = None
                alert.updated_at = current_time

    def _auto_resolve_alerts(self):
        """Auto-resolve alerts that are no longer triggering"""
        try:
            with open(self.telemetry_path, 'r') as f:
                telemetry = json.load(f)

            current_time = datetime.now()
            to_resolve = []

            for alert_id, alert in self.active_alerts.items():
                if alert.state != AlertState.ACTIVE:
                    continue

                rule = self.alert_rules.get(alert.rule_name)
                if not rule or not rule.auto_resolve:
                    continue

                # Check if condition is still met
                if not self._evaluate_condition(telemetry, rule):
                    to_resolve.append(alert_id)

            # Resolve alerts
            for alert_id in to_resolve:
                self.resolve_alert(alert_id, "auto-resolve")

        except Exception as e:
            print(f"[AlertManager] Auto-resolve error: {e}")

    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        for channel in alert.details.get("notification_channels", ["console"]):
            try:
                if channel == "console":
                    self._notify_console(alert)
                elif channel == "email":
                    self._notify_email(alert)
                elif channel == "log":
                    self._notify_log(alert)
            except Exception as e:
                print(f"[AlertManager] Notification error for {channel}: {e}")

    def _notify_console(self, alert: Alert):
        """Send console notification"""
        severity_color = {
            AlertSeverity.LOW: "\033[32m",      # Green
            AlertSeverity.MEDIUM: "\033[33m",   # Yellow
            AlertSeverity.HIGH: "\033[31m",    # Red
            AlertSeverity.CRITICAL: "\033[35m" # Magenta
        }.get(alert.severity, "\033[0m")

        reset_color = "\033[0m"
        print(f"{severity_color}[ALERT] {alert.message}{reset_color}")

    def _notify_email(self, alert: Alert):
        """Send email notification"""
        if not self.notification_config["email"]["enabled"]:
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.notification_config["email"]["from_address"]
            msg['To'] = ", ".join(self.notification_config["email"]["to_addresses"])
            msg['Subject'] = f"EchoStack Alert: {alert.severity.value.upper()} - {alert.message}"

            body = f"""
EchoStack Alert Notification

Severity: {alert.severity.value.upper()}
Type: {alert.alert_type.value}
Message: {alert.message}
Time: {alert.created_at}

Details:
{json.dumps(alert.details, indent=2)}

This is an automated message from EchoStack Alert Manager.
            """

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(
                self.notification_config["email"]["smtp_server"],
                self.notification_config["email"]["smtp_port"]
            )
            server.starttls()
            server.login(
                self.notification_config["email"]["username"],
                self.notification_config["email"]["password"]
            )
            server.sendmail(
                self.notification_config["email"]["from_address"],
                self.notification_config["email"]["to_addresses"],
                msg.as_string()
            )
            server.quit()

        except Exception as e:
            print(f"[AlertManager] Email notification failed: {e}")

    def _notify_log(self, alert: Alert):
        """Send log notification"""
        log_message = f"ALERT {alert.severity.value.upper()}: {alert.message} - Details: {alert.details}"
        self.logger.warning(log_message)

    def get_alert_status(self) -> Dict[str, Any]:
        """Get current alert status"""
        return {
            "active_alerts": len(self.active_alerts),
            "alerts_by_severity": {
                severity.value: len([a for a in self.active_alerts.values() if a.severity == severity])
                for severity in AlertSeverity
            },
            "suppressed_rules": len(self.suppression_rules),
            "total_rules": len(self.alert_rules),
            "alert_history_count": len(self.alert_history)
        }

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        return [
            {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "state": alert.state.value,
                "created_at": alert.created_at.isoformat(),
                "occurrence_count": alert.occurrence_count
            }
            for alert in self.active_alerts.values()
        ]

    def export_alert_config(self) -> Dict[str, Any]:
        """Export alert configuration"""
        return {
            "alert_rules": {name: {
                "name": rule.name,
                "type": rule.alert_type.value,
                "severity": rule.severity.value,
                "description": rule.description,
                "threshold": rule.threshold,
                "cooldown_period": rule.cooldown_period,
                "auto_resolve": rule.auto_resolve
            } for name, rule in self.alert_rules.items()},
            "notification_config": self.notification_config,
            "check_interval": self.check_interval
        }