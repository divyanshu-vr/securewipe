"""
User confirmation and safety control dialogs for secure deletion.
Implements multi-stage confirmation system with safety controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional, Callable
from pathlib import Path
import threading

from .modern_components import ModernColors, ModernButton, ModernCard, configure_modern_styles

try:
    from secure_logging.secure_logger import get_logger
    from utils.exceptions import SecureWipeError
    logger = get_logger(__name__)
except ImportError:
    # Fallback for development
    import logging
    logger = logging.getLogger(__name__)
    
    class SecureWipeError(Exception):
        pass


class DeletionSummary:
    """Data model for deletion summary information."""
    
    def __init__(self):
        self.total_files = 0
        self.total_size = 0
        self.categories = {
            'Safe': {'count': 0, 'size': 0},
            'Less Important': {'count': 0, 'size': 0},
            'Important': {'count': 0, 'size': 0}
        }
        self.files_by_category = {
            'Safe': [],
            'Less Important': [],
            'Important': []
        }
        self.protected_files = []
        self.backup_recommended = False


class ConfirmationDialog:
    """Base class for confirmation dialogs with modern dark theme."""
    
    def __init__(self, parent, title: str):
        self.parent = parent
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure modern dark styling
        configure_modern_styles()
        self.dialog.configure(bg=ModernColors.BACKGROUND)
        
        # Center dialog on parent
        self.dialog.geometry("600x400")
        self._center_dialog()
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - self.dialog.winfo_width()) // 2
        y = parent_y + (parent_height - self.dialog.winfo_height()) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        self._center_dialog()
        
        # Make dialog modal
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
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
        
    def _on_cancel(self):
        """Handle dialog cancellation."""
        self.result = False
        self.dialog.destroy()
        
    def show(self):
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class InitialConfirmationDialog(ConfirmationDialog):
    """First confirmation dialog showing deletion summary."""
    
    def __init__(self, parent, summary: DeletionSummary, 
                 modify_callback: Optional[Callable] = None):
        super().__init__(parent, "Confirm File Deletion")
        self.summary = summary
        self.modify_callback = modify_callback
        self._create_widgets()
        
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="⚠️", font=("Arial", 24)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Review Files for Deletion", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Summary information
        self._create_summary_section(main_frame)
        
        # Category breakdown
        self._create_category_section(main_frame)
        
        # Buttons
        self._create_buttons(main_frame)
        
    def _create_summary_section(self, parent):
        """Create summary information section."""
        summary_frame = ttk.LabelFrame(parent, text="Deletion Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(summary_frame, 
                 text=f"Total Files: {self.summary.total_files:,}").pack(anchor=tk.W)
        ttk.Label(summary_frame, 
                 text=f"Total Size: {self._format_size(self.summary.total_size)}").pack(anchor=tk.W)
        
        if self.summary.protected_files:
            ttk.Label(summary_frame, 
                     text=f"Protected Files (will be skipped): {len(self.summary.protected_files)}",
                     foreground="orange").pack(anchor=tk.W)
            
    def _create_category_section(self, parent):
        """Create category breakdown section."""
        category_frame = ttk.LabelFrame(parent, text="Files by Category", padding="10")
        category_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create treeview for category display
        tree = ttk.Treeview(category_frame, columns=("count", "size"), height=6)
        tree.heading("#0", text="Category")
        tree.heading("count", text="File Count")
        tree.heading("size", text="Total Size")
        
        tree.column("#0", width=200)
        tree.column("count", width=100)
        tree.column("size", width=150)
        
        # Add category data
        for category, data in self.summary.categories.items():
            if data['count'] > 0:
                tree.insert("", tk.END, text=category,
                           values=(f"{data['count']:,}", 
                                  self._format_size(data['size'])))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(category_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_buttons(self, parent):
        """Create dialog buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        if self.modify_callback:
            ttk.Button(button_frame, text="Modify Selection", 
                      command=self._on_modify).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Continue", 
                  command=self._on_continue).pack(side=tk.RIGHT)
        
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
        
    def _on_modify(self):
        """Handle modify selection button."""
        if self.modify_callback:
            self.result = "modify"
            self.dialog.destroy()
            
    def _on_continue(self):
        """Handle continue button."""
        self.result = True
        self.dialog.destroy()


