"""
JARVIS Focus Dashboard Screen
=============================

Purpose: TUI screen for displaying focus/distraction monitoring status.

Features:
- Current blocking status
- Distraction events log
- Pattern alerts
- Time saved from blocking
- Quick actions (enable/disable blocking)

EXAM IMPACT:
    Visual feedback for accountability.
    User can see their distraction patterns.
    Motivates consistent behaviour.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, Button, Label,
    DataTable, ProgressBar
)
from textual.screen import Screen
from textual.reactive import reactive
from datetime import datetime
from typing import Optional, Dict, List


# ============================================================================
# STYLES
# ============================================================================

FOCUS_CSS = """
/* Focus Dashboard Styles */

FocusScreen {
    background: #0d1117;
    color: #c9d1d9;
}

.dashboard-container {
    padding: 1 2;
}

.status-card {
    background: #161b22;
    border: solid #30363d;
    padding: 1;
    margin: 1;
    height: auto;
}

.status-title {
    color: #58a6ff;
    text-style: bold;
    margin-bottom: 1;
}

.status-value {
    color: #c9d1d9;
    text-align: center;
}

.status-value.success {
    color: #238636;
}

.status-value.warning {
    color: #d29922;
}

.status-value.danger {
    color: #f85149;
}

.stat-grid {
    layout: horizontal;
    height: auto;
}

.stat-box {
    background: #21262d;
    border: solid #30363d;
    padding: 1;
    margin: 1;
    width: 1fr;
}

.stat-number {
    color: #58a6ff;
    text-style: bold;
    text-align: center;
}

.stat-label {
    color: #8b949e;
    text-align: center;
}

.alert-box {
    background: #da3633;
    color: white;
    padding: 1;
    margin: 1;
}

.alert-box.warning {
    background: #d29922;
    color: black;
}

.event-log {
    background: #161b22;
    border: solid #30363d;
    height: 10;
    margin: 1;
}

.action-buttons {
    layout: horizontal;
    height: auto;
    margin-top: 1;
}

