"""Main application window for SecureWipe Desktop."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# Add shared module to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

from config.defaults import (
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
)
from config.settings import settings
from logging_setup import get_application_logger


class MainWindow:
    """Main application window with SecureWipe branding and navigation."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = get_application_logger(__name__, debug=debug)

        # Initialize tkinter
        self.root = tk.Tk()
        self._setup_window()
        self._create_menu()
        self._create_main_interface()
        self._setup_status_bar()

        self.logger.info("SecureWipe Desktop application initialized")

    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.root.title(WINDOW_TITLE)
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Set window geometry from settings
        width = settings.get("window_geometry.width", WINDOW_DEFAULT_WIDTH)
        height = settings.get("window_geometry.height", WINDOW_DEFAULT_HEIGHT)
        x = settings.get("window_geometry.x")
        y = settings.get("window_geometry.y")

        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")
            # Center window on screen
            self.root.eval("tk::PlaceWindow . center")

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu(self) -> None:
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self._on_closing)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_interface(self) -> None:
        """Create main application interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # SecureWipe branding header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        title_label = ttk.Label(
            header_frame, text="SecureWipe", font=("Arial", 24, "bold")
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(
            header_frame,
            text="Desktop Quick Clean - Secure File Deletion System",
            font=("Arial", 12),
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        self.scan_button = ttk.Button(
            nav_frame, text="Start File Scan", command=self._start_scan, state="normal"
        )
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))

        self.settings_button = ttk.Button(
            nav_frame, text="Settings", command=self._open_settings
        )
        self.settings_button.pack(side=tk.LEFT, padx=(0, 10))

        # Status indicator
        self.status_var = tk.StringVar(value="Ready to scan directories")
        status_label = ttk.Label(nav_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)

        # Main content area (placeholder for future file tree)
        content_frame = ttk.LabelFrame(
            main_frame, text="Directory Contents", padding="10"
        )
        content_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S)
        )

        placeholder_label = ttk.Label(
            content_frame,
            text="Click 'Start File Scan' to begin scanning your directories\\nfor files that can be securely deleted.",
            justify=tk.CENTER,
            font=("Arial", 11),
        )
        placeholder_label.pack(expand=True)

    def _setup_status_bar(self) -> None:
        """Create status bar at bottom of window."""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.status_text = tk.StringVar(value="SecureWipe Desktop - Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_text)
        status_label.pack(side=tk.LEFT, padx=5, pady=2)

        # Version info
        version_label = ttk.Label(status_frame, text="v1.0.0")
        version_label.pack(side=tk.RIGHT, padx=5, pady=2)

    def _start_scan(self) -> None:
        """Handle start scan button click."""
        self.logger.info("User initiated file scan")
        self.status_var.set("Scanning directories...")
        self.scan_button.config(state="disabled")

        # Placeholder for future scanner integration
        messagebox.showinfo(
            "File Scanner",
            "File scanning functionality will be implemented in the next story.\\n\\n"
            "This will scan your Documents, Downloads, Desktop, and temp directories.",
        )

        self.status_var.set("Scan completed")
        self.scan_button.config(state="normal")

    def _open_settings(self) -> None:
        """Handle settings button click."""
        self.logger.info("User opened settings")
        messagebox.showinfo(
            "Settings", "Settings configuration will be implemented in future stories."
        )

    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About SecureWipe",
            "SecureWipe Desktop v1.0.0\\n\\n"
            "Secure File Deletion System\\n"
            "Dual-mode operation: Desktop Quick Clean + Bootable Deep Clean\\n\\n"
            "Built with Python and tkinter",
        )

    def _on_closing(self) -> None:
        """Handle application closing."""
        # Save window geometry
        geometry = self.root.geometry()
        width, height, x, y = self._parse_geometry(geometry)

        settings.set("window_geometry.width", width)
        settings.set("window_geometry.height", height)
        settings.set("window_geometry.x", x)
        settings.set("window_geometry.y", y)
        settings.save()

        self.logger.info("SecureWipe Desktop application closing")
        self.root.destroy()

    def _parse_geometry(self, geometry: str) -> tuple:
        """Parse tkinter geometry string."""
        # Format: "widthxheight+x+y"
        size_pos = geometry.split("+")
        width, height = map(int, size_pos[0].split("x"))
        x = int(size_pos[1]) if len(size_pos) > 1 else 0
        y = int(size_pos[2]) if len(size_pos) > 2 else 0
        return width, height, x, y

    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.logger.info("Starting SecureWipe Desktop main loop")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
