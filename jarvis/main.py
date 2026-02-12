#!/usr/bin/env python3
"""
JARVIS - AI Study Assistant
===========================

Main entry point for JARVIS.

Usage:
    python main.py              # Start interactive mode
    python main.py --setup      # Run initial setup
    python main.py --test       # Run tests
    python main.py --version    # Show version

Target: Loyola Academy B.Sc CS Entrance Exam (May 2025)
Profile: Biology Stream → MPC Exam in 75 Days
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from jarvis import __version__, __author__, __target_exam__
from jarvis import check_dependencies, check_root_access, get_version_info


def print_banner():
    """Print JARVIS banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗            ║
║       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝            ║
║       ██║███████║██████╔╝██║   ██║██║███████╗            ║
║  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║            ║
║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║            ║
║   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝            ║
║                                                           ║
║           AI Study Assistant v{}                       ║
║                                                           ║
║  Target: {}                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""".format(__version__, __target_exam__)
    print(banner)


def print_system_status():
    """Print system status check results."""
    print("\n" + "═" * 60)
    print("SYSTEM STATUS CHECK")
    print("═" * 60)
    
    # Check dependencies
    print("\n📦 Dependencies:")
    deps = check_dependencies()
    for name, available in deps.items():
        status = "✓" if available else "✗"
        print(f"   {status} {name}")
    
    # Check root
    print("\n🔐 Root Access:")
    if check_root_access():
        print("   ✓ Root access available")
        print("   ✓ Focus module: FULLY functional")
    else:
        print("   ✗ Root access NOT available")
        print("   ⚠ Focus module: LIMITED (40% effective)")
    
    # Check config
    print("\n⚙️ Configuration:")
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        print(f"   ✓ Config found: {config_path}")
    else:
        print("   ⚠ Config not found, using defaults")
    
    # Check database
    print("\n💾 Database:")
    db_path = Path(__file__).parent.parent / "data" / "db" / "jarvis.db"
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"   ✓ Database exists ({size:,} bytes)")
    else:
        print("   ⚠ Database not initialized")
    
    print("\n" + "═" * 60)


def run_setup():
    """
    Run initial setup wizard.
    
    Reason:
        First-time users need guided setup.
        Creates necessary directories, database, and config.
    """
    print_banner()
    print("\n🚀 JARVIS SETUP WIZARD")
    print("=" * 60)
    
    # Create directories
    print("\n📁 Creating directories...")
    directories = [
        "data/db",
        "data/cache",
        "data/logs",
        "data/backup",
        "models",
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent.parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}/")
    
    # Initialize database
    print("\n💾 Initializing database...")
    try:
        from jarvis.core.config import load_config
        from jarvis.core.database import init_database
        
        config = load_config()
        
        async def init_db():
            db = await init_database(config)
            
            # Create default user
            user_id = await db.create_user("Student")
            print(f"   ✓ User created (ID: {user_id})")
            
            await db.close()
        
        asyncio.run(init_db())
        print("   ✓ Database initialized")
        
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo start JARVIS, run:")
    print("   python main.py")
    
    return True


def run_tests():
    """Run all tests."""
    print_banner()
    print("\n🧪 RUNNING TESTS")
    print("=" * 60)
    
    try:
        import pytest
        tests_dir = Path(__file__).parent.parent / "tests"
        
        if not tests_dir.exists():
            print("   ⚠ No tests directory found")
            return
        
        exit_code = pytest.main([str(tests_dir), "-v"])
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed (exit code: {exit_code})")
            
    except ImportError:
        print("   ✗ pytest not installed")
        print("   Run: pip install pytest")


def start_interactive():
    """Start interactive TUI mode."""
    print_banner()
    print_system_status()
    
    print("\n🚀 Starting JARVIS...")
    print("=" * 60)
    
    # Check if Textual is available
    try:
        from jarvis.ui.app import JarvisApp
        
        app = JarvisApp()
        app.run()
        
    except ImportError as e:
        print(f"\n❌ Cannot start UI: {e}")
        print("   Make sure textual is installed:")
        print("   pip install textual")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting JARVIS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="JARVIS - AI Study Assistant for Loyola Academy B.Sc CS"
    )
    
    parser.add_argument(
        "--setup", "-s",
        action="store_true",
        help="Run initial setup wizard"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run all tests"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version information"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status"
    )
    
    args = parser.parse_args()
    
    # Handle arguments
    if args.version:
        info = get_version_info()
        print(f"JARVIS v{info['version']}")
        print(f"Target: {info['target_exam']}")
        return 0
    
    if args.setup:
        success = run_setup()
        return 0 if success else 1
    
    if args.test:
        run_tests()
        return 0
    
    if args.status:
        print_banner()
        print_system_status()
        return 0
    
    # Default: start interactive mode
    start_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