.action-button {
    margin: 1;
}
"""


# ============================================================================
# FOCUS SCREEN
# ============================================================================

class FocusScreen(Screen):
    """
    Focus/Distraction Dashboard Screen.
    
    Shows:
    - Monitoring status
    - Blocking status
    - Recent distraction events
    - Detected patterns
    - Quick actions
    """
    
    CSS = FOCUS_CSS
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("p", "toggle_porn_block", "Porn Block"),
        Binding("m", "toggle_monitor", "Monitor"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    # Reactive variables
    monitor_active = reactive(False)
    porn_block_active = reactive(False)
    root_available = reactive(False)
    current_app = reactive("")
    is_distracting = reactive(False)
    events_logged = reactive(0)
    distractions_blocked = reactive(0)
    domains_blocked = reactive(0)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config
    
    def compose(self) -> ComposeResult:
        """Compose the focus dashboard."""
        yield Header(show_clock=True)
        
        with Container(classes="dashboard-container"):
            # Title
            yield Static("🔒 FOCUS CONTROL CENTER", classes="title")
            yield Static("Behaviour Domination System", classes="subtitle")
            yield Static("")
            
            # Status cards row
            with Horizontal(classes="stat-grid"):
                # Root status
                with Container(classes="stat-box"):
                    yield Static("ROOT", classes="stat-label")
                    yield Static("Checking...", id="root-status", classes="stat-number")
                
                # Monitor status
                with Container(classes="stat-box"):
                    yield Static("MONITOR", classes="stat-label")
                    yield Static("OFF", id="monitor-status", classes="stat-number danger")
                
                # Porn block status
                with Container(classes="stat-box"):
                    yield Static("PORN BLOCK", classes="stat-label")
                    yield Static("OFF", id="porn-status", classes="stat-number danger")
                
                # Current app
                with Container(classes="stat-box"):
                    yield Static("CURRENT APP", classes="stat-label")
                    yield Static("-", id="current-app", classes="stat-number")
            
            yield Static("")
            
            # Statistics row
            with Horizontal(classes="stat-grid"):
                with Container(classes="stat-box"):
                    yield Static("Events Logged", classes="stat-label")
                    yield Static("0", id="events-count", classes="stat-number")
                
                with Container(classes="stat-box"):
                    yield Static("Distractions Blocked", classes="stat-label")
                    yield Static("0", id="blocked-count", classes="stat-number")
                
                with Container(classes="stat-box"):
                    yield Static("Domains Blocked", classes="stat-label")
                    yield Static("0", id="domains-count", classes="stat-number")
            
            yield Static("")
            
            # Alert area
            yield Static("⚠️ PATTERNS & ALERTS", classes="status-title")
            with Container(classes="status-card", id="alerts-container"):
                yield Static("No active patterns detected.", id="alerts-text")
            
            yield Static("")
            
            # Recent events
            yield Static("📋 RECENT DISTRACTION EVENTS", classes="status-title")
            with Container(classes="event-log"):
                table = DataTable(id="events-table")
                table.add_columns("Time", "Event", "App", "Action")
                # Sample data
                table.add_row("10:30:45", "Distraction", "Instagram", "Blocked")
                table.add_row("10:25:12", "App Switch", "YouTube", "Logged")
                table.add_row("10:20:33", "Screen Off", "-", "Logged")
                yield table
            
            yield Static("")
            
            # Action buttons
            with Horizontal(classes="action-buttons"):
                yield Button("Toggle Monitor [m]", id="toggle-monitor", variant="primary")
                yield Button("Toggle Porn Block [p]", id="toggle-porn", variant="warning")
                yield Button("Refresh [r]", id="refresh", variant="default")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.title = "Focus Control"
        self._update_status()
    
    def _update_status(self) -> None:
        """Update all status displays."""
        # Check root
        try:
            from jarvis.focus import ROOT_AVAILABLE
            self.root_available = ROOT_AVAILABLE
        except ImportError:
            self.root_available = False
        
        # Update root status display
        root_widget = self.query_one("#root-status")
        if self.root_available:
            root_widget.update("✓ YES")
            root_widget.set_class(True, "success")
        else:
            root_widget.update("✗ NO")
            root_widget.set_class(True, "danger")
        
        # Update domains count
        try:
            from jarvis.focus import get_all_porn_domains
            domains = get_all_porn_domains()
            self.domains_blocked = len(domains)
            self.query_one("#domains-count").update(str(len(domains)))
        except ImportError:
            pass
        
        # Update current status
        self.query_one("#monitor-status").update(
            "ON" if self.monitor_active else "OFF"
        )
        self.query_one("#monitor-status").set_class(
            self.monitor_active, "success"
        )
        self.query_one("#monitor-status").set_class(
            not self.monitor_active, "danger"
        )
        
        self.query_one("#porn-status").update(
            "ON" if self.porn_block_active else "OFF"
        )
        self.query_one("#porn-status").set_class(
            self.porn_block_active, "success"
        )
        self.query_one("#porn-status").set_class(
            not self.porn_block_active, "danger"
        )
    
    def action_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()
    
    def action_toggle_monitor(self) -> None:
        """Toggle behaviour monitor."""
        # This would actually start/stop the monitor
        self.monitor_active = not self.monitor_active
        self._update_status()
    
    def action_toggle_porn_block(self) -> None:
        """Toggle porn blocking."""
        # This would actually apply/remove blocking
        self.porn_block_active = not self.porn_block_active
        self._update_status()
    
    def action_refresh(self) -> None:
        """Refresh all status."""
        self._update_status()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "toggle-monitor":
            self.action_toggle_monitor()
        elif button_id == "toggle-porn":
            self.action_toggle_porn_block()
        elif button_id == "refresh":
            self.action_refresh()
    
    def update_alerts(self, patterns: List[Dict]) -> None:
        """
        Update the alerts display.
        
        Args:
            patterns: List of detected patterns
        """
        alerts_widget = self.query_one("#alerts-text")
        
        if not patterns:
            alerts_widget.update("No active patterns detected.")
            return
        
        # Format alerts
        lines = []
        for p in patterns[:5]:  # Show top 5
            severity = p.get("severity", "low")
            desc = p.get("description", "Unknown pattern")
            
            if severity == "critical":
                lines.append(f"🔴 CRITICAL: {desc}")
            elif severity == "high":
                lines.append(f"🟠 HIGH: {desc}")
            else:
                lines.append(f"🟡 {desc}")
        
        alerts_widget.update("\n".join(lines))
    
    def update_events(self, events: List[Dict]) -> None:
        """
        Update the events table.
        
        Args:
            events: List of recent events
        """
        table = self.query_one("#events-table", DataTable)
        table.clear()
        
        for event in events[:10]:  # Show last 10
            time_str = event.get("time", "-")
            event_type = event.get("type", "-")
            app = event.get("app", "-")
            action = event.get("action", "-")
            table.add_row(time_str, event_type, app, action)


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def get_focus_screen(config=None) -> FocusScreen:
    """
    Create and return a FocusScreen instance.
    
    Args:
        config: Optional configuration
    
    Returns:
        FocusScreen instance
    """
    return FocusScreen(config=config)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("Focus Screen module loaded successfully.")
    print("Use with Textual app:")
    print("  from jarvis.ui.focus_screen import FocusScreen")
    print("  app.push_screen(FocusScreen())")