class BackupDialog(ConfirmationDialog):
    """Dialog for backup options for important files."""
    
    def __init__(self, parent, important_files: List[Path]):
        super().__init__(parent, "Backup Important Files")
        self.important_files = important_files
        self.backup_location = None
        self._create_widgets()
        
    def _create_widgets(self):
        """Create backup dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and explanation
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="💾", font=("Arial", 24)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Backup Important Files", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Explanation text
        explanation = ttk.Label(main_frame, 
                               text=f"We found {len(self.important_files)} files marked as 'Important'.\n"
                                   "Would you like to create a backup before deletion?",
                               wraplength=500)
        explanation.pack(pady=(0, 15))
        
        # Backup location selection
        location_frame = ttk.LabelFrame(main_frame, text="Backup Location", padding="10")
        location_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.location_var = tk.StringVar()
        location_entry = ttk.Entry(location_frame, textvariable=self.location_var, width=50)
        location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(location_frame, text="Browse...", 
                  command=self._browse_location).pack(side=tk.RIGHT, padx=(10, 0))
        
        # File list preview
        files_frame = ttk.LabelFrame(main_frame, text="Files to Backup", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create listbox with scrollbar
        listbox_frame = ttk.Frame(files_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(listbox_frame, height=8)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                 command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Add files to listbox
        for file_path in self.important_files[:20]:  # Show first 20
            self.file_listbox.insert(tk.END, str(file_path))
            
        if len(self.important_files) > 20:
            self.file_listbox.insert(tk.END, f"... and {len(self.important_files) - 20} more files")
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        self._create_backup_buttons(main_frame)
        
    def _create_backup_buttons(self, parent):
        """Create backup dialog buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Skip Backup", 
                  command=self._on_skip_backup).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Create Backup", 
                  command=self._on_create_backup).pack(side=tk.RIGHT)
        
    def _browse_location(self):
        """Browse for backup location."""
        location = filedialog.askdirectory(
            title="Select Backup Location",
            initialdir=str(Path.home())
        )
        if location:
            self.location_var.set(location)
            
    def _on_skip_backup(self):
        """Handle skip backup button."""
        # Show additional confirmation for skipping backup
        response = messagebox.askyesno(
            "Skip Backup Confirmation",
            "Are you sure you want to skip backing up important files?\n\n"
            "These files will be permanently deleted and cannot be recovered.",
            icon="warning"
        )
        if response:
            self.result = "skip"
            self.dialog.destroy()
            
    def _on_create_backup(self):
        """Handle create backup button."""
        if not self.location_var.get():
            messagebox.showerror("Error", "Please select a backup location.")
            return
            
        self.backup_location = Path(self.location_var.get())
        if not self.backup_location.exists():
            try:
                self.backup_location.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create backup directory: {e}")
                return
                
        self.result = "backup"
        self.dialog.destroy()


