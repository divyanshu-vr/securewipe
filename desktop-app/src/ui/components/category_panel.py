"""Category display and management UI component."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, Dict, List, Optional

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

from shared.models.file_info import FileInfo

from shared.secure_logging.secure_logger import get_logger

# Import categorizer
sys.path.append(str(Path(__file__).parent.parent.parent))
from scanner.categorizer import CategoryType, FileCategorizer

logger = get_logger(__name__)


class CategoryPanel(ttk.Frame):
    """UI panel for displaying and managing file categories."""

    def __init__(self, parent, categorizer: FileCategorizer, **kwargs):
        super().__init__(parent, **kwargs)
        self.categorizer = categorizer
        self.files: List[FileInfo] = []
        self.selected_files: List[FileInfo] = []
        self.category_change_callback: Optional[Callable] = None

        # Category colors
        self.category_colors = {
            CategoryType.SAFE: "#90EE90",  # Light green
            CategoryType.LESS_IMPORTANT: "#FFD700",  # Gold
            CategoryType.IMPORTANT: "#FFB6C1",  # Light pink
        }

        self._setup_ui()

    def _setup_ui(self):
        """Setup the category panel UI."""
        # Category legend
        legend_frame = ttk.LabelFrame(self, text="Category Legend", padding=5)
        legend_frame.pack(fill="x", padx=5, pady=5)

        # Safe category
        safe_frame = ttk.Frame(legend_frame)
        safe_frame.pack(fill="x", pady=2)
        safe_color = tk.Label(
            safe_frame, bg=self.category_colors[CategoryType.SAFE], width=3, height=1
        )
        safe_color.pack(side="left", padx=5)
        ttk.Label(
            safe_frame,
            text="Safe to Delete - Files that can be removed without data loss",
        ).pack(side="left")

        # Less important category
        less_frame = ttk.Frame(legend_frame)
        less_frame.pack(fill="x", pady=2)
        less_color = tk.Label(
            less_frame,
            bg=self.category_colors[CategoryType.LESS_IMPORTANT],
            width=3,
            height=1,
        )
        less_color.pack(side="left", padx=5)
        ttk.Label(
            less_frame, text="Less Important - User files that may have value"
        ).pack(side="left")

        # Important category
        important_frame = ttk.Frame(legend_frame)
        important_frame.pack(fill="x", pady=2)
        important_color = tk.Label(
            important_frame,
            bg=self.category_colors[CategoryType.IMPORTANT],
            width=3,
            height=1,
        )
        important_color.pack(side="left", padx=5)
        ttk.Label(
            important_frame, text="Important - System files and applications"
        ).pack(side="left")

        # File list with categories
        list_frame = ttk.LabelFrame(self, text="Files by Category", padding=5)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview for file display
        columns = ("Name", "Size", "Category", "Explanation")
        self.file_tree = ttk.Treeview(
            list_frame, columns=columns, show="tree headings", height=15
        )

        # Configure columns
        self.file_tree.heading("#0", text="Path")
        self.file_tree.column("#0", width=200)

        for col in columns:
            self.file_tree.heading(col, text=col)
            if col == "Size":
                self.file_tree.column(col, width=80, anchor="e")
            elif col == "Category":
                self.file_tree.column(col, width=120)
            else:
                self.file_tree.column(col, width=300)

        # Scrollbars
        v_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.file_tree.yview
        )
        h_scroll = ttk.Scrollbar(
            list_frame, orient="horizontal", command=self.file_tree.xview
        )
        self.file_tree.configure(
            yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set
        )

        # Pack treeview and scrollbars
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(
            button_frame, text="Change Category", command=self._change_category
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Bulk Change", command=self._bulk_change_category
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Reset Override", command=self._reset_override
        ).pack(side="left", padx=5)

        # Statistics
        self.stats_label = ttk.Label(self, text="No files loaded")
        self.stats_label.pack(pady=5)

        # Bind selection events
        self.file_tree.bind("<<TreeviewSelect>>", self._on_selection_change)

    def update_files(self, files: List[FileInfo]):
        """Update the file list and categorize files."""
        self.files = files
        self._refresh_display()

    def _refresh_display(self):
        """Refresh the file display with current categorization."""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # Categorize and display files
        category_counts = {cat: 0 for cat in CategoryType}

        for file_info in self.files:
            try:
                # Categorize file
                result = self.categorizer.categorize_file(file_info)

                # Update file info with category
                file_info.category = result.category.value
                file_info.category_reason = result.reason.value
                file_info.category_explanation = result.explanation

                # Format size
                size_str = self._format_size(file_info.size)

                # Insert into tree
                item_id = self.file_tree.insert(
                    "",
                    "end",
                    text=str(file_info.path.parent),
                    values=(
                        file_info.name,
                        size_str,
                        result.category.value.title(),
                        result.explanation,
                    ),
                )

                # Set background color based on category
                self.file_tree.set(item_id, "category_type", result.category.value)

                # Update counts
                category_counts[result.category] += 1

            except Exception as e:
                logger.error(f"Error displaying file {file_info.path}: {str(e)}")

        # Update statistics
        total_files = len(self.files)
        stats_text = (
            f"Total: {total_files} files | "
            f"Safe: {category_counts[CategoryType.SAFE]} | "
            f"Less Important: {category_counts[CategoryType.LESS_IMPORTANT]} | "
            f"Important: {category_counts[CategoryType.IMPORTANT]}"
        )
        self.stats_label.config(text=stats_text)

        # Apply colors to rows
        self._apply_row_colors()

    def _apply_row_colors(self):
        """Apply background colors to rows based on category."""
        for item in self.file_tree.get_children():
            values = self.file_tree.item(item, "values")
            if len(values) >= 3:
                category_name = values[2].lower()
                for cat_type in CategoryType:
                    if cat_type.value == category_name:
                        # Note: tkinter treeview doesn't support row background colors easily
                        # This would require custom styling or tags
                        break

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _on_selection_change(self, event):
        """Handle file selection changes."""
        selected_items = self.file_tree.selection()
        self.selected_files = []

        for item in selected_items:
            values = self.file_tree.item(item, "values")
            if values:
                # Find corresponding file info
                file_name = values[0]
                for file_info in self.files:
                    if file_info.name == file_name:
                        self.selected_files.append(file_info)
                        break

    def _change_category(self):
        """Change category for selected files."""
        if not self.selected_files:
            messagebox.showwarning(
                "No Selection", "Please select files to change category."
            )
            return

        # Show category selection dialog
        category = self._show_category_dialog()
        if category:
            self._apply_category_change(self.selected_files, category)

    def _bulk_change_category(self):
        """Bulk change category for multiple files."""
        if not self.files:
            messagebox.showwarning(
                "No Files", "No files available for bulk operations."
            )
            return

        # Show bulk change dialog
        result = self._show_bulk_change_dialog()
        if result:
            filter_category, new_category = result

            # Filter files by current category
            filtered_files = [
                f for f in self.files if f.category == filter_category.value
            ]

            if filtered_files:
                if messagebox.askyesno(
                    "Confirm Bulk Change",
                    f"Change category for {len(filtered_files)} files from "
                    f"{filter_category.value.title()} to {new_category.value.title()}?",
                ):
                    self._apply_category_change(filtered_files, new_category)
            else:
                messagebox.showinfo(
                    "No Files",
                    f"No files found in {filter_category.value.title()} category.",
                )

    def _reset_override(self):
        """Reset user overrides for selected files."""
        if not self.selected_files:
            messagebox.showwarning(
                "No Selection", "Please select files to reset overrides."
            )
            return

        if messagebox.askyesno(
            "Confirm Reset",
            f"Reset category overrides for {len(self.selected_files)} selected files?",
        ):
            for file_info in self.selected_files:
                self.categorizer.remove_user_override(file_info.path)

            self._refresh_display()

            if self.category_change_callback:
                self.category_change_callback()

    def _show_category_dialog(self) -> Optional[CategoryType]:
        """Show dialog for category selection."""
        dialog = tk.Toplevel(self)
        dialog.title("Change Category")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()

        selected_category = None

        ttk.Label(dialog, text="Select new category:").pack(pady=10)

        category_var = tk.StringVar()

        for category in CategoryType:
            ttk.Radiobutton(
                dialog,
                text=category.value.title(),
                variable=category_var,
                value=category.value,
            ).pack(anchor="w", padx=20)

        def on_ok():
            nonlocal selected_category
            if category_var.get():
                selected_category = CategoryType(category_var.get())
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(
            side="left", padx=5
        )

        dialog.wait_window()
        return selected_category

    def _show_bulk_change_dialog(self) -> Optional[tuple]:
        """Show dialog for bulk category changes."""
        dialog = tk.Toplevel(self)
        dialog.title("Bulk Change Categories")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()

        result = None

        ttk.Label(dialog, text="Change all files from:").pack(pady=5)
        from_var = tk.StringVar()
        from_combo = ttk.Combobox(
            dialog,
            textvariable=from_var,
            values=[cat.value.title() for cat in CategoryType],
        )
        from_combo.pack(pady=5)

        ttk.Label(dialog, text="To:").pack(pady=5)
        to_var = tk.StringVar()
        to_combo = ttk.Combobox(
            dialog,
            textvariable=to_var,
            values=[cat.value.title() for cat in CategoryType],
        )
        to_combo.pack(pady=5)

        def on_ok():
            nonlocal result
            if from_var.get() and to_var.get():
                from_cat = CategoryType(from_var.get().lower())
                to_cat = CategoryType(to_var.get().lower())
                result = (from_cat, to_cat)
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(
            side="left", padx=5
        )

        dialog.wait_window()
        return result

    def _apply_category_change(self, files: List[FileInfo], new_category: CategoryType):
        """Apply category change to files."""
        explanation = f"User changed category to {new_category.value.title()}"

        for file_info in files:
            self.categorizer.set_user_override(
                file_info.path, new_category, explanation
            )

        self._refresh_display()

        if self.category_change_callback:
            self.category_change_callback()

        messagebox.showinfo(
            "Category Changed",
            f"Changed category for {len(files)} files to {new_category.value.title()}",
        )

    def set_category_change_callback(self, callback: Callable):
        """Set callback for category changes."""
        self.category_change_callback = callback
