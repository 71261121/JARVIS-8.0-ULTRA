"""
JARVIS TUI Application
======================

Purpose: Main Textual application for JARVIS interface.

Design Principles:
- Clean, minimal interface
- High contrast for readability on mobile
- Keyboard-first navigation
- Mobile-friendly layout

Screens:
- DashboardScreen: Main overview, daily goals, progress
- StudyScreen: Active study session
- ProgressScreen: Charts, theta history, analytics
- SettingsScreen: Configuration options

Keyboard Shortcuts:
- q: Quit
- d: Dashboard
- s: Start study session
- p: Progress view
- ?: Help
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, Button, Label,
    ProgressBar, DataTable, TabbedContent, TabPane
)
from textual.screen import Screen
from textual.reactive import reactive
from datetime import datetime
from typing import Optional
import os
import sys

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from jarvis import __version__, check_dependencies, check_root_access
from jarvis.core.config import load_config, Config
from jarvis.utils.time_utils import get_time_greeting, calculate_days_remaining, get_current_phase, get_phase_name


# ============================================================================
# STYLES
# ============================================================================

CSS = """
/* JARVIS TUI Styles - Nordic Theme */

Screen {
    background: #0d1117;
    color: #c9d1d9;
}

Header {
    background: #161b22;
    color: #58a6ff;
    text-style: bold;
}

Footer {
    background: #161b22;
    color: #8b949e;
}

/* Dashboard */
.dashboard-container {
    padding: 1 2;
}

.stat-box {
    background: #161b22;
    border: solid #30363d;
    padding: 1 2;
    margin: 1;
    width: 1fr;
}

.stat-title {
    color: #8b949e;
    text-style: bold;
}

.stat-value {
    color: #58a6ff;
    text-style: bold;
    text-align: center;
}

/* Progress bars */
ProgressBar {
    height: 1;
}

ProgressBar > .bar--bar {
    background: #21262d;
    color: #238636;
}

/* Buttons */
Button {
    background: #238636;
    color: white;
    border: none;
    margin: 1;
}

Button:focus {
    background: #2ea043;
}

Button.danger {
    background: #da3633;
}

Button.warning {
    background: #d29922;
    color: black;
}

/* Labels */
.title {
    text-style: bold;
    color: #58a6ff;
    text-align: center;
}

.subtitle {
    color: #8b949e;
    text-align: center;
}

/* Containers */
.horizontal-box {
    layout: horizontal;
    height: auto;
}

.vertical-box {
    layout: vertical;
    height: auto;
}

/* Phase indicator */
.phase-current {
    background: #238636;
    color: white;
    padding: 1;
}

.phase-upcoming {
    background: #21262d;
    color: #8b949e;
    padding: 1;
}

/* Alert boxes */
.alert-success {
    background: #238636;
    color: white;
    padding: 1;
}

.alert-warning {
    background: #d29922;
    color: black;
    padding: 1;
}

.alert-danger {
    background: #da3633;
    color: white;
    padding: 1;
}

/* Study session */
.question-box {
    background: #161b22;
    border: solid #30363d;
    padding: 1;
    margin: 1;
}

.option-button {
    background: #21262d;
    color: #c9d1d9;
    border: solid #30363d;
    margin: 1;
    width: 100%;
}

.option-button:hover {
    background: #30363d;
}

.option-button.selected {
    background: #1f6feb;
}

.option-button.correct {
    background: #238636;
}

.option-button.wrong {
    background: #da3633;
}

/* Timer */
.timer-display {
    text-style: bold;
    color: #58a6ff;
    text-align: center;
}

.timer-display.warning {
    color: #d29922;
}

