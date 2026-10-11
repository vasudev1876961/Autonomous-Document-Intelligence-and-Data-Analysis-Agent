"""
SQLite Store: Relational persistent database for tasks, document manifests, plan steps,
evidence records, deterministic calculations, approval events, and audit logs.
"""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import json
from typing import Any, Optional
from config.settings import settings

class SQLiteStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.sqlite_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Documents
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                ingestion_timestamp TEXT NOT NULL,
                extraction_status TEXT NOT NULL,
                document_version TEXT DEFAULT '1.0'
            )
            """)

            # 2. Tasks
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                user_goal TEXT NOT NULL,
                task_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                completion_reason TEXT
            )
            """)

            # 3. Plan Steps
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_steps (
                step_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                description TEXT NOT NULL,
                dependencies TEXT,
                status TEXT NOT NULL,
                attempt_count INTEGER DEFAULT 1,
                result_reference TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            )
            """)

            # 4. Evidence
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                location_type TEXT,
                location_reference TEXT,
                content_snippet TEXT,
                content_hash TEXT,
                extraction_method TEXT,
                verification_status TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                FOREIGN KEY (document_id) REFERENCES documents (document_id)
            )
            """)

            # 5. Analysis Results
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                analysis_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                input_references TEXT,
                method TEXT NOT NULL,
                result_json TEXT NOT NULL,
                units TEXT,
                verification_status TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            )
            """)

            # 6. Approval Records
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS approval_records (
                approval_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                action_description TEXT NOT NULL,
                decision TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                review_comments TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            )
            """)

            # 7. Audit Logs
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                step_index INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            )
            """)

            conn.commit()

    def record_document(self, doc_id: str, name: str, ftype: str, fhash: str, status: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO documents 
                   (document_id, file_name, file_type, content_hash, ingestion_timestamp, extraction_status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (doc_id, name, ftype, fhash, datetime.now(timezone.utc).isoformat(), status)
            )
            conn.commit()

    def record_task(self, task_id: str, goal: str, status: str = "running") -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO tasks (task_id, user_goal, task_status, created_at)
                   VALUES (?, ?, ?, ?)""",
                (task_id, goal, status, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()

    def update_task_status(self, task_id: str, status: str, reason: Optional[str] = None) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """UPDATE tasks SET task_status = ?, completed_at = ?, completion_reason = ?
                   WHERE task_id = ?""",
                (status, datetime.now(timezone.utc).isoformat(), reason, task_id)
            )
            conn.commit()

    def record_plan_step(self, step_id: str, task_id: str, desc: str, deps: list[str], status: str, result_ref: str = "") -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO plan_steps 
                   (step_id, task_id, description, dependencies, status, result_reference)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (step_id, task_id, desc, json.dumps(deps), status, result_ref)
            )
            conn.commit()

    def record_evidence(
        self,
        evidence_id: str,
        task_id: str,
        document_id: str,
        loc_type: str,
        loc_ref: str,
        content: str,
        v_status: str = "verified"
    ) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO evidence 
                   (evidence_id, task_id, document_id, location_type, location_reference, content_snippet, verification_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (evidence_id, task_id, document_id, loc_type, loc_ref, content[:500], v_status)
            )
            conn.commit()

    def record_analysis_result(
        self,
        analysis_id: str,
        task_id: str,
        metric: str,
        inputs: str,
        method: str,
        result_obj: Any,
        units: str,
        v_status: str = "verified"
    ) -> None:
        res_str = json.dumps(result_obj) if not isinstance(result_obj, str) else result_obj
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO analysis_results 
                   (analysis_id, task_id, metric_name, input_references, method, result_json, units, verification_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (analysis_id, task_id, metric, inputs, method, res_str, units, v_status)
            )
            conn.commit()

    def record_approval(self, approval_id: str, task_id: str, action: str, decision: str, comments: str = "") -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO approval_records 
                   (approval_id, task_id, action_description, decision, timestamp, review_comments)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (approval_id, task_id, action, decision, datetime.now(timezone.utc).isoformat(), comments)
            )
            conn.commit()

    def log_audit(self, task_id: str, step_index: int, action: str, details: str = "") -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO audit_logs (task_id, step_index, action, details, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (task_id, step_index, action, details, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()

    def get_task_audit_trail(self, task_id: str) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM audit_logs WHERE task_id = ? ORDER BY log_id ASC", (task_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_task_evidence(self, task_id: str) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM evidence WHERE task_id = ?", (task_id,)).fetchall()
            return [dict(r) for r in rows]
