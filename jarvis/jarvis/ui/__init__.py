"""
JARVIS UI Module
================

Purpose: Terminal User Interface using Textual.

Components:
- Main dashboard
- Study session screens
- Progress charts
- Settings screens
- Focus control dashboard
- Pattern analysis dashboard
- Navigation system

Why Textual:
- Modern async framework
- CSS-like styling
- Responsive design
- Keyboard navigation
- Works in Termux

Design Principles:
- Clean, minimal interface
- High contrast for readability
- Keyboard-first navigation
- Mobile-friendly layout

Color Scheme (Nord):
- Primary: #1A1F16 (Deep Forest Ink)
- Body: #2D3329 (Dark Moss Gray)
- Secondary: #4A5548 (Neutral Olive)
- Accent: #94A3B8 (Steady Silver)
"""

from .app import JarvisApp
from .screens import DashboardScreen, StudyScreen, ProgressScreen, SettingsScreen
from .focus_screen import FocusScreen
from .pattern_screen import PatternScreen, display_pattern_summary

__all__ = [
    "JarvisApp",
    "DashboardScreen",
    "StudyScreen", 
    "ProgressScreen",
    "SettingsScreen",
    "FocusScreen",
    "PatternScreen",
    "display_pattern_summary",
]
