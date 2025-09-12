#!/usr/bin/env python3
"""
Demo script to generate and display a sample certificate.
This shows what a SecureWipe certificate looks like.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

def main():
    """Generate and display a sample certificate."""
    try:
        from certificate.certificate_generator import CertificateGenerator
        
        print("🔐 SecureWipe Certificate Generation Demo")
        print("=" * 50)
        
        # Create certificate generator
        generator = CertificateGenerator()
        print("✓ Certificate generator initialized")
        
        # Sample operation data
        operation_data = {
            "operation_type": "quick_clean",
            "deletion_method": "sdelete",
            "duration_seconds": 45.7
        }
        
        # Sample file operations (realistic data)
        file_operations = [
            {
                "path": "C:\\Users\\John\\AppData\\Local\\Temp\\tmp_file_001.tmp",
                "size_bytes": 2048576,  # 2MB
                "status": "deleted"
            },
            {
                "path": "C:\\Users\\John\\Downloads\\old_document.pdf",
                "size_bytes": 5242880,  # 5MB
                "status": "deleted"
            },
            {
                "path": "C:\\Users\\John\\Documents\\cache\\browser_cache.dat",
                "size_bytes": 15728640,  # 15MB
                "status": "deleted"
            },
            {
                "path": "C:\\Users\\John\\AppData\\Roaming\\app_logs.log",
                "size_bytes": 1048576,  # 1MB
                "status": "deleted"
            },
            {
                "path": "C:\\Windows\\System32\\important.dll",
                "size_bytes": 524288,  # 512KB
                "status": "failed",
                "reason": "System file - access denied"
            },
            {
                "path": "C:\\Users\\John\\Desktop\\temp_notes.txt",
                "size_bytes": 4096,  # 4KB
                "status": "deleted"
            }
        ]
        
        print(f"📁 Processing {len(file_operations)} file operations...")
        
        # Generate certificate
        certificate, cert_path = generator.generate_certificate(
            operation_data, 
            file_operations,
            Path("demo_certificate.json")
        )
        
        print(f"✓ Certificate generated: {cert_path}")
        
        # Display certificate contents
        print("\n📋 Certificate Contents:")
        print("=" * 50)
        
        with open(cert_path, 'r', encoding='utf-8') as f:
            cert_data = json.load(f)
        
        # Pretty print the certificate
        print(json.dumps(cert_data, indent=2, default=str))
        
        # Summary statistics
        print("\n📊 Certificate Summary:")
        print("=" * 30)
        print(f"Certificate ID: {cert_data['certificateId']}")
        print(f"Generated: {cert_data['timestamp']}")
        print(f"Device: {cert_data['deviceInfo']['hostname']} ({cert_data['deviceInfo']['operatingSystem']})")
        print(f"Operation: {cert_data['operationType'].replace('_', ' ').title()}")
        print(f"Deletion Method: {cert_data['deletionSummary']['deletionMethod'].upper()}")
        print(f"Total Files: {cert_data['deletionSummary']['totalFiles']:,}")
        print(f"Total Size: {cert_data['deletionSummary']['totalSizeBytes']:,} bytes ({cert_data['deletionSummary']['totalSizeBytes'] / 1024 / 1024:.1f} MB)")
        print(f"Success Rate: {cert_data['deletionSummary']['successCount']}/{cert_data['deletionSummary']['totalFiles']} ({cert_data['deletionSummary']['successCount']/cert_data['deletionSummary']['totalFiles']*100:.1f}%)")
        print(f"Duration: {cert_data['deletionSummary']['durationSeconds']:.1f} seconds")
        print(f"Signature Algorithm: {cert_data['cryptographicProof']['algorithm']}")
        
        # File operations breakdown
        print(f"\n📄 File Operations Breakdown:")
        print("-" * 30)
        for i, op in enumerate(cert_data['fileOperations'], 1):
            status_emoji = "✅" if op['operation'] == 'deleted' else "❌" if op['operation'] == 'failed' else "⏭️"
            size_mb = op['sizeBytes'] / 1024 / 1024
            print(f"{i:2d}. {status_emoji} {Path(op['path']).name} ({size_mb:.1f} MB)")
            if op['operation'] == 'failed' and 'reason' in op:
                print(f"     └─ Reason: {op['reason']}")
        
        print(f"\n🔒 Cryptographic Verification:")
        print("-" * 30)
        is_valid = generator.verify_certificate(cert_path)
        print(f"Signature Valid: {'✅ YES' if is_valid else '❌ NO'}")
        
        print(f"\n💾 Certificate saved to: {cert_path.absolute()}")
        print("\nThis certificate provides cryptographic proof of the secure deletion operation.")
        print("It can be shared, verified independently, and serves as compliance documentation.")
        
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()