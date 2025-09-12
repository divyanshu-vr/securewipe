"""
System file protection to prevent deletion of critical system directories and files.
Implements multiple safety checks and override mechanisms for advanced users.
"""

import os
import platform
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
import re

from shared.secure_logging.secure_logger import get_logger
from shared.utils.exceptions import SecureWipeError

logger = get_logger(__name__)


class ProtectionLevel:
    """Protection levels for system files."""
    CRITICAL = "critical"      # Cannot be deleted under any circumstances
    SYSTEM = "system"          # System files, requires admin override
    IMPORTANT = "important"    # Important files, requires confirmation
    USER = "user"             # User files, normal deletion


class SystemProtection:
    """System file protection with platform-specific rules."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.platform = platform.system().lower()
        
        # Initialize protection rules
        self._critical_paths = set()
        self._system_paths = set()
        self._important_paths = set()
        self._protected_patterns = []
        self._user_overrides = set()
        
        self._initialize_protection_rules()
        
    def _initialize_protection_rules(self):
        """Initialize platform-specific protection rules."""
        if self.platform == "windows":
            self._initialize_windows_protection()
        elif self.platform == "linux":
            self._initialize_linux_protection()
        elif self.platform == "darwin":  # macOS
            self._initialize_macos_protection()
        else:
            self.logger.warning(f"Unknown platform: {self.platform}, using generic protection")
            self._initialize_generic_protection()
            
    def _initialize_windows_protection(self):
        """Initialize Windows-specific protection rules."""
        # Critical system directories - never allow deletion
        system_drive = Path(os.environ.get('SYSTEMDRIVE', 'C:'))
        
        self._critical_paths.update([
            system_drive / "Windows",
            system_drive / "Windows" / "System32",
            system_drive / "Windows" / "SysWOW64",
            system_drive / "Program Files",
            system_drive / "Program Files (x86)",
            Path(os.environ.get('SYSTEMROOT', 'C:\\Windows')),
        ])
        
        # System directories - require admin override
        self._system_paths.update([
            system_drive / "ProgramData",
            system_drive / "Users" / "All Users",
            system_drive / "Users" / "Default",
            system_drive / "Users" / "Public",
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
        ])
        
        # Important user directories - require confirmation
        user_profile = Path(os.environ.get('USERPROFILE', ''))
        if user_profile.exists():
            self._important_paths.update([
                user_profile / "Documents",
                user_profile / "Desktop",
                user_profile / "Pictures",
                user_profile / "Videos",
                user_profile / "Music",
                user_profile / "AppData" / "Roaming",
                user_profile / "AppData" / "Local",
            ])
            
        # Protected file patterns
        self._protected_patterns.extend([
            re.compile(r'.*\.sys$', re.IGNORECASE),
            re.compile(r'.*\.dll$', re.IGNORECASE),
            re.compile(r'.*\.exe$', re.IGNORECASE),  # System executables
            re.compile(r'.*boot.*', re.IGNORECASE),
            re.compile(r'.*ntldr.*', re.IGNORECASE),
            re.compile(r'.*bootmgr.*', re.IGNORECASE),
        ])
        
    def _initialize_linux_protection(self):
        """Initialize Linux-specific protection rules."""
        # Critical system directories
        self._critical_paths.update([
            Path("/bin"),
            Path("/sbin"),
            Path("/usr/bin"),
            Path("/usr/sbin"),
            Path("/lib"),
            Path("/lib64"),
            Path("/usr/lib"),
            Path("/usr/lib64"),
            Path("/etc"),
            Path("/boot"),
            Path("/sys"),
            Path("/proc"),
            Path("/dev"),
        ])
        
        # System directories
        self._system_paths.update([
            Path("/var"),
            Path("/opt"),
            Path("/usr/share"),
            Path("/usr/local"),
            Path("/root"),
        ])
        
        # Important user directories
        home = Path.home()
        self._important_paths.update([
            home / "Documents",
            home / "Desktop",
            home / "Pictures",
            home / "Videos",
            home / "Music",
            home / ".config",
            home / ".local",
        ])
        
        # Protected patterns
        self._protected_patterns.extend([
            re.compile(r'.*/bin/.*'),
            re.compile(r'.*/sbin/.*'),
            re.compile(r'.*\.so(\.\d+)*$'),
            re.compile(r'/etc/.*'),
        ])
        
    def _initialize_macos_protection(self):
        """Initialize macOS-specific protection rules."""
        # Critical system directories
        self._critical_paths.update([
            Path("/System"),
            Path("/Library"),
            Path("/bin"),
            Path("/sbin"),
            Path("/usr/bin"),
            Path("/usr/sbin"),
            Path("/usr/lib"),
            Path("/private"),
        ])
        
        # System directories
        self._system_paths.update([
            Path("/Applications"),
            Path("/var"),
            Path("/opt"),
            Path("/usr/local"),
        ])
        
        # Important user directories
        home = Path.home()
        self._important_paths.update([
            home / "Documents",
            home / "Desktop",
            home / "Pictures",
            home / "Movies",
            home / "Music",
            home / "Library",
        ])
        
        # Protected patterns
        self._protected_patterns.extend([
            re.compile(r'.*/System/.*'),
            re.compile(r'.*\.dylib$'),
            re.compile(r'.*/bin/.*'),
            re.compile(r'.*/sbin/.*'),
        ])
        
    def _initialize_generic_protection(self):
        """Initialize generic protection rules for unknown platforms."""
        # Basic protection for any Unix-like system
        self._critical_paths.update([
            Path("/bin"),
            Path("/sbin"),
            Path("/usr"),
            Path("/etc"),
            Path("/lib"),
        ])
        
        home = Path.home()
        self._important_paths.update([
            home / "Documents",
            home / "Desktop",
        ])
        
    def check_file_protection(self, file_path: Path) -> Tuple[ProtectionLevel, str]:
        """
        Check protection level for a file or directory.
        
        Args:
            file_path: Path to check
            
        Returns:
            Tuple of (protection_level, reason)
        """
        try:
            resolved_path = file_path.resolve()
        except Exception:
            resolved_path = file_path
            
        # Check user overrides first
        if resolved_path in self._user_overrides:
            return ProtectionLevel.USER, "User override applied"
            
        # Check critical paths
        if self._is_protected_path(resolved_path, self._critical_paths):
            return ProtectionLevel.CRITICAL, "Critical system directory"
            
        # Check system paths
        if self._is_protected_path(resolved_path, self._system_paths):
            return ProtectionLevel.SYSTEM, "System directory"
            
        # Check important paths
        if self._is_protected_path(resolved_path, self._important_paths):
            return ProtectionLevel.IMPORTANT, "Important user directory"
            
        # Check protected patterns
        for pattern in self._protected_patterns:
            if pattern.match(str(resolved_path)):
                return ProtectionLevel.SYSTEM, f"Matches protected pattern: {pattern.pattern}"
                
        # Additional platform-specific checks
        protection_result = self._platform_specific_check(resolved_path)
        if protection_result:
            return protection_result
            
        return ProtectionLevel.USER, "User file"
        
    def _is_protected_path(self, file_path: Path, protected_paths: Set[Path]) -> bool:
        """Check if file path is within any protected directory."""
        try:
            for protected_path in protected_paths:
                try:
                    file_path.relative_to(protected_path)
                    return True
                except ValueError:
                    continue
        except Exception as e:
            self.logger.warning(f"Error checking protected path for {file_path}: {e}")
            
        return False
        
    def _platform_specific_check(self, file_path: Path) -> Optional[Tuple[ProtectionLevel, str]]:
        """Platform-specific protection checks."""
        if self.platform == "windows":
            return self._windows_specific_check(file_path)
        elif self.platform == "linux":
            return self._linux_specific_check(file_path)
        elif self.platform == "darwin":
            return self._macos_specific_check(file_path)
        return None
        
    def _windows_specific_check(self, file_path: Path) -> Optional[Tuple[ProtectionLevel, str]]:
        """Windows-specific protection checks."""
        path_str = str(file_path).lower()
        
        # Check for Windows system files
        if any(sys_indicator in path_str for sys_indicator in 
               ['\\windows\\', '\\system32\\', '\\syswow64\\', 'pagefile.sys', 'hiberfil.sys']):
            return ProtectionLevel.CRITICAL, "Windows system file"
            
        # Check for program files
        if '\\program files' in path_str:
            return ProtectionLevel.SYSTEM, "Program Files directory"
            
        # Check for registry-related files
        if any(reg_file in path_str for reg_file in ['ntuser.dat', 'system.dat', 'software.dat']):
            return ProtectionLevel.CRITICAL, "Registry file"
            
        return None
        
    def _linux_specific_check(self, file_path: Path) -> Optional[Tuple[ProtectionLevel, str]]:
        """Linux-specific protection checks."""
        path_str = str(file_path)
        
        # Check for system configuration files
        if path_str.startswith('/etc/'):
            return ProtectionLevel.SYSTEM, "System configuration file"
            
        # Check for kernel modules
        if '/lib/modules/' in path_str:
            return ProtectionLevel.CRITICAL, "Kernel module"
            
        # Check for init system files
        if any(init_path in path_str for init_path in ['/etc/init', '/etc/systemd', '/etc/rc']):
            return ProtectionLevel.CRITICAL, "Init system file"
            
        return None
        
    def _macos_specific_check(self, file_path: Path) -> Optional[Tuple[ProtectionLevel, str]]:
        """macOS-specific protection checks."""
        path_str = str(file_path)
        
        # Check for System Integrity Protection paths
        if path_str.startswith('/System/'):
            return ProtectionLevel.CRITICAL, "System Integrity Protection path"
            
        # Check for kernel extensions
        if '.kext' in path_str:
            return ProtectionLevel.CRITICAL, "Kernel extension"
            
        # Check for LaunchDaemons/LaunchAgents
        if any(launch_path in path_str for launch_path in 
               ['/Library/LaunchDaemons', '/Library/LaunchAgents']):
            return ProtectionLevel.SYSTEM, "Launch daemon/agent"
            
        return None
        
    def filter_protected_files(self, files: List[Path], 
                              allow_system: bool = False,
                              allow_important: bool = True) -> Tuple[List[Path], List[Dict]]:
        """
        Filter out protected files from deletion list.
        
        Args:
            files: List of files to check
            allow_system: Whether to allow system files with override
            allow_important: Whether to allow important files
            
        Returns:
            Tuple of (allowed_files, blocked_files_info)
        """
        allowed_files = []
        blocked_files = []
        
        for file_path in files:
            protection_level, reason = self.check_file_protection(file_path)
            
            if protection_level == ProtectionLevel.CRITICAL:
                blocked_files.append({
                    'path': file_path,
                    'level': protection_level,
                    'reason': reason,
                    'can_override': False
                })
            elif protection_level == ProtectionLevel.SYSTEM and not allow_system:
                blocked_files.append({
                    'path': file_path,
                    'level': protection_level,
                    'reason': reason,
                    'can_override': True
                })
            elif protection_level == ProtectionLevel.IMPORTANT and not allow_important:
                blocked_files.append({
                    'path': file_path,
                    'level': protection_level,
                    'reason': reason,
                    'can_override': True
                })
            else:
                allowed_files.append(file_path)
                
        self.logger.info(f"Protection filter: {len(allowed_files)} allowed, "
                        f"{len(blocked_files)} blocked from {len(files)} total files")
        
        return allowed_files, blocked_files
        
    def add_user_override(self, file_path: Path, confirmation_token: str = None):
        """
        Add user override for protected file.
        
        Args:
            file_path: Path to override
            confirmation_token: Security token for verification
        """
        # In a real implementation, you might want to verify the confirmation token
        # or require additional authentication for overrides
        
        resolved_path = file_path.resolve()
        protection_level, reason = self.check_file_protection(resolved_path)
        
        if protection_level == ProtectionLevel.CRITICAL:
            raise SecureWipeError(f"Cannot override critical system file: {file_path}")
            
        self._user_overrides.add(resolved_path)
        self.logger.warning(f"User override added for protected file: {file_path} ({reason})")
        
    def remove_user_override(self, file_path: Path):
        """Remove user override for file."""
        resolved_path = file_path.resolve()
        self._user_overrides.discard(resolved_path)
        self.logger.info(f"User override removed for: {file_path}")
        
    def get_protection_summary(self, files: List[Path]) -> Dict:
        """
        Get summary of protection levels for list of files.
        
        Returns:
            Dict with protection statistics
        """
        summary = {
            'total_files': len(files),
            'critical': 0,
            'system': 0,
            'important': 0,
            'user': 0,
            'overridden': 0,
            'details': []
        }
        
        for file_path in files:
            protection_level, reason = self.check_file_protection(file_path)
            
            if file_path.resolve() in self._user_overrides:
                summary['overridden'] += 1
            elif protection_level == ProtectionLevel.CRITICAL:
                summary['critical'] += 1
            elif protection_level == ProtectionLevel.SYSTEM:
                summary['system'] += 1
            elif protection_level == ProtectionLevel.IMPORTANT:
                summary['important'] += 1
            else:
                summary['user'] += 1
                
            summary['details'].append({
                'path': file_path,
                'level': protection_level,
                'reason': reason,
                'overridden': file_path.resolve() in self._user_overrides
            })
            
        return summary
        
    def validate_deletion_safety(self, files: List[Path]) -> Dict:
        """
        Validate overall safety of deletion operation.
        
        Returns:
            Dict with safety assessment
        """
        summary = self.get_protection_summary(files)
        
        safety = {
            'safe_to_proceed': True,
            'warnings': [],
            'errors': [],
            'requires_confirmation': False,
            'requires_admin': False
        }
        
        # Check for critical files
        if summary['critical'] > 0:
            safety['safe_to_proceed'] = False
            safety['errors'].append(f"{summary['critical']} critical system files cannot be deleted")
            
        # Check for system files
        if summary['system'] > 0:
            safety['requires_admin'] = True
            safety['warnings'].append(f"{summary['system']} system files require administrator override")
            
        # Check for important files
        if summary['important'] > 0:
            safety['requires_confirmation'] = True
            safety['warnings'].append(f"{summary['important']} important files require confirmation")
            
        # Check for high percentage of system files
        if len(files) > 0:
            system_percentage = (summary['system'] + summary['critical']) / len(files) * 100
            if system_percentage > 50:
                safety['warnings'].append(f"High percentage ({system_percentage:.1f}%) of system files selected")
                
        return safety