"""
Complaint workflow management
Defines valid status transitions and workflow rules
"""
from typing import Dict, List, Optional
from app.models.complaint import ComplaintStatus
from app.models.user import UserRole

# Define valid status transitions
# Key: current status, Value: list of allowed next statuses
STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "submitted": ["assigned", "rejected"],
    "assigned": ["in_progress", "rejected"],
    "in_progress": ["resolved", "assigned", "rejected"],
    "resolved": ["closed", "in_progress"],  # Can reopen if work not approved
    "closed": [],  # Terminal state
    "rejected": []  # Terminal state
}

# Role permissions for status transitions
# Key: (current_status, new_status), Value: list of allowed roles
TRANSITION_PERMISSIONS: Dict[tuple, List[str]] = {
    ("submitted", "assigned"): ["admin", "mla", "moderator"],
    ("submitted", "rejected"): ["admin", "mla", "moderator"],
    ("assigned", "in_progress"): ["admin", "dept_officer", "moderator"],
    ("assigned", "rejected"): ["admin", "moderator"],
    ("in_progress", "resolved"): ["admin", "dept_officer"],
    ("in_progress", "assigned"): ["admin", "moderator"],  # Reassign
    ("in_progress", "rejected"): ["admin", "moderator"],
    ("resolved", "closed"): ["admin", "mla", "moderator"],  # After approval
    ("resolved", "in_progress"): ["admin", "mla", "moderator"],  # Reject work
}

# Auto-assignment rules based on complaint category
CATEGORY_DEPARTMENT_MAPPING = {
    "road": "Road & Infrastructure",
    "water": "Water Supply",
    "electricity": "Electricity Board",
    "health": "Health Department",
    "education": "Education Department",
    "sanitation": "Sanitation & Waste Management",
    "other": "General Administration"
}


class WorkflowValidator:
    """Validates complaint workflow transitions"""
    
    @staticmethod
    def is_valid_transition(current_status: str, new_status: str) -> bool:
        """
        Check if status transition is allowed
        """
        if current_status not in STATUS_TRANSITIONS:
            return False
        
        allowed_statuses = STATUS_TRANSITIONS[current_status]
        return new_status in allowed_statuses
    
    @staticmethod
    def can_user_transition(
        current_status: str, 
        new_status: str, 
        user_role: str
    ) -> bool:
        """
        Check if user role is allowed to make this transition
        """
        transition_key = (current_status, new_status)
        
        if transition_key not in TRANSITION_PERMISSIONS:
            return False
        
        allowed_roles = TRANSITION_PERMISSIONS[transition_key]
        return user_role in allowed_roles
    
    @staticmethod
    def get_allowed_transitions(current_status: str) -> List[str]:
        """
        Get list of allowed next statuses
        """
        return STATUS_TRANSITIONS.get(current_status, [])
    
    @staticmethod
    def get_transition_reason(current_status: str, new_status: str) -> str:
        """
        Get human-readable reason for transition
        """
        reasons = {
            ("submitted", "assigned"): "Complaint assigned to department",
            ("submitted", "rejected"): "Complaint rejected",
            ("assigned", "in_progress"): "Work started",
            ("assigned", "rejected"): "Unable to process complaint",
            ("in_progress", "resolved"): "Work completed",
            ("in_progress", "assigned"): "Complaint reassigned",
            ("in_progress", "rejected"): "Unable to complete work",
            ("resolved", "closed"): "Work approved and complaint closed",
            ("resolved", "in_progress"): "Work not satisfactory, needs rework",
        }
        return reasons.get((current_status, new_status), "Status updated")
    
    @staticmethod
    def suggest_department(category: str) -> Optional[str]:
        """
        Suggest department based on complaint category
        """
        return CATEGORY_DEPARTMENT_MAPPING.get(category)
    
    @staticmethod
    def requires_work_approval(status: str) -> bool:
        """
        Check if this status requires work approval (photos)
        """
        return status == "resolved"
    
    @staticmethod
    def can_reopen(current_status: str) -> bool:
        """
        Check if complaint can be reopened
        """
        return current_status == "resolved"
    
    @staticmethod
    def is_terminal_status(status: str) -> bool:
        """
        Check if status is terminal (no further transitions)
        """
        return status in ["closed", "rejected"]


class WorkflowError(Exception):
    """Custom exception for workflow violations"""
    pass


def validate_status_transition(
    current_status: str,
    new_status: str,
    user_role: str,
    raise_exception: bool = True
) -> bool:
    """
    Validate a status transition
    
    Args:
        current_status: Current complaint status
        new_status: Desired new status
        user_role: Role of user making the change
        raise_exception: Whether to raise exception on failure
    
    Returns:
        True if valid, False or raises WorkflowError if invalid
    """
    validator = WorkflowValidator()
    
    # Check if transition is allowed
    if not validator.is_valid_transition(current_status, new_status):
        error_msg = (
            f"Invalid status transition from '{current_status}' to '{new_status}'. "
            f"Allowed transitions: {validator.get_allowed_transitions(current_status)}"
        )
        if raise_exception:
            raise WorkflowError(error_msg)
        return False
    
    # Check if user has permission
    if not validator.can_user_transition(current_status, new_status, user_role):
        error_msg = (
            f"User with role '{user_role}' is not authorized to transition "
            f"from '{current_status}' to '{new_status}'"
        )
        if raise_exception:
            raise WorkflowError(error_msg)
        return False
    
    return True
