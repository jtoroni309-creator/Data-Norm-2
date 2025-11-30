"""
Group Audit API Routes

Provides endpoints for managing group audit engagements, including:
- Parent/subsidiary engagement linking
- Component entity management
- Component auditor management
- Cross-entity risk consolidation
- Elimination entries
- Consolidated financial statement assembly
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database import get_db
from .models import (
    GroupEngagement,
    ComponentEntity,
    ComponentAuditor,
    EliminationEntry,
    ConsolidatedStatement,
    GroupAuditRiskConsolidation,
    Engagement,
    ComponentSignificance,
    ComponentAuditApproach,
    ComponentAuditorType,
    EliminationEntryType,
    ConsolidationMethod,
)

router = APIRouter(prefix="/group-audit", tags=["Group Audit"])


# ========================================
# Pydantic Schemas
# ========================================

class GroupEngagementCreate(BaseModel):
    parent_engagement_id: UUID
    group_name: str
    ultimate_parent_name: Optional[str] = None
    reporting_framework: str = "US GAAP"
    functional_currency: str = "USD"
    consolidation_date: Optional[date] = None
    reporting_period_end: Optional[date] = None


class GroupEngagementUpdate(BaseModel):
    group_name: Optional[str] = None
    ultimate_parent_name: Optional[str] = None
    reporting_framework: Optional[str] = None
    functional_currency: Optional[str] = None
    group_materiality: Optional[int] = None
    group_performance_materiality: Optional[int] = None
    component_materiality: Optional[int] = None
    clearly_trivial_threshold: Optional[int] = None
    group_risk_level: Optional[str] = None
    risk_factors: Optional[dict] = None
    consolidation_date: Optional[date] = None
    reporting_period_end: Optional[date] = None
    status: Optional[str] = None


class GroupEngagementResponse(BaseModel):
    id: UUID
    parent_engagement_id: UUID
    group_name: str
    ultimate_parent_name: Optional[str]
    reporting_framework: str
    functional_currency: str
    group_materiality: Optional[int]
    group_performance_materiality: Optional[int]
    component_materiality: Optional[int]
    clearly_trivial_threshold: Optional[int]
    group_risk_level: str
    risk_factors: Optional[dict]
    consolidation_date: Optional[date]
    reporting_period_end: Optional[date]
    status: str
    created_at: datetime
    updated_at: datetime
    component_count: Optional[int] = 0
    total_assets: Optional[int] = 0
    total_revenue: Optional[int] = 0

    class Config:
        from_attributes = True


class ComponentEntityCreate(BaseModel):
    entity_name: str
    entity_code: Optional[str] = None
    legal_name: Optional[str] = None
    jurisdiction: Optional[str] = None
    functional_currency: str = "USD"
    ownership_percentage: int = 100
    direct_parent_id: Optional[UUID] = None
    consolidation_method: str = "full_consolidation"
    total_assets: Optional[int] = None
    total_revenue: Optional[int] = None
    net_income: Optional[int] = None


class ComponentEntityUpdate(BaseModel):
    entity_name: Optional[str] = None
    entity_code: Optional[str] = None
    legal_name: Optional[str] = None
    jurisdiction: Optional[str] = None
    functional_currency: Optional[str] = None
    ownership_percentage: Optional[int] = None
    direct_parent_id: Optional[UUID] = None
    consolidation_method: Optional[str] = None
    significance: Optional[str] = None
    significance_factors: Optional[dict] = None
    total_assets: Optional[int] = None
    total_revenue: Optional[int] = None
    net_income: Optional[int] = None
    percentage_of_group_assets: Optional[int] = None
    percentage_of_group_revenue: Optional[int] = None
    audit_approach: Optional[str] = None
    scoped_accounts: Optional[list] = None
    component_materiality: Optional[int] = None
    component_performance_materiality: Optional[int] = None
    risk_level: Optional[str] = None
    identified_risks: Optional[list] = None
    status: Optional[str] = None
    completion_percentage: Optional[int] = None
    component_engagement_id: Optional[UUID] = None


class ComponentEntityResponse(BaseModel):
    id: UUID
    group_engagement_id: UUID
    component_engagement_id: Optional[UUID]
    entity_name: str
    entity_code: Optional[str]
    legal_name: Optional[str]
    jurisdiction: Optional[str]
    functional_currency: str
    ownership_percentage: int
    direct_parent_id: Optional[UUID]
    consolidation_method: Optional[str]
    significance: Optional[str]
    significance_factors: Optional[dict]
    total_assets: Optional[int]
    total_revenue: Optional[int]
    net_income: Optional[int]
    percentage_of_group_assets: Optional[int]
    percentage_of_group_revenue: Optional[int]
    audit_approach: Optional[str]
    scoped_accounts: Optional[list]
    component_materiality: Optional[int]
    component_performance_materiality: Optional[int]
    risk_level: str
    identified_risks: Optional[list]
    status: str
    completion_percentage: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComponentAuditorCreate(BaseModel):
    auditor_type: str
    firm_name: str
    firm_id: Optional[UUID] = None
    lead_partner_name: Optional[str] = None
    lead_partner_email: Optional[str] = None
    lead_partner_phone: Optional[str] = None
    reporting_deadline: Optional[date] = None


class ComponentAuditorUpdate(BaseModel):
    auditor_type: Optional[str] = None
    firm_name: Optional[str] = None
    lead_partner_name: Optional[str] = None
    lead_partner_email: Optional[str] = None
    lead_partner_phone: Optional[str] = None
    competence_assessment: Optional[str] = None
    independence_confirmed: Optional[bool] = None
    independence_confirmation_date: Optional[date] = None
    instructions_sent_date: Optional[date] = None
    instructions_acknowledged_date: Optional[date] = None
    reporting_deadline: Optional[date] = None
    deliverables: Optional[list] = None
    deliverables_received: Optional[bool] = None
    deliverables_reviewed: Optional[bool] = None
    issues_identified: Optional[list] = None
    findings_summary: Optional[str] = None
    status: Optional[str] = None


class ComponentAuditorResponse(BaseModel):
    id: UUID
    component_entity_id: UUID
    auditor_type: str
    firm_name: str
    firm_id: Optional[UUID]
    lead_partner_name: Optional[str]
    lead_partner_email: Optional[str]
    lead_partner_phone: Optional[str]
    competence_assessment: Optional[str]
    independence_confirmed: bool
    independence_confirmation_date: Optional[date]
    instructions_sent_date: Optional[date]
    instructions_acknowledged_date: Optional[date]
    reporting_deadline: Optional[date]
    deliverables: Optional[list]
    deliverables_received: bool
    deliverables_reviewed: bool
    issues_identified: Optional[list]
    findings_summary: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EliminationEntryCreate(BaseModel):
    entry_type: str
    description: str
    from_entity_id: Optional[UUID] = None
    to_entity_id: Optional[UUID] = None
    debit_account: Optional[str] = None
    debit_amount: Optional[int] = None
    credit_account: Optional[str] = None
    credit_amount: Optional[int] = None
    journal_lines: Optional[list] = None
    documentation: Optional[str] = None
    is_recurring: bool = False
    prior_year_amount: Optional[int] = None


class EliminationEntryUpdate(BaseModel):
    entry_type: Optional[str] = None
    description: Optional[str] = None
    from_entity_id: Optional[UUID] = None
    to_entity_id: Optional[UUID] = None
    debit_account: Optional[str] = None
    debit_amount: Optional[int] = None
    credit_account: Optional[str] = None
    credit_amount: Optional[int] = None
    journal_lines: Optional[list] = None
    documentation: Optional[str] = None
    is_recurring: Optional[bool] = None
    prior_year_amount: Optional[int] = None
    status: Optional[str] = None


class EliminationEntryResponse(BaseModel):
    id: UUID
    group_engagement_id: UUID
    entry_number: Optional[str]
    entry_type: str
    description: str
    from_entity_id: Optional[UUID]
    to_entity_id: Optional[UUID]
    debit_account: Optional[str]
    debit_amount: Optional[int]
    credit_account: Optional[str]
    credit_amount: Optional[int]
    journal_lines: Optional[list]
    documentation: Optional[str]
    is_recurring: bool
    prior_year_amount: Optional[int]
    status: str
    prepared_by: Optional[UUID]
    prepared_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskConsolidationCreate(BaseModel):
    risk_category: str
    risk_title: str
    risk_description: Optional[str] = None
    inherent_risk: str = "moderate"
    control_risk: str = "moderate"
    affected_components: Optional[list] = None
    pervasive: bool = False
    planned_response: Optional[str] = None
    audit_procedures: Optional[list] = None


class RiskConsolidationUpdate(BaseModel):
    risk_category: Optional[str] = None
    risk_title: Optional[str] = None
    risk_description: Optional[str] = None
    inherent_risk: Optional[str] = None
    control_risk: Optional[str] = None
    combined_risk: Optional[str] = None
    affected_components: Optional[list] = None
    pervasive: Optional[bool] = None
    planned_response: Optional[str] = None
    audit_procedures: Optional[list] = None
    status: Optional[str] = None
    conclusion: Optional[str] = None


class RiskConsolidationResponse(BaseModel):
    id: UUID
    group_engagement_id: UUID
    risk_category: str
    risk_title: str
    risk_description: Optional[str]
    inherent_risk: str
    control_risk: str
    combined_risk: str
    affected_components: Optional[list]
    pervasive: bool
    planned_response: Optional[str]
    audit_procedures: Optional[list]
    status: str
    conclusion: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialityAllocationRequest(BaseModel):
    group_materiality: int
    allocation_method: str = "proportional"  # proportional, risk_based, equal
    performance_materiality_percentage: int = 75


class MaterialityAllocationResponse(BaseModel):
    group_materiality: int
    group_performance_materiality: int
    component_materiality: int
    clearly_trivial_threshold: int
    component_allocations: List[dict]


# ========================================
# Group Engagement Endpoints
# ========================================

@router.post("/", response_model=GroupEngagementResponse, status_code=status.HTTP_201_CREATED)
async def create_group_engagement(
    data: GroupEngagementCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = "demo-user"
):
    """Create a new group audit engagement from an existing engagement"""
    # Verify parent engagement exists
    parent_result = await db.execute(
        select(Engagement).where(Engagement.id == data.parent_engagement_id)
    )
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent engagement not found")

    # Check if group engagement already exists for this parent
    existing = await db.execute(
        select(GroupEngagement).where(
            GroupEngagement.parent_engagement_id == data.parent_engagement_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="A group engagement already exists for this parent engagement"
        )

    group_engagement = GroupEngagement(
        id=uuid4(),
        parent_engagement_id=data.parent_engagement_id,
        group_name=data.group_name,
        ultimate_parent_name=data.ultimate_parent_name,
        reporting_framework=data.reporting_framework,
        functional_currency=data.functional_currency,
        consolidation_date=data.consolidation_date,
        reporting_period_end=data.reporting_period_end,
        created_by=UUID(user_id) if user_id != "demo-user" else uuid4(),
    )

    db.add(group_engagement)
    await db.commit()
    await db.refresh(group_engagement)

    return GroupEngagementResponse(
        **{k: v for k, v in group_engagement.__dict__.items() if not k.startswith('_')},
        component_count=0,
        total_assets=0,
        total_revenue=0
    )


@router.get("/{group_id}", response_model=GroupEngagementResponse)
async def get_group_engagement(
    group_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a group engagement with aggregated component metrics"""
    result = await db.execute(
        select(GroupEngagement)
        .options(selectinload(GroupEngagement.component_entities))
        .where(GroupEngagement.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group engagement not found")

    # Calculate aggregates
    component_count = len(group.component_entities)
    total_assets = sum(c.total_assets or 0 for c in group.component_entities)
    total_revenue = sum(c.total_revenue or 0 for c in group.component_entities)

    return GroupEngagementResponse(
        **{k: v for k, v in group.__dict__.items() if not k.startswith('_')},
        component_count=component_count,
        total_assets=total_assets,
        total_revenue=total_revenue
    )


@router.get("/by-engagement/{engagement_id}", response_model=GroupEngagementResponse)
async def get_group_by_engagement(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get group engagement by parent engagement ID"""
    result = await db.execute(
        select(GroupEngagement)
        .options(selectinload(GroupEngagement.component_entities))
        .where(GroupEngagement.parent_engagement_id == engagement_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="No group engagement found for this engagement")

    component_count = len(group.component_entities)
    total_assets = sum(c.total_assets or 0 for c in group.component_entities)
    total_revenue = sum(c.total_revenue or 0 for c in group.component_entities)

    return GroupEngagementResponse(
        **{k: v for k, v in group.__dict__.items() if not k.startswith('_')},
        component_count=component_count,
        total_assets=total_assets,
        total_revenue=total_revenue
    )


@router.patch("/{group_id}", response_model=GroupEngagementResponse)
async def update_group_engagement(
    group_id: UUID,
    data: GroupEngagementUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a group engagement"""
    result = await db.execute(
        select(GroupEngagement)
        .options(selectinload(GroupEngagement.component_entities))
        .where(GroupEngagement.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group engagement not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)

    await db.commit()
    await db.refresh(group)

    component_count = len(group.component_entities)
    total_assets = sum(c.total_assets or 0 for c in group.component_entities)
    total_revenue = sum(c.total_revenue or 0 for c in group.component_entities)

    return GroupEngagementResponse(
        **{k: v for k, v in group.__dict__.items() if not k.startswith('_')},
        component_count=component_count,
        total_assets=total_assets,
        total_revenue=total_revenue
    )


# ========================================
# Component Entity Endpoints
# ========================================

@router.post("/{group_id}/components", response_model=ComponentEntityResponse, status_code=status.HTTP_201_CREATED)
async def create_component_entity(
    group_id: UUID,
    data: ComponentEntityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a component entity to a group engagement"""
    # Verify group exists
    group_result = await db.execute(
        select(GroupEngagement).where(GroupEngagement.id == group_id)
    )
    if not group_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Group engagement not found")

    component = ComponentEntity(
        id=uuid4(),
        group_engagement_id=group_id,
        entity_name=data.entity_name,
        entity_code=data.entity_code,
        legal_name=data.legal_name,
        jurisdiction=data.jurisdiction,
        functional_currency=data.functional_currency,
        ownership_percentage=data.ownership_percentage,
        direct_parent_id=data.direct_parent_id,
        total_assets=data.total_assets,
        total_revenue=data.total_revenue,
        net_income=data.net_income,
    )

    # Set consolidation method enum
    if data.consolidation_method:
        component.consolidation_method = ConsolidationMethod(data.consolidation_method)

    db.add(component)
    await db.commit()
    await db.refresh(component)

    return ComponentEntityResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in component.__dict__.items() if not k.startswith('_')}
    )


@router.get("/{group_id}/components", response_model=List[ComponentEntityResponse])
async def list_component_entities(
    group_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all component entities in a group engagement"""
    result = await db.execute(
        select(ComponentEntity)
        .where(ComponentEntity.group_engagement_id == group_id)
        .order_by(ComponentEntity.entity_name)
    )
    components = result.scalars().all()

    return [
        ComponentEntityResponse(
            **{k: (v.value if hasattr(v, 'value') else v) for k, v in c.__dict__.items() if not k.startswith('_')}
        )
        for c in components
    ]


@router.get("/{group_id}/components/{component_id}", response_model=ComponentEntityResponse)
async def get_component_entity(
    group_id: UUID,
    component_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific component entity"""
    result = await db.execute(
        select(ComponentEntity)
        .where(
            and_(
                ComponentEntity.id == component_id,
                ComponentEntity.group_engagement_id == group_id
            )
        )
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component entity not found")

    return ComponentEntityResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in component.__dict__.items() if not k.startswith('_')}
    )


@router.patch("/{group_id}/components/{component_id}", response_model=ComponentEntityResponse)
async def update_component_entity(
    group_id: UUID,
    component_id: UUID,
    data: ComponentEntityUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a component entity"""
    result = await db.execute(
        select(ComponentEntity)
        .where(
            and_(
                ComponentEntity.id == component_id,
                ComponentEntity.group_engagement_id == group_id
            )
        )
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component entity not found")

    update_data = data.model_dump(exclude_unset=True)

    # Handle enum conversions
    if 'consolidation_method' in update_data and update_data['consolidation_method']:
        update_data['consolidation_method'] = ConsolidationMethod(update_data['consolidation_method'])
    if 'significance' in update_data and update_data['significance']:
        update_data['significance'] = ComponentSignificance(update_data['significance'])
    if 'audit_approach' in update_data and update_data['audit_approach']:
        update_data['audit_approach'] = ComponentAuditApproach(update_data['audit_approach'])

    for key, value in update_data.items():
        setattr(component, key, value)

    await db.commit()
    await db.refresh(component)

    return ComponentEntityResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in component.__dict__.items() if not k.startswith('_')}
    )


@router.delete("/{group_id}/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component_entity(
    group_id: UUID,
    component_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a component entity"""
    result = await db.execute(
        select(ComponentEntity)
        .where(
            and_(
                ComponentEntity.id == component_id,
                ComponentEntity.group_engagement_id == group_id
            )
        )
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component entity not found")

    await db.delete(component)
    await db.commit()


# ========================================
# Component Auditor Endpoints
# ========================================

@router.post("/{group_id}/components/{component_id}/auditors", response_model=ComponentAuditorResponse, status_code=status.HTTP_201_CREATED)
async def create_component_auditor(
    group_id: UUID,
    component_id: UUID,
    data: ComponentAuditorCreate,
    db: AsyncSession = Depends(get_db)
):
    """Assign an auditor to a component entity"""
    # Verify component exists
    component_result = await db.execute(
        select(ComponentEntity)
        .where(
            and_(
                ComponentEntity.id == component_id,
                ComponentEntity.group_engagement_id == group_id
            )
        )
    )
    if not component_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Component entity not found")

    auditor = ComponentAuditor(
        id=uuid4(),
        component_entity_id=component_id,
        auditor_type=ComponentAuditorType(data.auditor_type),
        firm_name=data.firm_name,
        firm_id=data.firm_id,
        lead_partner_name=data.lead_partner_name,
        lead_partner_email=data.lead_partner_email,
        lead_partner_phone=data.lead_partner_phone,
        reporting_deadline=data.reporting_deadline,
    )

    db.add(auditor)
    await db.commit()
    await db.refresh(auditor)

    return ComponentAuditorResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in auditor.__dict__.items() if not k.startswith('_')}
    )


@router.get("/{group_id}/components/{component_id}/auditors", response_model=List[ComponentAuditorResponse])
async def list_component_auditors(
    group_id: UUID,
    component_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all auditors for a component entity"""
    result = await db.execute(
        select(ComponentAuditor)
        .where(ComponentAuditor.component_entity_id == component_id)
    )
    auditors = result.scalars().all()

    return [
        ComponentAuditorResponse(
            **{k: (v.value if hasattr(v, 'value') else v) for k, v in a.__dict__.items() if not k.startswith('_')}
        )
        for a in auditors
    ]


@router.patch("/{group_id}/auditors/{auditor_id}", response_model=ComponentAuditorResponse)
async def update_component_auditor(
    group_id: UUID,
    auditor_id: UUID,
    data: ComponentAuditorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a component auditor"""
    result = await db.execute(
        select(ComponentAuditor).where(ComponentAuditor.id == auditor_id)
    )
    auditor = result.scalar_one_or_none()
    if not auditor:
        raise HTTPException(status_code=404, detail="Component auditor not found")

    update_data = data.model_dump(exclude_unset=True)

    if 'auditor_type' in update_data and update_data['auditor_type']:
        update_data['auditor_type'] = ComponentAuditorType(update_data['auditor_type'])

    for key, value in update_data.items():
        setattr(auditor, key, value)

    await db.commit()
    await db.refresh(auditor)

    return ComponentAuditorResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in auditor.__dict__.items() if not k.startswith('_')}
    )


# ========================================
# Elimination Entry Endpoints
# ========================================

@router.post("/{group_id}/eliminations", response_model=EliminationEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_elimination_entry(
    group_id: UUID,
    data: EliminationEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an elimination entry for consolidation"""
    # Verify group exists
    group_result = await db.execute(
        select(GroupEngagement).where(GroupEngagement.id == group_id)
    )
    if not group_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Group engagement not found")

    # Get next entry number
    count_result = await db.execute(
        select(func.count(EliminationEntry.id))
        .where(EliminationEntry.group_engagement_id == group_id)
    )
    count = count_result.scalar() or 0
    entry_number = f"ELIM-{count + 1:03d}"

    elimination = EliminationEntry(
        id=uuid4(),
        group_engagement_id=group_id,
        entry_number=entry_number,
        entry_type=EliminationEntryType(data.entry_type),
        description=data.description,
        from_entity_id=data.from_entity_id,
        to_entity_id=data.to_entity_id,
        debit_account=data.debit_account,
        debit_amount=data.debit_amount,
        credit_account=data.credit_account,
        credit_amount=data.credit_amount,
        journal_lines=data.journal_lines,
        documentation=data.documentation,
        is_recurring=data.is_recurring,
        prior_year_amount=data.prior_year_amount,
    )

    db.add(elimination)
    await db.commit()
    await db.refresh(elimination)

    return EliminationEntryResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in elimination.__dict__.items() if not k.startswith('_')}
    )


@router.get("/{group_id}/eliminations", response_model=List[EliminationEntryResponse])
async def list_elimination_entries(
    group_id: UUID,
    entry_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all elimination entries for a group engagement"""
    query = select(EliminationEntry).where(EliminationEntry.group_engagement_id == group_id)

    if entry_type:
        query = query.where(EliminationEntry.entry_type == EliminationEntryType(entry_type))

    query = query.order_by(EliminationEntry.entry_number)
    result = await db.execute(query)
    entries = result.scalars().all()

    return [
        EliminationEntryResponse(
            **{k: (v.value if hasattr(v, 'value') else v) for k, v in e.__dict__.items() if not k.startswith('_')}
        )
        for e in entries
    ]


@router.patch("/{group_id}/eliminations/{elimination_id}", response_model=EliminationEntryResponse)
async def update_elimination_entry(
    group_id: UUID,
    elimination_id: UUID,
    data: EliminationEntryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an elimination entry"""
    result = await db.execute(
        select(EliminationEntry)
        .where(
            and_(
                EliminationEntry.id == elimination_id,
                EliminationEntry.group_engagement_id == group_id
            )
        )
    )
    elimination = result.scalar_one_or_none()
    if not elimination:
        raise HTTPException(status_code=404, detail="Elimination entry not found")

    update_data = data.model_dump(exclude_unset=True)

    if 'entry_type' in update_data and update_data['entry_type']:
        update_data['entry_type'] = EliminationEntryType(update_data['entry_type'])

    for key, value in update_data.items():
        setattr(elimination, key, value)

    await db.commit()
    await db.refresh(elimination)

    return EliminationEntryResponse(
        **{k: (v.value if hasattr(v, 'value') else v) for k, v in elimination.__dict__.items() if not k.startswith('_')}
    )


@router.delete("/{group_id}/eliminations/{elimination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_elimination_entry(
    group_id: UUID,
    elimination_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete an elimination entry"""
    result = await db.execute(
        select(EliminationEntry)
        .where(
            and_(
                EliminationEntry.id == elimination_id,
                EliminationEntry.group_engagement_id == group_id
            )
        )
    )
    elimination = result.scalar_one_or_none()
    if not elimination:
        raise HTTPException(status_code=404, detail="Elimination entry not found")

    await db.delete(elimination)
    await db.commit()


# ========================================
# Risk Consolidation Endpoints
# ========================================

@router.post("/{group_id}/risks", response_model=RiskConsolidationResponse, status_code=status.HTTP_201_CREATED)
async def create_risk_consolidation(
    group_id: UUID,
    data: RiskConsolidationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = "demo-user"
):
    """Create a consolidated risk for the group"""
    # Verify group exists
    group_result = await db.execute(
        select(GroupEngagement).where(GroupEngagement.id == group_id)
    )
    if not group_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Group engagement not found")

    # Calculate combined risk
    risk_matrix = {
        ("low", "low"): "low",
        ("low", "moderate"): "moderate",
        ("low", "high"): "moderate",
        ("moderate", "low"): "moderate",
        ("moderate", "moderate"): "moderate",
        ("moderate", "high"): "high",
        ("high", "low"): "moderate",
        ("high", "moderate"): "high",
        ("high", "high"): "very_high",
        ("very_high", "low"): "high",
        ("very_high", "moderate"): "very_high",
        ("very_high", "high"): "very_high",
    }
    combined = risk_matrix.get((data.inherent_risk, data.control_risk), "moderate")

    risk = GroupAuditRiskConsolidation(
        id=uuid4(),
        group_engagement_id=group_id,
        risk_category=data.risk_category,
        risk_title=data.risk_title,
        risk_description=data.risk_description,
        inherent_risk=data.inherent_risk,
        control_risk=data.control_risk,
        combined_risk=combined,
        affected_components=data.affected_components,
        pervasive=data.pervasive,
        planned_response=data.planned_response,
        audit_procedures=data.audit_procedures,
        created_by=UUID(user_id) if user_id != "demo-user" else uuid4(),
    )

    db.add(risk)
    await db.commit()
    await db.refresh(risk)

    return RiskConsolidationResponse(
        **{k: v for k, v in risk.__dict__.items() if not k.startswith('_')}
    )


@router.get("/{group_id}/risks", response_model=List[RiskConsolidationResponse])
async def list_risk_consolidations(
    group_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all consolidated risks for a group"""
    result = await db.execute(
        select(GroupAuditRiskConsolidation)
        .where(GroupAuditRiskConsolidation.group_engagement_id == group_id)
        .order_by(GroupAuditRiskConsolidation.risk_category)
    )
    risks = result.scalars().all()

    return [
        RiskConsolidationResponse(
            **{k: v for k, v in r.__dict__.items() if not k.startswith('_')}
        )
        for r in risks
    ]


@router.patch("/{group_id}/risks/{risk_id}", response_model=RiskConsolidationResponse)
async def update_risk_consolidation(
    group_id: UUID,
    risk_id: UUID,
    data: RiskConsolidationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a consolidated risk"""
    result = await db.execute(
        select(GroupAuditRiskConsolidation)
        .where(
            and_(
                GroupAuditRiskConsolidation.id == risk_id,
                GroupAuditRiskConsolidation.group_engagement_id == group_id
            )
        )
    )
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk consolidation not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(risk, key, value)

    await db.commit()
    await db.refresh(risk)

    return RiskConsolidationResponse(
        **{k: v for k, v in risk.__dict__.items() if not k.startswith('_')}
    )


# ========================================
# Materiality Allocation Endpoint
# ========================================

@router.post("/{group_id}/allocate-materiality", response_model=MaterialityAllocationResponse)
async def allocate_materiality(
    group_id: UUID,
    data: MaterialityAllocationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Allocate group materiality to component entities"""
    # Get group and components
    result = await db.execute(
        select(GroupEngagement)
        .options(selectinload(GroupEngagement.component_entities))
        .where(GroupEngagement.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group engagement not found")

    components = group.component_entities
    if not components:
        raise HTTPException(status_code=400, detail="No component entities to allocate materiality")

    # Calculate group-level values
    group_materiality = data.group_materiality
    group_perf_mat = int(group_materiality * data.performance_materiality_percentage / 100)
    component_mat = int(group_perf_mat * 0.5)  # Component materiality typically 50% of PM
    trivial = int(group_materiality * 0.03)  # 3% of group materiality

    # Update group
    group.group_materiality = group_materiality
    group.group_performance_materiality = group_perf_mat
    group.component_materiality = component_mat
    group.clearly_trivial_threshold = trivial

    # Calculate total for proportional allocation
    total_assets = sum(c.total_assets or 0 for c in components)
    total_revenue = sum(c.total_revenue or 0 for c in components)

    component_allocations = []

    for component in components:
        if data.allocation_method == "proportional":
            # Use revenue proportion, fallback to assets
            if total_revenue > 0:
                proportion = (component.total_revenue or 0) / total_revenue
            elif total_assets > 0:
                proportion = (component.total_assets or 0) / total_assets
            else:
                proportion = 1 / len(components)

            comp_mat = max(int(component_mat * proportion), trivial)
        elif data.allocation_method == "risk_based":
            # Higher materiality for lower risk components
            risk_multipliers = {"low": 1.2, "moderate": 1.0, "high": 0.8}
            multiplier = risk_multipliers.get(component.risk_level, 1.0)
            comp_mat = int(component_mat * multiplier)
        else:  # equal
            comp_mat = int(component_mat / len(components))

        comp_perf_mat = int(comp_mat * data.performance_materiality_percentage / 100)

        component.component_materiality = comp_mat
        component.component_performance_materiality = comp_perf_mat

        # Calculate percentage of group
        if total_assets > 0:
            component.percentage_of_group_assets = int((component.total_assets or 0) / total_assets * 10000)
        if total_revenue > 0:
            component.percentage_of_group_revenue = int((component.total_revenue or 0) / total_revenue * 10000)

        component_allocations.append({
            "component_id": str(component.id),
            "entity_name": component.entity_name,
            "component_materiality": comp_mat,
            "component_performance_materiality": comp_perf_mat,
            "percentage_of_group_revenue": component.percentage_of_group_revenue,
            "percentage_of_group_assets": component.percentage_of_group_assets,
        })

    await db.commit()

    return MaterialityAllocationResponse(
        group_materiality=group_materiality,
        group_performance_materiality=group_perf_mat,
        component_materiality=component_mat,
        clearly_trivial_threshold=trivial,
        component_allocations=component_allocations
    )


# ========================================
# Dashboard/Summary Endpoints
# ========================================

@router.get("/{group_id}/dashboard")
async def get_group_dashboard(
    group_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard data for a group audit"""
    result = await db.execute(
        select(GroupEngagement)
        .options(
            selectinload(GroupEngagement.component_entities).selectinload(ComponentEntity.component_auditors),
            selectinload(GroupEngagement.elimination_entries),
            selectinload(GroupEngagement.risk_consolidations),
        )
        .where(GroupEngagement.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group engagement not found")

    components = group.component_entities
    eliminations = group.elimination_entries
    risks = group.risk_consolidations

    # Component statistics
    significant_components = [c for c in components if c.significance and c.significance.value == "significant"]
    completed_components = [c for c in components if c.status == "completed"]

    # Auditor statistics
    all_auditors = []
    for c in components:
        all_auditors.extend(c.component_auditors)
    external_auditors = [a for a in all_auditors if a.auditor_type.value != "group_team"]
    pending_deliverables = [a for a in all_auditors if not a.deliverables_received]

    # Elimination statistics
    total_eliminations = sum((e.debit_amount or 0) for e in eliminations)
    reviewed_eliminations = [e for e in eliminations if e.status in ("reviewed", "approved")]

    # Risk statistics
    high_risks = [r for r in risks if r.combined_risk in ("high", "very_high")]
    pervasive_risks = [r for r in risks if r.pervasive]

    return {
        "group": {
            "id": str(group.id),
            "group_name": group.group_name,
            "status": group.status,
            "group_materiality": group.group_materiality,
            "reporting_period_end": group.reporting_period_end,
        },
        "components": {
            "total": len(components),
            "significant": len(significant_components),
            "completed": len(completed_components),
            "in_progress": len([c for c in components if c.status == "in_progress"]),
            "pending": len([c for c in components if c.status == "pending"]),
            "total_assets": sum(c.total_assets or 0 for c in components),
            "total_revenue": sum(c.total_revenue or 0 for c in components),
        },
        "auditors": {
            "total": len(all_auditors),
            "external": len(external_auditors),
            "pending_deliverables": len(pending_deliverables),
            "independence_confirmed": len([a for a in all_auditors if a.independence_confirmed]),
        },
        "eliminations": {
            "total_count": len(eliminations),
            "total_amount": total_eliminations,
            "reviewed_count": len(reviewed_eliminations),
            "by_type": {
                t.value: len([e for e in eliminations if e.entry_type == t])
                for t in EliminationEntryType
            },
        },
        "risks": {
            "total": len(risks),
            "high_or_very_high": len(high_risks),
            "pervasive": len(pervasive_risks),
            "by_category": {},
        },
        "completion_status": {
            "components_complete": len(completed_components) == len(components) if components else False,
            "eliminations_reviewed": len(reviewed_eliminations) == len(eliminations) if eliminations else True,
            "overall_percentage": int(
                (len(completed_components) / len(components) * 100) if components else 0
            ),
        },
    }
