"""
Dashboard Module - Visual Telemetry Overlays
Provides real-time visual monitoring and telemetry display capabilities for EchoStack.
"""

import json
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math


class DashboardMode(Enum):
    COMPACT = "compact"
    FULL = "full"
    MINIMAL = "minimal"
    DEBUG = "debug"


class MetricType(Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    TREND = "trend"


@dataclass
class VisualMetric:
    """Represents a visual metric for dashboard display"""
    name: str
    value: Any
    metric_type: MetricType
    unit: str
    color: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    trend_data: Optional[List[Tuple[str, float]]] = None
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (200, 100)


class Dashboard:
    """
    Visual Telemetry Dashboard for EchoStack
    Provides real-time overlays and monitoring displays
    """

    def __init__(self, telemetry_path: str = "../telemetry.json", mode: DashboardMode = DashboardMode.FULL):
        self.telemetry_path = telemetry_path
        self.mode = mode
        self.metrics: Dict[str, VisualMetric] = {}
        self.display_buffer: List[str] = []
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.refresh_rate = 1.0  # seconds

        # Color schemes
        self.colors = {
            "normal": "\033[32m",    # Green
            "warning": "\033[33m",   # Yellow
            "critical": "\033[31m",  # Red
            "info": "\033[36m",      # Cyan
            "header": "\033[35m",    # Magenta
            "reset": "\033[0m"       # Reset
        }

        self._initialize_metrics()

    def start(self):
        """Start the dashboard display"""
        if self.running:
            return

        self.running = True
        self.update_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.update_thread.start()
        print("[Dashboard] Visual telemetry overlay started")

    def stop(self):
        """Stop the dashboard display"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        self._clear_display()
        print("[Dashboard] Visual telemetry overlay stopped")

    def set_mode(self, mode: DashboardMode):
        """Change dashboard display mode"""
        self.mode = mode
        print(f"[Dashboard] Mode changed to: {mode.value}")

    def add_custom_metric(self, metric: VisualMetric):
        """Add a custom metric to the dashboard"""
        self.metrics[metric.name] = metric
        print(f"[Dashboard] Added custom metric: {metric.name}")

    def remove_metric(self, metric_name: str):
        """Remove a metric from the dashboard"""
        if metric_name in self.metrics:
            del self.metrics[metric_name]
            print(f"[Dashboard] Removed metric: {metric_name}")

    def _initialize_metrics(self):
        """Initialize default dashboard metrics"""
        self.metrics = {
            "system_health": VisualMetric(
                name="System Health",
                value=0.98,
                metric_type=MetricType.GAUGE,
                unit="score",
                color="normal",
                threshold_warning=0.8,
                threshold_critical=0.6,
                position=(0, 0),
                size=(300, 80)
            ),
            "active_cycles": VisualMetric(
                name="Active Cycles",
                value=41,
                metric_type=MetricType.COUNTER,
                unit="cycles",
                color="info",
                position=(0, 1),
                size=(200, 60)
            ),
            "cpu_usage": VisualMetric(
                name="CPU Usage",
                value=15.2,
                metric_type=MetricType.GAUGE,
                unit="%",
                color="normal",
                threshold_warning=70.0,
                threshold_critical=90.0,
                position=(1, 0),
                size=(200, 80)
            ),
            "memory_usage": VisualMetric(
                name="Memory Usage",
                value=45.8,
                metric_type=MetricType.GAUGE,
                unit="MB",
                color="normal",
                threshold_warning=80.0,
                threshold_critical=95.0,
                position=(1, 1),
                size=(200, 80)
            ),
            "error_rate": VisualMetric(
                name="Error Rate",
                value=0.0,
                metric_type=MetricType.GAUGE,
                unit="%",
                color="normal",
                threshold_warning=1.0,
                threshold_critical=5.0,
                position=(2, 0),
                size=(200, 60)
            ),
            "response_time": VisualMetric(
                name="Response Time",
                value=12.5,
                metric_type=MetricType.GAUGE,
                unit="ms",
                color="normal",
                threshold_warning=50.0,
                threshold_critical=100.0,
                position=(2, 1),
                size=(200, 80)
            ),
            "vault_health": VisualMetric(
                name="Vault Health",
                value=1.0,
                metric_type=MetricType.GAUGE,
                unit="score",
                color="normal",
                threshold_warning=0.9,
                threshold_critical=0.7,
                position=(0, 2),
                size=(300, 60)
            ),
            "connection_status": VisualMetric(
                name="Connections",
                value=2,
                metric_type=MetricType.COUNTER,
                unit="active",
                color="info",
                position=(1, 2),
                size=(200, 60)
            )
        }

    def _display_loop(self):
        """Main display loop"""
        while self.running:
            try:
                self._update_metrics()
                self._render_dashboard()
                time.sleep(self.refresh_rate)
            except Exception as e:
                print(f"[Dashboard] Display error: {e}")
                time.sleep(2.0)

    def _update_metrics(self):
        """Update metric values from telemetry"""
        try:
            telemetry = {}
            try:
                with open(self.telemetry_path, 'r') as f:
                    telemetry = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file doesn't exist or is malformed, use defaults
                telemetry = {}

            # Ensure telemetry is a dict
            if not isinstance(telemetry, dict):
                telemetry = {}

            # Update system metrics with fallbacks
            self.metrics["system_health"].value = telemetry.get("system_info", {}).get("health_score",
                telemetry.get("system_health", 0.0))
            self.metrics["active_cycles"].value = telemetry.get("runtime_metrics", {}).get("cycles_completed",
                telemetry.get("active_cycles", 0))
            self.metrics["cpu_usage"].value = telemetry.get("performance_indicators", {}).get("cpu_usage_percent",
                telemetry.get("cpu_usage", 0.0))
            self.metrics["memory_usage"].value = telemetry.get("performance_indicators", {}).get("memory_usage_mb",
                telemetry.get("memory_usage", 0.0))
            self.metrics["error_rate"].value = telemetry.get("performance_indicators", {}).get("error_rate_percent",
                telemetry.get("error_rate", 0.0))
            self.metrics["response_time"].value = telemetry.get("performance_indicators", {}).get("response_time_p50_ms",
                telemetry.get("response_time", 0.0))

            # Update vault health (average of all vault scores or fallback)
            vault_scores = telemetry.get("vault_telemetry", {}).get("vault_health_scores", {})
            if vault_scores:
                avg_vault_health = sum(vault_scores.values()) / len(vault_scores)
                self.metrics["vault_health"].value = avg_vault_health
            else:
                self.metrics["vault_health"].value = telemetry.get("vault_health", 1.0)

            # Update connections
            self.metrics["connection_status"].value = telemetry.get("connection_metrics", {}).get("active_connections",
                telemetry.get("connections", 0))

            # Update colors based on thresholds
            self._update_metric_colors()

        except Exception as e:
            print(f"[Dashboard] Failed to update metrics: {e}")

    def _update_metric_colors(self):
        """Update metric colors based on threshold values"""
        for metric in self.metrics.values():
            if metric.threshold_critical is not None and metric.value >= metric.threshold_critical:
                metric.color = "critical"
            elif metric.threshold_warning is not None and metric.value >= metric.threshold_warning:
                metric.color = "warning"
            else:
                metric.color = "normal"

    def _render_dashboard(self):
        """Render the dashboard display"""
        self._clear_display()

        if self.mode == DashboardMode.MINIMAL:
            self._render_minimal()
        elif self.mode == DashboardMode.COMPACT:
            self._render_compact()
        elif self.mode == DashboardMode.DEBUG:
            self._render_debug()
        else:  # FULL
            self._render_full()

    def _render_full(self):
        """Render full dashboard"""
        print(f"{self.colors['header']}╔══════════════════════════════════════════════════════════════════════════════╗{self.colors['reset']}")
        print(f"{self.colors['header']}║                           EchoStack Telemetry Dashboard                        ║{self.colors['reset']}")
        print(f"{self.colors['header']}╠══════════════════════════════════════════════════════════════════════════════╣{self.colors['reset']}")

        # System Status Row
        self._render_metric_row([
            self.metrics["system_health"],
            self.metrics["active_cycles"],
            self.metrics["vault_health"]
        ])

        # Performance Row
        self._render_metric_row([
            self.metrics["cpu_usage"],
            self.metrics["memory_usage"],
            self.metrics["response_time"]
        ])

        # Health Row
        self._render_metric_row([
            self.metrics["error_rate"],
            self.metrics["connection_status"]
        ])

        print(f"{self.colors['header']}╚══════════════════════════════════════════════════════════════════════════════╝{self.colors['reset']}")

    def _render_compact(self):
        """Render compact dashboard"""
        health_color = self._get_metric_color(self.metrics["system_health"])
        cpu_color = self._get_metric_color(self.metrics["cpu_usage"])
        mem_color = self._get_metric_color(self.metrics["memory_usage"])

        print(f"{self.colors['header']}EchoStack{self.colors['reset']} | "
              f"Health:{health_color}{self.metrics['system_health'].value:.2f}{self.colors['reset']} | "
              f"CPU:{cpu_color}{self.metrics['cpu_usage'].value:.1f}%{self.colors['reset']} | "
              f"Mem:{mem_color}{self.metrics['memory_usage'].value:.1f}MB{self.colors['reset']} | "
              f"Cycles:{self.colors['info']}{self.metrics['active_cycles'].value}{self.colors['reset']}")

    def _render_minimal(self):
        """Render minimal dashboard"""
        health_color = self._get_metric_color(self.metrics["system_health"])
        print(f"EchoStack Health: {health_color}{self.metrics['system_health'].value:.2f}{self.colors['reset']}")

    def _render_debug(self):
        """Render debug dashboard with all metrics"""
        print(f"{self.colors['header']}EchoStack Debug Dashboard{self.colors['reset']}")
        print(f"{self.colors['header']}{'='*50}{self.colors['reset']}")

        for name, metric in self.metrics.items():
            color = self._get_metric_color(metric)
            print(f"{name}: {color}{metric.value} {metric.unit}{self.colors['reset']}")

        print(f"{self.colors['header']}{'='*50}{self.colors['reset']}")

    def _render_metric_row(self, metrics: List[VisualMetric]):
        """Render a row of metrics"""
        row_parts = []
        for metric in metrics:
            color = self._get_metric_color(metric)
            value_str = self._format_metric_value(metric)
            row_parts.append(f"{metric.name}: {color}{value_str}{self.colors['reset']}")

        print(f"║ {' │ '.join(row_parts):<78} ║")

    def _format_metric_value(self, metric: VisualMetric) -> str:
        """Format metric value for display"""
        if isinstance(metric.value, float):
            if metric.unit == "score":
                return f"{metric.value:.2f}"
            elif metric.unit == "%":
                return f"{metric.value:.1f}%"
            elif metric.unit in ["MB", "ms"]:
                return f"{metric.value:.1f}{metric.unit}"
            else:
                return f"{metric.value:.2f}"
        else:
            return f"{metric.value}"

    def _get_metric_color(self, metric: VisualMetric) -> str:
        """Get the color code for a metric"""
        return self.colors.get(metric.color, self.colors["normal"])

    def _clear_display(self):
        """Clear the terminal display"""
        print("\033[2J\033[H", end="")  # Clear screen and move cursor to top

    def get_metric_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of all current metrics"""
        return {
            name: {
                "value": metric.value,
                "unit": metric.unit,
                "color": metric.color,
                "threshold_warning": metric.threshold_warning,
                "threshold_critical": metric.threshold_critical
            }
            for name, metric in self.metrics.items()
        }

    def export_dashboard_config(self) -> Dict[str, Any]:
        """Export dashboard configuration"""
        return {
            "mode": self.mode.value,
            "refresh_rate": self.refresh_rate,
            "metrics": {name: {
                "name": m.name,
                "type": m.metric_type.value,
                "unit": m.unit,
                "position": m.position,
                "size": m.size,
                "threshold_warning": m.threshold_warning,
                "threshold_critical": m.threshold_critical
            } for name, m in self.metrics.items()}
        }