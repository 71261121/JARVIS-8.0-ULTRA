"""
JARVIS Core Module
==================

Core utilities:
- Configuration loading and validation
- Database connection and initialization
- Logging setup
- Common utilities

Reason for separation:
    Core functionality should not depend on other modules.
    This ensures the foundation is always stable.
"""

from .config import Config, load_config
from .database import Database, init_database
from .logging_setup import setup_logging, get_logger

__all__ = [
    "Config",
    "load_config", 
    "Database",
    "init_database",
    "setup_logging",
    "get_logger",
]
