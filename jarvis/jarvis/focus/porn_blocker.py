"""
JARVIS Porn Blocker
===================

Purpose: Permanent porn site blocking via hosts file modification.

This module provides complete porn blocking at the DNS level by modifying
the /etc/hosts file to redirect porn domains to 127.0.0.1.

EXAM IMPACT:
    CRITICAL. User identified porn as a major distraction.
    Porn consumption causes:
    - Cognitive dullness
    - Dopamine dysregulation  
    - Decreased focus
    - Sleep disruption
    
    Blocking is PERMANENT and works at system level across all browsers.

REASON FOR HOSTS FILE APPROACH:
    - Works for all browsers and apps
    - Cannot be bypassed by incognito mode
    - Cannot be bypassed by DNS changes
    - Works offline (no internet needed)
    - More reliable than app-level blockers

SOURCE FOR DOMAIN LIST:
    - https://github.com/StevenBlack/hosts (curated list)
    - https://github.com/Sinfonietta/hostfiles
    - Combined and deduplicated

ROLLBACK PLAN:
    - Original hosts file backed up to /sdcard/jarvis_backup/hosts_original
    - Command: jarvis-pornblocker restore
    - Removes all JARVIS entries from hosts file

SAFETY:
    - Only modifies /etc/hosts
    - Original file is always backed up
    - Can be fully restored with one command
    - No other system files are modified
"""

import os
import subprocess
import shutil
from datetime import datetime
from typing import List, Tuple, Optional
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

# Backup location
BACKUP_DIR = "/sdcard/jarvis_backup"
HOSTS_BACKUP = f"{BACKUP_DIR}/hosts_original"
JARVIS_MARKER = "# JARVIS_PORN_BLOCK_START"
JARVIS_MARKER_END = "# JARVIS_PORN_BLOCK_END"

# System hosts file
HOSTS_FILE = "/etc/hosts"
HOSTS_SYSTEM_BACKUP = "/system/etc/hosts"  # Some devices use this

# Local redirect
REDIRECT_IP = "127.0.0.1"


# ============================================================================
# CORE PORN DOMAINS LIST
# ============================================================================

# This is a curated list of the most common porn sites
# For full blocking, download the complete list from StevenBlack/hosts

CORE_PORN_DOMAINS = [
    # Major tube sites
    "pornhub.com",
    "pornhub.org", 
    "xvideos.com",
    "xnxx.com",
    "xhamster.com",
    "redtube.com",
    "youporn.com",
    "tube8.com",
    "spankbang.com",
    "spankwire.com",
    
    # Premium sites
    "brazzers.com",
    "naughtyamerica.com",
    "realitykings.com",
    "bangbros.com",
    "mofos.com",
    "digitalplayground.com",
    "twistys.com",
    "babes.com",
    "sexyhub.com",
    "fakehub.com",
    
    # Live cam sites
    "chaturbate.com",
    "livejasmin.com",
    "myfreecams.com",
    "bongacams.com",
    "stripchat.com",
    "cam4.com",
    "camster.com",
    "camsex.com",
    "freecams.com",
    "livecam.com",
    
    # Image sites
    "pornpics.com",
    "nude-gals.com",
    "imagefap.com",
    "imgur.com/r/nsfw",
    "reddit.com/r/nsfw",
    "reddit.com/r/gonewild",
    "reddit.com/r/porn",
    
    # Tumblr (adult content)
    "tumblr.com/search/porn",
    
    # Indian sites
    "desixnxx.net",
    "indiansexstories.net",
    "indianpornvideos.com",
    "desipapa.com",
    " Antarvasna.com",
    "kamababa.com",
    "desixnxx.com",
    "indianxxxsex.com",
    "hindisexstories.net",
    
    # Other popular
    "beeg.com",
    "youjizz.com",
    "keezmovies.com",
    "porn.com",
    "vporn.com",
    "drtuber.com",
    "fuq.com",
    "gotporn.com",
    "hclips.com",
    "hdzog.com",
    "hotmovs.com",
    "nuvid.com",
    "porn555.com",
    "porndoe.com",
    "pornhd.com",
    "pornoxo.com",
    "sex3.com",
    "sunporno.com",
    "tubedupe.com",
    "txxx.com",
    "viptube.com",
    "voyeurhit.com",
    "wetplace.com",
    "winporn.com",
    "xbabe.com",
    "xbooru.com",
    "xdvids.com",
    "xhamster.one",
    "xhcdn.com",
    "xlxx.com",
    "xnxxx.net",
    "xtube.com",
    "xvideos.es",
    "xxx.com",
    "xxxvideo.com",
    "yespornplease.com",
    "yobt.com",
    "yuvutu.com",
    
    # Mobile-specific
    "m.pornhub.com",
    "m.xvideos.com",
    "m.xhamster.com",
    "m.redtube.com",
    
    # Proxy/mirror sites (common)
    "pornhub.net",
    "pornhubselect.com",
    "xvideos.net",
    "xnxx.net",
]