.timer-display.danger {
    color: #f85149;
}
"""


# ============================================================================
# DASHBOARD SCREEN
# ============================================================================

class DashboardScreen(Screen):
    """Main dashboard screen showing daily overview."""
    
    CSS = CSS
    
    BINDINGS = [
        Binding("s", "start_study", "Start Study"),
        Binding("p", "show_progress", "Progress"),
        Binding("f", "show_focus", "Focus Control"),
        Binding("t", "show_settings", "Settings"),
        Binding("q", "quit", "Quit"),
    ]
    
    # Reactive variables
    user_name = reactive("Student")
    current_day = reactive(1)
    days_remaining = reactive(75)
    current_phase = reactive(1)
    current_xp = reactive(0)
    current_streak = reactive(0)
    target_xp = reactive(2000)
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__()
        self.config = config or load_config()
    
    def compose(self) -> ComposeResult:
        """Compose the dashboard."""
        yield Header(show_clock=True)
        
        with Container(classes="dashboard-container"):
            # Greeting
            yield Static(
                f"{get_time_greeting()}, {self.user_name}!",
                classes="title"
            )
            yield Static(
                f"Day {self.current_day} of 75 | Phase {self.current_phase}: {get_phase_name(self.current_phase)}",
                classes="subtitle"
            )
            
            yield Static("")  # Spacer
            
            # Stats row
            with Horizontal(classes="horizontal-box"):
                with Container(classes="stat-box"):
                    yield Static("XP", classes="stat-title")
                    yield Static(f"{self.current_xp:,}", classes="stat-value")
                
                with Container(classes="stat-box"):
                    yield Static("Streak", classes="stat-title")
                    yield Static(f"{self.current_streak} days 🔥", classes="stat-value")
                
                with Container(classes="stat-box"):
                    yield Static("Days Left", classes="stat-title")
                    yield Static(f"{self.days_remaining}", classes="stat-value")
            
            yield Static("")  # Spacer
            
            # Progress to next level
            yield Static("Progress to Next Level", classes="stat-title")
            yield ProgressBar(total=self.target_xp, progress=self.current_xp)
            
            yield Static("")  # Spacer
            
            # Today's goals
            yield Static("Today's Goals", classes="stat-title")
            with Container(classes="stat-box"):
                yield Static("☐ Mathematics: 20 questions (2 hours)")
                yield Static("☐ Physics: 15 questions (1.5 hours)")
                yield Static("☐ Chemistry: 10 questions (1 hour)")
                yield Static("☐ English: 5 questions (30 min)")
                yield Static("☐ Mock Test: 15 min mini test")
            
            yield Static("")  # Spacer
            
            # Phase progress
            yield Static("75-Day Plan Progress", classes="stat-title")
            with Horizontal(classes="horizontal-box"):
                for phase in [1, 2, 3, 4]:
                    phase_class = "phase-current" if phase == self.current_phase else "phase-upcoming"
                    yield Static(
                        f"P{phase}",
                        classes=phase_class
                    )
            
            yield Static("")  # Spacer
            
            # Start button
            yield Button("Start Study Session [s]", id="start-study", variant="success")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.title = "JARVIS Dashboard"
        
        # Load config data
        if self.config:
            self.days_remaining = self.config.user.days_remaining
            self.current_day = 76 - self.days_remaining  # Calculate current day
            self.current_phase = get_current_phase(self.current_day)
    
    def action_start_study(self) -> None:
        """Start study session."""
        self.app.push_screen("study")
    
    def action_show_progress(self) -> None:
        """Show progress screen."""
        self.app.push_screen("progress")
    
    def action_show_focus(self) -> None:
        """Show focus control screen."""
        self.app.push_screen("focus")
    
    def action_show_settings(self) -> None:
        """Show settings screen."""
        self.app.push_screen("settings")


# ============================================================================
# STUDY SCREEN
# ============================================================================

class StudyScreen(Screen):
    """Active study session screen."""
    
    CSS = CSS
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("1", "select_a", "Option A"),
        Binding("2", "select_b", "Option B"),
        Binding("3", "select_c", "Option C"),
        Binding("4", "select_d", "Option D"),
        Binding("enter", "submit", "Submit"),
        Binding("n", "next", "Next Question"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the study screen."""
        yield Header(show_clock=True)
        
        with Container(classes="dashboard-container"):
            # Session info
            with Horizontal(classes="horizontal-box"):
                yield Static("Mathematics - Question 1/20", classes="stat-title")
                yield Static("Timer: 00:00", classes="timer-display", id="timer")
            
            yield Static("")  # Spacer
            
            # Question
            with Container(classes="question-box"):
                yield Static(
                    "If x² - 5x + 6 = 0, what is the sum of squares of the roots?",
                    classes="title",
                    id="question-text"
                )
            
            yield Static("")  # Spacer
            
            # Options
            yield Button("A) 13", classes="option-button", id="option-a")
            yield Button("B) 25", classes="option-button", id="option-b")
            yield Button("C) 10", classes="option-button", id="option-c")
            yield Button("D) 9", classes="option-button", id="option-d")
            
            yield Static("")  # Spacer
            
            # Actions
            with Horizontal(classes="horizontal-box"):
                yield Button("Submit [Enter]", id="submit", variant="success")
                yield Button("Skip [n]", id="skip", variant="warning")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.title = "Study Session"
        self.selected_option = None
    
    def action_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()
    
    def action_select_a(self) -> None:
        """Select option A."""
        self._select_option("A")
    
    def action_select_b(self) -> None:
        """Select option B."""
        self._select_option("B")
    
    def action_select_c(self) -> None:
        """Select option C."""
        self._select_option("C")
    
    def action_select_d(self) -> None:
        """Select option D."""
        self._select_option("D")
    
    def _select_option(self, option: str) -> None:
        """Select an option."""
        self.selected_option = option
        # Update button styles
        for opt in ["a", "b", "c", "d"]:
            btn = self.query_one(f"#option-{opt}")
            btn.remove_class("selected")
        
        btn = self.query_one(f"#option-{option.lower()}")
        btn.add_class("selected")
    
    def action_submit(self) -> None:
        """Submit answer."""
        if self.selected_option:
            # Check answer and show feedback
            pass
    
    def action_next(self) -> None:
        """Skip to next question."""
        pass


