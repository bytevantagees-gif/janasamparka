"""Budget tracking and transparency API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user, get_user_constituency_id
from app.models.budget import WardBudget, DepartmentBudget, BudgetTransaction
from app.models.complaint import Complaint
from app.models.user import User, UserRole
from app.models.ward import Ward
from app.models.department import Department
from app.schemas.budget import (
    WardBudgetCreate,
    WardBudgetUpdate,
    WardBudgetResponse,
    DepartmentBudgetCreate,
    DepartmentBudgetUpdate,
    DepartmentBudgetResponse,
    BudgetTransactionCreate,
    BudgetTransactionResponse,
    ConstituencyBudgetOverview,
    BudgetSummary,
    BudgetTransparencyReport
)


router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])


# ===== Ward Budgets =====

@router.post("/wards", response_model=WardBudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_ward_budget(
    budget_data: WardBudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new ward budget (Admin/Moderator only)."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and moderators can create budgets"
        )
    
    # Check if budget already exists for this ward/year/category
    result = await db.execute(
        select(WardBudget).where(
            and_(
                WardBudget.ward_id == budget_data.ward_id,
                WardBudget.financial_year == budget_data.financial_year,
                WardBudget.category == budget_data.category
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget already exists for this ward, year, and category"
        )
    
    budget = WardBudget(
        ward_id=budget_data.ward_id,
        financial_year=budget_data.financial_year,
        category=budget_data.category,
        allocated=budget_data.allocated,
        notes=budget_data.notes
    )
    
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    
    return budget


@router.get("/wards/{ward_id}", response_model=List[WardBudgetResponse])
async def get_ward_budgets(
    ward_id: UUID,
    financial_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all budgets for a ward."""
    query = select(WardBudget).where(WardBudget.ward_id == ward_id)
    
    if financial_year:
        query = query.where(WardBudget.financial_year == financial_year)
    
    result = await db.execute(query)
    budgets = result.scalars().all()
    
    return budgets


