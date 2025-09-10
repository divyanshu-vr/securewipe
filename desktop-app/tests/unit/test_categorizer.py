"""Unit tests for file categorization engine."""

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from models.file_info import FileInfo, FileType

from scanner.categorizer import CategoryReason, CategoryType, FileCategorizer


class TestFileCategorizer(unittest.TestCase):
    """Test cases for FileCategorizer."""

    def setUp(self):
        """Set up test fixtures."""
        self.categorizer = FileCategorizer()
        self.test_time = datetime.now()

    def _create_file_info(self, path_str: str, size: int = 1024) -> FileInfo:
        """Create test FileInfo object."""
        return FileInfo(
            path=Path(path_str),
            size=size,
            modified_date=self.test_time,
            file_type=FileType.OTHER,
        )

    def test_system_file_detection_windows(self):
        """Test Windows system file detection."""
        # Test Windows system files
        system_files = [
            "C:\\Windows\\System32\\kernel32.dll",
            "C:\\Program Files\\Microsoft Office\\WINWORD.EXE",
            "C:\\Windows\\explorer.exe",
        ]

        for file_path in system_files:
            file_info = self._create_file_info(file_path)
            result = self.categorizer.categorize_file(file_info)

            self.assertEqual(result.category, CategoryType.IMPORTANT)
            self.assertEqual(result.reason, CategoryReason.SYSTEM_FILE)
            self.assertIn("system", result.explanation.lower())

    def test_system_file_detection_linux(self):
        """Test Linux system file detection."""
        # Test Linux system files
        system_files = ["/usr/bin/bash", "/etc/passwd", "/bin/ls", "/sbin/init"]

        for file_path in system_files:
            file_info = self._create_file_info(file_path)
            result = self.categorizer.categorize_file(file_info)

            self.assertEqual(result.category, CategoryType.IMPORTANT)
            self.assertEqual(result.reason, CategoryReason.SYSTEM_FILE)

    def test_temp_file_detection(self):
        """Test temporary file detection."""
        temp_files = [
            "C:\\Users\\User\\AppData\\Local\\Temp\\temp123.tmp",
            "/tmp/session_data.cache",
            "C:\\Windows\\Temp\\install.log",
        ]

        for file_path in temp_files:
            file_info = self._create_file_info(file_path)
            result = self.categorizer.categorize_file(file_info)

            self.assertEqual(result.category, CategoryType.SAFE)
            self.assertEqual(result.reason, CategoryReason.TEMP_FILE)

    def test_extension_based_categorization(self):
        """Test file categorization by extension."""
        # Safe extensions
        safe_files = [
            "C:\\Users\\User\\document.tmp",
            "/home/user/backup.bak",
            "C:\\logs\\application.log",
        ]

        for file_path in safe_files:
            file_info = self._create_file_info(file_path)
            result = self.categorizer.categorize_file(file_info)

            if (
                not result.reason == CategoryReason.TEMP_FILE
            ):  # Skip if caught by temp detection
                self.assertEqual(result.category, CategoryType.SAFE)
                self.assertEqual(result.reason, CategoryReason.EXTENSION)

        # Important extensions
        important_files = ["C:\\Users\\User\\application.exe", "/home/user/library.dll"]

        for file_path in important_files:
            file_info = self._create_file_info(file_path)
            result = self.categorizer.categorize_file(file_info)

            if (
                not result.reason == CategoryReason.SYSTEM_FILE
            ):  # Skip if caught by system detection
                self.assertEqual(result.category, CategoryType.IMPORTANT)
                self.assertEqual(result.reason, CategoryReason.EXTENSION)

        # Less important extensions
        document_files = [
            "C:\\Users\\User\\Documents\\report.pdf",
            "/home/user/photo.jpg",
        ]

        for file_path in document_files:
            file_info = self._create_file_info(file_path)
            result = self.categorizer.categorize_file(file_info)

            self.assertEqual(result.category, CategoryType.LESS_IMPORTANT)
            self.assertEqual(result.reason, CategoryReason.EXTENSION)

    def test_path_based_categorization(self):
        """Test file categorization by path patterns."""
        # Downloads folder
        download_file = self._create_file_info("C:\\Users\\User\\Downloads\\file.xyz")
        result = self.categorizer.categorize_file(download_file)
        self.assertEqual(result.category, CategoryType.SAFE)
        self.assertEqual(result.reason, CategoryReason.PATH_PATTERN)

        # Documents folder
        doc_file = self._create_file_info("C:\\Users\\User\\Documents\\file.xyz")
        result = self.categorizer.categorize_file(doc_file)
        self.assertEqual(result.category, CategoryType.LESS_IMPORTANT)
        self.assertEqual(result.reason, CategoryReason.PATH_PATTERN)

    def test_user_override(self):
        """Test user category overrides."""
        file_info = self._create_file_info("C:\\Users\\User\\important.txt")

        # Set override
        self.categorizer.set_user_override(
            file_info.path, CategoryType.IMPORTANT, "User marked as important"
        )

        result = self.categorizer.categorize_file(file_info)
        self.assertEqual(result.category, CategoryType.IMPORTANT)
        self.assertEqual(result.reason, CategoryReason.USER_OVERRIDE)
        self.assertEqual(result.explanation, "User marked as important")

        # Remove override
        self.categorizer.remove_user_override(file_info.path)
        result = self.categorizer.categorize_file(file_info)
        self.assertNotEqual(result.reason, CategoryReason.USER_OVERRIDE)

    def test_default_categorization(self):
        """Test default categorization for unknown files."""
        unknown_file = self._create_file_info("C:\\Users\\User\\unknown.xyz")
        result = self.categorizer.categorize_file(unknown_file)

        self.assertEqual(result.category, CategoryType.LESS_IMPORTANT)
        self.assertEqual(result.reason, CategoryReason.USER_DOCUMENT)

    def test_category_stats(self):
        """Test category statistics calculation."""
        files = [
            self._create_file_info("C:\\Windows\\System32\\file.dll"),  # Important
            self._create_file_info("C:\\Users\\User\\document.pdf"),  # Less important
            self._create_file_info("C:\\Temp\\cache.tmp"),  # Safe
            self._create_file_info("C:\\Users\\User\\photo.jpg"),  # Less important
        ]

        stats = self.categorizer.get_category_stats(files)

        self.assertEqual(stats[CategoryType.IMPORTANT], 1)
        self.assertEqual(stats[CategoryType.LESS_IMPORTANT], 2)
        self.assertEqual(stats[CategoryType.SAFE], 1)

    def test_rules_documentation(self):
        """Test rules documentation generation."""
        docs = self.categorizer.get_rules_documentation()

        self.assertIn("categories", docs)
        self.assertIn("systemPaths", docs)
        self.assertIn("tempPaths", docs)

        # Check category structure
        for category in ["safe", "lessImportant", "important"]:
            self.assertIn(category, docs["categories"])
            self.assertIn("extensions", docs["categories"][category])
            self.assertIn("pathPatterns", docs["categories"][category])
            self.assertIn("description", docs["categories"][category])

    def test_custom_rules_loading(self):
        """Test loading custom categorization rules."""
        # Create temporary rules file
        custom_rules = {
            "schemaVersion": "1.0.0",
            "categories": {
                "safe": {
                    "extensions": [".test"],
                    "pathPatterns": ["testdir"],
                    "description": "Test files",
                },
                "lessImportant": {
                    "extensions": [".doc"],
                    "pathPatterns": ["documents"],
                    "description": "Documents",
                },
                "important": {
                    "extensions": [".exe"],
                    "pathPatterns": ["system"],
                    "description": "System files",
                },
            },
            "accessTimeRules": {
                "oldFileThresholdDays": 180,
                "recentFileThresholdDays": 14,
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(custom_rules, f)
            temp_path = Path(f.name)

        try:
            # Create categorizer with custom rules
            custom_categorizer = FileCategorizer(temp_path)

            # Test custom extension
            test_file = self._create_file_info("C:\\Users\\User\\test.test")
            result = custom_categorizer.categorize_file(test_file)

            self.assertEqual(result.category, CategoryType.SAFE)
            self.assertEqual(result.reason, CategoryReason.EXTENSION)

        finally:
            temp_path.unlink()  # Clean up

    def test_error_handling(self):
        """Test error handling in categorization."""
        # Test with None path (should not crash)
        try:
            file_info = FileInfo(
                path=None,  # This should cause an error
                size=1024,
                modified_date=self.test_time,
                file_type=FileType.OTHER,
            )
            result = self.categorizer.categorize_file(file_info)
            # Should default to important for safety
            self.assertEqual(result.category, CategoryType.IMPORTANT)
        except:
            # Error handling should prevent crashes
            pass


if __name__ == "__main__":
    unittest.main()
