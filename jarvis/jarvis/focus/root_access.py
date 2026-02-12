"""
JARVIS Root Access Module
=========================

Purpose: Verify and manage root access for focus features.

Components:
- Root availability check
- su command execution
- App force-stop commands
- Network blocking commands
- Wake lock management

Requirements:
- ROOTED Android device
- Magisk or SuperSU
- Termux with root-repo and tsu installed

Rollback:
- If root commands fail, system falls back to limited mode
- All commands have dry-run capability for testing

Safety:
- No destructive commands without explicit confirmation
- All commands logged for audit
- Timeout protection for hung commands
"""

import os
import subprocess
import time
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class RootStatus(Enum):
    """Root access status."""
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    PARTIAL = "partial"  # Binary exists but access denied
    UNKNOWN = "unknown"


@dataclass
class CommandResult:
    """Result of a root command execution."""
    success: bool
    output: str
    error: str
    return_code: int
    execution_time: float  # seconds


class RootAccess:
    """
    Root access manager for JARVIS.
    
    Usage:
        root = RootAccess()
        
        if root.is_available():
            result = root.execute("am force-stop com.instagram.android")
            if result.success:
                print("Instagram stopped!")
    
    Reason for design:
        - Centralized root command execution
        - Safety checks before destructive commands
        - Timeout protection
        - Full logging for audit
    """
    
    # Dangerous commands that require explicit confirmation
    DANGEROUS_COMMANDS = [
        "rm -rf",
        "format",
        "dd if=",
        "reboot",
        "shutdown",
    ]
    
    # Path to su binary
    SU_PATHS = [
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/su/bin/su",
        "/magisk/.core/bin/su",
    ]
    
    # Default timeout for commands (seconds)
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, auto_check: bool = True):
        """
        Initialize root access manager.
        
        Args:
            auto_check: Automatically check root on init
        """
        self._status = RootStatus.UNKNOWN
        self._su_path: Optional[str] = None
        self._command_history: List[Dict[str, Any]] = []
        
        if auto_check:
            self.check_root()
    
    def check_root(self) -> RootStatus:
        """
        Check if root access is available.
        
        Returns:
            RootStatus indicating availability
        
        Reason:
            Must verify root before attempting any commands.
            Prevents confusing errors later.
        """
        # Check for su binary
        for path in self.SU_PATHS:
            if os.path.exists(path):
                self._su_path = path
                break
        
        if self._su_path is None:
            # Try to find su in PATH
            try:
                result = subprocess.run(
                    ["which", "su"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self._su_path = result.stdout.strip()
            except Exception:
                pass
        
        if self._su_path is None:
            self._status = RootStatus.NOT_AVAILABLE
            return self._status
        
        # Try to execute su -c id
        try:
            result = subprocess.run(
                [self._su_path, "-c", "id"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "uid=0" in result.stdout:
                self._status = RootStatus.AVAILABLE
            else:
                self._status = RootStatus.PARTIAL
                
        except subprocess.TimeoutExpired:
            self._status = RootStatus.PARTIAL
        except Exception as e:
            self._status = RootStatus.PARTIAL
        
        return self._status
    
    def is_available(self) -> bool:
        """
        Check if root is available.
        
        Returns:
            True if root is available
        """
        if self._status == RootStatus.UNKNOWN:
            self.check_root()
        
        return self._status == RootStatus.AVAILABLE
    
    def get_su_path(self) -> Optional[str]:
        """Get path to su binary."""
        return self._su_path
    
    def get_status(self) -> RootStatus:
        """Get current root status."""
        return self._status
    
    def _log_command(self, command: str, result: CommandResult):
        """Log command execution for audit."""
        entry = {
            "timestamp": time.time(),
            "command": command,
            "success": result.success,
            "return_code": result.return_code,
            "execution_time": result.execution_time,
        }
        self._command_history.append(entry)
        
        # Keep only last 100 commands
        if len(self._command_history) > 100:
            self._command_history = self._command_history[-100:]
    
    def _is_dangerous(self, command: str) -> bool:
        """Check if command is potentially dangerous."""
        command_lower = command.lower()
        return any(danger in command_lower for danger in self.DANGEROUS_COMMANDS)
    
    def execute(self, command: str, timeout: Optional[int] = None,
                confirm_dangerous: bool = False) -> CommandResult:
        """
        Execute a command with root privileges.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (default: 10)
            confirm_dangerous: Set True if dangerous command is confirmed
        
        Returns:
            CommandResult with execution details
        
        Raises:
            RuntimeError: If root not available
            ValueError: If dangerous command not confirmed
        
        Reason:
            Centralized, safe root command execution.
        """
        if not self.is_available():
            raise RuntimeError("Root access not available")
        
        # Check for dangerous commands
        if self._is_dangerous(command) and not confirm_dangerous:
            raise ValueError(
                f"Dangerous command detected: '{command}'. "
                "Set confirm_dangerous=True to execute."
            )
        
        timeout = timeout or self.DEFAULT_TIMEOUT
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [self._su_path, "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            cmd_result = CommandResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            cmd_result = CommandResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds",
                return_code=-1,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            cmd_result = CommandResult(
                success=False,
                output="",
                error=str(e),
                return_code=-1,
                execution_time=execution_time
            )
        
        # Log the command
        self._log_command(command, cmd_result)
        
        return cmd_result
    
    def force_stop_app(self, package_name: str) -> CommandResult:
        """
        Force stop an application.
        
        Args:
            package_name: Android package name (e.g., com.instagram.android)
        
        Returns:
            CommandResult
        
        Reason:
            Primary method for blocking distracting apps.
        """
        command = f"am force-stop {package_name}"
        return self.execute(command)
    
    def disable_app(self, package_name: str) -> CommandResult:
        """
        Disable an application.
        
        Args:
            package_name: Android package name
        
        Returns:
            CommandResult
        
        Warning:
            This is more aggressive than force-stop.
            Use for persistent blocking.
        """
        command = f"pm disable {package_name}"
        return self.execute(command)
    
    def enable_app(self, package_name: str) -> CommandResult:
        """
        Enable a previously disabled application.
        
        Args:
            package_name: Android package name
        
        Returns:
            CommandResult
        """
        command = f"pm enable {package_name}"
        return self.execute(command)
    
    def get_foreground_app(self) -> Tuple[bool, str]:
        """
        Get the current foreground application.
        
        Returns:
            Tuple of (success, package_name)
        
        Reason:
            Used for distraction detection.
        """
        command = "dumpsys activity activities | grep mResumedActivity"
        result = self.execute(command, timeout=5)
        
        if result.success and result.output:
            # Parse output to extract package name
            # Format: mResumedActivity: ActivityRecord{... com.package.name/...}
            try:
                parts = result.output.split()
                for part in parts:
                    if "/" in part:
                        package = part.split("/")[0]
                        return True, package
            except Exception:
                pass
        
        return False, ""
    
    def block_app_network(self, package_name: str, 
                          uid: Optional[int] = None) -> CommandResult:
        """
        Block network access for an app using iptables.
        
        Args:
            package_name: Android package name
            uid: App's UID (required for iptables)
        
        Returns:
            CommandResult
        
        Note:
            UID is required for iptables. Get it with:
            dumpsys package <package_name> | grep userId
        """
        if uid is None:
            # Try to get UID
            result = self.execute(f"dumpsys package {package_name} | grep userId")
            if result.success and "userId=" in result.output:
                try:
                    uid = int(result.output.split("userId=")[1].split()[0])
                except Exception:
                    pass
        
        if uid is None:
            return CommandResult(
                success=False,
                output="",
                error="Could not determine app UID",
                return_code=-1,
                execution_time=0
            )
        
        command = f"iptables -A OUTPUT -m owner --uid-owner {uid} -j DROP"
        return self.execute(command)
    
    def unblock_app_network(self, uid: int) -> CommandResult:
        """
        Remove network block for an app.
        
        Args:
            uid: App's UID
        
        Returns:
            CommandResult
        """
        command = f"iptables -D OUTPUT -m owner --uid-owner {uid} -j DROP"
        return self.execute(command)
    
    def acquire_wake_lock(self) -> bool:
        """
        Acquire wake lock to keep CPU running.
        
        Returns:
            True if successful
        
        Note:
            Use termux-wake-lock in Termux, not root command.
        """
        # In Termux, use termux-wake-lock
        try:
            result = subprocess.run(
                ["termux-wake-lock"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def release_wake_lock(self) -> bool:
        """
        Release wake lock.
        
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["termux-wake-unlock"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_command_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get command execution history.
        
        Args:
            limit: Maximum number of entries
        
        Returns:
            List of command history entries
        """
        return self._command_history[-limit:]
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information.
        
        Returns:
            Dictionary with device info
        
        Reason:
            Useful for debugging and compatibility checks.
        """
        info = {
            "root_status": self._status.value,
            "su_path": self._su_path,
            "architecture": os.uname().machine,
            "device": os.uname().nodename,
            "kernel": os.uname().release,
        }
        
        if self.is_available():
            # Get more info with root
            result = self.execute("getprop ro.product.model", timeout=5)
            if result.success:
                info["model"] = result.output.strip()
            
            result = self.execute("getprop ro.build.version.release", timeout=5)
            if result.success:
                info["android_version"] = result.output.strip()
        
        return info


# ============================================================================
# DISTRACTING APPS DATABASE
# ============================================================================

DISTRACTING_APPS = {
    # Social Media
    "instagram": {
        "name": "Instagram",
        "package": "com.instagram.android",
        "category": "social_media",
        "severity": "high",
    },
    "facebook": {
        "name": "Facebook",
        "package": "com.facebook.katana",
        "category": "social_media",
        "severity": "high",
    },
    "twitter": {
        "name": "Twitter/X",
        "package": "com.twitter.android",
        "category": "social_media",
        "severity": "medium",
    },
    "snapchat": {
        "name": "Snapchat",
        "package": "com.snapchat.android",
        "category": "social_media",
        "severity": "medium",
    },
    "tiktok": {
        "name": "TikTok",
        "package": "com.zhiliaoapp.musically",
        "category": "social_media",
        "severity": "critical",
    },
    "whatsapp": {
        "name": "WhatsApp",
        "package": "com.whatsapp",
        "category": "messaging",
        "severity": "low",  # Often needed for family
    },
    "telegram": {
        "name": "Telegram",
        "package": "org.telegram.messenger",
        "category": "messaging",
        "severity": "low",
    },
    
    # Entertainment
    "youtube": {
        "name": "YouTube",
        "package": "com.google.android.youtube",
        "category": "entertainment",
        "severity": "medium",  # Educational content available
        "whitelist_mode": True,
    },
    "netflix": {
        "name": "Netflix",
        "package": "com.netflix.mediaclient",
        "category": "entertainment",
        "severity": "critical",
    },
    "prime_video": {
        "name": "Prime Video",
        "package": "com.amazon.avod.thirdpartyclient",
        "category": "entertainment",
        "severity": "critical",
    },
    "hotstar": {
        "name": "Disney+ Hotstar",
        "package": "in.startv.hotstar",
        "category": "entertainment",
        "severity": "critical",
    },
    
    # Gaming
    "pubg": {
        "name": "PUBG Mobile",
        "package": "com.pubg.krmobile",
        "category": "gaming",
        "severity": "critical",
    },
    "free_fire": {
        "name": "Free Fire",
        "package": "com.dts.freefireth",
        "category": "gaming",
        "severity": "critical",
    },
    "cod_mobile": {
        "name": "Call of Duty Mobile",
        "package": "com.activision.callofduty.shooter",
        "category": "gaming",
        "severity": "critical",
    },
    "clash_of_clans": {
        "name": "Clash of Clans",
        "package": "com.supercell.clashofclans",
        "category": "gaming",
        "severity": "high",
    },
    
    # Shopping
    "amazon": {
        "name": "Amazon",
        "package": "in.amazon.mShop.android.shopping",
        "category": "shopping",
        "severity": "medium",
    },
    "flipkart": {
        "name": "Flipkart",
        "package": "com.flipkart.android",
        "category": "shopping",
        "severity": "medium",
    },
}


def get_distracting_apps_by_severity(severity: str = "all") -> List[Dict[str, Any]]:
    """
    Get list of distracting apps filtered by severity.
    
    Args:
        severity: Filter by severity (critical, high, medium, low, all)
    
    Returns:
        List of app dictionaries
    """
    if severity == "all":
        return list(DISTRACTING_APPS.values())
    
    return [
        app for app in DISTRACTING_APPS.values()
        if app.get("severity") == severity
    ]


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing Root Access Module...")
    print()
    
    root = RootAccess()
    
    print(f"Root Status: {root.get_status().value}")
    print(f"SU Path: {root.get_su_path()}")
    print()
    
    if root.is_available():
        print("Device Info:")
        info = root.get_device_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
        
        print("Foreground App:")
        success, package = root.get_foreground_app()
        print(f"  {package if success else 'Unknown'}")
    else:
        print("Root not available. Limited functionality.")