# ============================================================================
# PROGRESS SCREEN
# ============================================================================

class ProgressScreen(Screen):
    """Progress and analytics screen."""
    
    CSS = CSS
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("d", "dashboard", "Dashboard"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the progress screen."""
        yield Header(show_clock=True)
        
        with Container(classes="dashboard-container"):
            yield Static("Progress & Analytics", classes="title")
            yield Static("")  # Spacer
            
            # Subject thetas
            yield Static("Subject Ability (Theta)", classes="stat-title")
            with Container(classes="stat-box"):
                yield Static("Mathematics:     θ = +0.15  [Average]")
                yield Static("Physics:         θ = -0.35  [Below Average]")
                yield Static("Chemistry:       θ = +0.42  [Above Average]")
                yield Static("English:         θ = +0.10  [Average]")
            
            yield Static("")  # Spacer
            
            # Mock test history
            yield Static("Recent Mock Tests", classes="stat-title")
            table = DataTable()
            table.add_columns("Date", "Score", "Maths", "Physics", "Chem", "English")
            table.add_row("2025-02-11", "38/60", "12/20", "10/15", "10/15", "6/10")
            table.add_row("2025-02-10", "35/60", "11/20", "9/15", "10/15", "5/10")
            table.add_row("2025-02-09", "32/60", "10/20", "8/15", "9/15", "5/10")
            yield table
            
            yield Static("")  # Spacer
            
            # XP History
            yield Static("XP Earned This Week", classes="stat-title")
            with Horizontal(classes="horizontal-box"):
                with Container(classes="stat-box"):
                    yield Static("Today: +150 XP")
                    yield Static("Yesterday: +200 XP")
                    yield Static("This Week: +850 XP")
        
        yield Footer()
    
    def action_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()
    
    def action_dashboard(self) -> None:
        """Go to dashboard."""
        self.app.pop_screen()


# ============================================================================
# SETTINGS SCREEN
# ============================================================================

class SettingsScreen(Screen):
    """Settings and configuration screen."""
    
    CSS = CSS
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        yield Header(show_clock=True)
        
        with Container(classes="dashboard-container"):
            yield Static("Settings", classes="title")
            yield Static("")  # Spacer
            
            # System status
            yield Static("System Status", classes="stat-title")
            with Container(classes="stat-box"):
                yield Static("Root Access: Checking...")
                yield Static("AI Model: Not Loaded")
                yield Static("Database: OK")
            
            yield Static("")  # Spacer
            
            # Quick actions
            yield Static("Quick Actions", classes="stat-title")
            yield Button("Backup Database", id="backup", variant="success")
            yield Button("Reset Progress", id="reset", variant="warning")
            yield Button("Check for Updates", id="update", variant="success")
            
            yield Static("")  # Spacer
            
            # About
            yield Static("About", classes="stat-title")
            with Container(classes="stat-box"):
                yield Static(f"JARVIS v{__version__}")
                yield Static("Target: Loyola Academy B.Sc CS 2025")
                yield Static("Built for: ROOTED Android + Termux")
        
        yield Footer()
    
    def action_back(self) -> None:
        """Go back to dashboard."""
        self.app.pop_screen()
    
    def on_mount(self) -> None:
        """Check system status on mount."""
        root_status = "Available ✓" if check_root_access() else "Not Available ✗"
        # Update status display


# ============================================================================
# MAIN APP
# ============================================================================

class JarvisApp(App):
    """
    JARVIS Main Application.
    
    A TUI-based study assistant for competitive exam preparation.
    
    Usage:
        app = JarvisApp()
        app.run()
    """
    
    CSS = CSS
    
    SCREENS = {
        "dashboard": DashboardScreen,
        "study": StudyScreen,
        "progress": ProgressScreen,
        "settings": SettingsScreen,
        "focus": "jarvis.ui.focus_screen.FocusScreen",  # Lazy import
    }
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "dashboard", "Dashboard"),
        Binding("f", "focus", "Focus"),
        Binding("?", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.push_screen("dashboard")
    
    def action_dashboard(self) -> None:
        """Go to dashboard."""
        self.push_screen("dashboard")
    
    def action_focus(self) -> None:
        """Go to focus control screen."""
        self.push_screen("focus")
    
    def action_help(self) -> None:
        """Show help."""
        self.push_screen("settings")


# ============================================================================
# TEST / RUN
# ============================================================================

if __name__ == "__main__":
    app = JarvisApp()
    app.run()
