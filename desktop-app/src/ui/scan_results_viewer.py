"""
Comprehensive scan results viewer with modern UI.
Replaces simple popup with detailed file analysis and selection interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable
from pathlib import Path
import threading

from .modern_components import (
    ModernCard, ModernStats, ModernColors, ModernButton, configure_modern_styles
)


class FileTreeView(ttk.Frame):
    """Modern file tree view with category filtering and selection."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.files_by_category = {}
        self.selected_files = set()  # Will store file paths as strings
        self.selection_callback = None
        self.file_items = {}  # Track tree items for selection updates
        self.file_info_by_path = {}  # Map file paths to FileInfo objects
        
        self._create_layout()
    
    def _create_layout(self):
        """Create the tree view layout."""
        # Filter controls
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(filter_frame, text="Show categories:", 
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 8))
        
        # Category filters
        self.category_vars = {}
        categories = ['Safe', 'Less Important', 'Important', 'Protected']
        colors = {
            'Safe': ModernColors.SUCCESS,
            'Less Important': ModernColors.WARNING,
            'Important': ModernColors.INFO,
            'Protected': ModernColors.ERROR
        }
        
        for category in categories:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(filter_frame, text=category, 
                               variable=var, command=self._update_tree)
            cb.pack(side=tk.LEFT, padx=(0, 8))
            self.category_vars[category] = var
        
        # Selection controls
        select_frame = ttk.Frame(filter_frame)
        select_frame.pack(side=tk.RIGHT)
        
        ttk.Button(select_frame, text="Select All Safe", 
                  command=self._select_all_safe).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(select_frame, text="Clear Selection", 
                  command=self._clear_selection).pack(side=tk.LEFT)
        
        # Tree view with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure tree columns (include file_info for data storage and selection)
        columns = ('selected', 'size', 'category', 'path', 'file_info')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=12)
        
        # Configure headings (hide file_info column)
        self.tree.heading('#0', text='📁 File Name')
        self.tree.heading('selected', text='✓')
        self.tree.heading('size', text='📊 Size')
        self.tree.heading('category', text='🏷️ Category')
        self.tree.heading('path', text='📍 Location')
        
        # Configure column widths (hide file_info column)
        self.tree.column('#0', width=280, minwidth=200)
        self.tree.column('selected', width=40, minwidth=40, anchor='center')
        self.tree.column('size', width=100, minwidth=80)
        self.tree.column('category', width=120, minwidth=100)
        self.tree.column('path', width=320, minwidth=200)
        self.tree.column('file_info', width=0, minwidth=0)  # Hidden column for data
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection events
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        self.tree.bind('<Button-1>', self._on_click)
        self.tree.bind('<Double-Button-1>', self._on_double_click)
    
    def load_files(self, files_by_category: Dict[str, List]):
        """Load files into the tree view."""
        self.files_by_category = files_by_category
        
        # Build path to FileInfo mapping
        self.file_info_by_path.clear()
        for category, files in files_by_category.items():
            for file_info in files:
                file_path = str(file_info.path) if hasattr(file_info, 'path') else str(file_info)
                self.file_info_by_path[file_path] = file_info
        
        self._populate_tree()
    
    def _populate_tree(self):
        """Populate the tree with files."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Category colors
        colors = {
            'Safe': '#22c55e',
            'Less Important': '#f59e0b', 
            'Important': '#3b82f6',
            'Protected': '#ef4444'
        }
        
        # Add category nodes
        category_nodes = {}
        for category, files in self.files_by_category.items():
            if not self.category_vars.get(category, tk.BooleanVar(value=True)).get():
                continue
                
            if not files:
                continue
            
            # Create category node with icon
            total_size = sum(getattr(f, 'size', 0) for f in files)
            size_str = self._format_size(total_size)
            
            # Category icons
            category_icons = {
                'Safe': '✅',
                'Less Important': '⚠️',
                'Important': '🔶',
                'Protected': '🔒'
            }
            
            icon = category_icons.get(category, '📁')
            category_id = self.tree.insert('', 'end', 
                                         text=f"{icon} {category} ({len(files)} files)",
                                         values=('', size_str, category, '', ''),
                                         tags=(f'category_{category}',))
            category_nodes[category] = category_id
            
            # Configure category tag
            self.tree.tag_configure(f'category_{category}', 
                                  foreground=colors.get(category, ModernColors.FOREGROUND))
            
            # Add files under category
            for file_info in files[:100]:  # Limit to first 100 files for performance
                file_path = Path(file_info.path) if hasattr(file_info, 'path') else Path(str(file_info))
                file_size = getattr(file_info, 'size', 0)
                
                # File type icon
                file_icon = self._get_file_icon(file_path.suffix.lower())
                
                # Selection indicator
                file_path_str = str(file_path)
                selected_indicator = '☑️' if file_path_str in self.selected_files else '☐'
                
                file_id = self.tree.insert(category_id, 'end',
                                         text=f"{file_icon} {file_path.name}",
                                         values=(selected_indicator,
                                               self._format_size(file_size), 
                                               category, 
                                               str(file_path.parent),
                                               file_path_str),  # Store path string instead
                                         tags=(f'file_{category}',))
                
                # Track file items for updates
                self.file_items[file_path_str] = file_id
            
            # Show remaining count if truncated
            if len(files) > 100:
                self.tree.insert(category_id, 'end',
                               text=f"... and {len(files) - 100} more files",
                               values=('', '', ''),
                               tags=('truncated',))
        
        # Expand safe category by default
        if 'Safe' in category_nodes:
            self.tree.item(category_nodes['Safe'], open=True)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _get_file_icon(self, extension: str) -> str:
        """Get appropriate icon for file type."""
        icon_map = {
            # Documents
            '.pdf': '📄', '.doc': '📝', '.docx': '📝', '.txt': '📄',
            '.rtf': '📝', '.odt': '📝', '.pages': '📝',
            
            # Images
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
            '.bmp': '🖼️', '.svg': '🖼️', '.webp': '🖼️', '.ico': '🖼️',
            
            # Videos
            '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬', '.mov': '🎬',
            '.wmv': '🎬', '.flv': '🎬', '.webm': '🎬',
            
            # Audio
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵',
            '.ogg': '🎵', '.wma': '🎵',
            
            # Archives
            '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
            '.gz': '📦', '.bz2': '📦',
            
            # Code
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
            '.java': '☕', '.cpp': '⚙️', '.c': '⚙️', '.php': '🐘',
            
            # Executables
            '.exe': '⚙️', '.msi': '📦', '.app': '📱', '.deb': '📦',
            
            # Temporary/Cache
            '.tmp': '🗑️', '.temp': '🗑️', '.cache': '💾', '.log': '📋'
        }
        
        return icon_map.get(extension, '📄')
    
    def _update_tree(self):
        """Update tree display based on filter settings."""
        self._populate_tree()
    
    def _select_all_safe(self):
        """Select all files in the Safe category."""
        safe_files = self.files_by_category.get('Safe', [])
        for file_info in safe_files:
            file_path = str(file_info.path) if hasattr(file_info, 'path') else str(file_info)
            if file_path not in self.selected_files:
                self.selected_files.add(file_path)
                # Update visual indicator
                if file_path in self.file_items:
                    item_id = self.file_items[file_path]
                    current_values = list(self.tree.item(item_id, 'values'))
                    current_values[0] = '☑️'
                    self.tree.item(item_id, values=current_values)
        self._notify_selection_change()
    
    def _clear_selection(self):
        """Clear all selections."""
        # Update visual indicators
        for file_path in self.selected_files:
            if file_path in self.file_items:
                item_id = self.file_items[file_path]
                current_values = list(self.tree.item(item_id, 'values'))
                current_values[0] = '☐'
                self.tree.item(item_id, values=current_values)
        
        self.selected_files.clear()
        self._notify_selection_change()
    
    def _on_selection_change(self, event):
        """Handle tree selection changes."""
        # This is for visual selection in the tree
        pass
    
    def _on_click(self, event):
        """Handle tree item clicks for file selection."""
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)
        
        if not item:
            return
        
        # Get file path
        file_path = self.tree.set(item, 'file_info')
        if file_path:
            # Toggle selection on checkbox column or anywhere on the row
            if column == '#1' or column == '#0':  # Selected column or name column
                self._toggle_file_selection(file_path, item)
    
    def _on_double_click(self, event):
        """Handle double-click to expand/collapse categories."""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Check if it's a category item
        if not self.tree.set(item, 'file_info'):
            # Toggle category expansion
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)
    
    def _toggle_file_selection(self, file_path, item_id):
        """Toggle selection state of a file."""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            selected_indicator = '☐'
        else:
            self.selected_files.add(file_path)
            selected_indicator = '☑️'
        
        # Update the visual indicator
        current_values = list(self.tree.item(item_id, 'values'))
        current_values[0] = selected_indicator
        self.tree.item(item_id, values=current_values)
        
        self._notify_selection_change()
    
    def _select_less_important(self):
        """Select all files in the Less Important category."""
        less_important_files = self.files_by_category.get('Less Important', [])
        for file_info in less_important_files:
            file_path = str(file_info.path) if hasattr(file_info, 'path') else str(file_info)
            if file_path not in self.selected_files:
                self.selected_files.add(file_path)
                # Update visual indicator
                if file_path in self.file_items:
                    item_id = self.file_items[file_path]
                    current_values = list(self.tree.item(item_id, 'values'))
                    current_values[0] = '☑️'
                    self.tree.item(item_id, values=current_values)
        self._notify_selection_change()
    
    def _notify_selection_change(self):
        """Notify parent of selection changes."""
        if self.selection_callback:
            # Convert file paths back to FileInfo objects as a list
            selected_file_objects = []
            for file_path in self.selected_files:
                if file_path in self.file_info_by_path:
                    selected_file_objects.append(self.file_info_by_path[file_path])
            self.selection_callback(selected_file_objects)
    
    def set_selection_callback(self, callback: Callable):
        """Set callback for selection changes."""
        self.selection_callback = callback


class ScanResultsViewer(tk.Toplevel):
    """Comprehensive scan results viewer with modern UI."""
    
    def __init__(self, parent, scan_results: Dict, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure window with dark theme
        self.title("Scan Results - SecureWipe")
        self.geometry("1200x800")  # Larger default size
        self.resizable(True, True)
        self.minsize(1000, 700)  # Larger minimum size
        
        # Configure modern dark styling
        configure_modern_styles()
        self.configure(bg=ModernColors.BACKGROUND)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Data
        self.scan_results = scan_results
        self.selected_files = set()
        self.result = None
        
        # Callbacks
        self.proceed_callback = None
        self.modify_callback = None
        
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        self._center_window()
        self._load_results()
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better UX."""
        # Escape to cancel
        self.bind('<Escape>', lambda e: self._on_cancel())
        
        # Ctrl+A to select all safe files
        self.bind('<Control-a>', lambda e: self.file_tree._select_all_safe())
        
        # Delete key to clear selection
        self.bind('<Delete>', lambda e: self.file_tree._clear_selection())
        
        # Enter to proceed (if files selected)
        self.bind('<Return>', lambda e: self._on_proceed() if self.selected_files else None)
        
        # F5 to refresh/modify scan
        self.bind('<F5>', lambda e: self._on_modify())
    
    def _setup_ui(self):
        """Setup the modern dark UI layout with scrollable content."""
        # Create main container
        main_container = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable frame
        self._create_scrollable_content(main_container)
    
    def _create_scrollable_content(self, parent):
        """Create scrollable content area."""
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(parent, bg=ModernColors.BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=ModernColors.BACKGROUND)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add padding to scrollable content
        content_frame = tk.Frame(self.scrollable_frame, bg=ModernColors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, 
                          padx=ModernColors.SPACING['lg'], 
                          pady=ModernColors.SPACING['lg'])
        
        # Bind mousewheel to canvas for smooth scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Create content sections in the scrollable frame
        self._create_header(content_frame)
        self._create_summary(content_frame)
        self._create_file_view(content_frame)
        self._create_actions(content_frame)
    
    def _create_header(self, parent):
        """Create the header section."""
        header_card = ModernCard(parent, title="Scan Results")
        header_card.pack(fill=tk.X, pady=(0, 16))
        
        # Scan summary
        summary_text = (
            "File system scan completed successfully. Review the results below and "
            "select which files you want to securely delete. Files are automatically "
            "categorized by safety level."
        )
        
        summary_label = ttk.Label(header_card.content, text=summary_text,
                                 font=("Segoe UI", 10),
                                 wraplength=900,
                                 justify=tk.LEFT)
        summary_label.pack(anchor=tk.W, pady=(8, 0))
    
    def _create_summary(self, parent):
        """Create the summary statistics section."""
        summary_card = ModernCard(parent, title="📊 Summary Statistics")
        summary_card.pack(fill=tk.X, pady=(0, 16))
        
        self.summary_stats = ModernStats(summary_card.content)
        self.summary_stats.pack(fill=tk.X, pady=(8, 0))
        
        # Initialize stats (will be populated in _load_results)
        self.summary_stats.add_stat('total', '📁 Total Files', '0', row=0, column=0)
        self.summary_stats.add_stat('safe', '✅ Safe to Delete', '0', 'success', row=0, column=1)
        self.summary_stats.add_stat('selected', '☑️ Selected for Deletion', '0', 'info', row=0, column=2)
        
        self.summary_stats.add_stat('size_total', '💾 Total Size', '0 MB', row=1, column=0)
        self.summary_stats.add_stat('size_safe', '🟢 Safe Files Size', '0 MB', 'success', row=1, column=1)
        self.summary_stats.add_stat('size_selected', '🔵 Selected Size', '0 MB', 'info', row=1, column=2)
        
        # Add category breakdown
        self.summary_stats.add_stat('less_important', '⚠️ Less Important', '0', 'warning', row=2, column=0)
        self.summary_stats.add_stat('important', '🔶 Important', '0', 'warning', row=2, column=1)
        self.summary_stats.add_stat('protected', '🔒 Protected', '0', 'error', row=2, column=2)
    
    def _create_file_view(self, parent):
        """Create the file tree view section with fixed height."""
        files_card = ModernCard(parent, title="📂 Files by Category")
        files_card.pack(fill=tk.X, pady=(0, 16))
        
        # Add loading indicator
        self.loading_frame = tk.Frame(files_card.content, bg=ModernColors.CARD)
        self.loading_frame.pack(fill=tk.X, pady=(8, 0))
        
        loading_label = tk.Label(self.loading_frame, text="🔄 Loading file results...", 
                                font=("Segoe UI", 12),
                                bg=ModernColors.CARD,
                                fg=ModernColors.FOREGROUND)
        loading_label.pack(expand=True)
        
        # Create file tree with fixed height to ensure action buttons are visible
        self.file_tree = FileTreeView(files_card.content)
        # Initially hidden, will be shown after loading
        
        # Set selection callback
        self.file_tree.set_selection_callback(self._on_selection_change)
    
    def _create_actions(self, parent):
        """Create modern action buttons with dark theme."""
        actions_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        actions_frame.pack(fill=tk.X)
        
        # Left side - info
        info_frame = tk.Frame(actions_frame, bg=ModernColors.BACKGROUND)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.selection_info = tk.Label(info_frame, 
                                      text="Select files to proceed with deletion",
                                      font=("Segoe UI", 10),
                                      bg=ModernColors.BACKGROUND,
                                      fg=ModernColors.SECONDARY_TEXT)
        self.selection_info.pack(anchor=tk.W)
        
        # Keyboard shortcuts help
        shortcuts_text = "💡 Shortcuts: Ctrl+A (select safe), Delete (clear), Enter (proceed), Esc (cancel), F5 (modify)"
        shortcuts_label = tk.Label(info_frame, text=shortcuts_text,
                                  font=("Segoe UI", 9),
                                  bg=ModernColors.BACKGROUND,
                                  fg=ModernColors.MUTED_FOREGROUND)
        shortcuts_label.pack(anchor=tk.W, pady=(4, 0))
        
        # Right side - buttons
        buttons_frame = tk.Frame(actions_frame, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Create buttons in reverse order since we're packing from right
        self.proceed_button = ModernButton(buttons_frame, text="🗑️ Delete Selected Files", 
                                          variant="primary", size="md",
                                          command=self._on_proceed)
        self.proceed_button.configure(state=tk.DISABLED)
        self.proceed_button.pack(side=tk.RIGHT, padx=(0, 8))
        
        ModernButton(buttons_frame, text="⚙️ Modify Scan", 
                    variant="secondary", size="md",
                    command=self._on_modify).pack(side=tk.RIGHT, padx=(0, 8))
        
        ModernButton(buttons_frame, text="❌ Cancel", 
                    variant="ghost", size="md",
                    command=self._on_cancel).pack(side=tk.RIGHT, padx=(0, 8))
        
        # Add quick selection buttons
        quick_select_frame = tk.Frame(buttons_frame, bg=ModernColors.BACKGROUND)
        quick_select_frame.pack(side=tk.LEFT, padx=(0, 16))
        
        ModernButton(quick_select_frame, text="✅ Select All Safe", 
                    variant="ghost", size="sm",
                    command=lambda: self.file_tree._select_all_safe()).pack(side=tk.LEFT, padx=(0, 4))
        ModernButton(quick_select_frame, text="⚠️ Select Less Important", 
                    variant="ghost", size="sm",
                    command=lambda: self.file_tree._select_less_important()).pack(side=tk.LEFT, padx=(0, 4))
        ModernButton(quick_select_frame, text="🔄 Clear All", 
                    variant="ghost", size="sm",
                    command=lambda: self.file_tree._clear_selection()).pack(side=tk.LEFT)
    
    def _center_window(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def _load_results(self):
        """Load scan results into the UI."""
        # Extract data from scan results
        files_by_category = self.scan_results.get('categorized_files', {})
        total_files = self.scan_results.get('total_files', 0)
        
        # Calculate statistics
        safe_files = files_by_category.get('Safe', [])
        less_important = files_by_category.get('Less Important', [])
        important_files = files_by_category.get('Important', [])
        protected_files = files_by_category.get('Protected', [])
        
        # Calculate sizes
        def get_total_size(file_list):
            return sum(getattr(f, 'size', 0) for f in file_list)
        
        total_size = get_total_size(safe_files + less_important + important_files + protected_files)
        safe_size = get_total_size(safe_files)
        
        # Update summary statistics
        self.summary_stats.update_stat('total', f"{total_files:,}")
        self.summary_stats.update_stat('safe', f"{len(safe_files):,}")
        self.summary_stats.update_stat('selected', "0")
        
        self.summary_stats.update_stat('size_total', self._format_size(total_size))
        self.summary_stats.update_stat('size_safe', self._format_size(safe_size))
        self.summary_stats.update_stat('size_selected', "0 MB")
        
        # Update category breakdown
        self.summary_stats.update_stat('less_important', f"{len(less_important):,}")
        self.summary_stats.update_stat('important', f"{len(important_files):,}")
        self.summary_stats.update_stat('protected', f"{len(protected_files):,}")
        
        # Load files into tree
        self.file_tree.load_files(files_by_category)
        
        # Hide loading indicator and show tree
        self.loading_frame.pack_forget()
        self.file_tree.pack(fill=tk.X, pady=(8, 0))
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _on_selection_change(self, selected_files):
        """Handle file selection changes."""
        self.selected_files = selected_files
        
        # Update selection statistics
        selected_count = len(selected_files)
        selected_size = sum(getattr(f, 'size', 0) for f in selected_files)
        
        self.summary_stats.update_stat('selected', f"{selected_count:,}")
        self.summary_stats.update_stat('size_selected', self._format_size(selected_size))
        
        # Update proceed button state
        if selected_count > 0:
            self.proceed_button.configure(state=tk.NORMAL)
            self.proceed_button.configure(text=f"🗑️ Delete {selected_count:,} Selected Files")
            self.selection_info.configure(text=f"{selected_count:,} files selected for deletion ({self._format_size(selected_size)})")
        else:
            self.proceed_button.configure(state=tk.DISABLED)
            self.proceed_button.configure(text="🗑️ Delete Selected Files")
            self.selection_info.configure(text="Select files to proceed with deletion")
    
    def _on_proceed(self):
        """Handle proceed with deletion."""
        if not self.selected_files:
            messagebox.showwarning("No Selection", "Please select files to delete.")
            return
        
        # Confirm selection
        count = len(self.selected_files)
        size = sum(getattr(f, 'size', 0) for f in self.selected_files)
        
        message = (
            f"You have selected {count:,} files ({self._format_size(size)}) for secure deletion.\n\n"
            "This action cannot be undone. Are you sure you want to proceed?"
        )
        
        if messagebox.askyesno("Confirm Deletion", message, icon="warning"):
            # self.selected_files already contains FileInfo objects, no conversion needed
            self.result = {
                'action': 'proceed',
                'selected_files': self.selected_files
            }
            self.destroy()
    
    def _on_modify(self):
        """Handle modify scan settings."""
        self.result = {'action': 'modify'}
        self.destroy()
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.result = {'action': 'cancel'}
        self.destroy()
    
    def show_results(self) -> Optional[Dict]:
        """Show the results dialog and return user action."""
        self.wait_window()
        return self.result