"""
Modern UI components inspired by shadcn/ui for tkinter applications.
Provides clean, modern styling and responsive behavior.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
import threading
import time


class ModernColors:
    """Modern dark theme color palette for consistent theming."""
    
    # Background colors - Deep dark theme
    BACKGROUND = "#0a0a0a"  # Deep black for main background
    SURFACE = "#1a1a1a"    # Dark gray for cards and elevated surfaces
    SURFACE_VARIANT = "#2a2a2a"  # Medium gray for secondary surfaces
    CARD = "#1a1a1a"       # Same as surface for consistency
    
    # Border colors - Subtle dark borders
    BORDER = "#3a3a3a"     # Subtle borders and dividers
    BORDER_HOVER = "#4a4a4a"  # Lighter on hover
    BORDER_FOCUS = "#3b82f6"  # Accent color for focus states
    
    # Text colors - High contrast for readability
    FOREGROUND = "#ffffff"        # Pure white for headings and important text
    SECONDARY_TEXT = "#e5e5e5"    # Light gray for body text
    MUTED_FOREGROUND = "#a0a0a0"  # Medium gray for less important text
    DISABLED_TEXT = "#666666"     # Dark gray for disabled states
    
    # Primary colors - Modern blue accent
    PRIMARY = "#3b82f6"           # Blue for primary actions
    PRIMARY_FOREGROUND = "#ffffff"
    PRIMARY_HOVER = "#2563eb"     # Darker blue on hover
    PRIMARY_ACTIVE = "#1d4ed8"    # Even darker when active
    
    # Secondary colors - Neutral grays
    SECONDARY = "#2a2a2a"
    SECONDARY_FOREGROUND = "#e5e5e5"
    SECONDARY_HOVER = "#3a3a3a"
    SECONDARY_ACTIVE = "#1a1a1a"
    
    # Accent colors - Consistent with primary
    ACCENT = "#3b82f6"
    ACCENT_FOREGROUND = "#ffffff"
    ACCENT_HOVER = "#2563eb"
    
    # Status colors - Vibrant but not overwhelming
    SUCCESS = "#10b981"    # Green for success states
    SUCCESS_BG = "#064e3b" # Dark green background
    WARNING = "#f59e0b"    # Amber for warnings
    WARNING_BG = "#78350f" # Dark amber background
    ERROR = "#ef4444"      # Red for errors
    ERROR_BG = "#7f1d1d"   # Dark red background
    INFO = "#06b6d4"       # Cyan for information
    INFO_BG = "#164e63"    # Dark cyan background
    
    # Progress colors - Smooth gradients
    PROGRESS_BG = "#2a2a2a"
    PROGRESS_FILL = "#3b82f6"
    PROGRESS_GRADIENT_START = "#3b82f6"
    PROGRESS_GRADIENT_END = "#60a5fa"
    
    # Interactive states - Consistent opacity overlays
    HOVER_OVERLAY = "rgba(255, 255, 255, 0.1)"
    ACTIVE_OVERLAY = "rgba(255, 255, 255, 0.2)"
    FOCUS_RING = "rgba(59, 130, 246, 0.3)"
    
    # Shadows - Subtle elevation
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.5)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.5)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.5)"
    
    # Spacing system - 4px base unit
    SPACING = {
        'xs': 4,   # Tight spacing
        'sm': 8,   # Small spacing
        'md': 16,  # Medium spacing - most common
        'lg': 24,  # Large spacing
        'xl': 32,  # Extra large spacing
        '2xl': 48  # Section spacing
    }
    
    # Border radius system
    RADIUS = {
        'sm': 4,   # Small radius
        'md': 6,   # Medium radius - buttons
        'lg': 8,   # Large radius - cards
        'xl': 12,  # Extra large radius
        'full': 9999  # Fully rounded
    }


class ModernCard(tk.Frame):
    """Modern card component with dark theme styling and elevation."""
    
    def __init__(self, parent, title: Optional[str] = None, elevation: str = "md", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure card styling with dark theme
        self.configure(
            bg=ModernColors.CARD,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=ModernColors.BORDER,
            highlightbackground=ModernColors.BORDER
        )
        
        # Add padding frame for consistent spacing
        self.padding_frame = tk.Frame(self, bg=ModernColors.CARD)
        self.padding_frame.pack(fill=tk.BOTH, expand=True, 
                               padx=ModernColors.SPACING['lg'], 
                               pady=ModernColors.SPACING['lg'])
        
        # Create header if title provided
        if title:
            self.header = tk.Frame(self.padding_frame, bg=ModernColors.CARD)
            self.header.pack(fill=tk.X, pady=(0, ModernColors.SPACING['md']))
            
            self.title_label = tk.Label(
                self.header, 
                text=title,
                bg=ModernColors.CARD,
                fg=ModernColors.FOREGROUND,
                font=("Segoe UI", 14, "bold"),
                anchor="w"
            )
            self.title_label.pack(fill=tk.X)
            
            # Add subtle separator line
            separator = tk.Frame(self.header, bg=ModernColors.BORDER, height=1)
            separator.pack(fill=tk.X, pady=(ModernColors.SPACING['sm'], 0))
        
        # Content area
        self.content = tk.Frame(self.padding_frame, bg=ModernColors.CARD)
        self.content.pack(fill=tk.BOTH, expand=True)


class ModernProgressBar(tk.Canvas):
    """Modern progress bar with smooth animations and gradient fills."""
    
    def __init__(self, parent, width=400, height=12, variant="primary", **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=ModernColors.BACKGROUND, highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.progress = 0.0
        self.variant = variant
        self._animation_target = 0.0
        self._animation_step = 0
        
        # Color variants
        self.colors = {
            "primary": ModernColors.PRIMARY,
            "success": ModernColors.SUCCESS,
            "warning": ModernColors.WARNING,
            "error": ModernColors.ERROR,
            "info": ModernColors.INFO
        }
        
        # Create progress elements
        self._setup_progress_bar()
    
    def _setup_progress_bar(self):
        """Setup progress bar visual elements with modern styling."""
        # Background track with rounded appearance
        self.track_rect = self.create_rectangle(
            0, 0, self.width, self.height,
            fill=ModernColors.PROGRESS_BG,
            outline=ModernColors.BORDER,
            width=1
        )
        
        # Progress fill with gradient effect
        fill_color = self.colors.get(self.variant, ModernColors.PRIMARY)
        self.progress_rect = self.create_rectangle(
            1, 1, 1, self.height-1,
            fill=fill_color,
            outline=""
        )
        
        # Add subtle highlight on top for depth
        self.highlight_rect = self.create_rectangle(
            1, 1, 1, max(1, self.height // 3),
            fill=self._lighten_color(fill_color, 0.3),
            outline=""
        )
        
        # Add subtle inner shadow at bottom
        self.shadow_rect = self.create_rectangle(
            1, self.height - 2, 1, self.height - 1,
            fill=self._darken_color(fill_color, 0.2),
            outline=""
        )
    
    def _lighten_color(self, color: str, factor: float) -> str:
        """Lighten a hex color by a factor."""
        try:
            # Simple color lightening - convert to RGB and increase values
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except:
            return color
    
    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a hex color by a factor."""
        try:
            # Simple color darkening - convert to RGB and decrease values
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except:
            return color
    
    def set_progress(self, percentage: float, animate: bool = True):
        """Update progress with smooth animations."""
        self._animation_target = max(0.0, min(100.0, percentage))
        
        if animate and abs(self._animation_target - self.progress) > 1:
            self._animate_to_target()
        else:
            # Direct update for small changes or when animation disabled
            try:
                self.after_idle(lambda: self._update_progress_rect(self._animation_target))
            except tk.TclError:
                pass
    
    def _animate_to_target(self):
        """Animate progress to target value with smooth easing."""
        if abs(self.progress - self._animation_target) < 0.1:
            self._update_progress_rect(self._animation_target)
            return
        
        # Smooth easing animation with better performance
        diff = self._animation_target - self.progress
        step = diff * 0.2  # Slightly faster easing for responsiveness
        new_progress = self.progress + step
        
        try:
            self._update_progress_rect(new_progress)
            self.after(16, self._animate_to_target)  # 60fps for smooth animation
        except tk.TclError:
            pass
    
    def _update_progress_rect(self, percentage: float):
        """Update progress rectangle with enhanced styling."""
        try:
            if not self.winfo_exists():
                return
                
            self.progress = percentage
            fill_width = max(2, int((self.width - 2) * percentage / 100.0))
            
            # Update main progress fill
            self.coords(self.progress_rect, 1, 1, fill_width, self.height-1)
            
            # Update highlight (top portion)
            highlight_height = max(1, self.height // 3)
            self.coords(self.highlight_rect, 1, 1, fill_width, highlight_height)
            
            # Update shadow (bottom portion)
            self.coords(self.shadow_rect, 1, self.height - 2, fill_width, self.height - 1)
            
        except tk.TclError:
            pass
    
    def set_variant(self, variant: str):
        """Change the color variant of the progress bar."""
        self.variant = variant
        fill_color = self.colors.get(variant, ModernColors.PRIMARY)
        
        try:
            self.itemconfig(self.progress_rect, fill=fill_color)
            self.itemconfig(self.highlight_rect, fill=self._lighten_color(fill_color, 0.3))
            self.itemconfig(self.shadow_rect, fill=self._darken_color(fill_color, 0.2))
        except tk.TclError:
            pass


class ModernButton(tk.Button):
    """Modern button with enhanced styling, hover effects, and dark theme."""
    
    def __init__(self, parent, variant="default", size="md", icon=None, **kwargs):
        # Extract text and command before modifying kwargs
        text = kwargs.pop('text', '')
        command = kwargs.pop('command', None)
        
        # Configure colors based on variant
        self.variant = variant
        self.size = size
        self.icon = icon
        self._is_hovered = False
        self._is_pressed = False
        
        # Color schemes for different variants
        self.color_schemes = {
            "primary": {
                "bg": ModernColors.PRIMARY,
                "fg": ModernColors.PRIMARY_FOREGROUND,
                "hover_bg": ModernColors.PRIMARY_HOVER,
                "active_bg": ModernColors.PRIMARY_ACTIVE,
                "border": ModernColors.PRIMARY
            },
            "secondary": {
                "bg": ModernColors.SECONDARY,
                "fg": ModernColors.SECONDARY_FOREGROUND,
                "hover_bg": ModernColors.SECONDARY_HOVER,
                "active_bg": ModernColors.SECONDARY_ACTIVE,
                "border": ModernColors.BORDER
            },
            "ghost": {
                "bg": "transparent",
                "fg": ModernColors.FOREGROUND,
                "hover_bg": ModernColors.SECONDARY,
                "active_bg": ModernColors.SECONDARY_ACTIVE,
                "border": "transparent"
            },
            "destructive": {
                "bg": ModernColors.ERROR,
                "fg": "#ffffff",
                "hover_bg": self._darken_color(ModernColors.ERROR, 0.1),
                "active_bg": self._darken_color(ModernColors.ERROR, 0.2),
                "border": ModernColors.ERROR
            }
        }
        
        # Size configurations
        self.size_configs = {
            "sm": {"padding": (ModernColors.SPACING['md'], ModernColors.SPACING['xs']), "font_size": 9},
            "md": {"padding": (ModernColors.SPACING['lg'], ModernColors.SPACING['sm']), "font_size": 10},
            "lg": {"padding": (ModernColors.SPACING['xl'], ModernColors.SPACING['md']), "font_size": 11}
        }
        
        colors = self.color_schemes.get(variant, self.color_schemes["secondary"])
        size_config = self.size_configs.get(size, self.size_configs["md"])
        
        # Handle transparent background for ghost variant
        bg_color = colors["bg"] if colors["bg"] != "transparent" else ModernColors.BACKGROUND
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=colors["fg"],
            font=("Segoe UI", size_config["font_size"], "normal"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            **kwargs
        )
        
        # Apply padding by configuring the button
        pad_x, pad_y = size_config["padding"]
        self.configure(padx=pad_x, pady=pad_y)
        
        # Bind hover and click events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        # Store original command for state management
        self._original_command = command
    
    def _darken_color(self, color: str, factor: float) -> str:
        """Darken a hex color by a factor."""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except:
            return color
    
    def _on_enter(self, event):
        """Handle mouse enter event with smooth transition."""
        if self['state'] != 'disabled':
            self._is_hovered = True
            colors = self.color_schemes.get(self.variant, self.color_schemes["secondary"])
            hover_bg = colors["hover_bg"] if colors["hover_bg"] != "transparent" else ModernColors.SECONDARY
            
            # Smooth transition effect
            try:
                self.configure(bg=hover_bg, relief="flat")
            except tk.TclError:
                pass
    
    def _on_leave(self, event):
        """Handle mouse leave event with smooth transition."""
        self._is_hovered = False
        if not self._is_pressed:
            colors = self.color_schemes.get(self.variant, self.color_schemes["secondary"])
            bg_color = colors["bg"] if colors["bg"] != "transparent" else ModernColors.BACKGROUND
            
            # Smooth transition back to normal state
            try:
                self.configure(bg=bg_color, relief="flat")
            except tk.TclError:
                pass
    
    def _on_press(self, event):
        """Handle mouse press event."""
        if self['state'] != 'disabled':
            self._is_pressed = True
            colors = self.color_schemes.get(self.variant, self.color_schemes["secondary"])
            active_bg = colors["active_bg"] if colors["active_bg"] != "transparent" else ModernColors.SECONDARY_ACTIVE
            self.configure(bg=active_bg)
    
    def _on_release(self, event):
        """Handle mouse release event."""
        self._is_pressed = False
        if self._is_hovered:
            colors = self.color_schemes.get(self.variant, self.color_schemes["secondary"])
            hover_bg = colors["hover_bg"] if colors["hover_bg"] != "transparent" else ModernColors.SECONDARY
            self.configure(bg=hover_bg)
        else:
            colors = self.color_schemes.get(self.variant, self.color_schemes["secondary"])
            bg_color = colors["bg"] if colors["bg"] != "transparent" else ModernColors.BACKGROUND
            self.configure(bg=bg_color)
    
    def set_loading(self, loading: bool = True):
        """Set button to loading state."""
        if loading:
            self.configure(state='disabled', text="Loading...")
        else:
            self.configure(state='normal')
            # Restore original text if it was changed
            # Note: This would need to be enhanced to store original text


class ModernBadge(tk.Label):
    """Modern badge component for status indicators."""
    
    def __init__(self, parent, text="", variant="default", **kwargs):
        # Configure colors based on variant
        colors = {
            "default": (ModernColors.SECONDARY, ModernColors.SECONDARY_FOREGROUND),
            "success": (ModernColors.SUCCESS, "#ffffff"),
            "warning": (ModernColors.WARNING, "#ffffff"),
            "error": (ModernColors.ERROR, "#ffffff"),
            "info": (ModernColors.INFO, "#ffffff")
        }
        
        bg_color, fg_color = colors.get(variant, colors["default"])
        
        super().__init__(parent, text=text, bg=bg_color, fg=fg_color,
                        font=("Segoe UI", 9), padx=8, pady=2, **kwargs)


class ModernStats(ttk.Frame):
    """Modern statistics display component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.stats = {}
        self._create_layout()
    
    def _create_layout(self):
        """Create the statistics layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
    
    def add_stat(self, key: str, label: str, value: str = "0", 
                variant: str = "default", row: int = 0, column: int = 0):
        """Add a statistic to the display."""
        stat_frame = ttk.Frame(self)
        stat_frame.grid(row=row, column=column, padx=8, pady=4, sticky="ew")
        
        # Value label (large)
        value_label = ttk.Label(stat_frame, text=value, 
                               font=("Segoe UI", 16, "bold"))
        value_label.pack()
        
        # Description label (small)
        desc_label = ttk.Label(stat_frame, text=label, 
                              font=("Segoe UI", 9),
                              foreground=ModernColors.MUTED_FOREGROUND)
        desc_label.pack()
        
        self.stats[key] = {
            'value_label': value_label,
            'desc_label': desc_label,
            'variant': variant
        }
    
    def update_stat(self, key: str, value: str, variant: Optional[str] = None):
        """Update a statistic value."""
        if key in self.stats:
            stat = self.stats[key]
            stat['value_label'].config(text=value)
            
            if variant:
                # Update color based on variant
                colors = {
                    "success": ModernColors.SUCCESS,
                    "warning": ModernColors.WARNING,
                    "error": ModernColors.ERROR,
                    "info": ModernColors.INFO,
                    "default": ModernColors.FOREGROUND
                }
                color = colors.get(variant, ModernColors.FOREGROUND)
                stat['value_label'].config(foreground=color)


class ModernLogViewer(ttk.Frame):
    """Modern log viewer with filtering and search."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.log_entries = []
        self.filtered_entries = []
        self.filters = {
            'info': True,
            'success': True,
            'warning': True,
            'error': True
        }
        
        self._create_layout()
    
    def _create_layout(self):
        """Create the log viewer layout."""
        # Filter controls
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(filter_frame, text="Show:", 
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 8))
        
        # Filter checkboxes
        for level in ['info', 'success', 'warning', 'error']:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(filter_frame, text=level.title(), 
                               variable=var, command=self._update_filter)
            cb.pack(side=tk.LEFT, padx=(0, 8))
            setattr(self, f'{level}_var', var)
        
        # Clear button
        ttk.Button(filter_frame, text="Clear", 
                  command=self.clear_log).pack(side=tk.RIGHT)
        
        # Log display
        log_frame = ttk.Frame(self)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, 
                               font=("Consolas", 9), height=12,
                               bg=ModernColors.SURFACE,
                               fg=ModernColors.FOREGROUND,
                               selectbackground=ModernColors.ACCENT,
                               state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                 command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for different log levels
        self.log_text.tag_configure("info", foreground=ModernColors.INFO)
        self.log_text.tag_configure("success", foreground=ModernColors.SUCCESS)
        self.log_text.tag_configure("warning", foreground=ModernColors.WARNING)
        self.log_text.tag_configure("error", foreground=ModernColors.ERROR)
    
    def add_log(self, message: str, level: str = "info"):
        """Add a log entry."""
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            'timestamp': timestamp,
            'level': level.lower(),
            'message': message,
            'full_text': f"[{timestamp}] {level.upper()}: {message}"
        }
        
        self.log_entries.append(entry)
        self._update_display()
    
    def _update_filter(self):
        """Update filter settings and refresh display."""
        self.filters = {
            'info': self.info_var.get(),
            'success': self.success_var.get(),
            'warning': self.warning_var.get(),
            'error': self.error_var.get()
        }
        self._update_display()
    
    def _update_display(self):
        """Update the log display based on current filters."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        for entry in self.log_entries:
            if self.filters.get(entry['level'], True):
                start_pos = self.log_text.index(tk.END + "-1c")
                self.log_text.insert(tk.END, entry['full_text'] + "\n")
                end_pos = self.log_text.index(tk.END + "-1c")
                
                # Apply tag for coloring
                self.log_text.tag_add(entry['level'], start_pos, end_pos)
        
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear all log entries."""
        self.log_entries.clear()
        self._update_display()


def configure_modern_styles():
    """Configure modern dark theme ttk styles for the application."""
    style = ttk.Style()
    
    # Set the theme to a dark-compatible base
    try:
        # Try to use a dark theme if available
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
    except:
        pass
    
    # Configure root window and frame styles
    style.configure("TFrame",
                   background=ModernColors.BACKGROUND,
                   borderwidth=0)
    
    style.configure("TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 9))
    
    # Configure modern button styles with dark theme
    style.configure("Modern.TButton",
                   background=ModernColors.SECONDARY,
                   foreground=ModernColors.SECONDARY_FOREGROUND,
                   borderwidth=1,
                   focuscolor='none',
                   padding=(ModernColors.SPACING['md'], ModernColors.SPACING['sm']),
                   font=("Segoe UI", 9))
    
    style.map("Modern.TButton",
             background=[('active', ModernColors.SECONDARY_ACTIVE),
                        ('pressed', ModernColors.SECONDARY_ACTIVE),
                        ('!active', ModernColors.SECONDARY)],
             foreground=[('active', ModernColors.FOREGROUND),
                        ('!active', ModernColors.SECONDARY_FOREGROUND)],
             relief=[('pressed', 'flat'), ('!pressed', 'flat')])
    
    # Primary button style - accent colored
    style.configure("Primary.TButton",
                   background=ModernColors.PRIMARY,
                   foreground=ModernColors.PRIMARY_FOREGROUND,
                   borderwidth=0,
                   focuscolor='none',
                   padding=(ModernColors.SPACING['lg'], ModernColors.SPACING['md']),
                   font=("Segoe UI", 9, "bold"))
    
    style.map("Primary.TButton",
             background=[('active', ModernColors.PRIMARY_HOVER),
                        ('pressed', ModernColors.PRIMARY_ACTIVE),
                        ('!active', ModernColors.PRIMARY)],
             foreground=[('active', ModernColors.PRIMARY_FOREGROUND),
                        ('!active', ModernColors.PRIMARY_FOREGROUND)],
             relief=[('pressed', 'flat'), ('!pressed', 'flat')])
    
    # Accent button style (same as primary for consistency)
    style.configure("Accent.TButton",
                   background=ModernColors.ACCENT,
                   foreground=ModernColors.ACCENT_FOREGROUND,
                   borderwidth=0,
                   focuscolor='none',
                   padding=(ModernColors.SPACING['lg'], ModernColors.SPACING['md']),
                   font=("Segoe UI", 9, "bold"))
    
    style.map("Accent.TButton",
             background=[('active', ModernColors.ACCENT_HOVER),
                        ('pressed', ModernColors.PRIMARY_ACTIVE),
                        ('!active', ModernColors.ACCENT)],
             foreground=[('active', ModernColors.ACCENT_FOREGROUND),
                        ('!active', ModernColors.ACCENT_FOREGROUND)],
             relief=[('pressed', 'flat'), ('!pressed', 'flat')])
    
    # Configure card styles with dark theme
    style.configure("Card.TFrame",
                   background=ModernColors.CARD,
                   relief="flat",
                   borderwidth=1,
                   bordercolor=ModernColors.BORDER)
    
    style.configure("CardTitle.TLabel",
                   background=ModernColors.CARD,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 12, "bold"))
    
    # Configure modern label styles with typography hierarchy
    style.configure("Title.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 24, "bold"))
    
    style.configure("Heading1.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 20, "bold"))
    
    style.configure("Heading2.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 16, "bold"))
    
    style.configure("Heading3.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 14, "bold"))
    
    style.configure("Body.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.SECONDARY_TEXT,
                   font=("Segoe UI", 12))
    
    style.configure("Caption.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.MUTED_FOREGROUND,
                   font=("Segoe UI", 10))
    
    style.configure("Muted.TLabel",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.MUTED_FOREGROUND,
                   font=("Segoe UI", 9))
    
    # Configure entry and text widgets
    style.configure("Modern.TEntry",
                   fieldbackground=ModernColors.SURFACE,
                   background=ModernColors.SURFACE,
                   foreground=ModernColors.FOREGROUND,
                   bordercolor=ModernColors.BORDER,
                   lightcolor=ModernColors.BORDER,
                   darkcolor=ModernColors.BORDER,
                   insertcolor=ModernColors.FOREGROUND,
                   selectbackground=ModernColors.PRIMARY,
                   selectforeground=ModernColors.PRIMARY_FOREGROUND)
    
    # Configure treeview for dark theme
    style.configure("Modern.Treeview",
                   background=ModernColors.SURFACE,
                   foreground=ModernColors.FOREGROUND,
                   fieldbackground=ModernColors.SURFACE,
                   bordercolor=ModernColors.BORDER,
                   lightcolor=ModernColors.BORDER,
                   darkcolor=ModernColors.BORDER)
    
    style.configure("Modern.Treeview.Heading",
                   background=ModernColors.SURFACE_VARIANT,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 9, "bold"))
    
    style.map("Modern.Treeview",
             background=[('selected', ModernColors.PRIMARY)],
             foreground=[('selected', ModernColors.PRIMARY_FOREGROUND)])
    
    # Configure scrollbars for dark theme
    style.configure("Modern.Vertical.TScrollbar",
                   background=ModernColors.SURFACE_VARIANT,
                   troughcolor=ModernColors.SURFACE,
                   bordercolor=ModernColors.BORDER,
                   arrowcolor=ModernColors.MUTED_FOREGROUND,
                   darkcolor=ModernColors.SURFACE_VARIANT,
                   lightcolor=ModernColors.SURFACE_VARIANT)
    
    style.configure("Modern.Horizontal.TScrollbar",
                   background=ModernColors.SURFACE_VARIANT,
                   troughcolor=ModernColors.SURFACE,
                   bordercolor=ModernColors.BORDER,
                   arrowcolor=ModernColors.MUTED_FOREGROUND,
                   darkcolor=ModernColors.SURFACE_VARIANT,
                   lightcolor=ModernColors.SURFACE_VARIANT)
    
    # Configure checkbuttons for dark theme
    style.configure("Modern.TCheckbutton",
                   background=ModernColors.BACKGROUND,
                   foreground=ModernColors.FOREGROUND,
                   focuscolor='none',
                   font=("Segoe UI", 9))
    
    # Configure labelframes for dark theme
    style.configure("Modern.TLabelframe",
                   background=ModernColors.SURFACE,
                   bordercolor=ModernColors.BORDER,
                   lightcolor=ModernColors.BORDER,
                   darkcolor=ModernColors.BORDER)
    
    style.configure("Modern.TLabelframe.Label",
                   background=ModernColors.SURFACE,
                   foreground=ModernColors.FOREGROUND,
                   font=("Segoe UI", 10, "bold"))