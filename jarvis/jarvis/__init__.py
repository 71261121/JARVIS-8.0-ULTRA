#!/usr/bin/env python3
"""
JARVIS - AI Study Assistant for Loyola Academy B.Sc CS Entrance Exam
====================================================================

Personalized for: Biology Stream Student → MPC Exam in 75 Days

Architecture:
    - core/       : Core utilities, config loader, database
    - ai/         : AI engine, question generation
    - study/      : IRT, SM-2, question bank, sessions
    - focus/      : Root commands, distraction blocking
    - psych/      : XP, streaks, achievements, punishments
    - ui/         : Textual TUI interface
    - utils/      : Helper functions, logging

Platform: ROOTED Android + Termux
AI Engine: DeepSeek-R1:1.5B (Offline)

Author: JARVIS AI Research Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "JARVIS AI Research Team"
__target_exam__ = "Loyola Academy B.Sc CS 2025"

# Module availability flags
MODULES_AVAILABLE = {
    "core": True,
    "ai": False,      # Requires llama.cpp setup
    "study": True,
    "focus": False,   # Requires root access
    "psych": True,
    "ui": True,
}

def check_dependencies():
    """
    Check if all required dependencies are available.
    
    Returns:
        dict: Status of each dependency
    
    Reason:
        Early failure is better than runtime errors.
        User can fix issues before starting study.
    """
    import sys
    
    dependencies = {
        "python_version": sys.version_info >= (3, 8),
        "textual": False,
        "aiosqlite": False,
        "pydantic": False,
        "dateutil": False,
    }
    
    try:
        import textual
        dependencies["textual"] = True
    except ImportError:
        pass
    
    try:
        import aiosqlite
        dependencies["aiosqlite"] = True
    except ImportError:
        pass
    
    try:
        import pydantic
        dependencies["pydantic"] = True
    except ImportError:
        pass
    
    try:
        import dateutil
        dependencies["dateutil"] = True
    except ImportError:
        pass
    
    return dependencies

def check_root_access():
    """
    Check if device has root access.
    
    Returns:
        bool: True if root available, False otherwise
    
    Reason:
        Focus module requires root. Without root, system is 40% less effective.
        User must know this before starting.
    """
    import subprocess
    import os
    
    # Method 1: Check for su binary
    su_paths = ["/system/bin/su", "/system/xbin/su", "/sbin/su", "/su/bin/su"]
    for path in su_paths:
        if os.path.exists(path):
            try:
                # Try to execute su -c id
                result = subprocess.run(
                    [path, "-c", "id"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "uid=0" in result.stdout:
                    return True
            except Exception:
                pass
    
    # Method 2: Check for Magisk
    if os.path.exists("/sbin/.magisk"):
        return True
    
    return False

def get_version_info():
    """Return version information as dict."""
    return {
        "version": __version__,
        "author": __author__,
        "target_exam": __target_exam__,
    }


if __name__ == "__main__":
    # Quick self-test when run directly
    print(f"JARVIS v{__version__}")
    print(f"Target: {__target_exam__}")
    print()
    
    print("Checking dependencies...")
    deps = check_dependencies()
    for name, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {name}")
    
    print()
    print("Checking root access...")
    if check_root_access():
        print("  ✓ Root access available")
    else:
        print("  ✗ Root access NOT available (Focus module will be limited)")
    
    print()
    all_deps_ok = all(deps.values())
    if all_deps_ok:
        print("All dependencies OK. Ready to run JARVIS.")
    else:
        print("Some dependencies missing. Run: pip install -r requirements.txt")
