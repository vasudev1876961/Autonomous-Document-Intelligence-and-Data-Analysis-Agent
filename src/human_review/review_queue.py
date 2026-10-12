from datetime import datetime, timezone
from typing import Optional
from src.human_review.approval import ApprovalRequest, ApprovalDecision, RiskLevel
from src.memory.sqlite_store import SQLiteStore

class ReviewQueue:
    def __init__(self, store: Optional[SQLiteStore] = None):
        self.store = store or SQLiteStore()
        self.active_requests: dict[str, ApprovalRequest] = {}

    def create_request(
        self,
        request_id: str,
        task_id: str,
        risk_level: RiskLevel,
        action_type: str,
        title: str,
        description: str,
        proposed_action: str,
        options: Optional[list[str]] = None
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            request_id=request_id,
            task_id=task_id,
            risk_level=risk_level,
            action_type=action_type,
            title=title,
            description=description,
            proposed_action=proposed_action,
            options=options or ["Approve", "Reject", "Request Clarification"]
        )
        self.active_requests[request_id] = req
        return req

    def submit_decision(
        self,
        request_id: str,
        decision: ApprovalDecision,
        selected_option: Optional[str] = None,
        comments: str = "",
        decided_by: str = "User"
    ) -> Optional[ApprovalRequest]:
        req = self.active_requests.get(request_id)
        if not req:
            return None

        req.decision = decision
        req.selected_option = selected_option
        req.user_comment = comments
        req.decided_by = decided_by
        req.decided_at = datetime.now(timezone.utc)

        # Persist to SQLite store
        self.store.record_approval(
            approval_id=request_id,
            task_id=req.task_id,
            action=req.action_type,
            decision=decision.value,
            comments=f"Option: {selected_option} | Note: {comments}"
        )
        return req

    def get_pending_requests(self, task_id: Optional[str] = None) -> list[ApprovalRequest]:
        reqs = list(self.active_requests.values())
        if task_id:
            reqs = [r for r in reqs if r.task_id == task_id]
        return [r for r in reqs if r.decision == ApprovalDecision.PENDING]