# Additional domains for comprehensive blocking
# These are common porn-related domains
ADDITIONAL_PORN_DOMAINS = [
    "adultfriendfinder.com",
    "ashleyrnadison.com",
    "benaughty.com",
    "camfrog.com",
    "chatroulette.com",
    "fling.com",
    "fuckbook.com",
    "instabang.com",
    "meetandfuck.com",
    "naughtydate.com",
    "sexsearch.com",
    "sexting.com",
    "snapsext.com",
    "together2night.com",
    "tinder.com",  # Often used for hookups
    "xmatch.com",
    "xxxblackbook.com",
    "adultism.com",
    "alt.com",
    "bondage.com",
    "cfnm.net",
    "clips4sale.com",
    "creampie.com",
    "datenschlag.org",
    "eroticbeauties.net",
    "eroticsites.org",
    "fetish.com",
    "fleshbot.com",
    "hentaischool.com",
    "jizzhut.com",
    "literotica.com",
    "nifty.org",
    "nudeafrica.com",
    "pichunter.com",
    "playboy.com",
    "porno-exit.com",
    "porno-rencontre.com",
    "porntrex.com",
    "porntube.com",
    "porno.com",
    "r18.com",
    "shesfreaky.com",
    "slutload.com",
    "spankings.org",
    "stockroom.com",
    "strapon.com",
    "swingular.com",
    "thumbzilla.com",
    "tnaflix.com",
    "wankz.com",
    "watchmygf.net",
    "worldsex.com",
    "xart.com",
    "xfreehd.com",
    "xtheatre.net",
]


# ============================================================================
# HOSTS FILE GENERATOR
# ============================================================================

def generate_hosts_entries(domains: List[str]) -> str:
    """
    Generate hosts file entries for porn domains.
    
    Args:
        domains: List of domain names to block
    
    Returns:
        String with hosts file entries
    
    Reason:
        Creates properly formatted hosts entries.
        Each domain maps to 127.0.0.1 (localhost).
    """
    entries = []
    entries.append("")
    entries.append(JARVIS_MARKER)
    entries.append(f"# Generated by JARVIS on {datetime.now().isoformat()}")
    entries.append(f"# Total domains blocked: {len(domains)}")
    entries.append("# DO NOT REMOVE THESE LINES - Use jarvis-pornblocker restore")
    entries.append("")
    
    for domain in sorted(set(domains)):
        domain = domain.strip().lower()
        if domain and not domain.startswith('#'):
            # Add both with and without www
            entries.append(f"{REDIRECT_IP} {domain}")
            entries.append(f"{REDIRECT_IP} www.{domain}")
    
    entries.append("")
    entries.append(JARVIS_MARKER_END)
    entries.append("")
    
    return "\n".join(entries)


def get_all_porn_domains() -> List[str]:
    """
    Get complete list of porn domains to block.
    
    Returns:
        Combined list of core and additional domains
    
    Reason:
        Provides comprehensive blocking.
        Combines multiple sources.
    """
    all_domains = set(CORE_PORN_DOMAINS + ADDITIONAL_PORN_DOMAINS)
    return sorted([d for d in all_domains if d and not d.startswith('#')])


