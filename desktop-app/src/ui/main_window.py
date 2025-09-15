"""Main application window for SecureWipe Desktop with modern UI."""

import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# Add shared module to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

# Import modern UI components
try:
    from .modern_components import configure_modern_styles, ModernColors, ModernButton, ModernCard
except ImportError:
    from modern_components import configure_modern_styles, ModernColors, ModernButton, ModernCard

try:
    from ..config.defaults import (
        WINDOW_DEFAULT_HEIGHT,
        WINDOW_DEFAULT_WIDTH,
        WINDOW_MIN_HEIGHT,
        WINDOW_MIN_WIDTH,
        WINDOW_TITLE,
    )
except ImportError:
    from config.defaults import (
        WINDOW_DEFAULT_HEIGHT,
        WINDOW_DEFAULT_WIDTH,
        WINDOW_MIN_HEIGHT,
        WINDOW_MIN_WIDTH,
        WINDOW_TITLE,
    )

try:
    from ..config.settings import settings
except ImportError:
    from config.settings import settings

try:
    from ..logging_setup import get_application_logger
except ImportError:
    from logging_setup import get_application_logger


class MainWindow:
    """Main application window with SecureWipe branding and navigation."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.logger = get_application_logger(__name__, debug=debug)

        # Initialize tkinter with modern styling
        self.root = tk.Tk()
        configure_modern_styles()  # Apply modern theme
        self.root.configure(bg=ModernColors.BACKGROUND)
        
        self._setup_window()
        self._create_menu()
        self._create_main_interface()
        self._setup_status_bar()

        # Initialize workflow state
        self.scanned_files = []
        self.categorized_files = {}
        self.selected_files = []
        
        self.logger.info("SecureWipe Desktop application initialized with modern UI")

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
        """Create modern main application interface with dark theme."""
        # Main container with dark background
        main_frame = tk.Frame(self.root, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid weights for responsive layout
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Modern header section
        self._create_modern_header(main_frame)
        
        # Action buttons section
        self._create_action_section(main_frame)
        
        # Clean content area
        self._create_content_area(main_frame)

    def _create_modern_header(self, parent):
        """Create modern header with minimal branding."""
        header_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND, height=80)
        header_frame.pack(fill=tk.X, padx=ModernColors.SPACING['2xl'], 
                         pady=(ModernColors.SPACING['2xl'], ModernColors.SPACING['lg']))
        header_frame.pack_propagate(False)

        # Left side - branding
        brand_frame = tk.Frame(header_frame, bg=ModernColors.BACKGROUND)
        brand_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Main title with modern typography
        title_label = tk.Label(
            brand_frame,
            text="SecureWipe",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.FOREGROUND,
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")

        # Subtle subtitle
        subtitle_label = tk.Label(
            brand_frame,
            text="Secure File Deletion",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.MUTED_FOREGROUND,
            font=("Segoe UI", 12),
            anchor="w"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Right side - status indicator
        status_frame = tk.Frame(header_frame, bg=ModernColors.BACKGROUND)
        status_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.SUCCESS,
            font=("Segoe UI", 11, "bold"),
            anchor="e"
        )
        self.status_label.pack(side=tk.RIGHT, anchor="e", pady=(20, 0))

    def _create_action_section(self, parent):
        """Create modern action buttons section."""
        action_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        action_frame.pack(fill=tk.X, padx=ModernColors.SPACING['2xl'], 
                         pady=(0, ModernColors.SPACING['2xl']))

        # Center the buttons
        button_container = tk.Frame(action_frame, bg=ModernColors.BACKGROUND)
        button_container.pack(anchor="center")

        # Primary scan button with modern styling
        self.scan_button = ModernButton(
            button_container,
            text="🔍 Start Secure Scan",
            variant="primary",
            size="lg",
            command=self._start_scan
        )
        self.scan_button.pack(side=tk.LEFT, padx=(0, ModernColors.SPACING['lg']))

        # Secondary settings button
        self.settings_button = ModernButton(
            button_container,
            text="⚙️ Settings",
            variant="secondary",
            size="lg",
            command=self._open_settings
        )
        self.settings_button.pack(side=tk.LEFT)

    def _create_content_area(self, parent):
        """Create clean, minimal content area."""
        content_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        content_frame.pack(fill=tk.BOTH, expand=True, 
                          padx=ModernColors.SPACING['2xl'], 
                          pady=(0, ModernColors.SPACING['2xl']))

        # Modern card for content
        self.content_card = ModernCard(content_frame)
        self.content_card.pack(fill=tk.BOTH, expand=True)

        # Clean welcome state
        self._create_welcome_state()

    def _create_welcome_state(self):
        """Create clean welcome state without verbose text."""
        welcome_frame = tk.Frame(self.content_card.content, bg=ModernColors.CARD)
        welcome_frame.pack(fill=tk.BOTH, expand=True)

        # Center container
        center_frame = tk.Frame(welcome_frame, bg=ModernColors.CARD)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Modern icon/illustration placeholder
        icon_label = tk.Label(
            center_frame,
            text="🛡️",
            bg=ModernColors.CARD,
            fg=ModernColors.PRIMARY,
            font=("Segoe UI", 64)
        )
        icon_label.pack(pady=(0, ModernColors.SPACING['lg']))

        # Clean title
        title_label = tk.Label(
            center_frame,
            text="Ready to Secure Your System",
            bg=ModernColors.CARD,
            fg=ModernColors.FOREGROUND,
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, ModernColors.SPACING['sm']))

        # Minimal description
        desc_label = tk.Label(
            center_frame,
            text="Click 'Start Secure Scan' to begin analyzing your system for files that can be safely deleted.",
            bg=ModernColors.CARD,
            fg=ModernColors.SECONDARY_TEXT,
            font=("Segoe UI", 12),
            wraplength=400,
            justify="center"
        )
        desc_label.pack(pady=(0, ModernColors.SPACING['xl']))

        # Quick stats or features (minimal)
        features_frame = tk.Frame(center_frame, bg=ModernColors.CARD)
        features_frame.pack()

        features = [
            ("🔒", "Secure Deletion"),
            ("⚡", "Fast Scanning"),
            ("🎯", "Smart Detection")
        ]

        for i, (icon, text) in enumerate(features):
            feature_frame = tk.Frame(features_frame, bg=ModernColors.CARD)
            feature_frame.pack(side=tk.LEFT, padx=ModernColors.SPACING['lg'])

            feature_icon = tk.Label(
                feature_frame,
                text=icon,
                bg=ModernColors.CARD,
                fg=ModernColors.PRIMARY,
                font=("Segoe UI", 20)
            )
            feature_icon.pack()

            feature_text = tk.Label(
                feature_frame,
                text=text,
                bg=ModernColors.CARD,
                fg=ModernColors.MUTED_FOREGROUND,
                font=("Segoe UI", 9)
            )
            feature_text.pack(pady=(4, 0))

    def _setup_status_bar(self) -> None:
        """Create modern status bar at bottom of window."""
        status_frame = tk.Frame(self.root, bg=ModernColors.SURFACE_VARIANT, height=32)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        # Left side - status text
        self.status_text = tk.StringVar(value="SecureWipe Desktop - Ready")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_text,
            bg=ModernColors.SURFACE_VARIANT,
            fg=ModernColors.SECONDARY_TEXT,
            font=("Segoe UI", 9),
            anchor="w"
        )
        status_label.pack(side=tk.LEFT, padx=ModernColors.SPACING['md'], pady=6)

        # Right side - version info
        version_label = tk.Label(
            status_frame,
            text="v1.0.0",
            bg=ModernColors.SURFACE_VARIANT,
            fg=ModernColors.MUTED_FOREGROUND,
            font=("Segoe UI", 9),
            anchor="e"
        )
        version_label.pack(side=tk.RIGHT, padx=ModernColors.SPACING['md'], pady=6)

    def _start_scan(self) -> None:
        """Handle start scan button click with modern UI and optimized scanning."""
        self.logger.info("User initiated file scan")
        self._update_status("Scanning directories...", "info")
        self.scan_button.configure(state="disabled")
        
        try:
            # Import optimized components
            try:
                from ..scanner.file_scanner import FileScanner
                from ..scanner.categorizer import FileCategorizer
                from .modern_progress_dialog import ModernProgressDialog
                from .scan_results_viewer import ScanResultsViewer
                from ..deletion.secure_delete import SecureDeleteEngine
                from ..directory_detector import DirectoryDetector
            except ImportError:
                from scanner.file_scanner import FileScanner
                from scanner.categorizer import FileCategorizer
                from ui.modern_progress_dialog import ModernProgressDialog
                from ui.scan_results_viewer import ScanResultsViewer
                from deletion.secure_delete import SecureDeleteEngine
                from directory_detector import DirectoryDetector
            
            # Initialize components with optimized settings
            scanner = FileScanner(
                batch_size=5000,  # Larger batches for better performance
                progress_interval=0.05,  # More frequent updates for smooth UI
                max_workers=4  # Multi-threading for speed
            )
            categorizer = FileCategorizer()
            detector = DirectoryDetector(debug=self.debug)
            
            # Detect directories to scan
            user_dirs = detector.detect_user_directories()
            temp_dirs = detector.detect_temp_directories()
            
            # Collect accessible directories
            scan_directories = []
            for name, path in user_dirs.items():
                if path and path.exists():
                    scan_directories.append(path)
            
            # Add temp directories
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    scan_directories.append(temp_dir)
            
            if not scan_directories:
                messagebox.showwarning(
                    "No Directories",
                    "No accessible directories found to scan."
                )
                self._update_status("Ready", "ready")
                self.scan_button.configure(state="normal")
                return
            
            # Show modern progress dialog
            progress_dialog = ModernProgressDialog(
                self.root, 
                title="SecureWipe - File Scanning Progress"
            )
            
            # Start the optimized workflow
            self._run_optimized_workflow(
                scanner, categorizer, scan_directories, progress_dialog
            )
            
        except ImportError as e:
            self.logger.error(f"Component import error: {e}")
            messagebox.showerror(
                "Component Error",
                f"Required components not available: {e}\\n\\n"
                "Please ensure all components are properly installed."
            )
            self._update_status("Ready", "ready")
            self.scan_button.configure(state="normal")
        except Exception as e:
            self.logger.error(f"Scan initialization error: {e}")
            messagebox.showerror(
                "Scan Error",
                f"Error starting scan: {e}"
            )
            self._update_status("Ready", "ready")
            self.scan_button.configure(state="normal")

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
    
    def _run_optimized_workflow(self, scanner, categorizer, directories, progress_dialog):
        """Run the optimized scan and categorization workflow with modern UI."""
        import threading
        import time
        from tkinter import messagebox
        
        def workflow_thread():
            """Background thread for the optimized workflow."""
            try:
                # Start progress tracking without estimation (let scanner provide accurate count)
                progress_dialog.start_operation(
                    total_files=0,  # Will be updated by scanner
                    cancel_callback=lambda: setattr(scanner, '_cancelled', True)
                )
                
                # Phase 1: Accurate file scanning
                self.logger.info("Starting file scanning")
                progress_dialog.add_log("Starting file scanning...", "info")
                
                scanned_files = []
                
                def progress_callback(progress):
                    """Handle scan progress updates from scanner."""
                    # Update progress dialog with accurate data from scanner
                    progress_dialog.update_progress(
                        total_files=progress.total_files,
                        processed_files=progress.scanned_files,
                        current_file=str(progress.current_directory) if progress.current_directory else None,
                        current_directory=str(progress.current_directory) if progress.current_directory else None,
                        current_operation=f"Scanning {progress.current_directory.name if progress.current_directory else 'files'}...",
                        bytes_processed=progress.scanned_size
                    )
                
                def file_callback(file_info):
                    """Handle individual file discoveries."""
                    scanned_files.append(file_info)
                
                # Scan directories with accurate scanner
                scan_start = time.time()
                for file_info in scanner.scan_directories(
                    directories, progress_callback, file_callback
                ):
                    if scanner.is_cancelled:
                        break
                
                scan_duration = time.time() - scan_start
                
                if scanner.is_cancelled:
                    progress_dialog.add_log("Scan cancelled by user", "warning")
                    return
                
                self.scanned_files = scanned_files
                progress_dialog.add_log(
                    f"Scan completed: {len(scanned_files):,} files found in {scan_duration:.1f}s", 
                    "success"
                )
                
                # Phase 2: Fast file categorization
                self.logger.info("Starting file categorization")
                progress_dialog.add_log("Categorizing files by safety level...", "info")
                
                categorized_files = {
                    'Safe': [],
                    'Less Important': [],
                    'Important': [],
                    'Protected': []
                }
                
                categorize_start = time.time()
                for i, file_info in enumerate(scanned_files):
                    if scanner.is_cancelled:
                        break
                    
                    try:
                        category_result = categorizer.categorize_file(file_info)
                        category_name = category_result.category.value
                        
                        # Map category values to display names
                        category_map = {
                            'safe': 'Safe',
                            'lessImportant': 'Less Important', 
                            'important': 'Important',
                            'protected': 'Protected'
                        }
                        
                        display_category = category_map.get(category_name, 'Safe')
                        categorized_files[display_category].append(file_info)
                        
                        # Update progress
                        if i % 1000 == 0:  # Update every 1000 files for performance
                            progress_dialog.update_progress(
                                processed_files=i,
                                current_operation=f"Categorized {i:,}/{len(scanned_files):,} files"
                            )
                            
                    except Exception as e:
                        self.logger.warning(f"Error categorizing file {file_info}: {e}")
                        categorized_files['Safe'].append(file_info)  # Default to safe
                
                categorize_duration = time.time() - categorize_start
                self.categorized_files = categorized_files
                
                progress_dialog.add_log(
                    f"Categorization completed in {categorize_duration:.1f}s", 
                    "success"
                )
                
                # Complete the operation
                progress_dialog.complete_operation()
                
                # Phase 3: Show comprehensive results
                progress_dialog.after(0, lambda: self._show_modern_scan_results(progress_dialog))
                
            except Exception as e:
                self.logger.error(f"Workflow error: {e}")
                progress_dialog.add_log(f"Workflow error: {str(e)}", "error")
                messagebox.showerror(
                    "Workflow Error", f"An error occurred during scanning: {e}"
                )
            finally:
                # Re-enable scan button
                self.root.after(0, lambda: self.scan_button.configure(state="normal"))
                self.root.after(0, lambda: self._update_status("Scan completed", "success"))
        
        # Start workflow in background thread
        workflow_thread_obj = threading.Thread(target=workflow_thread, daemon=True)
        workflow_thread_obj.start()
        
        # Show progress dialog (it's already modal)
    
    def _show_modern_scan_results(self, progress_dialog):
        """Show comprehensive scan results with modern UI."""
        try:
            from .scan_results_viewer import ScanResultsViewer
        except ImportError:
            from ui.scan_results_viewer import ScanResultsViewer
        
        # Close progress dialog
        progress_dialog.destroy()
        
        # Prepare scan results data
        scan_results = {
            'total_files': len(self.scanned_files),
            'categorized_files': self.categorized_files,
            'scan_summary': {
                'safe_count': len(self.categorized_files.get('Safe', [])),
                'less_important_count': len(self.categorized_files.get('Less Important', [])),
                'important_count': len(self.categorized_files.get('Important', [])),
                'protected_count': len(self.categorized_files.get('Protected', []))
            }
        }
        
        # Show comprehensive results viewer
        results_viewer = ScanResultsViewer(self.root, scan_results)
        result = results_viewer.show_results()
        
        if result:
            if result['action'] == 'proceed':
                # User selected files for deletion
                selected_files = result['selected_files']
                if selected_files:
                    self._start_secure_deletion(selected_files)
                else:
                    messagebox.showinfo("No Selection", "No files were selected for deletion.")
            
            elif result['action'] == 'modify':
                # User wants to modify scan settings
                messagebox.showinfo("Modify Scan", "Scan modification will be available in future updates.")
            
            # 'cancel' action requires no further processing
    
    def _start_secure_deletion(self, files_to_delete):
        """Start the secure deletion process with progress tracking."""
        try:
            from ..deletion.secure_delete import SecureDeleteEngine
            from .progress_dialog import ProgressDialog
        except ImportError:
            from deletion.secure_delete import SecureDeleteEngine
            from ui.progress_dialog import ProgressDialog
        from tkinter import messagebox
        import threading
        
        if not files_to_delete:
            messagebox.showinfo("No Files", "No files selected for deletion.")
            return
        
        # Final confirmation
        confirm_message = (
            f"FINAL CONFIRMATION\\n\\n"
            f"You are about to PERMANENTLY DELETE {len(files_to_delete):,} files.\\n"
            f"This action CANNOT be undone.\\n\\n"
            f"Are you absolutely sure you want to proceed?"
        )
        
        final_confirm = messagebox.askyesno(
            "Final Confirmation", 
            confirm_message,
            icon='warning'
        )
        
        if not final_confirm:
            self.logger.info("User cancelled deletion at final confirmation")
            return
        
        # Create deletion progress dialog
        deletion_dialog = ProgressDialog(
            self.root,
            title="SecureWipe - Secure Deletion Progress"
        )
        
        # Initialize deletion engine with progress callback
        def deletion_progress_callback(progress_info):
            """Handle deletion progress updates."""
            deletion_dialog.after(0, lambda: deletion_dialog._update_ui(progress_info))
        
        deletion_engine = SecureDeleteEngine(progress_callback=deletion_progress_callback)
        
        def deletion_thread():
            """Background thread for secure deletion."""
            try:
                self.logger.info(f"Starting secure deletion of {len(files_to_delete)} files")
                
                # Execute secure deletion synchronously
                results = deletion_engine.delete_files_sync(files_to_delete)
                
                # Show completion results
                deletion_dialog.after(0, lambda: self._show_deletion_results(results, deletion_dialog, deletion_engine))
                
            except Exception as e:
                self.logger.error(f"Deletion error: {e}")
                deletion_dialog.after(0, lambda: deletion_dialog._log_message(
                    f"Deletion error: {str(e)}", "ERROR"
                ))
                deletion_dialog.after(0, lambda: messagebox.showerror(
                    "Deletion Error", f"An error occurred during deletion: {e}"
                ))
        
        # Start deletion in background thread
        deletion_thread_obj = threading.Thread(target=deletion_thread, daemon=True)
        deletion_thread_obj.start()
        
        # Show deletion progress dialog
        deletion_dialog.transient(self.root)
        deletion_dialog.grab_set()
    
    def _show_deletion_results(self, results, deletion_dialog, deletion_engine=None):
        """Show deletion completion results with certificate option."""
        from tkinter import messagebox
        
        # Close deletion dialog
        deletion_dialog.destroy()
        
        # Show results
        success_count = sum(1 for r in results if r.status.name == 'SUCCESS')
        error_count = sum(1 for r in results if r.status.name == 'ERROR')
        skipped_count = sum(1 for r in results if r.status.name == 'SKIPPED')
        
        result_message = (
            f"Secure Deletion Complete\\n\\n"
            f"Successfully deleted: {success_count:,} files\\n"
            f"Errors: {error_count:,} files\\n"
            f"Skipped: {skipped_count:,} files\\n\\n"
            f"All selected files have been securely overwritten and are unrecoverable."
        )
        
        # Check if certificate was generated
        certificate_info = None
        if deletion_engine:
            certificate_info = deletion_engine.get_last_certificate()
        
        if certificate_info:
            result_message += "\\n\\nA cryptographic certificate has been generated to verify this operation."
            
            # Show results with certificate option
            result = messagebox.askyesno(
                "Deletion Complete", 
                result_message + "\\n\\nWould you like to view the certificate?",
                icon='question'
            )
            
            if result:
                self._show_certificate_viewer(certificate_info)
        else:
            messagebox.showinfo("Deletion Complete", result_message)
        
        self.logger.info(f"Deletion completed: {success_count} success, {error_count} errors, {skipped_count} skipped")

    def _show_certificate_viewer(self, certificate_info):
        """Show certificate viewer window."""
        try:
            try:
                from .certificate_viewer import CertificateViewer
            except ImportError:
                from ui.certificate_viewer import CertificateViewer
            
            certificate, certificate_path = certificate_info
            viewer = CertificateViewer(self.root)
            viewer.show_certificate(certificate, certificate_path)
            
        except Exception as e:
            self.logger.error(f"Failed to show certificate viewer: {e}")
            messagebox.showerror(
                "Certificate Error",
                f"Failed to display certificate: {e}"
            )
    
    def _update_status(self, message: str, status_type: str = "info"):
        """Update the status display with modern styling."""
        self.status_var.set(message)
        
        # Update status color based on type
        colors = {
            "info": ModernColors.INFO,
            "success": ModernColors.SUCCESS,
            "warning": ModernColors.WARNING,
            "error": ModernColors.ERROR,
            "ready": ModernColors.SUCCESS
        }
        
        color = colors.get(status_type, ModernColors.SECONDARY_TEXT)
        self.status_label.configure(fg=color)

    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.logger.info("Starting SecureWipe Desktop main loop")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
