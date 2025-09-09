# Epic 1 Foundation & Core Infrastructure

**Epic Goal:** Establish project foundation with shared certificate schema, basic desktop file scanning, and rule-based categorization while delivering initial functional value through a working file scanner that demonstrates the core concept.

## Story 1.1 Project Setup and Shared Certificate Schema

As a **development team member**,  
I want **a properly configured monorepo with shared certificate schema**,  
so that **both desktop and bootable teams can develop in parallel with guaranteed certificate compatibility**.

### Acceptance Criteria
1. Monorepo structure created with desktop-app/, bootable-iso/, and shared/ folders
2. JSON Schema v1.0.0 defined in shared/schema.json with required fields (deviceId, timestamp, files, signature)
3. Python validation script validates certificate format compatibility
4. Git repository initialized with lightweight validation scripts (not full CI/CD)
5. Development environment setup documentation created for both teams
6. Shared cryptography library integration (pyca/cryptography) with basic key generation
7. Schema designed for additive-only changes with version compatibility

## Story 1.2 Desktop Application Foundation

As a **desktop application user**,  
I want **a basic desktop application that launches successfully on Windows**,  
so that **I can begin the file scanning process with confidence**.

### Acceptance Criteria
1. Python desktop application launches without errors on Windows 10/11
2. UI framework choice finalized by day 2 (tkinter for simplicity or Electron for richer UX)
3. Basic UI displays main window with SecureWipe branding and clear navigation
4. Application detects current user directories (Documents, Downloads, Desktop, temp folders)
5. Application gracefully handles missing directories or permission issues with clear messaging
6. Basic logging framework integrated for debugging and audit trail
7. Linux compatibility as stretch goal, not blocking requirement

## Story 1.3 File System Scanner with Progressive Display

As a **user preparing to dispose of my device**,  
I want **to see files being discovered in real-time with size and count information**,  
so that **I understand what data exists and can see progress even on slower systems**.

### Acceptance Criteria
1. Scanner traverses user directories and catalogs files with metadata (path, size, modified date)
2. Progressive display shows files as they're discovered, not waiting for complete scan
3. File count and total size updated in real-time for each directory category
4. Progress indicator shows scanning status with plain-language messages and estimated completion
5. Scanner handles edge cases gracefully: locked files (skip with notification), non-English filenames, symbolic links
6. Results displayed in organized list view with expandable directory trees
7. Scanning performance optimized for I/O efficiency, with fallback messaging for slow systems

## Story 1.4 Rule-Based File Categorization

As a **non-technical user**,  
I want **files automatically categorized by safety level with clear explanations**,  
so that **I can make informed decisions without technical expertise**.

### Acceptance Criteria
1. Files categorized into "Safe to Delete", "Less Important", and "Important" based on documented rules
2. Categorization rules consider file extension, path location, and last access time
3. System files and critical directories automatically marked as "Important" with explanations
4. Temporary files, cache, and downloads marked as "Safe to Delete" with rationale
5. User documents and media files marked as "Less Important" by default
6. Category assignment displayed with clear visual indicators and plain-language explanations
7. Manual override allows users to change category assignments with confirmation dialogs
8. Category rules documented and easily modifiable for future enhancements
9. Bulk operations available for changing multiple file categories efficiently
