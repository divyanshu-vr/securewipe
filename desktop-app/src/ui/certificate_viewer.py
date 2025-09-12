"""Certificate viewer and export functionality."""

import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

# Add shared modules to path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))

try:
    from shared.models.certificate import Certificate
    from shared.utils.qr_generator import generate_certificate_qr, is_qr_available
    from shared.secure_logging.secure_logger import get_logger
except ImportError:
    # Fallback for different import contexts
    from shared.models.certificate import Certificate
    from shared.utils.qr_generator import generate_certificate_qr, is_qr_available
    from shared.secure_logging.secure_logger import get_logger

logger = get_logger(__name__)


class CertificateViewer:
    """Certificate display and export interface."""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.certificate: Optional[Certificate] = None
        self.qr_image: Optional[bytes] = None
        
    def show_certificate(self, certificate: Certificate, certificate_path: Path):
        """
        Display certificate in a new window.
        
        Args:
            certificate: Certificate data to display
            certificate_path: Path where certificate was saved
        """
        self.certificate = certificate
        
        # Create certificate window
        cert_window = tk.Toplevel(self.parent)
        cert_window.title("SecureWipe Certificate")
        cert_window.geometry("800x600")
        cert_window.resizable(True, True)
        
        # Create main frame with scrollbar
        main_frame = ttk.Frame(cert_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Certificate info frame
        info_frame = ttk.LabelFrame(main_frame, text="Certificate Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._create_certificate_info(info_frame)
        
        # Operation summary frame
        summary_frame = ttk.LabelFrame(main_frame, text="Operation Summary")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._create_operation_summary(summary_frame)
        
        # QR code frame (if available)
        if is_qr_available():
            qr_frame = ttk.LabelFrame(main_frame, text="QR Code")
            qr_frame.pack(fill=tk.X, pady=(0, 10))
            
            self._create_qr_display(qr_frame, certificate_path)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Export Certificate",
            command=lambda: self._export_certificate(certificate_path)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="View JSON",
            command=self._view_json
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Close",
            command=cert_window.destroy
        ).pack(side=tk.RIGHT)
        
        logger.info("Certificate viewer displayed")
    
    def _create_certificate_info(self, parent: ttk.Frame):
        """Create certificate information display."""
        cert = self.certificate
        
        # Certificate ID and timestamp
        ttk.Label(parent, text="Certificate ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=cert.certificate_id).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Generated:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=cert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Device information
        ttk.Label(parent, text="Device ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=cert.device_info.device_id[:16] + "...").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Hostname:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=cert.device_info.hostname).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Operating System:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=f"{cert.device_info.operating_system} ({cert.device_info.architecture})").grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
    
    def _create_operation_summary(self, parent: ttk.Frame):
        """Create operation summary display."""
        summary = self.certificate.deletion_summary
        
        # Operation statistics
        ttk.Label(parent, text="Operation Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=self.certificate.operation_type.value.replace('_', ' ').title()).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Deletion Method:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=summary.deletion_method.value.upper()).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Total Files:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=f"{summary.total_files:,}").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Total Size:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=self._format_size(summary.total_size_bytes)).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Duration:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(parent, text=f"{summary.duration_seconds:.1f} seconds").grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(parent, text="Success Rate:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        success_rate = (summary.success_count / summary.total_files * 100) if summary.total_files > 0 else 0
        ttk.Label(parent, text=f"{success_rate:.1f}% ({summary.success_count}/{summary.total_files})").grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
    
    def _create_qr_display(self, parent: ttk.Frame, certificate_path: Path):
        """Create QR code display."""
        try:
            # Generate QR code
            qr_data = generate_certificate_qr(certificate_path)
            if qr_data:
                self.qr_image = qr_data
                
                # Display QR code info
                ttk.Label(parent, text="QR Code generated for certificate sharing").pack(pady=5)
                
                ttk.Button(
                    parent,
                    text="Save QR Code",
                    command=self._save_qr_code
                ).pack(pady=5)
            else:
                ttk.Label(parent, text="QR code generation not available").pack(pady=5)
                
        except Exception as e:
            logger.error(f"QR code display failed: {e}")
            ttk.Label(parent, text="QR code generation failed").pack(pady=5)
    
    def _export_certificate(self, current_path: Path):
        """Export certificate to user-specified location."""
        try:
            # Ask user for export location
            export_path = filedialog.asksaveasfilename(
                title="Export Certificate",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname=f"securewipe_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if export_path:
                # Copy certificate to new location
                import shutil
                shutil.copy2(current_path, export_path)
                
                messagebox.showinfo(
                    "Export Complete",
                    f"Certificate exported to:\n{export_path}"
                )
                logger.info(f"Certificate exported to {export_path}")
                
        except Exception as e:
            logger.error(f"Certificate export failed: {e}")
            messagebox.showerror("Export Failed", f"Failed to export certificate:\n{e}")
    
    def _save_qr_code(self):
        """Save QR code image."""
        if not self.qr_image:
            return
            
        try:
            qr_path = filedialog.asksaveasfilename(
                title="Save QR Code",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialname=f"certificate_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            
            if qr_path:
                with open(qr_path, 'wb') as f:
                    f.write(self.qr_image)
                
                messagebox.showinfo(
                    "QR Code Saved",
                    f"QR code saved to:\n{qr_path}"
                )
                logger.info(f"QR code saved to {qr_path}")
                
        except Exception as e:
            logger.error(f"QR code save failed: {e}")
            messagebox.showerror("Save Failed", f"Failed to save QR code:\n{e}")
    
    def _view_json(self):
        """Display certificate JSON in a new window."""
        if not self.certificate:
            return
            
        # Create JSON window
        json_window = tk.Toplevel(self.parent)
        json_window.title("Certificate JSON")
        json_window.geometry("600x400")
        
        # Create text widget with scrollbar
        frame = ttk.Frame(json_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Convert certificate to JSON
        cert_dict = self._certificate_to_dict()
        json_str = json.dumps(cert_dict, indent=2, default=str)
        
        text_widget.insert(tk.END, json_str)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _certificate_to_dict(self) -> dict:
        """Convert certificate to dictionary for JSON serialization."""
        cert = self.certificate
        
        return {
            "schemaVersion": cert.schema_version,
            "certificateId": cert.certificate_id,
            "timestamp": cert.timestamp.isoformat(),
            "deviceInfo": {
                "deviceId": cert.device_info.device_id,
                "hostname": cert.device_info.hostname,
                "operatingSystem": cert.device_info.operating_system,
                "architecture": cert.device_info.architecture,
                "userContext": cert.device_info.user_context
            },
            "operationType": cert.operation_type.value,
            "deletionSummary": {
                "totalFiles": cert.deletion_summary.total_files,
                "totalSizeBytes": cert.deletion_summary.total_size_bytes,
                "deletionMethod": cert.deletion_summary.deletion_method.value,
                "durationSeconds": cert.deletion_summary.duration_seconds,
                "successCount": cert.deletion_summary.success_count,
                "failureCount": cert.deletion_summary.failure_count
            },
            "fileOperations": [
                {
                    k: v for k, v in {
                        "path": op.path,
                        "sizeBytes": op.size_bytes,
                        "operation": op.operation.value,
                        "reason": op.reason
                    }.items() if v is not None
                }
                for op in cert.file_operations
            ],
            "cryptographicProof": {
                "algorithm": cert.cryptographic_proof.algorithm,
                "publicKey": cert.cryptographic_proof.public_key,
                "signature": cert.cryptographic_proof.signature,
                "signatureFormat": cert.cryptographic_proof.signature_format
            }
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"