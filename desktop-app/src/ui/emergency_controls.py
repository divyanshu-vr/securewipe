"""
Emergency controls and user education components for secure deletion.
Provides immediate cancellation and educational content about secure deletion.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, List
import threading
import time
from datetime import datetime

from shared.secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class EmergencyStopController:
    """Controller for emergency stop functionality during deletion operations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._stop_event = threading.Event()
        self._stop_callbacks = []
        self._is_active = False
        
    def activate(self):
        """Activate emergency stop monitoring."""
        self._stop_event.clear()
        self._is_active = True
        self.logger.info("Emergency stop activated")
        
    def deactivate(self):
        """Deactivate emergency stop monitoring."""
        self._is_active = False
        self.logger.info("Emergency stop deactivated")
        
    def trigger_stop(self, reason: str = "User requested"):
        """Trigger emergency stop."""
        if self._is_active:
            self._stop_event.set()
            self.logger.warning(f"Emergency stop triggered: {reason}")
            
            # Execute all stop callbacks
            for callback in self._stop_callbacks:
                try:
                    callback(reason)
                except Exception as e:
                    self.logger.error(f"Error in emergency stop callback: {e}")
                    
    def is_stop_requested(self) -> bool:
        """Check if emergency stop has been requested."""
        return self._stop_event.is_set()
        
    def add_stop_callback(self, callback: Callable[[str], None]):
        """Add callback to be executed on emergency stop."""
        self._stop_callbacks.append(callback)
        
    def remove_stop_callback(self, callback: Callable[[str], None]):
        """Remove stop callback."""
        if callback in self._stop_callbacks:
            self._stop_callbacks.remove(callback)


class EmergencyStopButton:
    """Emergency stop button widget with prominent styling."""
    
    def __init__(self, parent, stop_controller: EmergencyStopController):
        self.parent = parent
        self.stop_controller = stop_controller
        self.button = None
        self._create_button()
        
    def _create_button(self):
        """Create emergency stop button with prominent styling."""
        # Create frame for button with padding
        self.frame = ttk.Frame(self.parent)
        
        # Create the emergency stop button
        self.button = tk.Button(
            self.frame,
            text="🛑 EMERGENCY STOP",
            font=("Arial", 14, "bold"),
            bg="#ff4444",
            fg="white",
            activebackground="#cc0000",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=10,
            command=self._on_emergency_stop
        )
        self.button.pack(pady=10)
        
        # Add warning text
        warning_label = ttk.Label(
            self.frame,
            text="Click to immediately stop deletion process",
            font=("Arial", 10),
            foreground="red"
        )
        warning_label.pack()
        
    def _on_emergency_stop(self):
        """Handle emergency stop button click."""
        # Show confirmation dialog
        response = messagebox.askyesno(
            "Emergency Stop",
            "Are you sure you want to stop the deletion process immediately?\n\n"
            "This will halt the operation, but files already deleted cannot be recovered.",
            icon="warning"
        )
        
        if response:
            self.stop_controller.trigger_stop("Emergency stop button pressed")
            
    def pack(self, **kwargs):
        """Pack the button frame."""
        self.frame.pack(**kwargs)
        
    def grid(self, **kwargs):
        """Grid the button frame."""
        self.frame.grid(**kwargs)
        
    def enable(self):
        """Enable the emergency stop button."""
        if self.button:
            self.button.config(state=tk.NORMAL)
            
    def disable(self):
        """Disable the emergency stop button."""
        if self.button:
            self.button.config(state=tk.DISABLED)


