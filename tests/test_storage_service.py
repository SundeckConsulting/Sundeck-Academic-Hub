import unittest

from storage_service import StorageValidationError, validate_upload_candidate, build_object_key


class StorageServiceValidationTests(unittest.TestCase):
    def test_rejects_path_traversal_and_invalid_names(self):
        with self.assertRaises(StorageValidationError):
            validate_upload_candidate("../../etc/passwd", "application/pdf", 1024)

    def test_rejects_disallowed_mime_types(self):
        with self.assertRaises(StorageValidationError):
            validate_upload_candidate("invoice.exe", "application/x-msdownload", 1024)

    def test_rejects_files_larger_than_limit(self):
        with self.assertRaises(StorageValidationError):
            validate_upload_candidate("report.pdf", "application/pdf", 60 * 1024 * 1024)

    def test_builds_safe_key_for_project_resources(self):
        key = build_object_key("org-1", "project-2", "report.pdf")
        self.assertTrue(key.startswith("org-1/project-2/"))
        self.assertTrue(key.endswith("report.pdf"))
        self.assertNotIn("..", key)


if __name__ == "__main__":
    unittest.main()
