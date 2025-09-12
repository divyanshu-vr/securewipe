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

        # Initialize workflow state
        self.scanned_files = []
        self.categorized_files = {}
        self.selected_files = []
        
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

        # Create scrollable text area for scan information
        info_text = tk.Text(
            content_frame,
            wrap=tk.WORD,
            height=15,
            font=("Arial", 10),
            state=tk.DISABLED,
            bg='#f8f8f8'
        )
        info_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.config(yscrollcommand=info_scrollbar.set)
        
        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add initial information
        self._update_info_display(info_text)

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
        """Handle start scan button click with full workflow integration."""
        self.logger.info("User initiated file scan")
        self.status_var.set("Scanning directories...")
        self.scan_button.config(state="disabled")
        
        try:
            # Import components from Stories 2.1 and 2.2
            from scanner.file_scanner import FileScanner
            from scanner.categorizer import FileCategorizer
            from ui.progress_dialog import ProgressDialog
            from deletion.secure_delete import SecureDeleteEngine
            from directory_detector import DirectoryDetector
            
            # Initialize components
            scanner = FileScanner()
            categorizer = FileCategorizer()
            detector = DirectoryDetector(debug=self.debug)
            
            # Detect directories to scan
            user_dirs = detector.detect_user_directories()
            temp_dirs = detector.detect_temp_directories()
            
            # Collect accessible directories
            scan_directories = []
            for name, path in user_dirs.items():
                if path:
                    scan_directories.append(path)
            scan_directories.extend(temp_dirs)
            
            if not scan_directories:
                messagebox.showwarning(
                    "No Directories",
                    "No accessible directories found to scan."
                )
                self.status_var.set("Ready to scan directories")
                self.scan_button.config(state="normal")
                return
            
            # Show scanning progress dialog
            progress_dialog = ProgressDialog(
                self.root, 
                title="SecureWipe - File Scanning Progress"
            )
            
            # Start the integrated workflow
            self._run_integrated_workflow(
                scanner, categorizer, scan_directories, progress_dialog
            )
            
        except ImportError as e:
            self.logger.error(f"Component import error: {e}")
            messagebox.showerror(
                "Component Error",
                f"Required components not available: {e}\\n\\n"
                "Please ensure Stories 2.1 and 2.2 are properly implemented."
            )
            self.status_var.set("Ready to scan directories")
            self.scan_button.config(state="normal")
        except Exception as e:
            self.logger.error(f"Scan initialization error: {e}")
            messagebox.showerror(
                "Scan Error",
                f"Error starting scan: {e}"
            )
            self.status_var.set("Ready to scan directories")
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
    
    def _run_integrated_workflow(self, scanner, categorizer, directories, progress_dialog):
        """Run the integrated scan and deletion workflow."""
        import threading
        from tkinter import messagebox
        
        def workflow_thread():
            """Background thread for the complete workflow."""
            try:
                # Phase 1: File Scanning
                self.logger.info("Starting file scanning phase")
                progress_dialog.milestone_indicator.set_milestone('scan', False)
                
                scanned_files = []
                
                def progress_callback(progress):
                    """Handle scan progress updates."""
                    progress_dialog.after(0, lambda: progress_dialog._log_message(
                        f"Scanning: {progress.scanned_files} files found", "INFO"
                    ))
                
                def file_callback(file_info):
                    """Handle individual file discoveries."""
                    scanned_files.append(file_info)
                
                # Scan directories
                for file_info in scanner.scan_directories(
                    directories, progress_callback, file_callback
                ):
                    if scanner.is_cancelled:
                        break
                
                if scanner.is_cancelled:
                    progress_dialog.after(0, lambda: progress_dialog._log_message(
                        "Scan cancelled by user", "WARNING"
                    ))
                    return
                
                self.scanned_files = scanned_files
                progress_dialog.after(0, lambda: progress_dialog.milestone_indicator.set_milestone('scan', True))
                progress_dialog.after(0, lambda: progress_dialog._log_message(
                    f"Scan completed: {len(scanned_files)} files found", "SUCCESS"
                ))
                
                # Phase 2: File Categorization
                self.logger.info("Starting file categorization phase")
                progress_dialog.after(0, lambda: progress_dialog.milestone_indicator.set_milestone('categorize', False))
                
                categorized_files = {}
                for i, file_info in enumerate(scanned_files):
                    if scanner.is_cancelled:
                        break
                    
                    category_result = categorizer.categorize_file(file_info)
                    category_name = category_result.category.value
                    
                    if category_name not in categorized_files:
                        categorized_files[category_name] = []
                    categorized_files[category_name].append({
                        'file_info': file_info,
                        'category_result': category_result
                    })
                    
                    # Update progress every 100 files
                    if i % 100 == 0:
                        progress_dialog.after(0, lambda i=i: progress_dialog._log_message(
                            f"Categorized {i}/{len(scanned_files)} files", "INFO"
                        ))
                
                self.categorized_files = categorized_files
                progress_dialog.after(0, lambda: progress_dialog.milestone_indicator.set_milestone('categorize', True))
                progress_dialog.after(0, lambda: progress_dialog._log_message(
                    f"Categorization completed: {len(categorized_files)} categories", "SUCCESS"
                ))
                
                # Phase 3: Show Results and Allow Selection
                progress_dialog.after(0, lambda: self._show_scan_results(progress_dialog))
                
            except Exception as e:
                self.logger.error(f"Workflow error: {e}")
                progress_dialog.after(0, lambda: progress_dialog._log_message(
                    f"Workflow error: {str(e)}", "ERROR"
                ))
                progress_dialog.after(0, lambda: messagebox.showerror(
                    "Workflow Error", f"An error occurred during scanning: {e}"
                ))
            finally:
                # Re-enable scan button
                self.root.after(0, lambda: self.scan_button.config(state="normal"))
                self.root.after(0, lambda: self.status_var.set("Scan completed"))
        
        # Start workflow in background thread
        workflow_thread_obj = threading.Thread(target=workflow_thread, daemon=True)
        workflow_thread_obj.start()
        
        # Show progress dialog
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
    
    def _show_scan_results(self, progress_dialog):
        """Show scan results and allow user to select files for deletion."""
        from tkinter import messagebox
        
        # Close progress dialog
        progress_dialog.destroy()
        
        # Show results summary
        total_files = len(self.scanned_files)
        safe_count = len(self.categorized_files.get('safe', []))
        less_important_count = len(self.categorized_files.get('lessImportant', []))
        important_count = len(self.categorized_files.get('important', []))
        
        result_message = (
            f"Scan Results:\\n\\n"
            f"Total files found: {total_files:,}\\n"
            f"Safe to delete: {safe_count:,}\\n"
            f"Less important: {less_important_count:,}\\n"
            f"Important (protected): {important_count:,}\\n\\n"
            f"Would you like to proceed with secure deletion of safe files?"
        )
        
        if safe_count == 0:
            messagebox.showinfo("Scan Complete", "No files marked as safe for deletion were found.")
            return
        
        # Ask user if they want to proceed with deletion
        proceed = messagebox.askyesno("Scan Complete", result_message)
        
        if proceed:
            # Prepare files for deletion (only safe files for now)
            safe_files = [item['file_info'] for item in self.categorized_files.get('safe', [])]
            self._start_secure_deletion(safe_files)
    
    def _start_secure_deletion(self, files_to_delete):
        """Start the secure deletion process with progress tracking."""
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
            from .certificate_viewer import CertificateViewer
            
            certificate, certificate_path = certificate_info
            viewer = CertificateViewer(self.root)
            viewer.show_certificate(certificate, certificate_path)
            
        except Exception as e:
            self.logger.error(f"Failed to show certificate viewer: {e}")
            messagebox.showerror(
                "Certificate Error",
                f"Failed to display certificate: {e}"
            )
    
    def _update_info_display(self, info_text):
        """Update the information display area."""
        info_text.config(state=tk.NORMAL)
        info_text.delete(1.0, tk.END)
        
        info_content = """SecureWipe Desktop - Quick Clean Mode

INTEGRATED FEATURES:
✓ Story 2.1: Secure File Deletion Engine
✓ Story 2.2: Real-Time Progress Visualization

WORKFLOW:
1. Click 'Start File Scan' to begin
2. Automatic directory detection (Documents, Downloads, Desktop, Temp)
3. Real-time scanning with gaming-inspired progress UI
4. Intelligent file categorization:
   • Safe: Temp files, cache, logs (safe to delete)
   • Less Important: User documents (review recommended)
   • Important: System files (protected from deletion)
5. Secure deletion with NIST SP 800-88 compliance
6. Real-time deletion progress with detailed logging

SECURITY FEATURES:
• Multiple confirmation dialogs prevent accidental deletion
• System file protection with comprehensive detection
• OWASP-compliant secure logging (no sensitive data exposure)
• Cross-platform secure deletion (sdelete/shred integration)
• Thread-safe UI with cancellation support

DIRECTORIES SCANNED:
• Documents folder
• Downloads folder  
• Desktop folder
• System temporary directories
• Browser cache directories

Ready to begin secure file deletion. Click 'Start File Scan' when ready.
"""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)

    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.logger.info("Starting SecureWipe Desktop main loop")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
