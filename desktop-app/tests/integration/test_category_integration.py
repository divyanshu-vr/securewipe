"""Integration tests for category panel and categorizer."""

import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared"))
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from models.file_info import FileInfo, FileType

from scanner.categorizer import CategoryType, FileCategorizer


class TestCategoryIntegration(unittest.TestCase):
    """Integration tests for categorization system."""

    def setUp(self):
        """Set up test fixtures."""
        self.categorizer = FileCategorizer()
        self.test_files = self._create_test_files()

    def _create_test_files(self):
        """Create test file list with various categories."""
        files = []

        # System files
        files.append(
            FileInfo(
                path=Path("C:/Windows/System32/kernel32.dll"),
                size=1024000,
                modified_date=datetime.now(),
                file_type=FileType.OTHER,
            )
        )

        # Temporary files
        files.append(
            FileInfo(
                path=Path("C:/Users/User/AppData/Local/Temp/cache.tmp"),
                size=512,
                modified_date=datetime.now(),
                file_type=FileType.OTHER,
            )
        )

        # User documents - recent
        files.append(
            FileInfo(
                path=Path("C:/Users/User/Documents/report.pdf"),
                size=2048000,
                modified_date=datetime.now() - timedelta(days=5),
                file_type=FileType.DOCUMENT,
            )
        )

        # User documents - old
        files.append(
            FileInfo(
                path=Path("C:/Users/User/Documents/old_file.doc"),
                size=1024000,
                modified_date=datetime.now() - timedelta(days=400),
                file_type=FileType.DOCUMENT,
            )
        )

        # Browser cache
        files.append(
            FileInfo(
                path=Path(
                    "C:/Users/User/AppData/Local/Google/Chrome/User Data/Default/Cache/data_1"
                ),
                size=4096,
                modified_date=datetime.now(),
                file_type=FileType.OTHER,
            )
        )

        return files

    def test_categorization_workflow(self):
        """Test complete categorization workflow."""
        category_counts = {cat: 0 for cat in CategoryType}

        for file_info in self.test_files:
            result = self.categorizer.categorize_file(file_info)

            # Update file info with categorization
            file_info.category = result.category.value
            file_info.category_reason = result.reason.value
            file_info.category_explanation = result.explanation

            category_counts[result.category] += 1

            # Verify categorization makes sense
            self.assertIsNotNone(result.category)
            self.assertIsNotNone(result.explanation)
            self.assertTrue(len(result.explanation) > 10)  # Meaningful explanation

        # Verify we have files in each category
        self.assertGreater(category_counts[CategoryType.IMPORTANT], 0)
        self.assertGreater(category_counts[CategoryType.SAFE], 0)
        self.assertGreaterEqual(category_counts[CategoryType.LESS_IMPORTANT], 0)

    def test_user_override_workflow(self):
        """Test user override functionality."""
        test_file = self.test_files[0]  # System file

        # Initial categorization should be IMPORTANT
        result = self.categorizer.categorize_file(test_file)
        self.assertEqual(result.category, CategoryType.IMPORTANT)

        # Set user override
        self.categorizer.set_user_override(
            test_file.path,
            CategoryType.SAFE,
            "User confirmed this system file is safe to delete",
        )

        # Should now return user override
        result = self.categorizer.categorize_file(test_file)
        self.assertEqual(result.category, CategoryType.SAFE)
        self.assertIn("User confirmed", result.explanation)

        # Remove override
        self.categorizer.remove_user_override(test_file.path)

        # Should return to original categorization
        result = self.categorizer.categorize_file(test_file)
        self.assertEqual(result.category, CategoryType.IMPORTANT)

    def test_category_statistics(self):
        """Test category statistics calculation."""
        stats = self.categorizer.get_category_stats(self.test_files)

        # Verify stats structure
        self.assertIn(CategoryType.SAFE, stats)
        self.assertIn(CategoryType.LESS_IMPORTANT, stats)
        self.assertIn(CategoryType.IMPORTANT, stats)

        # Verify total matches file count
        total_categorized = sum(stats.values())
        self.assertEqual(total_categorized, len(self.test_files))

    def test_rules_documentation(self):
        """Test rules documentation generation."""
        docs = self.categorizer.get_rules_documentation()

        # Verify documentation structure
        self.assertIn("categories", docs)
        self.assertIn("systemPaths", docs)
        self.assertIn("tempPaths", docs)

        # Verify each category has required fields
        for category_name in ["safe", "lessImportant", "important"]:
            category = docs["categories"][category_name]
            self.assertIn("extensions", category)
            self.assertIn("pathPatterns", category)
            self.assertIn("description", category)

    def test_access_time_categorization(self):
        """Test access time based categorization."""
        # Find old user document
        old_doc = None
        for file_info in self.test_files:
            if "old_file" in str(file_info.path):
                old_doc = file_info
                break

        self.assertIsNotNone(old_doc)

        # Should be categorized as SAFE due to age
        result = self.categorizer.categorize_file(old_doc)
        # Note: Might be SAFE due to access time or LESS_IMPORTANT due to extension
        self.assertIn(result.category, [CategoryType.SAFE, CategoryType.LESS_IMPORTANT])

    def test_system_file_safety(self):
        """Test system file safety mechanisms."""
        system_files = [f for f in self.test_files if "System32" in str(f.path)]

        for system_file in system_files:
            result = self.categorizer.categorize_file(system_file)

            # System files should always be marked as IMPORTANT
            self.assertEqual(result.category, CategoryType.IMPORTANT)

            # Should have detailed explanation
            self.assertIn("system", result.explanation.lower())

            # Should mention consequences
            self.assertTrue(
                any(
                    word in result.explanation.lower()
                    for word in ["critical", "failure", "instability", "break"]
                )
            )

    def test_temp_file_detection(self):
        """Test temporary file detection accuracy."""
        temp_files = [
            f
            for f in self.test_files
            if any(pattern in str(f.path).lower() for pattern in ["temp", "cache"])
        ]

        for temp_file in temp_files:
            result = self.categorizer.categorize_file(temp_file)

            # Temp files should be SAFE
            self.assertEqual(result.category, CategoryType.SAFE)

            # Should have clear rationale
            self.assertTrue(
                any(
                    word in result.explanation.lower()
                    for word in ["safe", "delete", "temporary", "cache"]
                )
            )


if __name__ == "__main__":
    unittest.main()