class SecureDeletionEducationDialog:
    """Educational dialog explaining secure deletion process."""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Understanding Secure Deletion")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("700x600")
        
        self._center_dialog()
        self._create_content()
        
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        x = (self.parent.winfo_x() + 
             (self.parent.winfo_width() // 2) - 
             (self.dialog.winfo_width() // 2))
        y = (self.parent.winfo_y() + 
             (self.parent.winfo_height() // 2) - 
             (self.dialog.winfo_height() // 2))
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_content(self):
        """Create educational content."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="🎓", font=("Arial", 32)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Understanding Secure Deletion", 
                 font=("Arial", 18, "bold")).pack(side=tk.LEFT, padx=(15, 0))
        
        # Create notebook for tabbed content
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab 1: What is Secure Deletion?
        self._create_what_tab(notebook)
        
        # Tab 2: How it Works
        self._create_how_tab(notebook)
        
        # Tab 3: Safety Information
        self._create_safety_tab(notebook)
        
        # Tab 4: Best Practices
        self._create_practices_tab(notebook)
        
        # Close button
        ttk.Button(main_frame, text="I Understand", 
                  command=self.dialog.destroy).pack(pady=(15, 0))
                  
    def _create_what_tab(self, notebook):
        """Create 'What is Secure Deletion?' tab."""
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="What is Secure Deletion?")
        
        content = """
Regular Deletion vs. Secure Deletion

When you normally delete a file:
• The file appears to be gone from your computer
• The space is marked as "available" for new data
• The actual file data remains on the disk
• Specialized tools can recover the "deleted" file

When you securely delete a file:
• The file data is overwritten multiple times with random patterns
• The original data becomes unrecoverable
• Even professional data recovery services cannot restore the file
• The deletion is permanent and irreversible

Why Use Secure Deletion?

• Protect sensitive personal information
• Comply with privacy regulations
• Prevent identity theft from recovered data
• Ensure confidential business data stays confidential
• Prepare devices for disposal or resale
        """
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 11), 
                             bg=frame.cget('bg'), relief=tk.FLAT)
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
    def _create_how_tab(self, notebook):
        """Create 'How it Works' tab."""
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="How it Works")
        
        content = """
The Secure Deletion Process

SecureWipe uses industry-standard methods to permanently destroy your data:

1. File Identification
   • Scans and categorizes files by importance
   • Identifies system files that should not be deleted
   • Shows you exactly what will be removed

2. Multiple Overwrite Passes
   • Overwrites each file's data 3 times (DoD 5220.22-M standard)
   • Uses different patterns: zeros, ones, and random data
   • Ensures no trace of original data remains

3. Metadata Removal
   • Removes file names and directory entries
   • Clears file system metadata
   • Eliminates recovery breadcrumbs

4. Verification
   • Confirms successful overwriting
   • Generates certificate of destruction
   • Provides audit trail for compliance

Technical Details:
• Uses platform-native tools (sdelete on Windows, shred on Linux)
• Follows NIST guidelines for data sanitization
• Compatible with SSDs and traditional hard drives
        """
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 11), 
                             bg=frame.cget('bg'), relief=tk.FLAT)
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
    def _create_safety_tab(self, notebook):
        """Create 'Safety Information' tab."""
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="Safety Information")
        
        content = """
Important Safety Information

⚠️  PERMANENT DELETION WARNING
Secure deletion is IRREVERSIBLE. Once the process completes:
• Files cannot be recovered by any means
• No "undo" or "recycle bin" option exists
• Professional data recovery services cannot help

🛡️  Built-in Safety Features
SecureWipe includes multiple safety mechanisms:
• System file protection prevents critical file deletion
• Multiple confirmation steps before deletion begins
• Backup recommendations for important files
• Emergency stop button during deletion process
• Detailed preview of what will be deleted

🚨  Emergency Stop
During deletion, you can:
• Click the red "EMERGENCY STOP" button
• Stop the process immediately (within 1 second)
• Files already deleted cannot be recovered
• Remaining files will be preserved

📋  Before You Begin
Always:
• Review the file list carefully
• Create backups of important data
• Ensure you have administrator privileges
• Close other applications to prevent conflicts
• Have adequate time to complete the process

🔒  After Deletion
• Certificate of destruction is generated
• Audit log shows what was deleted
• System remains fully functional
• Freed space is available for new data
        """
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 11), 
                             bg=frame.cget('bg'), relief=tk.FLAT)
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
    def _create_practices_tab(self, notebook):
        """Create 'Best Practices' tab."""
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="Best Practices")
        
        content = """
Best Practices for Secure Deletion

📝  Preparation
• Create a complete backup of important files
• Document what you're deleting and why
• Schedule deletion during low-activity periods
• Ensure stable power supply (use UPS if available)
• Close unnecessary applications

🎯  File Selection
• Start with obviously safe files (temp files, cache)
• Be conservative with "Important" categorized files
• Review system protection warnings carefully
• Use the modification feature to adjust selections
• When in doubt, exclude the file

⏰  During Deletion
• Don't use the computer for other tasks
• Monitor progress regularly
• Keep the emergency stop button accessible
• Don't interrupt power or shut down
• Be patient - secure deletion takes time

✅  After Completion
• Review the completion certificate
• Verify expected files are gone
• Check that system still functions normally
• Store certificate for compliance records
• Update your backup strategy

🔄  Regular Maintenance
• Schedule regular secure deletion sessions
• Keep only files you actually need
• Use secure deletion for sensitive documents immediately
• Consider full disk encryption for ongoing protection
• Update SecureWipe regularly for latest security features

💡  Pro Tips
• Larger files take longer to securely delete
• SSDs may require different deletion methods
• Network drives cannot be securely deleted
• Some files may be locked by running programs
• Restart if you encounter persistent file locks
        """
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 11), 
                             bg=frame.cget('bg'), relief=tk.FLAT)
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)


class CompletionSummaryDialog:
    """Dialog showing post-deletion summary and accomplishments."""
    
    def __init__(self, parent, deletion_results: Dict):
        self.parent = parent
        self.results = deletion_results
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Deletion Complete")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("600x500")
        
        self._center_dialog()
        self._create_content()
        
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        x = (self.parent.winfo_x() + 
             (self.parent.winfo_width() // 2) - 
             (self.dialog.winfo_width() // 2))
        y = (self.parent.winfo_y() + 
             (self.parent.winfo_height() // 2) - 
             (self.dialog.winfo_height() // 2))
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_content(self):
        """Create completion summary content."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        success_icon = "✅" if self.results.get('success', False) else "⚠️"
        ttk.Label(header_frame, text=success_icon, font=("Arial", 32)).pack(side=tk.LEFT)
        
        title_text = "Secure Deletion Complete" if self.results.get('success', False) else "Deletion Completed with Issues"
        ttk.Label(header_frame, text=title_text, 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=(15, 0))
        
        # Results summary
        summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="15")
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Statistics
        stats = self.results.get('statistics', {})
        ttk.Label(summary_frame, 
                 text=f"Files Successfully Deleted: {stats.get('deleted_files', 0):,}",
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(summary_frame, 
                 text=f"Total Size Freed: {self._format_size(stats.get('deleted_size', 0))}",
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(summary_frame, 
                 text=f"Time Taken: {self._format_duration(stats.get('duration', 0))}").pack(anchor=tk.W)
        
        if stats.get('failed_files', 0) > 0:
            ttk.Label(summary_frame, 
                     text=f"Files Skipped/Failed: {stats.get('failed_files', 0)}",
                     foreground="orange").pack(anchor=tk.W)
        
        # Certificate information
        cert_frame = ttk.LabelFrame(main_frame, text="Certificate of Destruction", padding="15")
        cert_frame.pack(fill=tk.X, pady=(0, 15))
        
        cert_info = self.results.get('certificate', {})
        if cert_info:
            ttk.Label(cert_frame, 
                     text=f"Certificate ID: {cert_info.get('id', 'N/A')}").pack(anchor=tk.W)
            ttk.Label(cert_frame, 
                     text=f"Generated: {cert_info.get('timestamp', 'N/A')}").pack(anchor=tk.W)
            ttk.Label(cert_frame, 
                     text="A detailed certificate has been saved for your records.").pack(anchor=tk.W, pady=(10, 0))
        
        # Next steps
        next_frame = ttk.LabelFrame(main_frame, text="What's Next?", padding="15")
        next_frame.pack(fill=tk.X, pady=(0, 15))
        
        next_steps = [
            "• Your selected files have been permanently and securely deleted",
            "• The freed space is now available for new data",
            "• Keep the certificate for compliance or audit purposes",
            "• Consider running disk cleanup to optimize remaining space",
            "• Update your backup strategy based on what was deleted"
        ]
        
        for step in next_steps:
            ttk.Label(next_frame, text=step).pack(anchor=tk.W, pady=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        if cert_info:
            ttk.Button(button_frame, text="View Certificate", 
                      command=self._view_certificate).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT)
        
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
            
    def _view_certificate(self):
        """View the generated certificate."""
        # This would integrate with the certificate viewer
        messagebox.showinfo("Certificate", "Certificate viewer would open here.")


class EducationalTooltip:
    """Tooltip widget for providing educational information."""
    
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, event=None):
        """Show tooltip on mouse enter."""
        if self.tooltip:
            return
            
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, 
                        background="lightyellow", 
                        relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 10),
                        wraplength=300,
                        justify=tk.LEFT)
        label.pack()
        
    def _on_leave(self, event=None):
        """Hide tooltip on mouse leave."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None