import os
import sqlite3
import unittest
import jwt
from datetime import datetime, timezone

from academic_server import app, DB_PATH, JWT_SECRET, JWT_ALGORITHM, _issue_session


class DownloadAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.org_id = "test-org-123"
        self.other_org_id = "test-org-999"

        # Generate tokens with valid active sessions
        self.admin_token = _issue_session(
            {"sub": "admin-1", "role": "admin", "organization_id": self.org_id},
            3600,
        )
        self.teacher_token = _issue_session(
            {"sub": "prof-1", "role": "teacher", "organization_id": self.org_id},
            3600,
        )
        self.unassigned_teacher_token = _issue_session(
            {"sub": "prof-2", "role": "teacher", "organization_id": self.org_id},
            3600,
        )

        db = sqlite3.connect(DB_PATH)
        try:
            # Seed test project
            db.execute("INSERT OR REPLACE INTO projects (id, organization_id, name) VALUES (?, ?, ?)",
                       ("proj-1", self.org_id, "Test Project 1"))
            db.execute("INSERT OR REPLACE INTO professors (id, organization_id, name, email, passcode_hash) VALUES (?, ?, ?, ?, ?)",
                       ("prof-1", self.org_id, "Dr. Assigned", "prof1@test.edu", "dummyhash"))
            db.execute("INSERT OR REPLACE INTO professors (id, organization_id, name, email, passcode_hash) VALUES (?, ?, ?, ?, ?)",
                       ("prof-2", self.org_id, "Dr. Unassigned", "prof2@test.edu", "dummyhash"))
            db.execute("INSERT OR REPLACE INTO project_professors (project_id, professor_id) VALUES (?, ?)",
                       ("proj-1", "prof-1"))

            # Seed team and student file
            db.execute("INSERT OR REPLACE INTO student_teams (id, project_id, organization_id, name, passcode) VALUES (?, ?, ?, ?, ?)",
                       ("team-1", "proj-1", self.org_id, "Alpha Team", "123456"))
            db.execute("""
                INSERT OR REPLACE INTO student_files (id, team_id, file_name, file_size, file_type, file_path, uploaded_by, organization_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("file-1", "team-1", "deliverable.pdf", 100, "application/pdf", "local://dummy", "student@test.edu", self.org_id))

            # Seed project resource
            db.execute("""
                INSERT OR REPLACE INTO project_resources (id, organization_id, project_id, file_name, file_size, file_type, file_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("res-1", self.org_id, "proj-1", "handout.pdf", 200, "application/pdf", "local://dummy", datetime.now(timezone.utc).isoformat()))

            db.commit()
        finally:
            db.close()

    def test_teacher_list_project_resources(self):
        res = self.client.get(
            "/api/students/resources?team_id=team-1",
            headers={"Authorization": f"Bearer {self.teacher_token}"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(any(r["id"] == "res-1" for r in data))

    def test_tenant_admin_list_all_team_files(self):
        res = self.client.get(
            "/api/admin/students/files?project_id=proj-1",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(any(f["id"] == "file-1" for f in data))

    def test_unassigned_teacher_cannot_access_project_resources(self):
        res = self.client.get(
            "/api/students/resources?team_id=team-1",
            headers={"Authorization": f"Bearer {self.unassigned_teacher_token}"},
        )
        # Unassigned teacher should not get resources
        data = res.get_json()
        self.assertEqual(data, [])


if __name__ == "__main__":
    unittest.main()
