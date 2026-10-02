import unittest

from storage_service import StorageValidationError, validate_upload_candidate, build_object_key


class StorageServiceValidationTests(unittest.TestCase):
    def test_rejects_path_traversal_and_invalid_names(self):
        with self.assertRaises(StorageValidationError):
            validate_upload_candidate("../../etc/passwd", "application/pdf", 1024)

    def test_rejects_disallowed_mime_types(self):
        with self.assertRaises(StorageValidationError):
            validate_upload_candidate("invoice.exe", "application/x-msdownload", 1024)

    def test_accepts_files_up_to_250_mb(self):
        clean_name, mime = validate_upload_candidate("large_presentation.pptx", "application/vnd.openxmlformats-officedocument", 200 * 1024 * 1024)
        self.assertEqual(clean_name, "large_presentation.pptx")

    def test_rejects_files_larger_than_limit(self):
        with self.assertRaises(StorageValidationError) as ctx:
            validate_upload_candidate("giant_archive.zip", "application/zip", 251 * 1024 * 1024)
        self.assertIn("250 MB", str(ctx.exception))

    def test_builds_safe_key_for_project_resources(self):
        key = build_object_key("org-1", "project-2", "report.pdf")
        self.assertTrue(key.startswith("org-1/project-2/"))
        self.assertTrue(key.endswith("report.pdf"))
        self.assertNotIn("..", key)


if __name__ == "__main__":
    unittest.main()