class FinalConfirmationDialog(ConfirmationDialog):
    """Final 'point of no return' confirmation dialog."""
    
    def __init__(self, parent, summary: DeletionSummary):
        super().__init__(parent, "Final Confirmation - Point of No Return")
        self.summary = summary
        self.confirmation_text = ""
        self._create_widgets()
        
    def _create_widgets(self):
        """Create final confirmation widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning header
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(warning_frame, text="🚨", font=("Arial", 32)).pack(side=tk.LEFT)
        warning_label = ttk.Label(warning_frame, 
                                 text="FINAL WARNING - POINT OF NO RETURN", 
                                 font=("Arial", 16, "bold"),
                                 foreground="red")
        warning_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Explanation of secure deletion
        explanation_frame = ttk.LabelFrame(main_frame, text="What is Secure Deletion?", 
                                          padding="15")
        explanation_frame.pack(fill=tk.X, pady=(0, 15))
        
        explanation_text = (
            "Secure deletion permanently overwrites your files multiple times, "
            "making them unrecoverable even with specialized data recovery tools. "
            "This process cannot be undone.\n\n"
            "Regular deletion only removes file references - secure deletion "
            "destroys the actual data."
        )
        
        ttk.Label(explanation_frame, text=explanation_text, 
                 wraplength=500, justify=tk.LEFT).pack()
        
        # Final summary
        summary_frame = ttk.LabelFrame(main_frame, text="Final Summary", padding="15")
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(summary_frame, 
                 text=f"Files to be PERMANENTLY DELETED: {self.summary.total_files:,}",
                 font=("Arial", 12, "bold"),
                 foreground="red").pack(anchor=tk.W)
        ttk.Label(summary_frame, 
                 text=f"Total size: {self._format_size(self.summary.total_size)}",
                 font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Typed confirmation
        confirm_frame = ttk.LabelFrame(main_frame, text="Type Confirmation", padding="15")
        confirm_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(confirm_frame, 
                 text='Type "DELETE PERMANENTLY" to confirm (case sensitive):').pack(anchor=tk.W)
        
        self.confirm_var = tk.StringVar()
        self.confirm_entry = ttk.Entry(confirm_frame, textvariable=self.confirm_var, 
                                      font=("Arial", 12), width=30)
        self.confirm_entry.pack(pady=(10, 0))
        self.confirm_entry.bind('<KeyRelease>', self._on_text_change)
        
        # Buttons
        self._create_final_buttons(main_frame)
        
    def _create_final_buttons(self, parent):
        """Create final confirmation buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        self.delete_button = ttk.Button(button_frame, text="DELETE PERMANENTLY", 
                                       command=self._on_delete, state=tk.DISABLED)
        self.delete_button.pack(side=tk.RIGHT)
        
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
        
    def _on_text_change(self, event=None):
        """Handle confirmation text changes."""
        if self.confirm_var.get() == "DELETE PERMANENTLY":
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)
            
    def _on_delete(self):
        """Handle delete button."""
        if self.confirm_var.get() == "DELETE PERMANENTLY":
            self.result = True
            self.dialog.destroy()


class ConfirmationController:
    """Controller for managing the multi-stage confirmation process."""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.logger = get_logger(__name__)
        
    def run_confirmation_flow(self, summary: DeletionSummary, 
                            modify_callback: Optional[Callable] = None) -> Dict:
        """
        Run the complete confirmation flow.
        
        Returns:
            Dict with keys: 'confirmed', 'backup_location', 'backup_files'
        """
        result = {
            'confirmed': False,
            'backup_location': None,
            'backup_files': []
        }
        
        try:
            # Stage 1: Initial confirmation with summary
            initial_dialog = InitialConfirmationDialog(self.parent, summary, modify_callback)
            initial_result = initial_dialog.show()
            
            if initial_result == "modify":
                result['confirmed'] = "modify"
                return result
            elif not initial_result:
                return result
                
            # Stage 2: Backup dialog for important files
            important_files = summary.files_by_category.get('Important', [])
            if important_files:
                backup_dialog = BackupDialog(self.parent, important_files)
                backup_result = backup_dialog.show()
                
                if not backup_result:
                    return result
                elif backup_result == "backup":
                    result['backup_location'] = backup_dialog.backup_location
                    result['backup_files'] = important_files
                # If "skip", continue without backup
                
            # Stage 3: Final confirmation
            final_dialog = FinalConfirmationDialog(self.parent, summary)
            final_result = final_dialog.show()
            
            if final_result:
                result['confirmed'] = True
                self.logger.info("User completed confirmation flow for secure deletion")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in confirmation flow: {e}")
            messagebox.showerror("Error", f"An error occurred during confirmation: {e}")
            return result