@router.patch("/wards/{budget_id}", response_model=WardBudgetResponse)
async def update_ward_budget(
    budget_id: UUID,
    budget_data: WardBudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update ward budget (Admin/Moderator only)."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and moderators can update budgets"
        )
    
    result = await db.execute(select(WardBudget).where(WardBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if budget_data.allocated is not None:
        budget.allocated = budget_data.allocated
    if budget_data.spent is not None:
        budget.spent = budget_data.spent
    if budget_data.committed is not None:
        budget.committed = budget_data.committed
    if budget_data.notes is not None:
        budget.notes = budget_data.notes
    
    await db.commit()
    await db.refresh(budget)
    
    return budget


# ===== Department Budgets =====

@router.post("/departments", response_model=DepartmentBudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_department_budget(
    budget_data: DepartmentBudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new department budget (Admin/Moderator only)."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and moderators can create budgets"
        )
    
    # Check if budget already exists
    result = await db.execute(
        select(DepartmentBudget).where(
            and_(
                DepartmentBudget.department_id == budget_data.department_id,
                DepartmentBudget.constituency_id == budget_data.constituency_id,
                DepartmentBudget.financial_year == budget_data.financial_year,
                DepartmentBudget.category == budget_data.category
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget already exists for this department, year, and category"
        )
    
    budget = DepartmentBudget(
        department_id=budget_data.department_id,
        constituency_id=budget_data.constituency_id,
        financial_year=budget_data.financial_year,
        category=budget_data.category,
        allocated=budget_data.allocated,
        notes=budget_data.notes
    )
    
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    
    return budget


@router.get("/departments/{department_id}", response_model=List[DepartmentBudgetResponse])
async def get_department_budgets(
    department_id: UUID,
    constituency_id: Optional[UUID] = None,
    financial_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all budgets for a department."""
    query = select(DepartmentBudget).where(DepartmentBudget.department_id == department_id)
    
    if constituency_id:
        query = query.where(DepartmentBudget.constituency_id == constituency_id)
    if financial_year:
        query = query.where(DepartmentBudget.financial_year == financial_year)
    
    result = await db.execute(query)
    budgets = result.scalars().all()
    
    return budgets


# ===== Budget Transactions =====

@router.post("/wards/{budget_id}/transactions", response_model=BudgetTransactionResponse)
async def create_ward_transaction(
    budget_id: UUID,
    transaction_data: BudgetTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a ward budget transaction."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR, UserRole.DEPARTMENT_OFFICER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get budget
    result = await db.execute(select(WardBudget).where(WardBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    # Update budget based on transaction type
    if transaction_data.transaction_type == "expense":
        budget.spent += transaction_data.amount
    elif transaction_data.transaction_type == "commitment":
        budget.committed += transaction_data.amount
    elif transaction_data.transaction_type == "refund":
        budget.spent -= transaction_data.amount
    
    # Create transaction record
    transaction = BudgetTransaction(
        ward_budget_id=budget_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        description=transaction_data.description,
        complaint_id=transaction_data.complaint_id,
        performed_by=current_user.id
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.get("/transactions", response_model=List[BudgetTransactionResponse])
async def get_transactions(
    ward_budget_id: Optional[UUID] = None,
    department_budget_id: Optional[UUID] = None,
    limit: int = Query(50, ge=1, le=100),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get budget transactions. Non-admin users only see transactions from their constituency."""
    # Build base query with joins to get constituency info
    query = select(BudgetTransaction).outerjoin(WardBudget, BudgetTransaction.ward_budget_id == WardBudget.id).outerjoin(DepartmentBudget, BudgetTransaction.department_budget_id == DepartmentBudget.id)
    
    # Apply constituency filtering for non-admin users
    if constituency_filter:
        query = query.where(
            (WardBudget.constituency_id == constituency_filter) | 
            (DepartmentBudget.constituency_id == constituency_filter) |
            (BudgetTransaction.ward_budget_id.is_(None) & BudgetTransaction.department_budget_id.is_(None))
        )
    
    if ward_budget_id:
        query = query.where(BudgetTransaction.ward_budget_id == ward_budget_id)
    if department_budget_id:
        query = query.where(BudgetTransaction.department_budget_id == department_budget_id)
    
    query = query.order_by(BudgetTransaction.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return transactions


# ===== Budget Overview & Transparency =====

@router.get("/constituencies/{constituency_id}/overview", response_model=ConstituencyBudgetOverview)
async def get_constituency_budget_overview(
    constituency_id: UUID,
    financial_year: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive budget overview for a constituency."""
    # Get department budgets for this constituency
    dept_result = await db.execute(
        select(DepartmentBudget).where(
            and_(
                DepartmentBudget.constituency_id == constituency_id,
                DepartmentBudget.financial_year == financial_year
            )
        )
    )
    dept_budgets = dept_result.scalars().all()
    
    # Calculate totals
    total_allocated = sum(b.allocated for b in dept_budgets)
    total_spent = sum(b.spent for b in dept_budgets)
    total_committed = sum(b.committed for b in dept_budgets)
    total_remaining = total_allocated - total_spent - total_committed
    
    overall_utilization = ((total_spent + total_committed) / total_allocated * 100) if total_allocated > 0 else 0
    
    # Group by category
    category_map = {}
    for budget in dept_budgets:
        if budget.category not in category_map:
            category_map[budget.category] = {
                "allocated": 0,
                "spent": 0,
                "committed": 0
            }
        category_map[budget.category]["allocated"] += budget.allocated
        category_map[budget.category]["spent"] += budget.spent
        category_map[budget.category]["committed"] += budget.committed
    
    by_category = [
        BudgetSummary(
            category=cat,
            allocated=data["allocated"],
            spent=data["spent"],
            committed=data["committed"],
            remaining=data["allocated"] - data["spent"] - data["committed"],
            utilization_percentage=((data["spent"] + data["committed"]) / data["allocated"] * 100) if data["allocated"] > 0 else 0
        )
        for cat, data in category_map.items()
    ]
    
    return ConstituencyBudgetOverview(
        constituency_id=constituency_id,
        financial_year=financial_year,
        total_allocated=total_allocated,
        total_spent=total_spent,
        total_committed=total_committed,
        total_remaining=total_remaining,
        overall_utilization=overall_utilization,
        by_category=by_category
    )


@router.get("/constituencies/{constituency_id}/transparency", response_model=BudgetTransparencyReport)
async def get_transparency_report(
    constituency_id: UUID,
    financial_year: str,
    db: AsyncSession = Depends(get_db)
):
    """Public budget transparency report (no authentication required)."""
    # Get constituency name
    from app.models.constituency import Constituency
    const_result = await db.execute(select(Constituency).where(Constituency.id == constituency_id))
    constituency = const_result.scalar_one_or_none()
    
    if not constituency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constituency not found")
    
    # Get department budgets
    dept_result = await db.execute(
        select(DepartmentBudget).where(
            and_(
                DepartmentBudget.constituency_id == constituency_id,
                DepartmentBudget.financial_year == financial_year
            )
        )
    )
    dept_budgets = dept_result.scalars().all()
    
    total_budget = sum(b.allocated for b in dept_budgets)
    spent_to_date = sum(b.spent for b in dept_budgets)
    
    # Get complaint counts
    resolved_result = await db.execute(
        select(func.count(Complaint.id)).where(
            and_(
                Complaint.constituency_id == constituency_id,
                Complaint.status == "resolved"
            )
        )
    )
    projects_completed = resolved_result.scalar() or 0
    
    ongoing_result = await db.execute(
        select(func.count(Complaint.id)).where(
            and_(
                Complaint.constituency_id == constituency_id,
                Complaint.status.in_(["assigned", "in_progress"])
            )
        )
    )
    projects_ongoing = ongoing_result.scalar() or 0
    
    # Top spending categories
    category_spending = {}
    for budget in dept_budgets:
        if budget.category not in category_spending:
            category_spending[budget.category] = 0
        category_spending[budget.category] += budget.spent
    
    top_spending = [
        {"category": cat, "amount": amt}
        for cat, amt in sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Recent transactions
    tx_result = await db.execute(
        select(BudgetTransaction)
        .join(DepartmentBudget)
        .where(DepartmentBudget.constituency_id == constituency_id)
        .order_by(BudgetTransaction.created_at.desc())
        .limit(20)
    )
    recent_transactions = tx_result.scalars().all()
    
    return BudgetTransparencyReport(
        constituency_id=constituency_id,
        constituency_name=constituency.name,
        financial_year=financial_year,
        total_budget=total_budget,
        spent_to_date=spent_to_date,
        projects_completed=projects_completed,
        projects_ongoing=projects_ongoing,
        top_spending_categories=top_spending,
        recent_transactions=recent_transactions,
        utilization_by_month=[]  # TODO: Implement monthly breakdown
    )
