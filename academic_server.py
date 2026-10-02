import uuid
from io import BytesIO
from flask import Flask, request, jsonify, send_file, send_from_directory, g, redirect
from flask_cors import CORS
from functools import wraps
import sqlite3
import secrets
from storage_service import ObjectStorageService, StorageValidationError, build_object_key, validate_upload_candidate

class MockRow:
    def __init__(self, team_id):
        self.team_id = team_id
    def __getitem__(self, key):
        if key == 0 or key == 'team_id': return self.team_id
        raise KeyError(key)
import os
from werkzeug.utils import secure_filename

DB_PATH = os.path.join(os.path.dirname(__file__), 'academic.db')


import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()
import string
def send_otp_email(recipient_email, otp_code):
    try:
        load_dotenv()
        host = os.getenv("SMTP_SERVER", "smtp.ionos.de")
        port = int(os.getenv("SMTP_PORT", 465))
        user = os.getenv("SMTP_USER")
        passw = os.getenv("SMTP_PASS")
        
        if not user or not passw:
            print("Warning: SMTP credentials not set in .env. Email not sent.")
            return False
            
        msg = MIMEText(f"Hello,\n\nYour secure access code for the Sundeck Academic Hub is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nBest regards,\nSundeck Consulting Team")
        msg['Subject'] = "Sundeck Academic Hub - Access Code"
        msg['From'] = f"Sundeck Consulting <{user}>"
        msg['To'] = recipient_email
        
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                server.login(user, passw)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.starttls()
                server.login(user, passw)
                server.send_message(msg)
        return True
    except Exception as e:
        app.logger.error("OTP email delivery failed (%s)", type(e).__name__)


import jwt
import os
import time
from datetime import datetime, timedelta, timezone

import queue
import threading
import json
from flask import Response

class RealtimeManager:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add_client(self, q, org_id, project_id, team_id, student_id, client_id):
        app.logger.info("SSE client connected")
        with self.lock:
            self.clients.append({
                'q': q, 
                'org_id': org_id, 
                'project_id': project_id, 
                'team_id': team_id, 
                'student_id': student_id,
                'client_id': client_id
            })

    def remove_client(self, q):
        with self.lock:
            self.clients = [c for c in self.clients if c['q'] != q]

    def broadcast(self, org_id, project_id, event_type, payload, exclude_client_id=None):
        app.logger.info("SSE broadcast event=%s", event_type)
        message = json.dumps({"type": event_type, "payload": payload})
        with self.lock:
            for client in self.clients:
                if client['org_id'] == org_id and client['project_id'] == project_id:
                    if exclude_client_id and client.get('client_id') == exclude_client_id:
                        continue
                    try:
                        client['q'].put_nowait(message)
                    except queue.Full:
                        pass

realtime_manager = RealtimeManager()

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 52 * 1024 * 1024

APP_ENV = os.environ.get("APP_ENV", "development").strip().lower()
storage_service = ObjectStorageService()
if APP_ENV == "production" and not storage_service.is_enabled:
    raise RuntimeError("Contabo Object Storage must be configured in production via environment variables")
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    if APP_ENV == "production":
        raise RuntimeError("JWT_SECRET must be configured in production")
    JWT_SECRET = secrets.token_urlsafe(48)
if len(JWT_SECRET.encode("utf-8")) < 32:
    raise RuntimeError("JWT_SECRET must contain at least 32 bytes")

ADMIN_PASSCODE = os.environ.get("ADMIN_PASSCODE", "")

CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
if CORS_ALLOWED_ORIGINS:
    CORS(app, resources={r"/api/*": {"origins": CORS_ALLOWED_ORIGINS, "allow_headers": ["Authorization", "Content-Type", "X-Client-ID"]}})

JWT_ALGORITHM = "HS256"
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60
ADMIN_IDLE_SECONDS = 30 * 60
USER_IDLE_SECONDS = 60 * 60
STUDENT_PRIVACY_NOTICE_VERSION = "academic-hub-notice-2026-09-v1"
STUDENT_MARKETING_PERMISSION_VERSION = "academic-hub-marketing-2026-09-v3-work-only-anonymized"

def _ensure_student_consent_table(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS student_consent_events (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            consent_type TEXT NOT NULL,
            granted INTEGER NOT NULL CHECK (granted IN (0, 1)),
            wording_version TEXT NOT NULL,
            recorded_at TEXT NOT NULL
        )
    """)

def _latest_student_consent(db, student_id, consent_type):
    _ensure_student_consent_table(db)
    return db.execute("""
        SELECT granted, wording_version, recorded_at
        FROM student_consent_events
        WHERE student_id = ? AND consent_type = ?
        ORDER BY recorded_at DESC, rowid DESC
        LIMIT 1
    """, (student_id, consent_type)).fetchone()

def _issue_session(payload, idle_seconds):
    now = int(time.time())
    session_id = str(uuid.uuid4())
    expires_at = now + SESSION_MAX_AGE_SECONDS
    payload.update({"sid": session_id, "iat": now, "exp": expires_at})
    with sqlite3.connect('academic.db') as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS academic_sessions (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                organization_id TEXT,
                idle_timeout_seconds INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                last_activity_at INTEGER NOT NULL
            )
        """)
        db.execute("""
            INSERT INTO academic_sessions
                (id, role, organization_id, idle_timeout_seconds, expires_at, last_activity_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, payload.get("role"), payload.get("organization_id"), idle_seconds, expires_at, now))
        db.execute("DELETE FROM academic_sessions WHERE expires_at <= ?", (now,))
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def _touch_session(payload):
    session_id = payload.get("sid")
    if not session_id:
        return False
    now = int(time.time())
    with sqlite3.connect('academic.db') as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS academic_sessions (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                organization_id TEXT,
                idle_timeout_seconds INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                last_activity_at INTEGER NOT NULL
            )
        """)
        session = db.execute("""
            SELECT role, organization_id, idle_timeout_seconds, expires_at, last_activity_at
            FROM academic_sessions WHERE id = ?
        """, (session_id,)).fetchone()
        if not session:
            return False
        role, org_id, idle_seconds, expires_at, last_activity_at = session
        if (role != payload.get("role") or org_id != payload.get("organization_id")
                or now >= expires_at or now - last_activity_at >= idle_seconds):
            db.execute("DELETE FROM academic_sessions WHERE id = ?", (session_id,))
            return False
        db.execute("UPDATE academic_sessions SET last_activity_at = ? WHERE id = ?", (now, session_id))
        return True

def _issue_admin_session(payload):
    return _issue_session(payload, ADMIN_IDLE_SECONDS)

# Ensure upload directory exists for any local fallback during development; production persists to Contabo Object Storage.
STUDENT_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "storage", "students")
os.makedirs(STUDENT_UPLOAD_FOLDER, exist_ok=True)
PROJECT_RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), "storage", "project_resources")
os.makedirs(PROJECT_RESOURCE_FOLDER, exist_ok=True)


def _storage_reference_for(key):
    if not key:
        return key
    if isinstance(key, str) and key.startswith("s3://"):
        return key
    return storage_service.reference_for(key) if storage_service.is_enabled else key


def _delete_storage_reference(file_reference):
    if not file_reference:
        return
    try:
        if isinstance(file_reference, str) and file_reference.startswith("s3://"):
            storage_service.delete_key(file_reference)
            return
        if os.path.isfile(file_reference):
            os.remove(file_reference)
    except Exception:
        app.logger.exception("Unable to remove persisted file %s", file_reference)


def _download_reference(file_reference, file_name):
    if not file_reference:
        return jsonify({"error": "File not found"}), 404
    if isinstance(file_reference, str) and file_reference.startswith("s3://"):
        signed_url = storage_service.generate_signed_download_url(file_reference, file_name)
        if not signed_url:
            return jsonify({"error": "File download is unavailable"}), 404
        return redirect(signed_url, code=302)
    if not os.path.isfile(file_reference):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_reference, as_attachment=True, download_name=file_name)


