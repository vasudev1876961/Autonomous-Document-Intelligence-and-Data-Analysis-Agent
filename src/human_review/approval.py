"""
Human-in-the-Loop (HITL) Policy, Approval Models, and Action Types.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"
    REQUEST_CLARIFICATION = "request_clarification"
    PENDING = "pending"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class ApprovalRequest(BaseModel):
    request_id: str
    task_id: str
    risk_level: RiskLevel
    action_type: str # "reconcile_conflict", "approve_plan", "clarify_period", "verify_anomaly"
    title: str
    description: str
    proposed_action: str
    options: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    decision: ApprovalDecision = ApprovalDecision.PENDING
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    user_comment: Optional[str] = None
    selected_option: Optional[str] = None