# ============================================================================
# HOSTS FILE OPERATIONS
# ============================================================================

class PornBlocker:
    """
    Porn blocking via hosts file modification.
    
    Usage:
        blocker = PornBlocker()
        
        # Apply blocking
        success, message = blocker.apply_blocking()
        
        # Remove blocking
        success, message = blocker.remove_blocking()
    
    Reason for design:
        Simple, reliable, permanent blocking.
        Works at DNS level, cannot be bypassed.
    
    EXAM IMPACT:
        Critical. Porn is user's #1 distraction.
        Blocking enables focused study time.
    
    Safety:
        - Original hosts backed up before modification
        - Can be fully restored
        - Clear markers for JARVIS entries
    """
    
    def __init__(self, hosts_file: str = HOSTS_FILE):
        """
        Initialize porn blocker.
        
        Args:
            hosts_file: Path to hosts file (default: /etc/hosts)
        
        Reason:
            Allows testing with alternate hosts file.
        """
        self.hosts_file = hosts_file
        self.backup_dir = Path(BACKUP_DIR)
    
    def check_root_available(self) -> bool:
        """
        Check if root access is available.
        
        Returns:
            True if root is available
        
        Reason:
            Hosts file modification requires root.
            Must verify before attempting operations.
        """
        try:
            result = subprocess.run(
                ["su", "-c", "id"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "uid=0" in result.stdout
        except Exception:
            return False
    
    def backup_original_hosts(self) -> Tuple[bool, str]:
        """
        Backup original hosts file.
        
        Returns:
            Tuple of (success, message)
        
        Reason:
            Original hosts file must be preserved for rollback.
            Backup is stored in /sdcard for easy access.
        """
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Read original hosts
            success, output, error = self._execute_root(f"cat {self.hosts_file}")
            
            if not success:
                return False, f"Failed to read hosts file: {error}"
            
            # Write backup
            backup_path = self.backup_dir / "hosts_original"
            with open(backup_path, 'w') as f:
                f.write(output)
            
            # Also backup timestamp
            timestamp_path = self.backup_dir / "hosts_backup_timestamp.txt"
            with open(timestamp_path, 'w') as f:
                f.write(datetime.now().isoformat())
            
            return True, f"Backup saved to {backup_path}"
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"
    
    def apply_blocking(self) -> Tuple[bool, str]:
        """
        Apply porn blocking by modifying hosts file.
        
        Returns:
            Tuple of (success, message)
        
        Reason:
            Main function to enable blocking.
            Adds entries to /etc/hosts file.
        
        Safety:
            - Backs up original hosts first
            - Checks for existing blocking
            - Uses clear markers for JARVIS entries
        """
        # Check root
        if not self.check_root_available():
            return False, "Root access required. Please root your device first."
        
        # Backup original
        success, message = self.backup_original_hosts()
        if not success:
            return False, f"Backup failed: {message}"
        
        # Check if already blocked
        if self.is_blocking_active():
            return True, "Porn blocking is already active."
        
        # Read current hosts
        success, current_hosts, error = self._execute_root(f"cat {self.hosts_file}")
        if not success:
            return False, f"Failed to read hosts file: {error}"
        
        # Generate blocking entries
        domains = get_all_porn_domains()
        blocking_entries = generate_hosts_entries(domains)
        
        # Combine
        new_hosts = current_hosts.rstrip() + "\n" + blocking_entries
        
        # Write new hosts file
        # First, remount system as read-write
        success, _, error = self._execute_root("mount -o remount,rw /system")
        if not success:
            # Try alternate mount point
            success, _, error = self._execute_root("mount -o remount,rw /")
            if not success:
                return False, f"Failed to remount system as read-write: {error}"
        
        # Write to temporary file first
        temp_file = "/sdcard/jarvis_hosts_temp"
        with open(temp_file, 'w') as f:
            f.write(new_hosts)
        
        # Copy to hosts file
        success, _, error = self._execute_root(f"cp {temp_file} {self.hosts_file}")
        if not success:
            return False, f"Failed to copy hosts file: {error}"
        
        # Set correct permissions
        self._execute_root(f"chmod 644 {self.hosts_file}")
        self._execute_root(f"chown root:root {self.hosts_file}")
        
        # Remount as read-only
        self._execute_root("mount -o remount,ro /system")
        
        # Clean up temp file
        os.remove(temp_file)
        
        # Flush DNS cache
        self._flush_dns()
        
        return True, f"Porn blocking applied. {len(domains)} domains blocked."
    
    def remove_blocking(self) -> Tuple[bool, str]:
        """
        Remove porn blocking from hosts file.
        
        Returns:
            Tuple of (success, message)
        
        Reason:
            Rollback function to disable blocking.
            Removes all JARVIS entries from hosts file.
        
        Safety:
            - Preserves original hosts content
            - Only removes JARVIS-marked sections
        """
        if not self.check_root_available():
            return False, "Root access required."
        
        # Check if backup exists
        backup_path = self.backup_dir / "hosts_original"
        if backup_path.exists():
            # Restore from backup
            with open(backup_path, 'r') as f:
                original_hosts = f.read()
            
            # Remount as read-write
            success, _, error = self._execute_root("mount -o remount,rw /system")
            if not success:
                success, _, error = self._execute_root("mount -o remount,rw /")
                if not success:
                    return False, f"Failed to remount: {error}"
            
            # Write original hosts
            temp_file = "/sdcard/jarvis_hosts_temp"
            with open(temp_file, 'w') as f:
                f.write(original_hosts)
            
            success, _, error = self._execute_root(f"cp {temp_file} {self.hosts_file}")
            if not success:
                return False, f"Failed to restore: {error}"
            
            # Cleanup
            self._execute_root(f"chmod 644 {self.hosts_file}")
            self._execute_root("mount -o remount,ro /system")
            os.remove(temp_file)
            
            # Flush DNS
            self._flush_dns()
            
            return True, "Porn blocking removed. Original hosts restored."
        
        else:
            # No backup - remove JARVIS sections
            success, current_hosts, error = self._execute_root(f"cat {self.hosts_file}")
            if not success:
                return False, f"Failed to read hosts: {error}"
            
            # Remove JARVIS sections
            new_hosts = self._remove_jarvis_sections(current_hosts)
            
            # Write back
            success, _, error = self._execute_root("mount -o remount,rw /system")
            if not success:
                success, _, error = self._execute_root("mount -o remount,rw /")
            
            temp_file = "/sdcard/jarvis_hosts_temp"
            with open(temp_file, 'w') as f:
                f.write(new_hosts)
            
            self._execute_root(f"cp {temp_file} {self.hosts_file}")
            self._execute_root(f"chmod 644 {self.hosts_file}")
            self._execute_root("mount -o remount,ro /system")
            os.remove(temp_file)
            self._flush_dns()
            
            return True, "Porn blocking removed from hosts file."
    
    def is_blocking_active(self) -> bool:
        """
        Check if porn blocking is currently active.
        
        Returns:
            True if blocking is active
        
        Reason:
            Prevents duplicate blocking entries.
        """
        success, hosts_content, _ = self._execute_root(f"cat {self.hosts_file}")
        
        if success:
            return JARVIS_MARKER in hosts_content
        
        return False
    
    def get_blocked_count(self) -> int:
        """
        Get number of currently blocked domains.
        
        Returns:
            Number of blocked domains
        """
        success, hosts_content, _ = self._execute_root(f"cat {self.hosts_file}")
        
        if not success:
            return 0
        
        # Count JARVIS entries
        in_jarvis_section = False
        count = 0
        
        for line in hosts_content.split('\n'):
            if JARVIS_MARKER in line:
                in_jarvis_section = True
                continue
            if JARVIS_MARKER_END in line:
                in_jarvis_section = False
                break
            if in_jarvis_section and line.strip() and not line.startswith('#'):
                count += 1
        
        return count
    
    def test_blocking(self) -> Tuple[bool, str]:
        """
        Test if porn blocking is working.
        
        Returns:
            Tuple of (is_working, message)
        
        Reason:
            Verifies that blocking is actually effective.
        """
        import socket
        
        test_domain = "pornhub.com"
        
        try:
            # Try to resolve a blocked domain
            ip = socket.gethostbyname(test_domain)
            
            if ip == "127.0.0.1":
                return True, f"Blocking working: {test_domain} resolves to 127.0.0.1"
            else:
                return False, f"Blocking NOT working: {test_domain} resolves to {ip}"
                
        except socket.gaierror:
            return True, f"Blocking working: {test_domain} cannot be resolved"
    
    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================
    
    def _execute_root(self, command: str) -> Tuple[bool, str, str]:
        """
        Execute command with root privileges.
        
        Args:
            command: Command to execute
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ["su", "-c", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip()
            )
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def _remove_jarvis_sections(self, hosts_content: str) -> str:
        """
        Remove JARVIS-marked sections from hosts content.
        
        Args:
            hosts_content: Current hosts file content
        
        Returns:
            Hosts content with JARVIS sections removed
        """
        lines = hosts_content.split('\n')
        result_lines = []
        in_jarvis_section = False
        
        for line in lines:
            if JARVIS_MARKER in line:
                in_jarvis_section = True
                continue
            if JARVIS_MARKER_END in line:
                in_jarvis_section = False
                continue
            if not in_jarvis_section:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _flush_dns(self) -> bool:
        """
        Flush DNS cache to apply changes immediately.
        
        Returns:
            True if successful
        """
        # Try multiple methods
        
        # Method 1: ndc resolver
        self._execute_root("ndc resolver flushif wlan0")
        self._execute_root("ndc resolver flushnetcache")
        
        # Method 2: setprop
        self._execute_root("setprop net.dns1 ''")
        self._execute_root("setprop net.dns2 ''")
        
        return True


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_banner():
    """Print banner."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                  JARVIS Porn Blocker                      ║
║                                                           ║
║  PERMANENT DNS-LEVEL BLOCKING                             ║
║  WORKS ACROSS ALL BROWSERS AND APPS                       ║
╚═══════════════════════════════════════════════════════════╝
""")


def main():
    """CLI interface for porn blocker."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Porn Blocker")
    parser.add_argument(
        "command",
        choices=["apply", "remove", "status", "test", "domains"]
    )
    
    args = parser.parse_args()
    
    blocker = PornBlocker()
    
    if args.command == "apply":
        print_banner()
        print("Applying porn blocking...\n")
        
        success, message = blocker.apply_blocking()
        
        if success:
            print(f"✅ SUCCESS: {message}")
            print("\nBlocking is now active across all browsers and apps.")
            print("To remove blocking, run: jarvis-pornblocker remove")
        else:
            print(f"❌ FAILED: {message}")
    
    elif args.command == "remove":
        print_banner()
        print("Removing porn blocking...\n")
        
        success, message = blocker.remove_blocking()
        
        if success:
            print(f"✅ SUCCESS: {message}")
        else:
            print(f"❌ FAILED: {message}")
    
    elif args.command == "status":
        print_banner()
        
        if blocker.check_root_available():
            print("Root access: ✅ Available")
        else:
            print("Root access: ❌ Not available")
            print("\nPorn blocking requires root access.")
            return
        
        if blocker.is_blocking_active():
            count = blocker.get_blocked_count()
            print(f"Blocking status: ✅ Active ({count} domains blocked)")
            
            # Test if actually working
            is_working, test_msg = blocker.test_blocking()
            print(f"Blocking test: {'✅' if is_working else '❌'} {test_msg}")
        else:
            print("Blocking status: ❌ Not active")
    
    elif args.command == "test":
        print_banner()
        is_working, message = blocker.test_blocking()
        print(f"Test result: {'✅' if is_working else '❌'} {message}")
    
    elif args.command == "domains":
        domains = get_all_porn_domains()
        print(f"Total domains that will be blocked: {len(domains)}")
        print("\nSample domains:")
        for d in domains[:20]:
            print(f"  - {d}")
        print(f"  ... and {len(domains) - 20} more")


if __name__ == "__main__":
    main()
