# Requirements

## Functional

**FR1:** Desktop application scans user directories (Documents, Downloads, Desktop, temp folders) and displays files with size/count summaries  
**FR2:** System categorizes files using rule-based logic (extension, path, access time) into "Safe to Delete/Less Important/Important" categories  
**FR3:** AI suggestions appear in separate tab as advisory-only recommendations with confidence scoring  
**FR4:** Secure file deletion uses OS-native tools (sdelete on Windows, shred on Linux) with real-time progress visualization  
**FR5:** System generates JSON certificates with device ID, timestamp, file paths, and cryptographic signatures using local self-signed keys  
**FR6:** Standalone verifier application validates certificate signatures against embedded public keys without internet dependency  
**FR7:** Bootable ISO provides simple wizard interface for complete system wiping with hardware detection  
**FR8:** System gracefully handles edge cases including locked files, encrypted drives, and non-English filenames with clear user messaging  
**FR9:** Double confirmation prevents accidental deletion of critical system files through safe defaults  
**FR10:** Certificate verification demonstrates tamper-proof nature through QR codes and local verification tools

## Non Functional

**NFR1:** Complete user folder scan completes in under 2 minutes for typical user data volumes  
**NFR2:** File deletion progress displays in real-time with plain-language status messages  
**NFR3:** Complete wipe process from scan to certificate takes under 10 minutes  
**NFR4:** Bootable ISO boots successfully in VM environment with UEFI/Secure Boot compatibility  
**NFR5:** Cross-platform compatibility supports Windows 10/11 (primary) and Linux Ubuntu/Debian (secondary)  
**NFR6:** Offline-first architecture operates without internet dependencies or cloud services  
**NFR7:** NIST SP 800-88 compliant deletion methods for demonstration purposes  
**NFR8:** Certificate verification achieves 100% accuracy using offline cryptographic validation  
**NFR9:** System handles 90%+ of common edge cases without crashes or data loss  
**NFR10:** Modular codebase enables parallel team development with shared JSON certificate format