def _ensure_project_resources_table(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS project_resources (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_by TEXT,
            folder_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    columns = {row[1] for row in db.execute("PRAGMA table_info(project_resources)").fetchall()}
    if "folder_id" not in columns:
        db.execute("ALTER TABLE project_resources ADD COLUMN folder_id TEXT")
    db.execute("""
        CREATE TABLE IF NOT EXISTS project_resource_folders (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            created_by_student_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS project_resource_comments (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            author_student_id TEXT,
            author_role TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)


def _ensure_project_management_tables(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS project_tasks (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            team_id TEXT NOT NULL,
            activity_id TEXT,
            name TEXT NOT NULL,
            description TEXT,
            owner_student_id TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'Not Started',
            priority TEXT DEFAULT 'Medium',
            created_at TEXT NOT NULL
        )
    ''')
    columns = {row[1] for row in db.execute("PRAGMA table_info(project_tasks)").fetchall()}
    if "activity_id" not in columns:
        db.execute("ALTER TABLE project_tasks ADD COLUMN activity_id TEXT")
        
    db.execute('''
        CREATE TABLE IF NOT EXISTS work_packages (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            team_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            work_package_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS project_deliverables (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            team_id TEXT NOT NULL,
            task_id TEXT,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            deadline TEXT,
            owner_student_id TEXT,
            file_id TEXT,
            version INTEGER DEFAULT 1,
            submitted_at TEXT,
            review_status TEXT,
            feedback TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS project_dependencies (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            from_task_id TEXT NOT NULL,
            to_task_id TEXT NOT NULL,
            dependency_type TEXT DEFAULT 'Finish-to-Start',
            reason TEXT DEFAULT '',
            expected_date TEXT,
            created_at TEXT NOT NULL
        )
    ''')



def _get_accessible_team_id(db, requested_team_id=None):
    if g.role == "student":
        row = db.execute("""
            SELECT t.id
            FROM students s
            JOIN student_teams t ON t.id = s.team_id AND t.organization_id = s.organization_id
            WHERE s.id = ? AND s.organization_id = ?
        """, (g.student_id, g.org_id)).fetchone()
        if not row or (requested_team_id and str(requested_team_id) != str(row[0])):
            return None
        return row[0]

    if not requested_team_id:
        return None

    if g.role == "teacher":
        row = db.execute("""
            SELECT t.id
            FROM student_teams t
            JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
            JOIN project_professors pp ON pp.project_id = p.id
            WHERE t.id = ? AND t.organization_id = ? AND pp.professor_id = ?
        """, (requested_team_id, g.org_id, g.student_id)).fetchone()
    elif g.role == "admin":
        row = db.execute("""
            SELECT id FROM student_teams
            WHERE id = ? AND organization_id = ?
        """, (requested_team_id, g.org_id)).fetchone()
    else:
        return None
    return row[0] if row else None


def _get_student_project_id(db, student_id, org_id):
    if g.role in ["teacher", "admin"]:
        data = request.get_json(silent=True)
        requested_team_id = request.args.get("team_id") or (data.get("team_id") if isinstance(data, dict) else None) or request.form.get("team_id")
        team_id = _get_accessible_team_id(db, requested_team_id)
        if not team_id:
            return None
        row = db.execute("""
            SELECT t.project_id
            FROM student_teams t
            JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
            WHERE t.id = ? AND t.organization_id = ?
        """, (team_id, org_id)).fetchone()
        return row[0] if row else None

    row = db.execute("""
        SELECT t.project_id
        FROM students s
        JOIN student_teams t ON t.id = s.team_id AND t.organization_id = s.organization_id
        JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
        WHERE s.id = ? AND s.organization_id = ?
    """, (student_id, org_id)).fetchone()
    return row[0] if row else None


def _resolve_project_access(db, project_id, requested_team_id=None):
    team_id = None
    if g.role == "student":
        team_id = _get_accessible_team_id(db, requested_team_id)
        if not team_id:
            return False, None
        row = db.execute("""
            SELECT 1 FROM student_teams
            WHERE id = ? AND project_id = ? AND organization_id = ?
        """, (team_id, project_id, g.org_id)).fetchone()
        return bool(row), team_id

    if g.role == "teacher":
        row = db.execute("""
            SELECT 1 FROM projects p
            JOIN project_professors pp ON pp.project_id = p.id
            WHERE p.id = ? AND p.organization_id = ? AND pp.professor_id = ?
        """, (project_id, g.org_id, g.student_id)).fetchone()
    elif g.role == "admin":
        row = db.execute("SELECT 1 FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id)).fetchone()
    else:
        return False, None

    if not row:
        return False, None
    if requested_team_id:
        team_id = _get_accessible_team_id(db, requested_team_id)
        if not team_id:
            return False, None
        row = db.execute("""
            SELECT 1 FROM student_teams
            WHERE id = ? AND project_id = ? AND organization_id = ?
        """, (team_id, project_id, g.org_id)).fetchone()
        if not row:
            return False, None
    return True, team_id

# Portals


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    asset_directory = os.path.join(os.path.dirname(__file__), "assets")
    return send_from_directory(asset_directory, filename)

@app.route("/i18n.js", methods=["GET"])
def serve_i18n_js():
    return send_file(os.path.join(os.path.dirname(__file__), "i18n.js"))

@app.route("/legal", methods=["GET"])
def serve_legal():
    return send_file(os.path.join(os.path.dirname(__file__), "legal.html"))

@app.route("/", methods=["GET"])
def serve_academic_index():
    return send_file(os.path.join(os.path.dirname(__file__), "academic-index.html"))


@app.route("/admin", methods=["GET"])
def serve_academic_admin():
    return send_file(os.path.join(os.path.dirname(__file__), "academic-admin.html"))

@app.route("/sundeck-admin", methods=["GET"])
def serve_sundeck_admin():
    return send_file(os.path.join(os.path.dirname(__file__), "sundeck-admin.html"))

@app.route("/student-portal", methods=["GET"])
def serve_student_portal():
    return send_file(os.path.join(os.path.dirname(__file__), "student-portal.html"))

@app.route("/teacher-portal", methods=["GET"])
def serve_teacher_portal():
    return send_file(os.path.join(os.path.dirname(__file__), "teacher-portal.html"))

# Teacher Login
@app.route("/api/teacher/auth/request-otp", methods=["POST"])
def request_teacher_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM professors WHERE email = ?", (email,))
        prof = cur.fetchone()
        
        if not prof:
            return jsonify({"success": True, "message": "If the account exists, an access code will be sent."})
            
        otp = str(secrets.randbelow(900000) + 100000)
        expiry = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        
        cur.execute("UPDATE professors SET otp_code = ?, otp_expiry = ? WHERE email = ?", (otp, expiry, email))
        db.commit()
        
    email_sent = send_otp_email(email, otp)
    
    if not email_sent:
        app.logger.warning("Unable to deliver teacher access code")
    return jsonify({"success": True, "message": "If the account exists, an access code will be sent."})

@app.route("/api/teacher/auth/verify-otp", methods=["POST"])
def verify_teacher_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP required"}), 400
        
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("BEGIN IMMEDIATE")
        cur.execute("SELECT * FROM professors WHERE email = ? AND otp_code = ?", (email, otp))
        prof = cur.fetchone()
        
        if not prof:
            db.rollback()
            return jsonify({"error": "Invalid OTP or email"}), 401

        try:
            otp_expiry = datetime.fromisoformat(prof["otp_expiry"])
            if otp_expiry.tzinfo is None:
                otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            otp_expiry = datetime.min.replace(tzinfo=timezone.utc)

        if otp_expiry <= datetime.now(timezone.utc):
            cur.execute("UPDATE professors SET otp_code = NULL, otp_expiry = NULL WHERE id = ?", (prof["id"],))
            db.commit()
            return jsonify({"error": "Login code expired. Request a new code."}), 401
            
        cur.execute("UPDATE professors SET otp_code = NULL, otp_expiry = NULL WHERE email = ?", (email,))
        db.commit()
        
    payload = {
        "sub": str(prof['id']),
        "email": email,
        "role": "teacher",
        "organization_id": prof['organization_id']
    }
    
    token = _issue_session(payload, USER_IDLE_SECONDS)
    
    return jsonify({
        "success": True,
        "role": "teacher",
        "token": token
    })

def require_teacher_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return jsonify({}), 200
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("role") != "teacher":
                return jsonify({"error": "Unauthorized"}), 401
            if not _touch_session(payload):
                return jsonify({"error": "Session expired"}), 401
            g.org_id = payload.get("organization_id")
            g.role = payload.get("role")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


# Admin Login
@app.route("/api/admin/auth/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    passcode = data.get("passcode")
    
    if not ADMIN_PASSCODE or not isinstance(passcode, str) or not secrets.compare_digest(passcode, ADMIN_PASSCODE):
        return jsonify({"error": "Invalid admin passcode"}), 401
        
    payload = {
        "sub": "sundeck_admin",
        "role": "sundeck_admin",
        "organization_id": "*",
    }
    
    token = _issue_admin_session(payload)
    
    return jsonify({
        "role": "sundeck_admin",
        "token": token
    })



def require_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return jsonify({}), 200
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            role = payload.get("role")
            if role not in ["admin", "teacher", "sundeck_admin"]:
                return jsonify({"error": "Unauthorized"}), 401
            if not _touch_session(payload):
                return jsonify({"error": "Session expired"}), 401
            g.org_id = payload.get("organization_id")
            g.role = role
            g.user_id = payload.get("sub")
            if role == "teacher" and not (
                (request.endpoint == "manage_teams" and request.method == "GET")
                or (request.endpoint == "download_team_file" and request.method == "GET")
            ):
                return jsonify({"error": "Unauthorized"}), 403
            if role == "sundeck_admin" and request.endpoint not in {
                "get_organizations", "create_organization", "delete_organization", "assume_organization"
            }:
                return jsonify({"error": "Unauthorized"}), 403
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

# Admin Endpoints for Academic Management (moved from CRM backend)

@app.route("/api/admin/teachers", methods=["GET", "POST"])
@require_admin_auth
def manage_teachers():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        if not name or not email: return jsonify({"error": "Name and email required"}), 400
        try:
            prof_id = str(uuid.uuid4())
            passcode = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            with sqlite3.connect('academic.db') as db:
                cur = db.cursor()
                cur.execute("INSERT INTO professors (id, organization_id, name, email, passcode_hash) VALUES (?, ?, ?, ?, ?)", (prof_id, g.org_id, name, email, passcode))
                db.commit()
                return jsonify({"success": True, "id": prof_id, "passcode": passcode})
        except sqlite3.IntegrityError:
            return jsonify({"error": "Email already exists"}), 400
            
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT id, name, email FROM professors WHERE organization_id = ?", (g.org_id,))
        teachers = [dict(row) for row in cur.fetchall()]
        for t in teachers:
            cur.execute("""
                SELECT p.id, p.name 
                FROM projects p 
                JOIN project_professors pp ON p.id = pp.project_id 
                WHERE pp.professor_id = ? AND p.organization_id = ?
            """, (t['id'], g.org_id))
            t['projects'] = [dict(r) for r in cur.fetchall()]
            
            notice = _latest_student_consent(db, t['id'], "privacy_notice_ack")
            marketing = _latest_student_consent(db, t['id'], "marketing_use")
            
            t['privacy_status'] = "Accepted" if (notice and notice[0]) else "Pending"
            t['privacy_date'] = notice[2] if notice else None
            t['privacy_version'] = notice[1] if notice else None
            
            t['marketing_status'] = "Granted" if (marketing and marketing[0]) else "Declined" if marketing else "Pending"
            t['marketing_date'] = marketing[2] if marketing else None
            t['marketing_version'] = marketing[1] if marketing else None
        return jsonify(teachers)


@app.route("/api/admin/teachers/<teacher_id>/projects", methods=["PUT"])
@require_admin_auth
def update_teacher_projects(teacher_id):
    data = request.get_json(silent=True) or {}
    project_ids = data.get("project_ids", [])
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT id FROM professors WHERE id = ? AND organization_id = ?", (teacher_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Teacher not found"}), 404
            
        # Verify all projects belong to org
        valid_projects = []
        for pid in project_ids:
            if db.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (pid, g.org_id)).fetchone():
                valid_projects.append(pid)
                
        # Delete existing
        cur.execute("DELETE FROM project_professors WHERE professor_id = ? AND project_id IN (SELECT id FROM projects WHERE organization_id = ?)", (teacher_id, g.org_id))
        
        # Insert new
        for pid in valid_projects:
            cur.execute("INSERT INTO project_professors (project_id, professor_id) VALUES (?, ?)", (pid, teacher_id))
            
        db.commit()
        return jsonify({"success": True})

@app.route("/api/admin/teachers/<teacher_id>", methods=["PUT", "DELETE"])
@require_admin_auth
def update_or_delete_teacher(teacher_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT id FROM professors WHERE id = ? AND organization_id = ?", (teacher_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Teacher not found"}), 404

        if request.method == "PUT":
            data = request.get_json(silent=True) or {}
            name = (data.get("name") or "").strip()
            email = (data.get("email") or "").strip().lower()
            if not name or not email:
                return jsonify({"error": "Name and email required"}), 400
            try:
                cur.execute(
                    "UPDATE professors SET name = ?, email = ? WHERE id = ? AND organization_id = ?",
                    (name, email, teacher_id, g.org_id),
                )
                db.commit()
                return jsonify({"success": True})
            except sqlite3.IntegrityError:
                return jsonify({"error": "Email already exists"}), 400

        cur.execute("DELETE FROM project_professors WHERE professor_id = ?", (teacher_id,))
        cur.execute("UPDATE projects SET created_by = NULL WHERE created_by = ? AND organization_id = ?", (teacher_id, g.org_id))
        cur.execute("DELETE FROM professors WHERE id = ? AND organization_id = ?", (teacher_id, g.org_id))
        db.commit()
        return jsonify({"success": True})


@app.route("/api/admin/projects", methods=["GET", "POST"])
@require_admin_auth
def manage_projects():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        description = (data.get("description") or "").strip()
        if not name: return jsonify({"error": "Project name required"}), 400
        try:
            project_id = str(uuid.uuid4())
            with sqlite3.connect('academic.db') as db:
                cur = db.cursor()
                cur.execute("INSERT INTO projects (id, organization_id, name, description) VALUES (?, ?, ?, ?)", (project_id, g.org_id, name, description))
                
                # Auto-create default folders for resources
                now_str = datetime.now(timezone.utc).isoformat()
                for folder_name in ["Briefs", "Templates", "Reference Files"]:
                    cur.execute("""
                        INSERT INTO project_resource_folders 
                        (id, organization_id, project_id, name, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), g.org_id, project_id, folder_name, now_str))
                
                db.commit()
                return jsonify({"success": True, "id": project_id})
        except Exception:
            app.logger.exception("Unable to create project")
            return jsonify({"error": "Unable to create project"}), 500
            
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM projects WHERE organization_id = ?", (g.org_id,))
        projects = [dict(row) for row in cur.fetchall()]
        
        for p in projects:
            cur.execute("""
                SELECT prof.id, prof.name, prof.email 
                FROM professors prof
                JOIN project_professors pp ON prof.id = pp.professor_id
                WHERE pp.project_id = ? AND prof.organization_id = ?
            """, (p['id'], g.org_id))
            p['teachers'] = [dict(r) for r in cur.fetchall()]
            
        return jsonify(projects)

@app.route("/api/admin/projects/<project_id>", methods=["PUT", "DELETE"])
@require_admin_auth
def update_or_delete_project(project_id):
    file_paths = []
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Project not found"}), 404

        if request.method == "PUT":
            data = request.get_json(silent=True) or {}
            name = (data.get("name") or "").strip()
            description = (data.get("description") or "").strip()
            if not name:
                return jsonify({"error": "Project name required"}), 400
            cur.execute(
                "UPDATE projects SET name = ?, description = ? WHERE id = ? AND organization_id = ?",
                (name, description, project_id, g.org_id),
            )
            db.commit()
            return jsonify({"success": True})

        cur.execute("SELECT id FROM student_teams WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id))
        for (team_id,) in cur.fetchall():
            file_paths.extend(_delete_team_records(cur, team_id))
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        cur.execute("SELECT file_path FROM project_resources WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id))
        file_paths.extend(row[0] for row in cur.fetchall() if row[0])
        cur.execute("DELETE FROM project_resource_comments WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id))
        cur.execute("DELETE FROM project_resource_folders WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id))
        cur.execute("DELETE FROM project_resources WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id))
        cur.execute("DELETE FROM project_professors WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
        db.commit()

    _remove_uploaded_files(file_paths)
    return jsonify({"success": True})

@app.route("/api/admin/projects/<project_id>/resources", methods=["GET", "POST"])
@require_admin_auth
def manage_project_resources(project_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403

    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Project not found"}), 404
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)

        if request.method == "GET":
            cur.execute("""
                SELECT id, project_id, folder_id, file_name, file_size, file_type, created_at
                FROM project_resources
                WHERE project_id = ? AND organization_id = ?
                ORDER BY created_at DESC
            """, (project_id, g.org_id))
            return jsonify([dict(row) for row in cur.fetchall()])

        resource = request.files.get("file")
        if not resource or not resource.filename:
            return jsonify({"error": "Select a file to upload"}), 400
        try:
            file_name, file_type = validate_upload_candidate(resource.filename, resource.mimetype, len(resource.read()))
        except StorageValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        finally:
            resource.stream.seek(0)
        folder_id = (request.form.get("folder_id") or "").strip() or None
        if folder_id:
            cur.execute("""
                SELECT id FROM project_resource_folders
                WHERE id = ? AND project_id = ? AND organization_id = ?
            """, (folder_id, project_id, g.org_id))
            if not cur.fetchone():
                return jsonify({"error": "Folder not found in this project"}), 404
        resource_id = str(uuid.uuid4())
        storage_key = build_object_key(g.org_id, project_id, file_name, folder_id or resource_id)
        try:
            payload = resource.read()
            file_size = len(payload)
            if file_size > MAX_UPLOAD_BYTES:
                return jsonify({"error": "Files must be 50 MB or smaller"}), 413
            storage_reference = storage_service.upload_bytes(storage_key, payload, file_type, {"org_id": g.org_id, "project_id": project_id, "uploaded_by": "admin"})
            created_at = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO project_resources
                    (id, organization_id, project_id, folder_id, file_name, file_size, file_type, file_path, uploaded_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (resource_id, g.org_id, project_id, folder_id, file_name, file_size,
                  file_type, storage_reference, None, created_at))
            db.commit()
        except Exception:
            app.logger.exception("Unable to save project resource")
            _delete_storage_reference(storage_reference if 'storage_reference' in locals() else None)
            return jsonify({"error": "Unable to save project resource"}), 500

        return jsonify({
            "success": True,
            "resource": {
                "id": resource_id,
                "project_id": project_id,
                "folder_id": folder_id,
                "file_name": file_name,
                "file_size": file_size,
                "file_type": file_type,
                "created_at": created_at,
            },
        }), 201

@app.route("/api/admin/projects/<project_id>/resources/<resource_id>", methods=["DELETE"])
@require_admin_auth
def delete_project_resource(project_id, resource_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        cur.execute("""
            SELECT file_path FROM project_resources
            WHERE id = ? AND project_id = ? AND organization_id = ?
        """, (resource_id, project_id, g.org_id))
        resource = cur.fetchone()
        if not resource:
            return jsonify({"error": "Project resource not found"}), 404
        cur.execute("DELETE FROM project_resource_comments WHERE resource_id = ? AND organization_id = ?", (resource_id, g.org_id))
        cur.execute("DELETE FROM project_resources WHERE id = ? AND project_id = ? AND organization_id = ?", (resource_id, project_id, g.org_id))
        db.commit()
    _remove_uploaded_files([resource[0]])
    return jsonify({"success": True})

@app.route("/api/admin/projects/<project_id>/resources/<resource_id>/download", methods=["GET"])
@require_admin_auth
def download_project_resource_admin(project_id, resource_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403
    return _send_project_resource(project_id, resource_id, g.org_id)

def _send_project_resource(project_id, resource_id, org_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        cur = db.cursor()
        cur.execute("""
            SELECT r.file_path, r.file_name
            FROM project_resources r
            JOIN projects p ON p.id = r.project_id
            WHERE r.id = ? AND r.project_id = ? AND r.organization_id = ? AND p.organization_id = ?
        """, (resource_id, project_id, org_id, org_id))
        resource = cur.fetchone()
    if not resource:
        return jsonify({"error": "Project resource not found"}), 404
    return _download_reference(resource["file_path"], resource["file_name"])

@app.route("/api/admin/projects/<project_id>/resource-folders", methods=["GET", "POST"])
@require_admin_auth
def manage_project_resource_folders(project_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Project not found"}), 404
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        if request.method == "GET":
            cur.execute("""
                SELECT id, project_id, name, created_by_student_id, created_at
                FROM project_resource_folders
                WHERE project_id = ? AND organization_id = ?
                ORDER BY name COLLATE NOCASE, created_at
            """, (project_id, g.org_id))
            return jsonify([dict(row) for row in cur.fetchall()])
        return _create_project_resource_folder(db, project_id, g.org_id, None, request.get_json(silent=True) or {})

def _create_project_resource_folder(db, project_id, org_id, student_id, data):
    folder_name = (data.get("name") or "").strip()
    if not folder_name:
        return jsonify({"error": "Folder name is required"}), 400
    if len(folder_name) > 80:
        return jsonify({"error": "Folder names must be 80 characters or fewer"}), 400
    cur = db.cursor()
    cur.execute("""
        SELECT 1 FROM project_resource_folders
        WHERE project_id = ? AND organization_id = ? AND name = ? COLLATE NOCASE
    """, (project_id, org_id, folder_name))
    if cur.fetchone():
        return jsonify({"error": "A folder with this name already exists"}), 409
    folder_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    cur.execute("""
        INSERT INTO project_resource_folders
            (id, organization_id, project_id, name, created_by_student_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (folder_id, org_id, project_id, folder_name, student_id, created_at))
    db.commit()
    return jsonify({"success": True, "folder": {"id": folder_id, "project_id": project_id, "name": folder_name, "created_at": created_at}}), 201

@app.route("/api/admin/projects/<project_id>/resource-folders/<folder_id>", methods=["PUT"])
@require_admin_auth
def rename_project_resource_folder(project_id, folder_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403
    data = request.get_json(silent=True) or {}
    new_name = (data.get("name") or "").strip()
    if not new_name:
        return jsonify({"error": "Folder name is required"}), 400
    if len(new_name) > 80:
        return jsonify({"error": "Folder names must be 80 characters or fewer"}), 400
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        # Check if another folder exists with the same name
        cur.execute("SELECT 1 FROM project_resource_folders WHERE project_id = ? AND organization_id = ? AND name = ? COLLATE NOCASE AND id != ?", (project_id, g.org_id, new_name, folder_id))
        if cur.fetchone():
            return jsonify({"error": "A folder with this name already exists"}), 409
        cur.execute("UPDATE project_resource_folders SET name = ? WHERE id = ? AND project_id = ? AND organization_id = ?", (new_name, folder_id, project_id, g.org_id))
        if cur.rowcount == 0:
            return jsonify({"error": "Folder not found"}), 404
        db.commit()
    return jsonify({"success": True})

@app.route("/api/admin/projects/<project_id>/resource-folders/<folder_id>", methods=["DELETE"])
@require_admin_auth
def delete_project_resource_folder(project_id, folder_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT file_path FROM project_resources WHERE folder_id = ? AND project_id = ? AND organization_id = ?", (folder_id, project_id, g.org_id))
        files = cur.fetchall()
        for f in files:
            _delete_storage_reference(f[0])
        cur.execute("DELETE FROM project_resources WHERE folder_id = ? AND project_id = ? AND organization_id = ?", (folder_id, project_id, g.org_id))
        cur.execute("DELETE FROM project_resource_folders WHERE id = ? AND project_id = ? AND organization_id = ?", (folder_id, project_id, g.org_id))
        if cur.rowcount == 0:
            return jsonify({"error": "Folder not found"}), 404
        db.commit()
    return jsonify({"success": True})

def _resource_comments_response(db, project_id, resource_id, org_id):
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute("""
        SELECT id FROM project_resources
        WHERE id = ? AND project_id = ? AND organization_id = ?
    """, (resource_id, project_id, org_id))
    if not cur.fetchone():
        return None
    cur.execute("""
        SELECT c.id, c.body, c.author_role, c.created_at,
               CASE WHEN c.author_role = 'admin' THEN 'Tenant Admin'
                    ELSE COALESCE(s.name, 'Student') END AS author_name
        FROM project_resource_comments c
        LEFT JOIN students s ON s.id = c.author_student_id
        WHERE c.resource_id = ? AND c.project_id = ? AND c.organization_id = ?
        ORDER BY c.created_at, c.id
    """, (resource_id, project_id, org_id))
    return [dict(row) for row in cur.fetchall()]

@app.route("/api/admin/projects/<project_id>/resources/<resource_id>/comments", methods=["GET", "POST"])
@require_admin_auth
def admin_project_resource_comments(project_id, resource_id):
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403
    with sqlite3.connect('academic.db') as db:
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        if request.method == "GET":
            comments = _resource_comments_response(db, project_id, resource_id, g.org_id)
            if comments is None:
                return jsonify({"error": "Project resource not found"}), 404
            return jsonify(comments)
        data = request.get_json(silent=True) or {}
        body = (data.get("body") or "").strip()
        if not body or len(body) > 3000:
            return jsonify({"error": "Comments must contain 1 to 3000 characters"}), 400
        if _resource_comments_response(db, project_id, resource_id, g.org_id) is None:
            return jsonify({"error": "Project resource not found"}), 404
        comment_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        db.execute("""
            INSERT INTO project_resource_comments
                (id, organization_id, project_id, resource_id, author_student_id, author_role, body, created_at)
            VALUES (?, ?, ?, ?, NULL, 'admin', ?, ?)
        """, (comment_id, g.org_id, project_id, resource_id, body, created_at))
        db.commit()
        return jsonify({"success": True, "id": comment_id, "created_at": created_at}), 201

@app.route("/api/admin/students/teams", methods=["GET", "POST"])
@require_admin_auth
def manage_teams():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        project_id = data.get("project_id")
        if not name or not project_id: return jsonify({"error": "Team name and project required"}), 400
        try:
            team_id = str(uuid.uuid4())
            passcode = str(secrets.randbelow(900000) + 100000)
            with sqlite3.connect('academic.db') as db:
                cur = db.cursor()
                cur.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
                if not cur.fetchone():
                    return jsonify({"error": "Project not found"}), 404
                cur.execute("INSERT INTO student_teams (id, organization_id, project_id, name, passcode) VALUES (?, ?, ?, ?, ?)", (team_id, g.org_id, project_id, name, passcode))
                db.commit()
                return jsonify({"success": True, "id": team_id, "passcode": passcode})
        except sqlite3.IntegrityError:
            return jsonify({"error": "Team already exists"}), 400
            
    project_id_filter = request.args.get('project_id')
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        if g.role == "teacher":
            query = """
                SELECT DISTINCT t.id, t.organization_id, t.project_id, t.name
                FROM student_teams t
                JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
                JOIN project_professors pp ON pp.project_id = p.id
                WHERE t.organization_id = ? AND p.organization_id = ? AND pp.professor_id = ?
            """
            params = [g.org_id, g.org_id, g.user_id]
            if project_id_filter:
                query += " AND t.project_id = ?"
                params.append(project_id_filter)
            cur.execute(query, params)
        elif project_id_filter:
            cur.execute("SELECT id, organization_id, project_id, name FROM student_teams WHERE organization_id = ? AND project_id = ?", (g.org_id, project_id_filter))
        else:
            cur.execute("SELECT id, organization_id, project_id, name FROM student_teams WHERE organization_id = ?", (g.org_id,))
        teams = [dict(row) for row in cur.fetchall()]
        
        # Count members and files
        for team in teams:
            cur.execute("SELECT COUNT(*) as count FROM students WHERE team_id = ? AND organization_id = ?", (team['id'], g.org_id))
            team['members_count'] = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM student_files WHERE team_id = ? AND organization_id = ?", (team['id'], g.org_id))
            team['files_count'] = cur.fetchone()['count']
            
        return jsonify(teams)

@app.route("/api/admin/students", methods=["POST"])
@require_admin_auth
def admin_create_student():
    data = request.get_json(silent=True) or {}
    team_id = data.get("team_id")
    email = data.get("email")
    name = (data.get("name") or "").strip()
    if not team_id or not email or not name:
        return jsonify({"error": "Missing fields"}), 400
    try:
        student_id = str(uuid.uuid4())
        with sqlite3.connect('academic.db') as db:
            cur = db.cursor()
            cur.execute("SELECT id FROM student_teams WHERE id = ? AND organization_id = ?", (team_id, g.org_id))
            if not cur.fetchone():
                return jsonify({"error": "Team not found"}), 404
            cur.execute("INSERT INTO students (id, team_id, organization_id, email, name) VALUES (?, ?, ?, ?, ?)", (student_id, team_id, g.org_id, email.lower().strip(), name))
            db.commit()
            return jsonify({"success": True, "id": student_id})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Student email already exists"}), 400


def _delete_team_records(cur, team_id):
    cur.execute("SELECT file_path FROM student_files WHERE team_id = ?", (team_id,))
    file_paths = [row[0] for row in cur.fetchall() if row[0]]
    cur.execute("DELETE FROM student_files WHERE team_id = ?", (team_id,))
    cur.execute("DELETE FROM students WHERE team_id = ?", (team_id,))
    cur.execute("DELETE FROM student_teams WHERE id = ?", (team_id,))
    return file_paths

def _remove_uploaded_files(file_paths):
    for file_path in file_paths or []:
        _delete_storage_reference(file_path)

@app.route("/api/admin/students/teams/<team_id>", methods=["PUT"])
@require_admin_auth
def update_team(team_id):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    project_id = data.get("project_id")
    if not name: return jsonify({"error": "Name required"}), 400
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        if project_id:
            cur.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
            if not cur.fetchone():
                return jsonify({"error": "Project not found"}), 404
            cur.execute("UPDATE student_teams SET name = ?, project_id = ? WHERE id = ? AND organization_id = ?", (name, project_id, team_id, g.org_id))
        else:
            cur.execute("UPDATE student_teams SET name = ? WHERE id = ? AND organization_id = ?", (name, team_id, g.org_id))
        if cur.rowcount == 0:
            return jsonify({"error": "Team not found"}), 404
        db.commit()
    return jsonify({"success": True})

@app.route("/api/admin/students/teams/<team_id>", methods=["DELETE"])
@require_admin_auth
def delete_team(team_id):
    file_paths = []
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT id FROM student_teams WHERE id = ? AND organization_id = ?", (team_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Team not found"}), 404
        file_paths = _delete_team_records(cur, team_id)
        db.commit()
    _remove_uploaded_files(file_paths)
    return jsonify({"success": True})

@app.route("/api/admin/students", methods=["GET"])
@require_admin_auth
def get_students():
    team_id = request.args.get("team_id")
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        if team_id:
            cur.execute("SELECT id, team_id, email, name FROM students WHERE team_id = ? AND organization_id = ?", (team_id, g.org_id))
        else:
            cur.execute("SELECT id, team_id, email, name FROM students WHERE organization_id = ?", (g.org_id,))
        return jsonify([dict(row) for row in cur.fetchall()])

@app.route("/api/admin/students/<student_id>", methods=["PUT", "DELETE"])
@require_admin_auth
def update_or_delete_student(student_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Student not found"}), 404
        if request.method == "PUT":
            data = request.get_json(silent=True) or {}
            name = (data.get("name") or "").strip()
            email = (data.get("email") or "").strip().lower()
            if not name or not email:
                return jsonify({"error": "Name and email required"}), 400
            try:
                cur.execute("UPDATE students SET name = ?, email = ? WHERE id = ? AND organization_id = ?", (name, email, student_id, g.org_id))
                db.commit()
                return jsonify({"success": True})
            except sqlite3.IntegrityError:
                return jsonify({"error": "Student email already exists"}), 400
        cur.execute("DELETE FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
        db.commit()
    return jsonify({"success": True})

@app.route("/api/admin/students/files/<file_id>", methods=["DELETE"])
@require_admin_auth
def delete_team_file(file_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("""
            SELECT f.file_path
            FROM student_files f
            JOIN student_teams t ON t.id = f.team_id
            WHERE f.id = ? AND t.organization_id = ?
        """, (file_id, g.org_id))
        file_record = cur.fetchone()
        if not file_record:
            return jsonify({"error": "File not found"}), 404
        _delete_storage_reference(file_record[0])
        cur.execute("DELETE FROM student_files WHERE id = ?", (file_id,))
        db.commit()
    return jsonify({"success": True})


@app.route("/api/admin/students/files", methods=["GET"])
@require_admin_auth
def get_team_files():
    team_id = request.args.get("team_id")
    if not team_id:
        return jsonify({"error": "team_id required"}), 400
        
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("""
            SELECT f.id, f.file_name, f.uploaded_at, f.uploaded_by as student_name
            FROM student_files f
            JOIN student_teams t ON t.id = f.team_id
            WHERE f.team_id = ? AND t.organization_id = ?
            ORDER BY f.uploaded_at DESC
        """, (team_id, g.org_id))
        files = [dict(row) for row in cur.fetchall()]
        return jsonify(files)

@app.route("/api/admin/students/files/<file_id>/download", methods=["GET"])
@require_admin_auth
def download_team_file(file_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        if g.role == "teacher":
            cur.execute("""
                SELECT f.file_path, f.file_name
                FROM student_files f
                JOIN student_teams t ON t.id = f.team_id AND t.organization_id = f.organization_id
                JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
                JOIN project_professors pp ON pp.project_id = p.id AND pp.professor_id = ?
                WHERE f.id = ? AND t.organization_id = ?
            """, (g.user_id, file_id, g.org_id))
        else:
            cur.execute("""
                SELECT f.file_path, f.file_name
                FROM student_files f
                JOIN student_teams t ON t.id = f.team_id AND t.organization_id = f.organization_id
                WHERE f.id = ? AND t.organization_id = ?
            """, (file_id, g.org_id))
        file_record = cur.fetchone()

    if not file_record:
        return jsonify({"error": "File not found"}), 404

    return _download_reference(file_record["file_path"], file_record["file_name"])

# Student Portal Endpoints
@app.route("/api/students/auth/request-otp", methods=["POST"])
def request_student_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email = ?", (email,))
        student = cur.fetchone()
        
        if not student:
            return jsonify({"success": True, "message": "If the account exists, an access code will be sent."})
            
        # Generate a real random 6-digit OTP
        otp = str(secrets.randbelow(900000) + 100000)
        expiry = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        
        cur.execute("UPDATE students SET otp_code = ?, otp_expiry = ? WHERE email = ?", (otp, expiry, email))
        db.commit()
        
    # Attempt to send the email
    email_sent = send_otp_email(email, otp)
    
    if not email_sent:
        app.logger.warning("Unable to deliver student access code")
    return jsonify({"success": True, "message": "If the account exists, an access code will be sent."})

@app.route("/api/students/auth/verify-otp", methods=["POST"])
def verify_student_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP required"}), 400
        
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("BEGIN IMMEDIATE")
        cur.execute("SELECT * FROM students WHERE email = ? AND otp_code = ?", (email, otp))
        student = cur.fetchone()
        
        if not student:
            db.rollback()
            return jsonify({"error": "Invalid OTP or email"}), 401

        try:
            otp_expiry = datetime.fromisoformat(student["otp_expiry"])
            if otp_expiry.tzinfo is None:
                otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            otp_expiry = datetime.min.replace(tzinfo=timezone.utc)

        if otp_expiry <= datetime.now(timezone.utc):
            cur.execute("UPDATE students SET otp_code = NULL, otp_expiry = NULL WHERE id = ?", (student["id"],))
            db.commit()
            return jsonify({"error": "Login code expired. Request a new code."}), 401
            
        cur.execute("UPDATE students SET otp_code = NULL, otp_expiry = NULL WHERE email = ?", (email,))
        if cur.rowcount != 1:
            db.rollback()
            return jsonify({"error": "Login code already used. Request a new code."}), 401
        db.commit()
        
    payload = {
        "sub": str(student['id']),
        "email": email,
        "role": "student",
        "organization_id": student['organization_id'] if 'organization_id' in student.keys() else "95e69b14-e4f2-407b-8d60-1e6f43e6b0b1"
    }
    
    token = _issue_session(payload, USER_IDLE_SECONDS)
    
    return jsonify({
        "success": True,
        "token": token,
        "student": {
            "id": student['id'],
            "name": student['name'],
            "email": student['email'],
            "team_id": student['team_id']
        }
    })

def require_student_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return jsonify({}), 200
        token = request.args.get("token")
        auth_header = request.headers.get("Authorization")
        if not token and auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error": "Missing or invalid token"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("role") not in ["student", "teacher", "admin"]:
                return jsonify({"error": "Unauthorized"}), 401
            if not _touch_session(payload):
                return jsonify({"error": "Session expired"}), 401
            g.org_id = payload.get("organization_id")
            g.role = payload.get("role")
            g.student_id = payload["sub"]
            if g.role == "student" and request.endpoint != "student_consent":
                with sqlite3.connect('academic.db') as db:
                    notice = _latest_student_consent(db, g.student_id, "privacy_notice_ack")
                if not notice or not notice[0] or notice[1] != STUDENT_PRIVACY_NOTICE_VERSION:
                    return jsonify({"error": "Privacy notice acknowledgement required", "consent_required": True}), 403
            project_id = (request.view_args or {}).get("project_id")
            if project_id and request.path.startswith("/api/projects/"):
                data = request.get_json(silent=True)
                requested_team_id = request.args.get("team_id") or (data.get("team_id") if isinstance(data, dict) else None) or request.form.get("team_id")
                with sqlite3.connect("academic.db") as db:
                    allowed, team_id = _resolve_project_access(db, project_id, requested_team_id)
                if not allowed:
                    return jsonify({"error": "Project not found or access denied"}), 403
                g.project_team_id = team_id
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/api/students/consent", methods=["GET", "POST"])
@require_student_auth
def student_consent():
    with sqlite3.connect('academic.db') as db:
        _ensure_student_consent_table(db)
        if request.method == "GET":
            notice = _latest_student_consent(db, g.student_id, "privacy_notice_ack")
            marketing = _latest_student_consent(db, g.student_id, "marketing_use")
            notice_complete = bool(notice and notice[0] and notice[1] == STUDENT_PRIVACY_NOTICE_VERSION)
            marketing_current = bool(marketing and marketing[1] == STUDENT_MARKETING_PERMISSION_VERSION)
            return jsonify({
                "required": not notice_complete,
                "marketing_choice_required": not marketing_current,
                "privacy_notice_version": STUDENT_PRIVACY_NOTICE_VERSION,
                "marketing_permission_version": STUDENT_MARKETING_PERMISSION_VERSION,
                "marketing_use": bool(marketing[0]) if marketing_current else False,
                "marketing_choice_recorded": marketing_current,
            })

        data = request.get_json(silent=True) or {}
        if data.get("privacy_notice_acknowledged") is not True:
            return jsonify({"error": "Please acknowledge the course privacy notice to continue."}), 400
        marketing_use = data.get("marketing_use")
        if type(marketing_use) is not bool:
            return jsonify({"error": "Choose yes or no for the optional marketing permission."}), 400

        now = datetime.now(timezone.utc).isoformat()
        entries = (
            ("privacy_notice_ack", 1, STUDENT_PRIVACY_NOTICE_VERSION),
            ("marketing_use", int(marketing_use), STUDENT_MARKETING_PERMISSION_VERSION),
        )
        for consent_type, granted, wording_version in entries:
            db.execute("""
                INSERT INTO student_consent_events
                    (id, student_id, consent_type, granted, wording_version, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), g.student_id, consent_type, granted, wording_version, now))
        db.commit()
        return jsonify({"success": True, "marketing_use": marketing_use})

@app.route("/api/admin/students/consent", methods=["GET"])
@require_admin_auth
def tenant_student_consent_report():
    if g.role != "admin":
        return jsonify({"error": "Tenant administrator access required"}), 403

    team_id = request.args.get("team_id")
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        _ensure_student_consent_table(db)
        cur = db.cursor()
        if team_id:
            cur.execute("SELECT id FROM student_teams WHERE id = ? AND organization_id = ?", (team_id, g.org_id))
            if not cur.fetchone():
                return jsonify({"error": "Team not found"}), 404
            cur.execute("SELECT id, name, email, team_id FROM students WHERE organization_id = ? AND team_id = ? ORDER BY name", (g.org_id, team_id))
        else:
            cur.execute("SELECT id, name, email, team_id FROM students WHERE organization_id = ? ORDER BY name", (g.org_id,))

        report = []
        for student in cur.fetchall():
            events = {}
            for consent_type in ("privacy_notice_ack", "marketing_use"):
                events[consent_type] = _latest_student_consent(db, student["id"], consent_type)

            def serialize_event(event):
                if not event:
                    return {"granted": None, "recorded_at": None, "wording_version": None}
                return {"granted": bool(event[0]), "recorded_at": event[2], "wording_version": event[1]}

            report.append({
                "student_id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "team_id": student["team_id"],
                "privacy_notice": serialize_event(events["privacy_notice_ack"]),
                "marketing_use": serialize_event(events["marketing_use"]),
            })

        return jsonify(report)

@app.route("/api/students/files", methods=["GET"])
@require_student_auth
def list_student_files():
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        data = request.get_json(silent=True)
        req_team = request.args.get('team_id') or (data.get('team_id') if isinstance(data, dict) else None) or request.form.get('team_id')
        team_id = _get_accessible_team_id(db, req_team)
        if not team_id:
            return jsonify({"error": "Student not found"}), 404
        cur.execute("""
            SELECT f.id, f.file_name, f.uploaded_at, f.folder_id
            FROM student_files f
            JOIN student_teams t ON t.id = f.team_id AND t.organization_id = f.organization_id
            WHERE f.team_id = ? AND f.organization_id = ? AND t.organization_id = ?
            ORDER BY f.uploaded_at DESC
        """, (team_id, g.org_id, g.org_id))
        files = [dict(row) for row in cur.fetchall()]
        return jsonify(files)


@app.route("/api/teacher/projects", methods=["GET"])
@require_student_auth
def get_teacher_projects():
    if g.role != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("""
            SELECT p.id, p.name, p.description
            FROM projects p 
            JOIN project_professors pp ON p.id = pp.project_id 
            WHERE pp.professor_id = ? AND p.organization_id = ?
        """, (g.student_id, g.org_id))
        projects = [dict(row) for row in cur.fetchall()]
        
        for p in projects:
            cur.execute("SELECT id, name, project_id FROM student_teams WHERE project_id = ? AND organization_id = ?", (p['id'], g.org_id))
            p['teams'] = [dict(r) for r in cur.fetchall()]
            
        return jsonify(projects)

@app.route("/api/students/team", methods=["GET"])
@require_student_auth
def get_student_team():
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("""
            SELECT t.id, t.name, t.project_id
            FROM students s
            JOIN student_teams t ON t.id = s.team_id
            WHERE s.id = ? AND s.organization_id = ? AND t.organization_id = ?
        """, (g.student_id, g.org_id, g.org_id))
        team = cur.fetchone()
        if not team:
            return jsonify({"error": "Team not found"}), 404

        cur.execute("""
            SELECT id, name
            FROM students
            WHERE team_id = ? AND organization_id = ?
            ORDER BY name COLLATE NOCASE, id
        """, (team["id"], g.org_id))
        members = [
            {"id": member["id"], "name": member["name"], "is_current_student": member["id"] == g.student_id}
            for member in cur.fetchall()
        ]
        return jsonify({"id": team["id"], "name": team["name"], "project_id": team["project_id"], "members": members})

@app.route("/api/students/resources", methods=["GET"])
@require_student_auth
def list_student_project_resources():
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        cur = db.cursor()
        cur.execute("""
            SELECT r.id, r.project_id, r.folder_id, r.file_name, r.file_size, r.file_type, r.created_at
            FROM students s
            JOIN student_teams t ON t.id = s.team_id AND t.organization_id = s.organization_id
            JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
            JOIN project_resources r ON r.project_id = p.id AND r.organization_id = p.organization_id
            WHERE s.id = ? AND s.organization_id = ?
            ORDER BY r.created_at DESC
        """, (g.student_id, g.org_id))
        return jsonify([dict(row) for row in cur.fetchall()])

@app.route("/api/students/resource-folders", methods=["GET", "POST"])
@require_student_auth
def student_project_resource_folders():
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        project_id = _get_student_project_id(db, g.student_id, g.org_id)
        if not project_id:
            return jsonify({"error": "Project not found for your team"}), 404
        if request.method == "GET":
            cur = db.execute("""
                SELECT id, project_id, name, created_at
                FROM project_resource_folders
                WHERE project_id = ? AND organization_id = ?
                ORDER BY name COLLATE NOCASE, created_at
            """, (project_id, g.org_id))
            return jsonify([dict(row) for row in cur.fetchall()])
        return _create_project_resource_folder(db, project_id, g.org_id, g.student_id, request.get_json(silent=True) or {})

@app.route("/api/students/resources/<resource_id>/comments", methods=["GET", "POST"])
@require_student_auth
def student_project_resource_comments(resource_id):
    with sqlite3.connect('academic.db') as db:
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        project_id = _get_student_project_id(db, g.student_id, g.org_id)
        if not project_id:
            return jsonify({"error": "Project not found for your team"}), 404
        if request.method == "GET":
            comments = _resource_comments_response(db, project_id, resource_id, g.org_id)
            if comments is None:
                return jsonify({"error": "Project resource not found"}), 404
            return jsonify(comments)

        data = request.get_json(silent=True) or {}
        body = (data.get("body") or "").strip()
        if not body or len(body) > 3000:
            return jsonify({"error": "Comments must contain 1 to 3000 characters"}), 400
        if _resource_comments_response(db, project_id, resource_id, g.org_id) is None:
            return jsonify({"error": "Project resource not found"}), 404
        comment_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        db.execute("""
            INSERT INTO project_resource_comments
                (id, organization_id, project_id, resource_id, author_student_id, author_role, body, created_at)
            VALUES (?, ?, ?, ?, ?, 'student', ?, ?)
        """, (comment_id, g.org_id, project_id, resource_id, g.student_id, body, created_at))
        db.commit()
        return jsonify({"success": True, "id": comment_id, "created_at": created_at}), 201

@app.route("/api/students/resources/<resource_id>/download", methods=["GET"])
@require_student_auth
def download_student_project_resource(resource_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        _ensure_project_resources_table(db)
        _ensure_project_management_tables(db)
        cur = db.cursor()
        cur.execute("""
            SELECT r.project_id
            FROM students s
            JOIN student_teams t ON t.id = s.team_id AND t.organization_id = s.organization_id
            JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
            JOIN project_resources r ON r.project_id = p.id AND r.organization_id = p.organization_id
            WHERE s.id = ? AND s.organization_id = ? AND r.id = ?
        """, (g.student_id, g.org_id, resource_id))
        resource = cur.fetchone()
    if not resource:
        return jsonify({"error": "Project resource not found"}), 404
    return _send_project_resource(resource["project_id"], resource_id, g.org_id)

@app.route("/api/students/files", methods=["POST"])
@require_student_auth
def upload_student_file():
    student_id = g.student_id
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    folder_id = request.form.get('folder_id')
    uploaded_filename = file.filename
    if not uploaded_filename:
        return jsonify({"error": "No selected file"}), 400

    try:
        safe_filename, file_type = validate_upload_candidate(uploaded_filename, file.mimetype, len(file.read()))
    except StorageValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        file.stream.seek(0)
    file_id = str(uuid.uuid4())
    folder_id = (folder_id or "").strip() or None

    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("SELECT team_id, email, organization_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
        student_info = cur.fetchone()
        if not student_info:
            return jsonify({"error": "Student not found"}), 404
        if folder_id and not cur.execute("SELECT 1 FROM student_file_folders WHERE id = ? AND team_id = ? AND organization_id = ?", (folder_id, student_info[0], student_info[2])).fetchone():
            return jsonify({"error": "Folder not found"}), 404

        file_bytes = file.read()
        file_size = len(file_bytes)
        if file_size > MAX_UPLOAD_BYTES:
            return jsonify({"error": "Files must be 50 MB or smaller"}), 413
        storage_key = build_object_key(g.org_id, student_info[0], safe_filename, folder_id or file_id)
        storage_reference = storage_service.upload_bytes(storage_key, file_bytes, file_type, {"org_id": g.org_id, "team_id": student_info[0], "uploaded_by": student_info[1]})
        cur.execute("""
            INSERT INTO student_files (id, team_id, file_name, file_size, file_type, file_path, uploaded_by, organization_id, folder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file_id, student_info[0], safe_filename, file_size, file_type, storage_reference, student_info[1], student_info[2], folder_id))
        db.commit()

    return jsonify({"success": True})

@app.route("/api/students/file-folders", methods=["GET", "POST"])
@require_student_auth
def student_file_folders():
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        data = request.get_json(silent=True)
        req_team = request.args.get('team_id') or (data.get('team_id') if isinstance(data, dict) else None) or request.form.get('team_id')
        team_id = _get_accessible_team_id(db, req_team)
        if not team_id:
            return jsonify({"error": "Student not found"}), 404
            
        if request.method == "GET":
            cur.execute("""
                SELECT id, team_id, name, created_at
                FROM student_file_folders
                WHERE team_id = ? AND organization_id = ?
                ORDER BY name COLLATE NOCASE, created_at
            """, (team_id, g.org_id))
            return jsonify([dict(row) for row in cur.fetchall()])
            
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        if not name or len(name) > 80:
            return jsonify({"error": "Folder name is required"}), 400
            
        folder_id = str(uuid.uuid4())
        db.execute("""
            INSERT INTO student_file_folders (id, team_id, organization_id, name)
            VALUES (?, ?, ?, ?)
        """, (folder_id, team_id, g.org_id, name))
        db.commit()
        
        return jsonify({
            "id": folder_id,
            "name": name,
            "team_id": team_id
        })

@app.route("/api/students/profile", methods=["GET"])
@require_student_auth
def get_student_profile():
    student_id = g.student_id
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("""
            SELECT s.id, s.name, s.email, s.team_id, o.name as org_name, o.logo_url as org_logo
            FROM students s
            LEFT JOIN organizations o ON s.organization_id = o.id
            WHERE s.id = ?
        """, (student_id,))
        student = cur.fetchone()
        
    if not student:
        return jsonify({"error": "Student not found"}), 404
        
    return jsonify({
        "id": student["id"],
        "name": student["name"],
        "email": student["email"],
        "team_id": student["team_id"]
    })




# ── SUNDECK SUPERADMIN ENDPOINTS ─────────────────────────────────────────────

@app.route("/api/admin/projects/<project_id>/teachers", methods=["GET", "POST"])
@require_admin_auth
def project_teachers(project_id):
    if request.method == "POST":
        data = request.get_json(silent=True)
        teacher_id = data.get("teacher_id")
        if not teacher_id: return jsonify({"error": "teacher_id required"}), 400
        with sqlite3.connect('academic.db') as db:
            cur = db.cursor()
            cur.execute("SELECT id FROM projects WHERE id = ? AND organization_id = ?", (project_id, g.org_id))
            if not cur.fetchone():
                return jsonify({"error": "Project not found"}), 404
            cur.execute("SELECT id FROM professors WHERE id = ? AND organization_id = ?", (teacher_id, g.org_id))
            if not cur.fetchone():
                return jsonify({"error": "Teacher not found"}), 404
            try:
                cur.execute("INSERT INTO project_professors (project_id, professor_id) VALUES (?, ?)", (project_id, teacher_id))
                db.commit()
                return jsonify({"success": True})
            except sqlite3.IntegrityError:
                return jsonify({"error": "Teacher already assigned or invalid IDs"}), 400
                
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("""
            SELECT p.id, p.name, p.email 
            FROM professors p
            JOIN project_professors pp ON p.id = pp.professor_id
            WHERE pp.project_id = ? AND p.organization_id = ?
        """, (project_id, g.org_id))
        teachers = [dict(row) for row in cur.fetchall()]
        return jsonify(teachers)

@app.route("/api/admin/projects/<project_id>/teachers/<teacher_id>", methods=["DELETE"])
@require_admin_auth
def remove_project_teacher(project_id, teacher_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("""
            DELETE FROM project_professors
            WHERE project_id = ? AND professor_id = ?
                AND project_id IN (SELECT id FROM projects WHERE organization_id = ?)
                AND professor_id IN (SELECT id FROM professors WHERE organization_id = ?)
        """, (project_id, teacher_id, g.org_id, g.org_id))
        db.commit()
        return jsonify({"success": True})

@app.route("/api/sundeck/organizations", methods=["GET", "OPTIONS"])
@require_admin_auth
def get_organizations():
    if g.role != "sundeck_admin":
        return jsonify({"error": "Forbidden. Requires Superadmin."}), 403
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM organizations ORDER BY created_at DESC")
        orgs = [dict(row) for row in cur.fetchall()]
        
        for org in orgs:
            cur.execute("SELECT COUNT(*) as count FROM students WHERE organization_id = ?", (org['id'],))
            org['students_count'] = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM professors WHERE organization_id = ?", (org['id'],))
            org['teachers_count'] = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM projects WHERE organization_id = ?", (org['id'],))
            org['projects_count'] = cur.fetchone()['count']
            
        return jsonify(orgs)

@app.route("/api/sundeck/organizations", methods=["POST", "OPTIONS"])
@require_admin_auth
def create_organization():
    if g.role != "sundeck_admin":
        return jsonify({"error": "Forbidden. Requires Superadmin."}), 403
        
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    org_type = data.get("type", "University")
    if not name:
        return jsonify({"error": "Organization name required"}), 400
        
    org_id = str(uuid.uuid4())
    short_name = data.get("short_name", "")
    country = data.get("country", "")
    city = data.get("city", "")
    
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("""
            INSERT INTO organizations (id, name, type, short_name, country, city, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (org_id, name, org_type, short_name, country, city, 'active'))
        db.commit()
        return jsonify({"success": True, "id": org_id})

@app.route("/api/sundeck/organizations/<org_id>", methods=["DELETE", "OPTIONS"])
@require_admin_auth
def delete_organization(org_id):
    if g.role != "sundeck_admin":
        return jsonify({"error": "Forbidden. Requires Superadmin."}), 403
        
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        cur.execute("DELETE FROM organizations WHERE id = ?", (org_id,))
        db.commit()
        return jsonify({"success": True})

@app.route("/api/admin/auth/assume", methods=["POST", "OPTIONS"])
@require_admin_auth
def assume_organization():
    if g.role != "sundeck_admin":
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    org_id = data.get("organization_id")
    if not org_id: return jsonify({"error": "organization_id required"}), 400
    
    payload = {
        "sub": "admin",
        "role": "admin",
        "organization_id": org_id,
    }
    token = _issue_admin_session(payload)
    return jsonify({"token": token, "role": "admin"})

@app.route("/api/auth/session/activity", methods=["POST"])
def session_activity():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401
    try:
        payload = jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Session expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    if payload.get("role") not in ["admin", "teacher", "student", "sundeck_admin"] or not _touch_session(payload):
        return jsonify({"error": "Session expired"}), 401
    return jsonify({"success": True})

@app.route("/api/auth/session/logout", methods=["POST"])
def revoke_session():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"success": True})
    try:
        payload = jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
    except jwt.InvalidTokenError:
        return jsonify({"success": True})
    session_id = payload.get("sid")
    if session_id:
        with sqlite3.connect('academic.db') as db:
            db.execute("DELETE FROM academic_sessions WHERE id = ?", (session_id,))
    return jsonify({"success": True})


@app.route("/api/students/files/<file_id>", methods=["PUT", "DELETE"])
@require_student_auth
def manage_student_file(file_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        data = request.get_json(silent=True)
        req_team = request.args.get('team_id') or (data.get('team_id') if isinstance(data, dict) else None) or request.form.get('team_id')
        team_id = _get_accessible_team_id(db, req_team)
        if not team_id:
            return jsonify({"error": "Student not found"}), 404
            
        cur.execute("SELECT * FROM student_files WHERE id = ? AND team_id = ? AND organization_id = ?", (file_id, team_id, g.org_id))
        file_record = cur.fetchone()
        if not file_record:
            return jsonify({"error": "File not found"}), 404

        if request.method == "DELETE":
            _delete_storage_reference(file_record["file_path"])
            cur.execute("DELETE FROM student_files WHERE id = ? AND team_id = ? AND organization_id = ?", (file_id, team_id, g.org_id))
            db.commit()
            return jsonify({"success": True})
            
        if request.method == "PUT":
            name = (data.get("name") or "").strip()
            folder_id = data.get("folder_id")
            
            if name:
                safe_name = secure_filename(name)
                if not safe_name or len(safe_name) > 255:
                    return jsonify({"error": "File name is invalid"}), 400
                cur.execute("UPDATE student_files SET file_name = ? WHERE id = ? AND team_id = ? AND organization_id = ?", (safe_name, file_id, team_id, g.org_id))
            if "folder_id" in data:
                if folder_id and not db.execute("SELECT 1 FROM student_file_folders WHERE id = ? AND team_id = ? AND organization_id = ?", (folder_id, team_id, g.org_id)).fetchone():
                    return jsonify({"error": "Folder not found"}), 404
                cur.execute("UPDATE student_files SET folder_id = ? WHERE id = ? AND team_id = ? AND organization_id = ?", (folder_id, file_id, team_id, g.org_id))
                
            db.commit()
            return jsonify({"success": True})

@app.route("/api/students/file-folders/<folder_id>", methods=["PUT", "DELETE"])
@require_student_auth
def manage_student_file_folder(folder_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        data = request.get_json(silent=True)
        req_team = request.args.get('team_id') or (data.get('team_id') if isinstance(data, dict) else None) or request.form.get('team_id')
        team_id = _get_accessible_team_id(db, req_team)
        if not team_id:
            return jsonify({"error": "Student not found"}), 404
            
        cur.execute("SELECT id FROM student_file_folders WHERE id = ? AND team_id = ? AND organization_id = ?", (folder_id, team_id, g.org_id))
        if not cur.fetchone():
            return jsonify({"error": "Folder not found"}), 404

        if request.method == "DELETE":
            cur.execute("UPDATE student_files SET folder_id = NULL WHERE folder_id = ? AND team_id = ? AND organization_id = ?", (folder_id, team_id, g.org_id))
            cur.execute("DELETE FROM student_file_folders WHERE id = ? AND team_id = ? AND organization_id = ?", (folder_id, team_id, g.org_id))
            db.commit()
            return jsonify({"success": True})
            
        if request.method == "PUT":
            name = (data.get("name") or "").strip()
            if not name or len(name) > 80:
                return jsonify({"error": "Folder name is required"}), 400
                
            cur.execute("UPDATE student_file_folders SET name = ? WHERE id = ? AND team_id = ? AND organization_id = ?", (name, folder_id, team_id, g.org_id))
            db.commit()
            return jsonify({"success": True})



# --- PROJECT MANAGEMENT API ---

@app.route("/api/projects/<project_id>/work_packages", methods=["GET"])
@require_student_auth
def get_project_work_packages(project_id):
    team_id = request.args.get("team_id")
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        query = "SELECT * FROM work_packages WHERE project_id = ? AND organization_id = ?"
        params = [project_id, g.org_id]
        team_id = g.project_team_id or team_id
        if team_id:
            query += " AND team_id = ?"
            params.append(team_id)
        wps = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"work_packages": wps})

@app.route("/api/projects/<project_id>/work_packages", methods=["POST"])
@require_student_auth
def create_project_work_package(project_id):
    data = request.get_json(silent=True) or {}
    wp_id = str(uuid.uuid4())
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student or not student[0]:
            return jsonify({"error": "Student not assigned to a team"}), 403
            
        student_team_id = student[0]
        
        db.execute("""
            INSERT INTO work_packages (id, organization_id, project_id, team_id, name, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            wp_id, g.org_id, project_id, student_team_id, data.get("name"), data.get("description", ""), datetime.now(timezone.utc).isoformat()
        ))
        db.commit()
    return jsonify({"success": True, "work_package_id": wp_id})

@app.route("/api/projects/<project_id>/activities", methods=["GET"])
@require_student_auth
def get_project_activities(project_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        query = """
            SELECT a.* FROM activities a
            JOIN work_packages wp ON wp.id = a.work_package_id
            WHERE a.project_id = ? AND a.organization_id = ? AND wp.organization_id = ?
        """
        params = [project_id, g.org_id, g.org_id]
        if g.project_team_id:
            query += " AND wp.team_id = ?"
            params.append(g.project_team_id)
        acts = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"activities": acts})

@app.route("/api/projects/<project_id>/activities", methods=["POST"])
@require_student_auth
def create_project_activity(project_id):
    data = request.get_json(silent=True) or {}
    act_id = str(uuid.uuid4())
    wp_id = data.get("work_package_id")
    
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        # Verify student team
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        # Verify WP ownership
        cur.execute("SELECT team_id FROM work_packages WHERE id = ? AND project_id = ? AND organization_id = ?", (wp_id, project_id, g.org_id))
        wp = cur.fetchone()
        if not wp:
            return jsonify({"error": "Work package not found"}), 404
        if wp[0] != student[0]:
            return jsonify({"error": "Unauthorized to add activity to another team's work package"}), 403
            
        db.execute("""
            INSERT INTO activities (id, organization_id, project_id, work_package_id, name, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            act_id, g.org_id, project_id, wp_id, data.get("name"), data.get("description", ""), datetime.now(timezone.utc).isoformat()
        ))
        db.commit()
    return jsonify({"success": True, "activity_id": act_id})




@app.route("/api/projects/<project_id>/work_packages/<wp_id>", methods=["PUT"])
@require_student_auth
def update_project_work_package(project_id, wp_id):
    data = request.get_json(silent=True) or {}
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        cur.execute("SELECT team_id FROM work_packages WHERE id = ? AND project_id = ? AND organization_id = ?", (wp_id, project_id, g.org_id))
        wp = cur.fetchone()
        if not wp:
            return jsonify({"error": "Work package not found"}), 404
            
        if wp[0] != student[0]:
            return jsonify({"error": "Unauthorized to edit work package belonging to another team"}), 403
            
        db.execute(
            "UPDATE work_packages SET name = ?, description = ? WHERE id = ? AND project_id = ? AND organization_id = ?",
            (data.get("name"), data.get("description", ""), wp_id, project_id, g.org_id)
        )
        db.commit()
    return jsonify({"success": True})

@app.route("/api/projects/<project_id>/activities/<act_id>", methods=["PUT"])
@require_student_auth
def update_project_activity(project_id, act_id):
    data = request.get_json(silent=True) or {}
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        cur.execute("""
            SELECT wp.team_id 
            FROM activities a 
            JOIN work_packages wp ON a.work_package_id = wp.id 
            WHERE a.id = ? AND a.project_id = ? AND a.organization_id = ? AND wp.organization_id = ?
        """, (act_id, project_id, g.org_id, g.org_id))
        act = cur.fetchone()
        if not act:
            return jsonify({"error": "Activity not found"}), 404
            
        if act[0] != student[0]:
            return jsonify({"error": "Unauthorized to edit activity belonging to another team"}), 403
            
        db.execute(
            "UPDATE activities SET name = ?, description = ? WHERE id = ? AND project_id = ? AND organization_id = ?",
            (data.get("name"), data.get("description", ""), act_id, project_id, g.org_id)
        )
        db.commit()
    return jsonify({"success": True})

@app.route("/api/projects/<project_id>/work_packages/<wp_id>", methods=["DELETE"])
@require_student_auth
def delete_project_work_package(project_id, wp_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        cur.execute("SELECT team_id FROM work_packages WHERE id = ? AND project_id = ? AND organization_id = ?", (wp_id, project_id, g.org_id))
        wp = cur.fetchone()
        if not wp:
            return jsonify({"error": "Work package not found"}), 404
            
        if wp[0] != student[0]:
            return jsonify({"error": "Unauthorized to delete work package belonging to another team"}), 403

        # Get all activities for this wp
            acts = db.execute("SELECT id FROM activities WHERE work_package_id = ? AND organization_id = ?", (wp_id, g.org_id)).fetchall()
        for act in acts:
            db.execute("DELETE FROM project_tasks WHERE activity_id = ? AND organization_id = ?", (act[0], g.org_id))
        db.execute("DELETE FROM activities WHERE work_package_id = ? AND organization_id = ?", (wp_id, g.org_id))
        db.execute("DELETE FROM work_packages WHERE id = ? AND project_id = ? AND organization_id = ?", (wp_id, project_id, g.org_id))
        db.commit()
    return jsonify({"success": True})

@app.route("/api/projects/<project_id>/activities/<act_id>", methods=["DELETE"])
@require_student_auth
def delete_project_activity(project_id, act_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        cur.execute("""
            SELECT wp.team_id 
            FROM activities a 
            JOIN work_packages wp ON a.work_package_id = wp.id 
            WHERE a.id = ? AND a.project_id = ? AND a.organization_id = ? AND wp.organization_id = ?
        """, (act_id, project_id, g.org_id, g.org_id))
        act = cur.fetchone()
        if not act:
            return jsonify({"error": "Activity not found"}), 404
            
        if act[0] != student[0]:
            return jsonify({"error": "Unauthorized to delete activity belonging to another team"}), 403

        db.execute("DELETE FROM project_tasks WHERE activity_id = ? AND organization_id = ?", (act_id, g.org_id))
        db.execute("DELETE FROM activities WHERE id = ? AND project_id = ? AND organization_id = ?", (act_id, project_id, g.org_id))
        db.commit()
    return jsonify({"success": True})

@app.route("/api/projects/<project_id>/tasks", methods=["GET"])
@require_student_auth
def get_project_tasks(project_id):
    team_id = request.args.get("team_id")
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        
        query = "SELECT * FROM project_tasks WHERE project_id = ? AND organization_id = ?"
        params = [project_id, g.org_id]
        team_id = g.project_team_id or team_id
        if team_id:
            query += " AND team_id = ?"
            params.append(team_id)
            
        tasks = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"tasks": tasks})

@app.route("/api/projects/<project_id>/teams", methods=["GET"])
@require_student_auth
def get_project_teams_student(project_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        query = "SELECT id, name, project_id FROM student_teams WHERE project_id = ? AND organization_id = ?"
        params = [project_id, g.org_id]
        if g.project_team_id:
            query += " AND id = ?"
            params.append(g.project_team_id)
        teams = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"teams": teams})


@app.route("/api/projects/<project_id>/tasks", methods=["POST"])
@require_student_auth
def create_project_task(project_id):
    data = request.get_json(silent=True) or {}
    task_id = str(uuid.uuid4())
    act_id = data.get("activity_id")
    
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student or not student[0]:
            return jsonify({"error": "Student not assigned to a team"}), 403
            
        cur.execute("SELECT work_packages.team_id FROM activities JOIN work_packages ON activities.work_package_id = work_packages.id AND work_packages.organization_id = activities.organization_id WHERE activities.id = ? AND activities.project_id = ? AND activities.organization_id = ?", (act_id, project_id, g.org_id))
        act = cur.fetchone()
        if not act or act[0] != student[0]:
            return jsonify({"error": "Unauthorized to add task to another team's activity"}), 403
            
        student_team_id = student[0]
        
        db.execute('''
            INSERT INTO project_tasks (id, organization_id, project_id, team_id, activity_id, name, description, owner_student_id, start_date, end_date, status, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            g.org_id,
            project_id,
            student_team_id,
            act_id,
            data.get("name"),
            data.get("description", ""),
            data.get("owner_student_id"),
            data.get("start_date"),
            data.get("end_date"),
            data.get("status", "Not Started"),
            data.get("priority", "Medium"),
            datetime.now(timezone.utc).isoformat()
        ))
        db.commit()
        
    return jsonify({"success": True, "task_id": task_id})

@app.route("/api/projects/<project_id>/tasks/<task_id>", methods=["PUT"])
@require_student_auth
def update_project_task(project_id, task_id):
    data = request.get_json(silent=True) or {}
    
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        cur.execute("SELECT team_id FROM project_tasks WHERE id = ? AND project_id = ? AND organization_id = ?", (task_id, project_id, g.org_id))
        task = cur.fetchone()
        if not task:
            return jsonify({"error": "Task not found"}), 404
            
        if task[0] != student[0]:
            return jsonify({"error": "Unauthorized to edit task belonging to another team"}), 403

        # Handle simple updates
        fields = []
        params = []
        for key in ["name", "description", "owner_student_id", "start_date", "end_date", "status", "priority"]:
            if key in data:
                fields.append(f"{key} = ?")
                params.append(data[key])
                
        if fields:
            params.append(task_id)
            params.append(project_id)
            params.extend([g.org_id])
            db.execute(f"UPDATE project_tasks SET {', '.join(fields)} WHERE id = ? AND project_id = ? AND organization_id = ?", params)
            db.commit()
            
    return jsonify({"success": True})

@app.route("/api/projects/<project_id>/tasks/<task_id>", methods=["DELETE"])
@require_student_auth
def delete_project_task(project_id, task_id):
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        # Verify student team
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        student_team_id = student[0]
        
        # Verify task belongs to student's team
        cur.execute("SELECT team_id FROM project_tasks WHERE id = ? AND project_id = ? AND organization_id = ?", (task_id, project_id, g.org_id))
        task = cur.fetchone()
        if not task:
            return jsonify({"error": "Task not found"}), 404
            
        if task[0] != student_team_id:
            return jsonify({"error": "Unauthorized to delete task belonging to another team"}), 403
            
        # Delete dependencies
        db.execute("DELETE FROM project_dependencies WHERE (from_task_id = ? OR to_task_id = ?) AND organization_id = ?", (task_id, task_id, g.org_id))
        
        # Decouple deliverables (don't delete the files themselves)
        db.execute("UPDATE project_deliverables SET task_id = NULL WHERE task_id = ? AND organization_id = ?", (task_id, g.org_id))
        
        # Delete the task
        db.execute("DELETE FROM project_tasks WHERE id = ? AND project_id = ? AND organization_id = ?", (task_id, project_id, g.org_id))
        db.commit()
        
    return jsonify({"success": True})

@app.route("/api/projects/<project_id>/dependencies", methods=["GET"])
@require_student_auth
def get_project_dependencies(project_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        deps = [dict(row) for row in db.execute("SELECT * FROM project_dependencies WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id)).fetchall()]
        return jsonify({"dependencies": deps})

@app.route("/api/projects/<project_id>/dependencies", methods=["POST"])
@require_student_auth
def create_project_dependency(project_id):
    data = request.get_json(silent=True) or {}
    dep_id = str(uuid.uuid4())
    reason = data.get("reason", "")
    what_needed = data.get("request_what_needed", "")
    if not isinstance(reason, str) or len(reason) > 3000 or not isinstance(what_needed, str) or len(what_needed) > 3000:
        return jsonify({"error": "Dependency details are invalid"}), 400
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        student_team_id = student[0]

        from_task_id = data.get("from_task_id")
        to_task_id = data.get("to_task_id")
        requested_from_team_id = data.get("request_from_team_id")
        if requested_from_team_id and str(requested_from_team_id) != str(student_team_id):
            return jsonify({"error": "Unauthorized to create dependency for another team"}), 403
        if from_task_id:
            source_task = cur.execute("""
                SELECT team_id FROM project_tasks
                WHERE id = ? AND project_id = ? AND organization_id = ?
            """, (from_task_id, project_id, g.org_id)).fetchone()
            if not source_task or source_task[0] != student_team_id:
                return jsonify({"error": "Source task is outside the authorized team"}), 403
        if not to_task_id:
            to_task_id = f"TEAM_{student_team_id}"
        elif str(to_task_id).startswith("TEAM_"):
            target_team_id = str(to_task_id)[5:]
            if not cur.execute("SELECT 1 FROM student_teams WHERE id = ? AND project_id = ? AND organization_id = ?", (target_team_id, project_id, g.org_id)).fetchone():
                return jsonify({"error": "Target team is outside the authorized project"}), 400
        else:
            if not cur.execute("SELECT 1 FROM project_tasks WHERE id = ? AND project_id = ? AND organization_id = ?", (to_task_id, project_id, g.org_id)).fetchone():
                return jsonify({"error": "Target task is outside the authorized project"}), 400

        request_from_wp_id = data.get("request_from_wp_id")
        if request_from_wp_id and not cur.execute("SELECT 1 FROM work_packages WHERE id = ? AND project_id = ? AND organization_id = ? AND team_id = ?", (request_from_wp_id, project_id, g.org_id, student_team_id)).fetchone():
            return jsonify({"error": "Work package is outside the authorized team"}), 403
        request_from_act_id = data.get("request_from_act_id")
        if request_from_act_id and not cur.execute("""
            SELECT 1 FROM activities a
            JOIN work_packages wp ON wp.id = a.work_package_id AND wp.organization_id = a.organization_id
            WHERE a.id = ? AND a.project_id = ? AND a.organization_id = ? AND wp.team_id = ?
        """, (request_from_act_id, project_id, g.org_id, student_team_id)).fetchone():
            return jsonify({"error": "Activity is outside the authorized team"}), 403

        status = "Mapped"
        if not from_task_id:
            from_task_id = f"PENDING_{dep_id}"
            status = "Pending"
            
        db.execute('''
            INSERT INTO project_dependencies (
                id, organization_id, project_id, from_task_id, to_task_id, dependency_type, 
                reason, expected_date, created_at, status, request_from_team_id, 
                request_from_wp_id, request_from_act_id, request_what_needed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dep_id, g.org_id, project_id, from_task_id, to_task_id,
            data.get("dependency_type", "Finish-to-Start"), data.get("reason", ""),
            data.get("expected_date", ""), datetime.now(timezone.utc).isoformat(),
            status, student_team_id, request_from_wp_id,
            request_from_act_id, what_needed
        ))
        db.commit()
    return jsonify({"success": True, "dependency_id": dep_id})

@app.route("/api/projects/<project_id>/dependencies/<dep_id>/map", methods=["PUT"])
@require_student_auth
def map_project_dependency(project_id, dep_id):
    data = request.get_json(silent=True) or {}
    new_from_task_id = data.get("from_task_id")
    if not new_from_task_id:
        return jsonify({"error": "from_task_id is required"}), 400
        
    with sqlite3.connect('academic.db') as db:
        cur = db.cursor()
        # Verify the user is in the team that received the request
        req_team = request.args.get('team_id') or (request.get_json(silent=True) or {}).get('team_id') or request.form.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            student = MockRow(req_team)
        else:
            cur.execute("SELECT team_id FROM students WHERE id = ? AND organization_id = ?", (g.student_id, g.org_id))
            student = cur.fetchone()
        
        cur.execute("SELECT request_from_team_id, status FROM project_dependencies WHERE id = ? AND project_id = ? AND organization_id = ?", (dep_id, project_id, g.org_id))
        dep = cur.fetchone()
        if not dep:
            return jsonify({"error": "Dependency request not found"}), 404
            
        if dep[0] != student[0]:
            return jsonify({"error": "Unauthorized to map this request"}), 403

        if not cur.execute("SELECT 1 FROM project_tasks WHERE id = ? AND project_id = ? AND organization_id = ? AND team_id = ?", (new_from_task_id, project_id, g.org_id, dep[0])).fetchone():
            return jsonify({"error": "Task is outside the requesting team"}), 403
            
        cur.execute("UPDATE project_dependencies SET from_task_id = ?, status = 'Mapped' WHERE id = ? AND project_id = ? AND organization_id = ?", (new_from_task_id, dep_id, project_id, g.org_id))
        db.commit()
    return jsonify({"success": True})


@app.route("/api/projects/<project_id>/deliverables", methods=["GET"])
@require_student_auth
def get_project_deliverables(project_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        query = "SELECT * FROM project_deliverables WHERE project_id = ? AND organization_id = ?"
        params = [project_id, g.org_id]
        if g.project_team_id:
            query += " AND team_id = ?"
            params.append(g.project_team_id)
        dels = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"deliverables": dels})


# --- ADMIN PROJECT MANAGEMENT API ---

@app.route("/api/admin/projects/<project_id>/tasks", methods=["GET"])
@require_admin_auth
def admin_get_project_tasks(project_id):
    team_id = request.args.get("team_id")
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        
        query = "SELECT * FROM project_tasks WHERE project_id = ? AND organization_id = ?"
        params = [project_id, g.org_id]
        if team_id:
            query += " AND team_id = ?"
            params.append(team_id)
            
        tasks = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"tasks": tasks})

@app.route("/api/admin/projects/<project_id>/dependencies", methods=["GET"])
@require_admin_auth
def admin_get_project_dependencies(project_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        deps = [dict(row) for row in db.execute("SELECT * FROM project_dependencies WHERE project_id = ? AND organization_id = ?", (project_id, g.org_id)).fetchall()]
        return jsonify({"dependencies": deps})

@app.route("/api/admin/projects/<project_id>/deliverables", methods=["GET"])
@require_admin_auth
def admin_get_project_deliverables(project_id):
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        query = "SELECT * FROM project_deliverables WHERE project_id = ? AND organization_id = ?"
        params = [project_id, g.org_id]
        if g.project_team_id:
            query += " AND team_id = ?"
            params.append(g.project_team_id)
        dels = [dict(row) for row in db.execute(query, params).fetchall()]
        return jsonify({"deliverables": dels})

@app.route("/api/stream", methods=["GET"])
@require_student_auth

def stream_events():
    student_id = g.student_id
    org_id = g.org_id
    client_id = request.args.get('client_id')
    with sqlite3.connect('academic.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        
        req_team = request.args.get('team_id')
        if getattr(g, 'role', '') in ['teacher', 'admin'] and req_team:
            team_id = _get_accessible_team_id(db, req_team)
            if not team_id:
                return jsonify({"error": "Team not found"}), 404
            cur.execute("SELECT project_id FROM student_teams WHERE id = ? AND organization_id = ?", (team_id, org_id))
            row = cur.fetchone()
            if not row: return jsonify({"error": "Team not found"}), 404
            project_id = row["project_id"]
        else:
            cur.execute("""
                SELECT t.id AS team_id, t.project_id
                FROM students s
                JOIN student_teams t ON s.team_id = t.id AND t.organization_id = s.organization_id
                JOIN projects p ON p.id = t.project_id AND p.organization_id = t.organization_id
                WHERE s.id = ? AND s.organization_id = ?
            """, (student_id, org_id))
            row = cur.fetchone()
            if not row:
                return jsonify({"error": "Student not found"}), 404
            project_id = row["project_id"]
            team_id = row["team_id"]


    def event_stream():
        q = queue.Queue(maxsize=100)
        realtime_manager.add_client(q, org_id, project_id, team_id, student_id, client_id)
        try:
            # Send initial ping to establish connection
            yield "data: {\"type\": \"CONNECTED\"}\n\n"
            while True:
                message = q.get()
                yield f"data: {message}\n\n"
        except GeneratorExit:
            realtime_manager.remove_client(q)
            
    return Response(event_stream(), mimetype="text/event-stream")

@app.after_request
def after_request_broadcast(response):
    try:
        if request.method in ["POST", "PUT", "DELETE"] and response.status_code == 200:
            if "/api/projects/" in request.path or "/api/students/" in request.path:
                parts = request.path.split("/")
                project_id = None
                if "projects" in parts:
                    idx = parts.index("projects")
                    if len(parts) > idx + 1:
                        project_id = parts[idx+1]
                
                if not project_id and hasattr(g, 'student_id') and hasattr(g, 'org_id'):
                    with sqlite3.connect(DB_PATH) as db:
                        cur = db.cursor()
                        cur.execute("SELECT t.project_id FROM students s JOIN student_teams t ON s.team_id = t.id WHERE s.id = ? AND s.organization_id = ?", (g.student_id, g.org_id))
                        row = cur.fetchone()
                        if row:
                            project_id = row[0]
                
                if project_id and hasattr(g, 'org_id'):
                    collection = None
                    for col in ["tasks", "dependencies", "work_packages", "activities", "files", "file-folders"]:
                        if col in parts:
                            collection = col
                            break
                    if collection:
                        client_id = request.headers.get('X-Client-ID')
                        realtime_manager.broadcast(g.org_id, project_id, "COLLECTION_MUTATED", {"collection": collection}, exclude_client_id=client_id)
                        
                        # Generate some intelligent notifications based on the request
                        if collection == "dependencies" and request.method == "POST":
                            realtime_manager.broadcast(g.org_id, project_id, "NOTIFICATION", {"title": "New Dependency Request", "message": "A team has requested a new dependency."}, exclude_client_id=client_id)
                        elif collection == "dependencies" and request.method == "PUT":
                            realtime_manager.broadcast(g.org_id, project_id, "NOTIFICATION", {"title": "Dependency Updated", "message": "A dependency status has been updated."}, exclude_client_id=client_id)
                        elif collection == "files" and request.method == "POST":
                            realtime_manager.broadcast(g.org_id, project_id, "NOTIFICATION", {"title": "Deliverable Uploaded", "message": "A new deliverable was uploaded."}, exclude_client_id=client_id)
    except Exception:
        app.logger.exception("Unable to process realtime broadcast")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)

