"""
Task History and episodic memory query manager.
"""
from typing import Any, Optional
from src.memory.sqlite_store import SQLiteStore

class TaskHistoryManager:
    def __init__(self, store: Optional[SQLiteStore] = None):
        self.store = store or SQLiteStore()

    def get_past_investigations(self) -> list[dict[str, Any]]:
        with self.store._get_connection() as conn:
            rows = conn.execute(
                "SELECT task_id, user_goal, task_status, created_at, completed_at, completion_reason FROM tasks ORDER BY created_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_task_details(self, task_id: str) -> dict[str, Any]:
        with self.store._get_connection() as conn:
            task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not task:
                return {}
            steps = conn.execute("SELECT * FROM plan_steps WHERE task_id = ?", (task_id,)).fetchall()
            evidence = conn.execute("SELECT * FROM evidence WHERE task_id = ?", (task_id,)).fetchall()
            analysis = conn.execute("SELECT * FROM analysis_results WHERE task_id = ?", (task_id,)).fetchall()
            approvals = conn.execute("SELECT * FROM approval_records WHERE task_id = ?", (task_id,)).fetchall()
            logs = conn.execute("SELECT * FROM audit_logs WHERE task_id = ? ORDER BY step_index ASC", (task_id,)).fetchall()

            return {
                "task": dict(task),
                "steps": [dict(s) for s in steps],
                "evidence": [dict(e) for e in evidence],
                "analysis": [dict(a) for a in analysis],
                "approvals": [dict(ap) for ap in approvals],
                "logs": [dict(l) for l in logs]
            }
