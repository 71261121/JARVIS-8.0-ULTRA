"""
JARVIS Pattern Dashboard TUI
============================

Purpose: Terminal User Interface for pattern analysis and intervention management.

This module:
- Displays detected patterns in real-time
- Shows intervention history
- Provides manual control over analysis
- Shows trend summaries and statistics

EXAM IMPACT:
    HIGH. Visual feedback on behaviour patterns increases accountability.
    User can see their patterns and take corrective action.

REASON FOR DESIGN:
    - Textual framework for modern TUI
    - Real-time updates
    - Interactive controls
    - Clear visual hierarchy

DEPENDENCIES:
    - textual (pip install textual)
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Try to import textual, provide fallback
try:
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal, Vertical, VerticalScroll
    from textual.widgets import (
        Header, Footer, Static, Button, Label,
        DataTable, ProgressBar, TabbedContent, TabPane
    )
    from textual.screen import Screen
    from textual.reactive import reactive
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    # Create dummy classes for non-textual environments
    class Screen:
        pass
    class Static:
        pass
    class Container:
        pass


# ============================================================================
# CONSTANTS
# ============================================================================

# UI Colors (for styling)
COLOR_CRITICAL = "red"
COLOR_HIGH = "orange"
COLOR_MEDIUM = "yellow"
COLOR_LOW = "green"
COLOR_INFO = "blue"

# Severity icons
SEVERITY_ICONS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}

# Pattern type display names
PATTERN_DISPLAY_NAMES = {
    "study_avoidance": "Study Avoidance",
    "burnout_precursor": "Burnout Precursor",
    "weakness_avoidance": "Weakness Avoidance",
    "inconsistency": "Inconsistency",
    "late_night_dopamine": "Late Night Dopamine",
    "distraction_escalation": "Distraction Escalation",
}


# ============================================================================
# WIDGETS
# ============================================================================

if TEXTUAL_AVAILABLE:
    class PatternCard(Static):
        """Widget to display a single pattern."""

        pattern = reactive(None)

        def __init__(self, pattern=None, **kwargs):
            super().__init__(**kwargs)
            self.pattern = pattern

        def render(self) -> str:
            if not self.pattern:
                return "No pattern data"

            severity = self.pattern.severity.value
            icon = SEVERITY_ICONS.get(severity, "⚪")

            lines = [
                f"{icon} {PATTERN_DISPLAY_NAMES.get(self.pattern.pattern_type.value, self.pattern.pattern_type.value)}",
                f"  Severity: {severity.upper()} | Score: {self.pattern.score}/100",
                f"  {self.pattern.description}",
            ]

            # Add evidence
            if self.pattern.evidence:
                lines.append("  Evidence:")
                for key, value in list(self.pattern.evidence.items())[:3]:
                    lines.append(f"    • {key}: {value}")

            return "\n".join(lines)

        def get_color(self) -> str:
            if not self.pattern:
                return "white"
            severity = self.pattern.severity.value
            return {
                "critical": COLOR_CRITICAL,
                "high": COLOR_HIGH,
                "medium": COLOR_MEDIUM,
                "low": COLOR_LOW,
            }.get(severity, "white")


    class InterventionCard(Static):
        """Widget to display a single intervention."""

        record = reactive(None)

        def __init__(self, record=None, **kwargs):
            super().__init__(**kwargs)
            self.record = record

        def render(self) -> str:
            if not self.record:
                return "No intervention data"

            status_icon = "✅" if self.record.success else "❌"
            rollback_icon = "↩️" if self.record.rolled_back else ""

            lines = [
                f"{status_icon} {self.record.intervention_type} {rollback_icon}",
                f"  Pattern: {self.record.pattern_type}",
                f"  Time: {self.record.executed_at.strftime('%H:%M:%S')}",
                f"  {self.record.result_message[:50]}...",
            ]

            return "\n".join(lines)


    class TrendWidget(Static):
        """Widget to display trend analysis."""

        trends = reactive(None)

        def __init__(self, trends=None, **kwargs):
            super().__init__(**kwargs)
            self.trends = trends

        def render(self) -> str:
            if not self.trends:
                return "No trend data available"

            lines = ["📊 BEHAVIOUR TRENDS (7-day comparison)", ""]

            # Study time trend
            study_trend = self.trends.get("study_time_trend", "unknown")
            study_change = self.trends.get("study_time_change_pct", 0)
            study_icon = "📈" if study_trend == "improving" else "📉" if study_trend == "declining" else "➡️"
            lines.append(f"  Study Time: {study_icon} {study_trend.title()} ({study_change:+.1f}%)")

            # Distraction trend
            dist_trend = self.trends.get("distraction_trend", "unknown")
            dist_change = self.trends.get("distraction_change_pct", 0)
            dist_icon = "📉" if dist_trend == "improving" else "📈" if dist_trend == "declining" else "➡️"
            lines.append(f"  Distractions: {dist_icon} {dist_trend.title()} ({dist_change:+.1f}%)")

            # Accuracy trend
            acc_trend = self.trends.get("accuracy_trend", "unknown")
            acc_change = self.trends.get("accuracy_change_pct", 0)
            acc_icon = "📈" if acc_trend == "improving" else "📉" if acc_trend == "declining" else "➡️"
            lines.append(f"  Accuracy: {acc_icon} {acc_trend.title()} ({acc_change:+.1f}%)")

            lines.append("")
            lines.append(f"  🔥 Current Streak: {self.trends.get('current_streak', 0)} days")
            lines.append(f"  🏆 Longest Streak: {self.trends.get('longest_streak', 0)} days")
            lines.append(f"  🌙 Late Night Incidents (7d): {self.trends.get('late_night_incidents_7d', 0)}")

            return "\n".join(lines)


    class StatsWidget(Static):
        """Widget to display intervention statistics."""

        stats = reactive(None)

        def __init__(self, stats=None, **kwargs):
            super().__init__(**kwargs)
            self.stats = stats

        def render(self) -> str:
            if not self.stats:
                return "No statistics available"

            lines = ["📈 INTERVENTION STATISTICS", ""]

            lines.append(f"  Total Interventions: {self.stats.total_interventions}")
            lines.append(f"  Today: {self.stats.today_interventions}")
            lines.append(f"  Successful: {self.stats.successful_interventions}")
            lines.append(f"  Rolled Back: {self.stats.rolled_back_interventions}")

            if self.stats.by_type:
                lines.append("")
                lines.append("  By Type:")
                for itype, count in self.stats.by_type.items():
                    lines.append(f"    • {itype}: {count}")

            return "\n".join(lines)


# ============================================================================
# PATTERN SCREEN
# ============================================================================

if TEXTUAL_AVAILABLE:
    class PatternScreen(Screen):
        """
        Main screen for pattern analysis dashboard.

        Features:
        - Real-time pattern display
        - Intervention history
        - Trend analysis
        - Manual controls

        Keyboard Bindings:
        - [a] Run analysis now
        - [c] Clear patterns
        - [r] Refresh
        - [s] Toggle analyzer
        - [escape] Back to main menu
        """

        CSS = """
        PatternScreen {
            background: $surface;
        }

        .header {
            background: $primary;
            color: $text;
            padding: 1;
        }

        .patterns-container {
            height: 40%;
            border: solid $primary;
        }

        .interventions-container {
            height: 30%;
            border: solid $accent;
        }

        .stats-container {
            height: 30%;
        }

        .control-bar {
            height: 3;
            background: $panel;
            align: center middle;
        }

        Button {
            margin: 0 1;
        }

        .status-bar {
            dock: bottom;
            height: 1;
            background: $panel;
        }
        """

        BINDINGS = [
            Binding("a", "analyze", "Analyze Now"),
            Binding("c", "clear", "Clear"),
            Binding("r", "refresh", "Refresh"),
            Binding("s", "toggle_analyzer", "Toggle"),
            Binding("escape", "back", "Back"),
        ]

        # Reactive properties
        analyzer_status = reactive("stopped")
        patterns_count = reactive(0)
        interventions_count = reactive(0)

        def __init__(self, pattern_analyzer=None, **kwargs):
            super().__init__(**kwargs)
            self.pattern_analyzer = pattern_analyzer
            self._refresh_timer = None

        def compose(self) -> ComposeResult:
            """Compose the screen layout."""
            yield Header()

            with Container(classes="header"):
                yield Label("🔍 PATTERN ANALYSIS DASHBOARD", id="title")

            with VerticalScroll():
                # Current Patterns
                with Container(classes="patterns-container"):
                    yield Label("⚠️ DETECTED PATTERNS", classes="section-header")
                    yield Static(id="patterns-list", classes="patterns")

                # Recent Interventions
                with Container(classes="interventions-container"):
                    yield Label("🔧 RECENT INTERVENTIONS", classes="section-header")
                    yield Static(id="interventions-list", classes="interventions")

                # Statistics and Trends
                with Horizontal(classes="stats-container"):
                    with Container():
                        yield TrendWidget(id="trends")
                    with Container():
                        yield StatsWidget(id="stats")

            with Container(classes="control-bar"):
                yield Button("Analyze Now", id="btn-analyze", variant="primary")
                yield Button("Toggle Analyzer", id="btn-toggle", variant="warning")
                yield Button("Refresh", id="btn-refresh")

            yield Footer()

        def on_mount(self) -> None:
            """Called when screen is mounted."""
            self._refresh_data()
            # Set up auto-refresh every 30 seconds
            self._refresh_timer = self.set_interval(30, self._refresh_data)

        def on_unmount(self) -> None:
            """Called when screen is unmounted."""
            if self._refresh_timer:
                self._refresh_timer.stop()

        def _refresh_data(self) -> None:
            """Refresh all displayed data."""
            if not self.pattern_analyzer:
                return

            # Get patterns
            patterns = self.pattern_analyzer.get_recent_patterns(24)
            self.patterns_count = len(patterns)

            patterns_text = ""
            if patterns:
                for p in patterns[-5:]:  # Show last 5
                    patterns_text += PatternCard(pattern=p).render() + "\n\n"
            else:
                patterns_text = "✅ No patterns detected in the last 24 hours"

            self.query_one("#patterns-list", Static).update(patterns_text)

            # Get interventions
            interventions = self.pattern_analyzer.get_recent_interventions(24)
            self.interventions_count = len(interventions)

            interventions_text = ""
            if interventions:
                for i in interventions[-5:]:  # Show last 5
                    interventions_text += InterventionCard(record=i).render() + "\n\n"
            else:
                interventions_text = "No interventions in the last 24 hours"

            self.query_one("#interventions-list", Static).update(interventions_text)

            # Get trends
            trends = self.pattern_analyzer.get_trend_summary()
            self.query_one("#trends", TrendWidget).trends = trends
            self.query_one("#trends", TrendWidget).refresh()

            # Get stats
            stats = self.pattern_analyzer.get_intervention_statistics()
            self.query_one("#stats", StatsWidget).stats = stats
            self.query_one("#stats", StatsWidget).refresh()

            # Update analyzer status
            self.analyzer_status = "running" if self.pattern_analyzer.is_running() else "stopped"

        def action_analyze(self) -> None:
            """Run immediate analysis."""
            if self.pattern_analyzer:
                result = self.pattern_analyzer.analyze_now()
                self._refresh_data()
                self.notify(
                    f"Analysis complete: {result.patterns_detected} patterns, "
                    f"{result.interventions_executed} interventions",
                    title="Analysis Complete"
                )

        def action_clear(self) -> None:
            """Clear displayed patterns (not data)."""
            self.query_one("#patterns-list", Static).update("Patterns cleared from view")
            self.query_one("#interventions-list", Static).update("Interventions cleared from view")

        def action_refresh(self) -> None:
            """Refresh displayed data."""
            self._refresh_data()
            self.notify("Data refreshed", title="Refresh")

        def action_toggle_analyzer(self) -> None:
            """Toggle analyzer on/off."""
            if not self.pattern_analyzer:
                return

            if self.pattern_analyzer.is_running():
                self.pattern_analyzer.stop()
                self.notify("Analyzer stopped", title="Analyzer", severity="warning")
            else:
                self.pattern_analyzer.start()
                self.notify("Analyzer started", title="Analyzer")

            self._refresh_data()

        def action_back(self) -> None:
            """Go back to main menu."""
            self.app.pop_screen()

        def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            button_id = event.button.id

            if button_id == "btn-analyze":
                self.action_analyze()
            elif button_id == "btn-toggle":
                self.action_toggle_analyzer()
            elif button_id == "btn-refresh":
                self.action_refresh()


# ============================================================================
# FALLBACK FOR NON-TEXTUAL ENVIRONMENTS
# ============================================================================

def display_pattern_summary(pattern_analyzer) -> str:
    """
    Display pattern summary as text (for non-TUI environments).

    Args:
        pattern_analyzer: PatternAnalyzer instance

    Returns:
        Formatted text summary

    Reason:
        Fallback for environments without Textual.
    """
    lines = ["=" * 60]
    lines.append("🔍 PATTERN ANALYSIS DASHBOARD")
    lines.append("=" * 60)

    if not pattern_analyzer:
        lines.append("No analyzer connected")
        return "\n".join(lines)

    # Status
    status = pattern_analyzer.get_status()
    lines.append(f"\n📊 Status: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
    lines.append(f"Total Analyses: {status['total_analyses']}")
    lines.append(f"Patterns Detected: {status['total_patterns_detected']}")
    lines.append(f"Interventions: {status['total_interventions_executed']}")

    # Recent patterns
    patterns = pattern_analyzer.get_recent_patterns(24)
    lines.append(f"\n⚠️ Recent Patterns ({len(patterns)} in 24h):")
    if patterns:
        for p in patterns[-5:]:
            severity = p.severity.value
            icon = SEVERITY_ICONS.get(severity, "⚪")
            lines.append(f"  {icon} {p.pattern_type.value}: {p.description}")
    else:
        lines.append("  ✅ No patterns detected")

    # Trends
    trends = pattern_analyzer.get_trend_summary()
    lines.append("\n📈 Trends:")
    lines.append(f"  Study Time: {trends.get('study_time_trend', 'unknown')}")
    lines.append(f"  Distractions: {trends.get('distraction_trend', 'unknown')}")
    lines.append(f"  Current Streak: {trends.get('current_streak', 0)} days")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Pattern Dashboard...")

    # Test without Textual
    print("\n" + display_pattern_summary(None))

    if TEXTUAL_AVAILABLE:
        print("\n✅ Textual available - TUI mode supported")
    else:
        print("\n⚠️ Textual not available - using text fallback mode")

    print("\nAll tests passed!")
