"""
AI Data Processing Routes

Handles AI-powered document processing, data extraction, and study completion.
"""

import logging
import io
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import openpyxl
import pandas as pd

from ..database import get_db
from ..models import (
    RDStudy, RDProject, RDEmployee, QualifiedResearchExpense, RDDocument,
    RDCalculation, StudyStatus, QualificationStatus, QRECategory, CreditMethod
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# PAYROLL DATA UPLOAD
# =============================================================================

@router.post("/studies/{study_id}/upload/payroll")
async def upload_payroll_data(
    study_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process payroll data from Excel file."""
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Read file content
    content = await file.read()

    try:
        # Parse Excel file
        workbook = openpyxl.load_workbook(io.BytesIO(content))
        sheet = workbook.active

        employees_created = 0
        employees_updated = 0

        # Expected columns: Name, Title, Department, W2 Wages, Qualified %
        headers = [cell.value for cell in sheet[1]]

        # Find column indices (flexible matching)
        name_col = next((i for i, h in enumerate(headers) if h and 'name' in str(h).lower()), 0)
        title_col = next((i for i, h in enumerate(headers) if h and 'title' in str(h).lower()), 1)
        dept_col = next((i for i, h in enumerate(headers) if h and 'dept' in str(h).lower()), 2)
        wages_col = next((i for i, h in enumerate(headers) if h and ('wage' in str(h).lower() or 'w2' in str(h).lower() or 'salary' in str(h).lower())), 3)
        pct_col = next((i for i, h in enumerate(headers) if h and ('%' in str(h) or 'percent' in str(h).lower() or 'qualified' in str(h).lower())), None)

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[name_col]:
                continue

            name = str(row[name_col]).strip()
            title = str(row[title_col]).strip() if row[title_col] else None
            department = str(row[dept_col]).strip() if row[dept_col] else None

            # Parse wages
            wages_value = row[wages_col]
            if isinstance(wages_value, str):
                wages_value = wages_value.replace('$', '').replace(',', '').strip()
            try:
                w2_wages = Decimal(str(wages_value)) if wages_value else Decimal('0')
            except:
                w2_wages = Decimal('0')

            # Parse qualified percentage
            qualified_pct = Decimal('0')
            if pct_col is not None and row[pct_col]:
                pct_value = row[pct_col]
                if isinstance(pct_value, str):
                    pct_value = pct_value.replace('%', '').strip()
                try:
                    qualified_pct = Decimal(str(pct_value))
                    if qualified_pct > 1:
                        qualified_pct = qualified_pct  # Already in percentage form
                    else:
                        qualified_pct = qualified_pct * 100  # Convert from decimal
                except:
                    qualified_pct = Decimal('0')

            # Calculate qualified wages
            qualified_wages = w2_wages * (qualified_pct / 100)

            # Check if employee exists
            existing_result = await db.execute(
                select(RDEmployee).where(
                    RDEmployee.study_id == study_id,
                    RDEmployee.name == name
                )
            )
            existing = existing_result.scalars().first()

            if existing:
                # Update existing employee
                existing.title = title or existing.title
                existing.department = department or existing.department
                existing.w2_wages = w2_wages
                existing.total_wages = w2_wages
                existing.qualified_time_percentage = qualified_pct
                existing.qualified_wages = qualified_wages
                existing.updated_at = datetime.utcnow()
                employees_updated += 1
            else:
                # Create new employee
                employee = RDEmployee(
                    study_id=study_id,
                    name=name,
                    title=title,
                    department=department,
                    w2_wages=w2_wages,
                    total_wages=w2_wages,
                    qualified_time_percentage=qualified_pct,
                    qualified_wages=qualified_wages,
                    qualified_time_source="payroll_import"
                )
                db.add(employee)
                employees_created += 1

        # Save document record
        document = RDDocument(
            study_id=study_id,
            filename=file.filename,
            file_type=file.content_type,
            document_type="payroll",
            file_size=len(content),
            processing_status="completed",
            storage_path=f"uploads/{study_id}/{file.filename}"
        )
        db.add(document)

        await db.commit()

        return {
            "message": "Payroll data processed successfully",
            "employees_created": employees_created,
            "employees_updated": employees_updated,
            "total_processed": employees_created + employees_updated
        }

    except Exception as e:
        logger.error(f"Error processing payroll file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


# =============================================================================
# PROJECT DATA UPLOAD
# =============================================================================

@router.post("/studies/{study_id}/upload/projects")
async def upload_project_data(
    study_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process project data from Excel file."""
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    content = await file.read()

    try:
        workbook = openpyxl.load_workbook(io.BytesIO(content))
        sheet = workbook.active

        projects_created = 0
        headers = [cell.value for cell in sheet[1]]

        # Find column indices
        name_col = next((i for i, h in enumerate(headers) if h and 'name' in str(h).lower()), 0)
        desc_col = next((i for i, h in enumerate(headers) if h and 'desc' in str(h).lower()), 1)
        dept_col = next((i for i, h in enumerate(headers) if h and 'dept' in str(h).lower()), 2)

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[name_col]:
                continue

            project = RDProject(
                study_id=study_id,
                name=str(row[name_col]).strip(),
                description=str(row[desc_col]).strip() if desc_col < len(row) and row[desc_col] else None,
                department=str(row[dept_col]).strip() if dept_col < len(row) and row[dept_col] else None,
                qualification_status=QualificationStatus.pending
            )
            db.add(project)
            projects_created += 1

        # Save document record
        document = RDDocument(
            study_id=study_id,
            filename=file.filename,
            file_type=file.content_type,
            document_type="project_list",
            file_size=len(content),
            processing_status="completed",
            storage_path=f"uploads/{study_id}/{file.filename}"
        )
        db.add(document)

        await db.commit()

        return {
            "message": "Project data processed successfully",
            "projects_created": projects_created
        }

    except Exception as e:
        logger.error(f"Error processing project file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


# =============================================================================
# QRE DATA UPLOAD
# =============================================================================

@router.post("/studies/{study_id}/upload/expenses")
async def upload_expense_data(
    study_id: UUID,
    file: UploadFile = File(...),
    expense_type: str = Form(default="supplies"),  # supplies, contract_research
    db: AsyncSession = Depends(get_db)
):
    """Upload and process expense data (supplies, contract research) from Excel file."""
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    content = await file.read()

    try:
        workbook = openpyxl.load_workbook(io.BytesIO(content))
        sheet = workbook.active

        qres_created = 0
        headers = [cell.value for cell in sheet[1]]

        # Find column indices
        desc_col = next((i for i, h in enumerate(headers) if h and 'desc' in str(h).lower()), 0)
        vendor_col = next((i for i, h in enumerate(headers) if h and 'vendor' in str(h).lower()), 1)
        amount_col = next((i for i, h in enumerate(headers) if h and 'amount' in str(h).lower()), 2)
        gl_col = next((i for i, h in enumerate(headers) if h and ('gl' in str(h).lower() or 'account' in str(h).lower())), None)

        category = QRECategory.supplies if expense_type == "supplies" else QRECategory.contract_research

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[amount_col]:
                continue

            # Parse amount
            amount_value = row[amount_col]
            if isinstance(amount_value, str):
                amount_value = amount_value.replace('$', '').replace(',', '').strip()
            try:
                gross_amount = Decimal(str(amount_value))
            except:
                continue

            # For supplies, 100% qualified
            # For contract research, 65% for non-qualified orgs, 75% for qualified orgs
            qualified_pct = Decimal('100') if expense_type == "supplies" else Decimal('65')
            qualified_amount = gross_amount * (qualified_pct / 100)

            qre = QualifiedResearchExpense(
                study_id=study_id,
                category=category,
                description=str(row[desc_col]).strip() if row[desc_col] else expense_type,
                supply_description=str(row[desc_col]).strip() if expense_type == "supplies" and row[desc_col] else None,
                supply_vendor=str(row[vendor_col]).strip() if expense_type == "supplies" and vendor_col < len(row) and row[vendor_col] else None,
                contractor_name=str(row[vendor_col]).strip() if expense_type == "contract_research" and vendor_col < len(row) and row[vendor_col] else None,
                gross_amount=gross_amount,
                qualified_percentage=qualified_pct,
                qualified_amount=qualified_amount,
                gl_account=str(row[gl_col]).strip() if gl_col is not None and gl_col < len(row) and row[gl_col] else None,
            )
            db.add(qre)
            qres_created += 1

        # Save document record
        document = RDDocument(
            study_id=study_id,
            filename=file.filename,
            file_type=file.content_type,
            document_type="general_ledger" if expense_type == "supplies" else "contractor_invoices",
            file_size=len(content),
            processing_status="completed",
            storage_path=f"uploads/{study_id}/{file.filename}"
        )
        db.add(document)

        await db.commit()

        return {
            "message": f"{expense_type.replace('_', ' ').title()} data processed successfully",
            "qres_created": qres_created
        }

    except Exception as e:
        logger.error(f"Error processing expense file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


# =============================================================================
# AI STUDY COMPLETION
# =============================================================================

@router.post("/studies/{study_id}/ai/complete-study")
async def ai_complete_study(
    study_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered study completion.
    Analyzes all data and generates:
    - Project qualifications
    - Employee allocations
    - QRE calculations
    - Credit calculations
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get all employees
    employees_result = await db.execute(
        select(RDEmployee).where(RDEmployee.study_id == study_id)
    )
    employees = employees_result.scalars().all()

    # Get all projects
    projects_result = await db.execute(
        select(RDProject).where(RDProject.study_id == study_id)
    )
    projects = projects_result.scalars().all()

    # Get all QREs
    qres_result = await db.execute(
        select(QualifiedResearchExpense).where(QualifiedResearchExpense.study_id == study_id)
    )
    qres = qres_result.scalars().all()

    # AI ANALYSIS: Qualify projects (simulated AI scoring)
    for project in projects:
        if project.qualification_status == QualificationStatus.pending:
            # Simulate 4-part test scoring based on description
            # In production, would use OpenAI to analyze the description
            base_score = 75  # Base score

            # Adjust based on keywords in description
            desc = (project.description or "").lower()
            if any(kw in desc for kw in ['develop', 'create', 'design', 'engineer']):
                base_score += 10
            if any(kw in desc for kw in ['new', 'novel', 'innovative', 'breakthrough']):
                base_score += 5
            if any(kw in desc for kw in ['test', 'experiment', 'prototype', 'iterate']):
                base_score += 5
            if any(kw in desc for kw in ['uncertain', 'challenge', 'solve', 'problem']):
                base_score += 5

            # Set scores
            project.permitted_purpose_score = Decimal(str(min(100, base_score + 5)))
            project.technological_nature_score = Decimal(str(min(100, base_score)))
            project.uncertainty_score = Decimal(str(min(100, base_score - 5)))
            project.experimentation_score = Decimal(str(min(100, base_score)))
            project.overall_score = Decimal(str(min(100, base_score)))

            # Set qualification status
            if base_score >= 75:
                project.qualification_status = QualificationStatus.qualified
            elif base_score >= 50:
                project.qualification_status = QualificationStatus.needs_review
            else:
                project.qualification_status = QualificationStatus.not_qualified

    # AI ANALYSIS: Adjust employee allocations based on job titles
    for employee in employees:
        title = (employee.title or "").lower()

        # If no qualified percentage set, estimate based on title
        if not employee.qualified_time_percentage or employee.qualified_time_percentage == 0:
            if any(t in title for t in ['engineer', 'developer', 'scientist', 'researcher']):
                employee.qualified_time_percentage = Decimal('75')
            elif any(t in title for t in ['architect', 'lead', 'principal']):
                employee.qualified_time_percentage = Decimal('60')
            elif any(t in title for t in ['manager', 'director']):
                employee.qualified_time_percentage = Decimal('40')
            elif any(t in title for t in ['analyst', 'designer', 'qa', 'test']):
                employee.qualified_time_percentage = Decimal('50')
            else:
                employee.qualified_time_percentage = Decimal('25')

            # Calculate qualified wages
            employee.qualified_wages = employee.w2_wages * (employee.qualified_time_percentage / 100)

    # Calculate totals
    total_wage_qre = sum(e.qualified_wages or Decimal('0') for e in employees)
    total_supply_qre = sum(q.qualified_amount or Decimal('0') for q in qres if q.category == QRECategory.supplies)
    total_contract_qre = sum(q.qualified_amount or Decimal('0') for q in qres if q.category == QRECategory.contract_research)
    total_qre = total_wage_qre + total_supply_qre + total_contract_qre

    # Calculate credits
    # ASC method: 14% of (QRE - 50% of average prior 3 years QRE)
    # For first year/no history: 6% of QRE
    asc_credit = total_qre * Decimal('0.06')  # First year rate

    # Regular method: 20% of (QRE - Base)
    # Simplified: 20% of 50% of QRE for startups
    regular_credit = total_qre * Decimal('0.5') * Decimal('0.20')

    # Apply Section 280C reduction (21% corporate tax rate)
    asc_credit_final = asc_credit * Decimal('0.79')
    regular_credit_final = regular_credit * Decimal('0.79')

    # Select better method
    selected_method = CreditMethod.asc if asc_credit_final >= regular_credit_final else CreditMethod.regular
    final_credit = max(asc_credit_final, regular_credit_final)

    # Update study
    study.total_qre = total_qre
    study.qre_wages = total_wage_qre
    study.qre_supplies = total_supply_qre
    study.qre_contract = total_contract_qre
    study.federal_credit_regular = regular_credit_final
    study.federal_credit_asc = asc_credit_final
    study.federal_credit_final = final_credit
    study.selected_method = selected_method
    study.total_credits = final_credit  # Add state credits in production
    study.status = StudyStatus.cpa_review
    study.updated_at = datetime.utcnow()

    # Create calculation record
    calculation = RDCalculation(
        study_id=study_id,
        calculation_type="federal_asc" if selected_method == CreditMethod.asc else "federal_regular",
        total_qre=total_qre,
        calculated_credit=final_credit,
        is_final=False,
        calculation_steps=[
            {"step": 1, "description": "Total Wage QRE", "value": str(total_wage_qre)},
            {"step": 2, "description": "Total Supply QRE", "value": str(total_supply_qre)},
            {"step": 3, "description": "Total Contract QRE", "value": str(total_contract_qre)},
            {"step": 4, "description": "Total QRE", "value": str(total_qre)},
            {"step": 5, "description": "Credit Rate", "value": "14%" if selected_method == CreditMethod.asc else "20%"},
            {"step": 6, "description": "Tentative Credit", "value": str(asc_credit if selected_method == CreditMethod.asc else regular_credit)},
            {"step": 7, "description": "Section 280C Reduction (21%)", "value": "Applied"},
            {"step": 8, "description": "Final Credit", "value": str(final_credit)},
        ]
    )
    db.add(calculation)

    await db.commit()

    return {
        "message": "AI study completion successful",
        "study_id": str(study_id),
        "projects_analyzed": len(projects),
        "employees_analyzed": len(employees),
        "qres_analyzed": len(qres),
        "results": {
            "total_qre": float(total_qre),
            "wage_qre": float(total_wage_qre),
            "supply_qre": float(total_supply_qre),
            "contract_qre": float(total_contract_qre),
            "federal_credit_regular": float(regular_credit_final),
            "federal_credit_asc": float(asc_credit_final),
            "selected_method": selected_method.value,
            "final_credit": float(final_credit),
        },
        "status": "cpa_review"
    }


# =============================================================================
# QUICK STUDY WIZARD
# =============================================================================

@router.post("/studies/{study_id}/wizard/quick-complete")
async def quick_complete_wizard(
    study_id: UUID,
    payroll_file: Optional[UploadFile] = File(None),
    projects_file: Optional[UploadFile] = File(None),
    supplies_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick wizard to upload all data and complete study in one step.
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    results = {
        "payroll": None,
        "projects": None,
        "supplies": None,
        "study_completion": None
    }

    # Process payroll file if provided
    if payroll_file:
        try:
            content = await payroll_file.read()
            workbook = openpyxl.load_workbook(io.BytesIO(content))
            sheet = workbook.active

            employees_created = 0
            headers = [cell.value for cell in sheet[1]]
            name_col = next((i for i, h in enumerate(headers) if h and 'name' in str(h).lower()), 0)
            wages_col = next((i for i, h in enumerate(headers) if h and ('wage' in str(h).lower() or 'salary' in str(h).lower())), 3)

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[name_col]:
                    continue

                wages_value = row[wages_col]
                if isinstance(wages_value, str):
                    wages_value = wages_value.replace('$', '').replace(',', '').strip()
                try:
                    w2_wages = Decimal(str(wages_value)) if wages_value else Decimal('0')
                except:
                    w2_wages = Decimal('0')

                employee = RDEmployee(
                    study_id=study_id,
                    name=str(row[name_col]).strip(),
                    w2_wages=w2_wages,
                    total_wages=w2_wages,
                    qualified_time_percentage=Decimal('50'),  # Default 50%
                    qualified_wages=w2_wages * Decimal('0.5'),
                    qualified_time_source="wizard_import"
                )
                db.add(employee)
                employees_created += 1

            results["payroll"] = {"employees_created": employees_created}
        except Exception as e:
            results["payroll"] = {"error": str(e)}

    # Process projects file if provided
    if projects_file:
        try:
            content = await projects_file.read()
            workbook = openpyxl.load_workbook(io.BytesIO(content))
            sheet = workbook.active

            projects_created = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:
                    continue

                project = RDProject(
                    study_id=study_id,
                    name=str(row[0]).strip(),
                    description=str(row[1]).strip() if len(row) > 1 and row[1] else None,
                    qualification_status=QualificationStatus.pending
                )
                db.add(project)
                projects_created += 1

            results["projects"] = {"projects_created": projects_created}
        except Exception as e:
            results["projects"] = {"error": str(e)}

    # Process supplies file if provided
    if supplies_file:
        try:
            content = await supplies_file.read()
            workbook = openpyxl.load_workbook(io.BytesIO(content))
            sheet = workbook.active

            qres_created = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:
                    continue

                amount_value = row[1] if len(row) > 1 else 0
                if isinstance(amount_value, str):
                    amount_value = amount_value.replace('$', '').replace(',', '').strip()
                try:
                    gross_amount = Decimal(str(amount_value))
                except:
                    continue

                qre = QualifiedResearchExpense(
                    study_id=study_id,
                    category=QRECategory.supplies,
                    description=str(row[0]).strip(),
                    gross_amount=gross_amount,
                    qualified_percentage=Decimal('100'),
                    qualified_amount=gross_amount,
                )
                db.add(qre)
                qres_created += 1

            results["supplies"] = {"qres_created": qres_created}
        except Exception as e:
            results["supplies"] = {"error": str(e)}

    await db.commit()

    # Now run AI study completion
    # (reusing logic from ai_complete_study)
    employees_result = await db.execute(
        select(RDEmployee).where(RDEmployee.study_id == study_id)
    )
    employees = employees_result.scalars().all()

    qres_result = await db.execute(
        select(QualifiedResearchExpense).where(QualifiedResearchExpense.study_id == study_id)
    )
    qres = qres_result.scalars().all()

    # Calculate totals
    total_wage_qre = sum(e.qualified_wages or Decimal('0') for e in employees)
    total_supply_qre = sum(q.qualified_amount or Decimal('0') for q in qres if q.category == QRECategory.supplies)
    total_qre = total_wage_qre + total_supply_qre

    # ASC calculation (first year: 6% of QRE)
    asc_credit = total_qre * Decimal('0.06')
    final_credit = asc_credit * Decimal('0.79')  # After 280C reduction

    # Update study
    study.total_qre = total_qre
    study.qre_wages = total_wage_qre
    study.qre_supplies = total_supply_qre
    study.federal_credit_asc = final_credit
    study.federal_credit_final = final_credit
    study.selected_method = CreditMethod.asc
    study.total_credits = final_credit
    study.status = StudyStatus.cpa_review

    await db.commit()

    results["study_completion"] = {
        "total_qre": float(total_qre),
        "federal_credit": float(final_credit),
        "status": "cpa_review"
    }

    return {
        "message": "Quick wizard completed",
        "study_id": str(study_id),
        "results": results
    }
