"""File tree component for displaying scan results."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Dict

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

try:
    from shared.models.file_info import FileInfo, FileType
except ImportError:
    # Fallback for testing
    from dataclasses import dataclass
    from datetime import datetime
    from enum import Enum

    class FileType(Enum):
        DOCUMENT = "document"
        IMAGE = "image"
        VIDEO = "video"
        AUDIO = "audio"
        ARCHIVE = "archive"
        EXECUTABLE = "executable"
        OTHER = "other"

    @dataclass
    class FileInfo:
        path: Path
        size: int
        modified_date: datetime
        file_type: FileType
        is_accessible: bool = True


class FileTreeView(ttk.Frame):
    """Tree view component for displaying files with progressive updates."""

    def __init__(self, parent, **kwargs):
        """Initialize file tree view."""
        super().__init__(parent, **kwargs)

        self._setup_ui()
        self._file_nodes: Dict[str, str] = {}  # path -> tree_id mapping
        self._directory_nodes: Dict[str, str] = {}  # path -> tree_id mapping
        self._file_count_by_type: Dict[FileType, int] = {}
        self._total_size_by_type: Dict[FileType, int] = {}

        # Initialize counters
        for file_type in FileType:
            self._file_count_by_type[file_type] = 0
            self._total_size_by_type[file_type] = 0

    def _setup_ui(self):
        """Setup the tree view UI."""
        # Create main frame with scrollbars
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tree view with columns
        columns = ("size", "type", "modified", "status")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="tree headings")

        # Configure columns
        self.tree.heading("#0", text="File/Directory")
        self.tree.heading("size", text="Size")
        self.tree.heading("type", text="Type")
        self.tree.heading("modified", text="Modified")
        self.tree.heading("status", text="Status")

        # Column widths
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("size", width=100, minwidth=80)
        self.tree.column("type", width=100, minwidth=80)
        self.tree.column("modified", width=150, minwidth=120)
        self.tree.column("status", width=100, minwidth=80)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            main_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            main_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Summary frame
        summary_frame = ttk.LabelFrame(self, text="Summary by Type")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)

        # Summary tree
        summary_columns = ("count", "total_size")
        self.summary_tree = ttk.Treeview(
            summary_frame, columns=summary_columns, show="tree headings", height=8
        )

        self.summary_tree.heading("#0", text="File Type")
        self.summary_tree.heading("count", text="Count")
        self.summary_tree.heading("total_size", text="Total Size")

        self.summary_tree.column("#0", width=150)
        self.summary_tree.column("count", width=100)
        self.summary_tree.column("total_size", width=150)

        self.summary_tree.pack(fill=tk.X, padx=5, pady=5)

        # Initialize summary rows
        self._summary_nodes = {}
        for file_type in FileType:
            node_id = self.summary_tree.insert(
                "", "end", text=file_type.value.title(), values=("0", "0 MB")
            )
            self._summary_nodes[file_type] = node_id

    def add_file(self, file_info: FileInfo):
        """Add a file to the tree view progressively."""
        try:
            # Ensure parent directories exist
            parent_id = self._ensure_directory_path(file_info.path.parent)

            # Format file information
            size_str = self._format_size(file_info.size)
            type_str = file_info.file_type.value.title()
            modified_str = file_info.modified_date.strftime("%Y-%m-%d %H:%M")
            status_str = "OK" if file_info.is_accessible else "Error"

            # Add file node
            file_id = self.tree.insert(
                parent_id,
                "end",
                text=file_info.name,
                values=(size_str, type_str, modified_str, status_str),
            )

            # Store mapping
            self._file_nodes[str(file_info.path)] = file_id

            # Update counters
            self._file_count_by_type[file_info.file_type] += 1
            self._total_size_by_type[file_info.file_type] += file_info.size

            # Update summary (batch updates for performance)
            if self._file_count_by_type[file_info.file_type] % 10 == 0:
                self._update_summary_for_type(file_info.file_type)

        except Exception as e:
            # Handle errors gracefully
            print(f"Error adding file {file_info.path}: {e}")

    def _ensure_directory_path(self, directory: Path) -> str:
        """Ensure all parent directories exist in tree and return the final parent ID."""
        if str(directory) in self._directory_nodes:
            return self._directory_nodes[str(directory)]

        # Handle root case
        if directory.parent == directory:
            # This is a root directory
            dir_id = self.tree.insert(
                "", "end", text=str(directory), values=("", "Directory", "", "")
            )
            self._directory_nodes[str(directory)] = dir_id
            return dir_id

        # Recursively ensure parent exists
        parent_id = self._ensure_directory_path(directory.parent)

        # Create this directory
        dir_id = self.tree.insert(
            parent_id, "end", text=directory.name, values=("", "Directory", "", "")
        )
        self._directory_nodes[str(directory)] = dir_id

        return dir_id

    def _update_summary_for_type(self, file_type: FileType):
        """Update summary display for a specific file type."""
        count = self._file_count_by_type[file_type]
        total_size = self._total_size_by_type[file_type]
        size_str = self._format_size(total_size)

        node_id = self._summary_nodes[file_type]
        self.summary_tree.item(node_id, values=(f"{count:,}", size_str))

    def update_all_summaries(self):
        """Update all summary displays (call at end of scan)."""
        for file_type in FileType:
            self._update_summary_for_type(file_type)

    def clear(self):
        """Clear all tree contents."""
        # Clear trees
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reset mappings and counters
        self._file_nodes.clear()
        self._directory_nodes.clear()

        for file_type in FileType:
            self._file_count_by_type[file_type] = 0
            self._total_size_by_type[file_type] = 0

        # Reset summary
        for file_type in FileType:
            node_id = self._summary_nodes[file_type]
            self.summary_tree.item(node_id, values=("0", "0 MB"))

    def _format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(size_bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"

    def get_statistics(self) -> Dict:
        """Get current tree statistics."""
        total_files = sum(self._file_count_by_type.values())
        total_size = sum(self._total_size_by_type.values())

        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_type": dict(self._file_count_by_type),
            "size_by_type": dict(self._total_size_by_type),
        }
