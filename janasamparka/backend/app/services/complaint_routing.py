"""
Complaint routing service - Ward-centric approach.

NEW FLOW:
1. Citizen submits complaint → Goes to WARD
2. Ward Officer reviews → Assigns to appropriate DEPARTMENT
3. Department Officer works on it → Updates with public notes
4. Citizen sees public notes, not internal discussions

Wards are under:
- Gram Panchayats (GP) - rural villages
- Taluk Panchayats (TP) - town panchayats  
- City Corporations - urban areas
"""
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.ward import Ward
from app.models.department import Department


def assign_complaint_to_ward(
    db: Session,
    complaint: Complaint,
    ward_id: UUID
) -> bool:
    """
    Initial assignment: Complaint goes to ward.
    Ward officer will then assign to appropriate department.
    
    Returns:
        bool: True if assignment successful
    """
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        return False
    
    complaint.assignment_type = "ward"
    complaint.ward_id = ward_id
    complaint.dept_id = None
    complaint.assigned_to = None
    complaint.ward_officer_id = None  # Will be set when ward officer picks it up
    
    return True


def ward_assign_to_department(
    db: Session,
    complaint: Complaint,
    dept_id: UUID,
    ward_officer_id: UUID,
    public_note: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Ward officer assigns complaint to department.
    
    JURISDICTION VALIDATION:
    - Ward in Puttur GP → Only Puttur GP departments
    - Ward in Puttur TP → Only Puttur TP departments  
    - Ward in Mangalore City Corp → Only Mangalore Corp departments
    
    This ensures Puttur PWD != Mangalore PWD
    
    Args:
        complaint: The complaint to assign
        dept_id: Department to assign to
        ward_officer_id: Ward officer making the assignment
        public_note: Public note explaining why this department (visible to citizen)
    
    Returns:
        Tuple[bool, Optional[str]]: (Success, Error message if failed)
    """
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        return False, "Department not found"
    
    # Get the ward to determine jurisdiction
    ward = db.query(Ward).filter(Ward.id == complaint.ward_id).first()
    if not ward:
        return False, "Ward not found"
    
    # JURISDICTION CHECK: Department must match ward's parent body
    jurisdiction_match = False
    error_msg = "Department jurisdiction mismatch"
    
    if ward.gram_panchayat_id:
        # Ward belongs to Gram Panchayat - department must serve this GP
        if dept.gram_panchayat_id == ward.gram_panchayat_id:
            jurisdiction_match = True
        else:
            error_msg = f"This department does not serve the ward's Gram Panchayat"
    
    elif ward.taluk_panchayat_id:
        # Ward belongs to Taluk Panchayat - department must serve this TP
        if dept.taluk_panchayat_id == ward.taluk_panchayat_id:
            jurisdiction_match = True
        else:
            error_msg = f"This department does not serve the ward's Taluk Panchayat"
    
    elif ward.city_corporation_id:
        # Ward belongs to City Corporation - department must serve this corporation
        if dept.city_corporation_id == ward.city_corporation_id:
            jurisdiction_match = True
        else:
            error_msg = f"This department does not serve the ward's City Corporation"
    
    else:
        return False, "Ward has no parent panchayat/corporation assigned"
    
    if not jurisdiction_match:
        return False, error_msg
    
    # Assignment successful - update complaint
    complaint.assignment_type = "department"
    complaint.dept_id = dept_id
    complaint.ward_officer_id = ward_officer_id
    complaint.assigned_to = None  # Department head will assign to specific officer
    
    # Add public note if provided
    if public_note:
        existing_notes = complaint.public_notes or ""
        timestamp = complaint.updated_at.strftime("%Y-%m-%d %H:%M") if complaint.updated_at else ""
        new_note = f"[{timestamp}] Ward Officer: {public_note}"
        complaint.public_notes = f"{existing_notes}\n\n{new_note}".strip()
    
    return True, None


def department_assign_to_officer(
    db: Session,
    complaint: Complaint,
    officer_id: UUID
) -> bool:
    """
    Department head assigns complaint to specific department officer.
    
    Returns:
        bool: True if assignment successful
    """
    from app.models.user import User
    officer = db.query(User).filter(User.id == officer_id).first()
    if not officer:
        return False
    
    complaint.assigned_to = officer_id
    return True


def add_public_note(
    complaint: Complaint,
    note: str,
    officer_name: str
) -> None:
    """
    Add a public note that citizens can see.
    These should be meaningful updates about progress.
    
    Examples:
    - "Work order issued to contractor"
    - "Materials procured, work will start on Monday"
    - "Work completed, please verify"
    """
    existing_notes = complaint.public_notes or ""
    timestamp = complaint.updated_at.strftime("%Y-%m-%d %H:%M") if complaint.updated_at else ""
    new_note = f"[{timestamp}] {officer_name}: {note}"
    complaint.public_notes = f"{existing_notes}\n\n{new_note}".strip()


def add_internal_note(
    complaint: Complaint,
    note: str,
    officer_name: str
) -> None:
    """
    Add an internal note only visible to officers.
    Used for coordination, budget discussions, etc.
    
    Examples:
    - "Budget approval pending from ZP"
    - "Need to coordinate with PWD for drainage connection"
    - "Citizen called, very angry, priority high"
    """
    existing_notes = complaint.internal_notes or ""
    timestamp = complaint.updated_at.strftime("%Y-%m-%d %H:%M") if complaint.updated_at else ""
    new_note = f"[{timestamp}] {officer_name}: {note}"
    complaint.internal_notes = f"{existing_notes}\n\n{new_note}".strip()


# Legacy functions kept for backward compatibility (but not used in new flow)
def escalate_to_taluk_panchayat(db: Session, complaint: Complaint) -> bool:
    """DEPRECATED: Use ward_assign_to_department instead."""
    return False


def escalate_to_zilla_panchayat(db: Session, complaint: Complaint) -> bool:
    """DEPRECATED: Use ward_assign_to_department instead."""
    return False


def transfer_to_department(db: Session, complaint: Complaint, dept_id: UUID) -> bool:
    """DEPRECATED: Use ward_assign_to_department instead."""
    return False


def reassign_to_gram_panchayat(db: Session, complaint: Complaint, gp_id: UUID) -> bool:
    """DEPRECATED: Not used in new ward-centric flow."""
    return False


def determine_complaint_assignment(
    db: Session,
    category: str,
    gram_panchayat_id: Optional[UUID],
    constituency_id: UUID,
    citizen_selected_dept: bool = False,
    dept_id: Optional[UUID] = None
) -> Tuple[str, Optional[UUID], Optional[UUID], Optional[UUID], Optional[UUID]]:
    """
    DEPRECATED: New flow always assigns to ward first.
    Kept for backward compatibility.
    
    Returns: ("ward", None, None, None, None)
    """
    return ("ward", None, None, None, None)

