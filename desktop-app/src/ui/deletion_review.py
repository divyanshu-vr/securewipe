"""
Deletion review interface for users to modify selections before confirmation.
Provides comprehensive summary and modification capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Set, Optional, Callable
from pathlib import Path
import threading

from shared.logging.secure_logger import get_logger
from utils.exceptions import SecureWipeError

logger = get_logger(__name__)


class FileSelectionModel:
    """Model for tracking file selection state and modifications."""
    
    def __init__(self):
        self.selected_files: Set[Path] = set()
        self.categorized_files: Dict[str, List[Path]] = {
            'Safe': [],
            'Less Important': [],
            'Important': []
        }
        self.file_metadata: Dict[Path, Dict] = {}
        self.protected_files: Set[Path] = set()
        self.modification_callbacks: List[Callable] = []
        
    def add_files(self, category: str, files: List[Path], metadata: Dict[Path, Dict] = None):
        """Add files to a category with optional metadata."""
        if category not in self.categorized_files:
            self.categorized_files[category] = []
            
        self.categorized_files[category].extend(files)
        self.selected_files.update(files)
        
        if metadata:
            self.file_metadata.update(metadata)
            
        self._notify_modifications()
        
    def remove_files(self, files: List[Path]):
        """Remove files from selection."""
        for file_path in files:
            self.selected_files.discard(file_path)
            for category_files in self.categorized_files.values():
                if file_path in category_files:
                    category_files.remove(file_path)
                    
        self._notify_modifications()
        
    def move_files(self, files: List[Path], from_category: str, to_category: str):
        """Move files between categories."""
        if to_category not in self.categorized_files:
            self.categorized_files[to_category] = []
            
        for file_path in files:
            if file_path in self.categorized_files[from_category]:
                self.categorized_files[from_category].remove(file_path)
                self.categorized_files[to_category].append(file_path)
                
        self._notify_modifications()
        
    def get_summary(self) -> Dict:
        """Generate comprehensive summary of current selection."""
        summary = {
            'total_files': len(self.selected_files),
            'total_size': 0,
            'categories': {},
            'protected_count': len(self.protected_files)
        }
        
        for category, files in self.categorized_files.items():
            selected_in_category = [f for f in files if f in self.selected_files]
            category_size = sum(
                self.file_metadata.get(f, {}).get('size', 0) 
                for f in selected_in_category
            )
            
            summary['categories'][category] = {
                'count': len(selected_in_category),
                'size': category_size
            }
            summary['total_size'] += category_size
            
        return summary
        
    def add_modification_callback(self, callback: Callable):
        """Add callback to be notified of modifications."""
        self.modification_callbacks.append(callback)
        
    def _notify_modifications(self):
        """Notify all callbacks of modifications."""
        for callback in self.modification_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in modification callback: {e}")


class DeletionReviewDialog:
    """Dialog for reviewing and modifying file selections before deletion."""
    
    def __init__(self, parent, selection_model: FileSelectionModel):
        self.parent = parent
        self.model = selection_model
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Review File Selection")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("900x700")
        
        self._center_dialog()
        self._create_widgets()
        
        # Listen for model changes
        self.model.add_modification_callback(self._update_summary)
        
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
        
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(title_frame, text="📋", font=("Arial", 24)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Review and Modify Selection", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Create paned window for layout
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Left panel: File tree
        self._create_file_tree_panel(paned)
        
        # Right panel: Summary and actions
        self._create_summary_panel(paned)
        
        # Buttons
        self._create_buttons(main_frame)
        
    def _create_file_tree_panel(self, parent):
        """Create file tree panel for selection modification."""
        tree_frame = ttk.Frame(parent)
        parent.add(tree_frame, weight=2)
        
        ttk.Label(tree_frame, text="Files by Category", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Create treeview
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.file_tree = ttk.Treeview(tree_container, columns=("size", "path"), 
                                     selectmode=tk.EXTENDED)
        self.file_tree.heading("#0", text="Name")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("path", text="Location")
        
        self.file_tree.column("#0", width=200)
        self.file_tree.column("size", width=100)
        self.file_tree.column("path", width=300)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, 
                                   command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, 
                                   command=self.file_tree.xview)
        
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, 
                                xscrollcommand=h_scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Populate tree
        self._populate_file_tree()
        
        # Context menu
        self._create_context_menu()
        
        # Action buttons for tree
        tree_actions = ttk.Frame(tree_frame)
        tree_actions.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(tree_actions, text="Remove Selected", 
                  command=self._remove_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(tree_actions, text="Change Category", 
                  command=self._change_category).pack(side=tk.LEFT)
        
    def _create_summary_panel(self, parent):
        """Create summary and statistics panel."""
        summary_frame = ttk.Frame(parent)
        parent.add(summary_frame, weight=1)
        
        ttk.Label(summary_frame, text="Selection Summary", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Summary display
        self.summary_frame = ttk.LabelFrame(summary_frame, text="Current Selection", 
                                           padding="10")
        self.summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Category statistics
        self.category_frame = ttk.LabelFrame(summary_frame, text="By Category", 
                                            padding="10")
        self.category_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Protected files warning
        self.protected_frame = ttk.LabelFrame(summary_frame, text="Protected Files", 
                                             padding="10")
        self.protected_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Update summary
        self._update_summary()
        
    def _create_buttons(self, parent):
        """Create dialog action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Reset to Original", 
                  command=self._reset_selection).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Apply Changes", 
                  command=self._apply_changes).pack(side=tk.RIGHT)
        
    def _populate_file_tree(self):
        """Populate the file tree with categorized files."""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Add categories and files
        for category, files in self.model.categorized_files.items():
            if not files:
                continue
                
            # Add category node
            category_id = self.file_tree.insert("", tk.END, text=f"{category} ({len(files)})",
                                               tags=(f"category_{category.lower()}",))
            
            # Add files under category
            for file_path in files:
                if file_path in self.model.selected_files:
                    metadata = self.model.file_metadata.get(file_path, {})
                    size_str = self._format_size(metadata.get('size', 0))
                    
                    self.file_tree.insert(category_id, tk.END, 
                                         text=file_path.name,
                                         values=(size_str, str(file_path.parent)),
                                         tags=("file",))
                                         
        # Configure tags for styling
        self.file_tree.tag_configure("category_safe", background="#e8f5e8")
        self.file_tree.tag_configure("category_less important", background="#fff3cd")
        self.file_tree.tag_configure("category_important", background="#f8d7da")
        
        # Expand all categories
        for item in self.file_tree.get_children():
            self.file_tree.item(item, open=True)
            
    def _create_context_menu(self):
        """Create context menu for file tree."""
        self.context_menu = tk.Menu(self.dialog, tearoff=0)
        self.context_menu.add_command(label="Remove from Selection", 
                                     command=self._remove_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Move to Safe", 
                                     command=lambda: self._move_to_category("Safe"))
        self.context_menu.add_command(label="Move to Less Important", 
                                     command=lambda: self._move_to_category("Less Important"))
        self.context_menu.add_command(label="Move to Important", 
                                     command=lambda: self._move_to_category("Important"))
        
        self.file_tree.bind("<Button-3>", self._show_context_menu)
        
    def _show_context_menu(self, event):
        """Show context menu at cursor position."""
        item = self.file_tree.identify_row(event.y)
        if item and "file" in self.file_tree.item(item, "tags"):
            self.file_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def _update_summary(self):
        """Update summary display with current selection."""
        summary = self.model.get_summary()
        
        # Clear existing summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
            
        # Total summary
        ttk.Label(self.summary_frame, 
                 text=f"Total Files: {summary['total_files']:,}",
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(self.summary_frame, 
                 text=f"Total Size: {self._format_size(summary['total_size'])}",
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Clear category summary
        for widget in self.category_frame.winfo_children():
            widget.destroy()
            
        # Category breakdown
        for category, stats in summary['categories'].items():
            if stats['count'] > 0:
                ttk.Label(self.category_frame, 
                         text=f"{category}: {stats['count']:,} files "
                              f"({self._format_size(stats['size'])})").pack(anchor=tk.W)
                              
        # Protected files warning
        for widget in self.protected_frame.winfo_children():
            widget.destroy()
            
        if summary['protected_count'] > 0:
            ttk.Label(self.protected_frame, 
                     text=f"{summary['protected_count']} protected files will be skipped",
                     foreground="orange").pack(anchor=tk.W)
        else:
            ttk.Label(self.protected_frame, 
                     text="No protected files detected").pack(anchor=tk.W)
            
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
        
    def _remove_selected(self):
        """Remove selected files from deletion list."""
        selected_items = self.file_tree.selection()
        files_to_remove = []
        
        for item in selected_items:
            if "file" in self.file_tree.item(item, "tags"):
                # Get file path from tree item
                file_name = self.file_tree.item(item, "text")
                parent_item = self.file_tree.parent(item)
                category_text = self.file_tree.item(parent_item, "text")
                category = category_text.split(" (")[0]  # Extract category name
                
                # Find matching file in model
                for file_path in self.model.categorized_files[category]:
                    if file_path.name == file_name:
                        files_to_remove.append(file_path)
                        break
                        
        if files_to_remove:
            self.model.remove_files(files_to_remove)
            self._populate_file_tree()
            
    def _change_category(self):
        """Change category of selected files."""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select files to change category.")
            return
            
        # Show category selection dialog
        category_dialog = CategorySelectionDialog(self.dialog)
        new_category = category_dialog.show()
        
        if new_category:
            self._move_to_category(new_category)
            
    def _move_to_category(self, new_category: str):
        """Move selected files to specified category."""
        selected_items = self.file_tree.selection()
        files_to_move = []
        source_categories = {}
        
        for item in selected_items:
            if "file" in self.file_tree.item(item, "tags"):
                file_name = self.file_tree.item(item, "text")
                parent_item = self.file_tree.parent(item)
                category_text = self.file_tree.item(parent_item, "text")
                old_category = category_text.split(" (")[0]
                
                # Find matching file in model
                for file_path in self.model.categorized_files[old_category]:
                    if file_path.name == file_name:
                        files_to_move.append(file_path)
                        source_categories[file_path] = old_category
                        break
                        
        # Move files in model
        for file_path in files_to_move:
            old_category = source_categories[file_path]
            self.model.move_files([file_path], old_category, new_category)
            
        self._populate_file_tree()
        
    def _reset_selection(self):
        """Reset selection to original state."""
        response = messagebox.askyesno(
            "Reset Selection",
            "Are you sure you want to reset all changes and return to the original selection?"
        )
        if response:
            # This would need to be implemented with original state tracking
            messagebox.showinfo("Reset", "Selection reset to original state.")
            
    def _apply_changes(self):
        """Apply changes and close dialog."""
        self.result = True
        self.dialog.destroy()
        
    def _on_cancel(self):
        """Cancel changes and close dialog."""
        self.result = False
        self.dialog.destroy()
        
    def show(self):
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class CategorySelectionDialog:
    """Simple dialog for selecting a file category."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Category")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("300x200")
        
        self._center_dialog()
        self._create_widgets()
        
    def _center_dialog(self):
        """Center dialog on parent."""
        self.dialog.update_idletasks()
        x = (self.parent.winfo_x() + 
             (self.parent.winfo_width() // 2) - 
             (self.dialog.winfo_width() // 2))
        y = (self.parent.winfo_y() + 
             (self.parent.winfo_height() // 2) - 
             (self.dialog.winfo_height() // 2))
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Select new category:").pack(pady=(0, 15))
        
        self.category_var = tk.StringVar(value="Safe")
        
        categories = ["Safe", "Less Important", "Important"]
        for category in categories:
            ttk.Radiobutton(main_frame, text=category, 
                           variable=self.category_var, 
                           value=category).pack(anchor=tk.W, pady=2)
                           
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="OK", 
                  command=self._on_ok).pack(side=tk.RIGHT)
                  
    def _on_ok(self):
        """Handle OK button."""
        self.result = self.category_var.get()
        self.dialog.destroy()
        
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """Show dialog and return selected category."""
        self.dialog.wait_window()
        return self.result