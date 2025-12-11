"""
Document Processing Routes

API endpoints for AI-powered document processing including:
- Invoice OCR and expense recognition
- W-2 processing for wage documentation
- 1099 processing for contractor documentation
- PA R&D document package creation
"""

import logging
import io
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import RDStudy, RDDocument, QualifiedResearchExpense, QRECategory
from ..ai.invoice_ocr_service import InvoiceOCRService, PADocumentPackageService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_invoice_service(request: Request) -> InvoiceOCRService:
    """Get or create invoice OCR service."""
    if not hasattr(request.app.state, 'invoice_service'):
        openai_client = getattr(request.app.state, 'openai_client', None)
        request.app.state.invoice_service = InvoiceOCRService(openai_client=openai_client)
    return request.app.state.invoice_service


# =============================================================================
# INVOICE PROCESSING
# =============================================================================

@router.post("/studies/{study_id}/documents/invoice/upload")
async def upload_and_process_invoice(
    study_id: UUID,
    file: UploadFile = File(...),
    auto_create_expense: bool = Form(default=True),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process an invoice using AI-powered OCR.

    Returns extracted invoice data with R&D qualification analysis.
    Optionally creates a QRE expense record automatically.
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Read file content
    content = await file.read()

    # Get invoice service
    invoice_service = get_invoice_service(request)

    try:
        # Process invoice with AI
        extracted = await invoice_service.process_invoice(
            file_content=content,
            filename=file.filename or "invoice.pdf",
            study_id=study_id
        )

        # Save document record
        document = RDDocument(
            study_id=study_id,
            filename=file.filename,
            file_type=file.content_type,
            document_type="invoice",
            file_size=len(content),
            processing_status="completed",
            storage_path=f"uploads/{study_id}/{file.filename}",
            extracted_data={
                "vendor_name": extracted.vendor_name,
                "invoice_number": extracted.invoice_number,
                "invoice_date": str(extracted.invoice_date) if extracted.invoice_date else None,
                "total_amount": float(extracted.total_amount),
                "qualified_amount": float(extracted.qualified_amount),
                "category": extracted.primary_category.value,
                "ocr_confidence": extracted.ocr_confidence,
                "ai_confidence": extracted.ai_analysis_confidence,
                "line_items": [
                    {
                        "description": item.description,
                        "amount": float(item.amount),
                        "category": item.category.value,
                        "rd_qualified": item.rd_qualified
                    }
                    for item in extracted.line_items
                ]
            }
        )
        db.add(document)

        # Create QRE expense if requested and invoice qualifies
        expense_created = None
        if auto_create_expense and extracted.qualified_amount > 0:
            # Map category
            category_mapping = {
                "supplies": QRECategory.SUPPLIES,
                "contract_research": QRECategory.CONTRACT_RESEARCH,
                "computer_rental": QRECategory.COMPUTER_RENTAL,
            }
            qre_category = category_mapping.get(
                extracted.primary_category.value,
                QRECategory.SUPPLIES
            )

            qre = QualifiedResearchExpense(
                study_id=study_id,
                category=qre_category,
                description=f"Invoice {extracted.invoice_number or 'N/A'} - {extracted.vendor_name or 'Unknown Vendor'}",
                supply_vendor=extracted.vendor_name if qre_category == QRECategory.SUPPLIES else None,
                contractor_name=extracted.vendor_name if qre_category == QRECategory.CONTRACT_RESEARCH else None,
                gross_amount=extracted.total_amount,
                qualified_percentage=extracted.qualification_percentage,
                qualified_amount=extracted.qualified_amount,
                invoice_number=extracted.invoice_number,
                invoice_date=extracted.invoice_date,
                source_document_id=document.id
            )
            db.add(qre)
            expense_created = {
                "category": qre_category.value,
                "gross_amount": float(extracted.total_amount),
                "qualified_amount": float(extracted.qualified_amount)
            }

        await db.commit()
        await db.refresh(document)

        return {
            "success": True,
            "document_id": str(document.id),
            "invoice": {
                "vendor_name": extracted.vendor_name,
                "vendor_state": extracted.vendor_state,
                "invoice_number": extracted.invoice_number,
                "invoice_date": str(extracted.invoice_date) if extracted.invoice_date else None,
                "subtotal": float(extracted.subtotal),
                "tax_amount": float(extracted.tax_amount),
                "total_amount": float(extracted.total_amount),
                "line_items": [
                    {
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price) if item.unit_price else None,
                        "amount": float(item.amount),
                        "category": item.category.value,
                        "rd_qualified": item.rd_qualified,
                        "qualification_reason": item.qualification_reason
                    }
                    for item in extracted.line_items
                ]
            },
            "rd_qualification": {
                "primary_category": extracted.primary_category.value,
                "qualified_percentage": float(extracted.qualification_percentage),
                "qualified_amount": float(extracted.qualified_amount),
                "pa_qualified": extracted.pa_qualified
            },
            "confidence": {
                "ocr": extracted.ocr_confidence,
                "ai_analysis": extracted.ai_analysis_confidence
            },
            "expense_created": expense_created,
            "processing_notes": extracted.processing_notes
        }

    except Exception as e:
        logger.error(f"Invoice processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process invoice: {str(e)}")


@router.post("/studies/{study_id}/documents/invoices/batch")
async def batch_process_invoices(
    study_id: UUID,
    files: List[UploadFile] = File(...),
    auto_create_expenses: bool = Form(default=True),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch process multiple invoices with AI-powered OCR.

    Returns summary of all processed invoices.
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    invoice_service = get_invoice_service(request)

    results = []
    total_qualified = Decimal("0")
    total_amount = Decimal("0")
    errors = []

    for file in files:
        try:
            content = await file.read()

            extracted = await invoice_service.process_invoice(
                file_content=content,
                filename=file.filename or "invoice.pdf",
                study_id=study_id
            )

            # Save document
            document = RDDocument(
                study_id=study_id,
                filename=file.filename,
                file_type=file.content_type,
                document_type="invoice",
                file_size=len(content),
                processing_status="completed",
                storage_path=f"uploads/{study_id}/{file.filename}",
            )
            db.add(document)

            # Create expense if qualified
            if auto_create_expenses and extracted.qualified_amount > 0:
                qre = QualifiedResearchExpense(
                    study_id=study_id,
                    category=QRECategory.SUPPLIES,
                    description=f"Invoice {extracted.invoice_number or 'N/A'} - {extracted.vendor_name}",
                    supply_vendor=extracted.vendor_name,
                    gross_amount=extracted.total_amount,
                    qualified_percentage=extracted.qualification_percentage,
                    qualified_amount=extracted.qualified_amount,
                )
                db.add(qre)

            results.append({
                "filename": file.filename,
                "vendor": extracted.vendor_name,
                "total": float(extracted.total_amount),
                "qualified": float(extracted.qualified_amount),
                "category": extracted.primary_category.value,
                "confidence": extracted.ai_analysis_confidence
            })

            total_amount += extracted.total_amount
            total_qualified += extracted.qualified_amount

        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })

    await db.commit()

    return {
        "success": True,
        "processed_count": len(results),
        "error_count": len(errors),
        "total_amount": float(total_amount),
        "total_qualified": float(total_qualified),
        "results": results,
        "errors": errors
    }


# =============================================================================
# W-2 PROCESSING
# =============================================================================

@router.post("/studies/{study_id}/documents/w2/upload")
async def upload_and_process_w2(
    study_id: UUID,
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process a W-2 document using AI-powered OCR.

    Extracts employee wage information for R&D credit documentation.
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    content = await file.read()
    invoice_service = get_invoice_service(request)

    try:
        extracted = await invoice_service.process_w2(content, file.filename or "w2.pdf")

        # Save document record
        document = RDDocument(
            study_id=study_id,
            filename=file.filename,
            file_type=file.content_type,
            document_type="w2",
            file_size=len(content),
            processing_status="completed",
            storage_path=f"uploads/{study_id}/{file.filename}",
            extracted_data={
                "employee_name": extracted.employee_name,
                "employer_name": extracted.employer_name,
                "employer_state": extracted.employer_state,
                "wages_box1": float(extracted.wages_box1),
                "state_wages": {k: float(v) for k, v in extracted.state_wages.items()},
                "ocr_confidence": extracted.ocr_confidence
            }
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        return {
            "success": True,
            "document_id": str(document.id),
            "w2_data": {
                "employee_name": extracted.employee_name,
                "ssn_last4": extracted.ssn_last4,
                "employer_name": extracted.employer_name,
                "employer_ein": extracted.employer_ein,
                "employer_state": extracted.employer_state,
                "employer_address": extracted.employer_address,
                "wages_box1": float(extracted.wages_box1),
                "federal_tax_withheld": float(extracted.federal_tax_withheld),
                "social_security_wages": float(extracted.social_security_wages),
                "medicare_wages": float(extracted.medicare_wages),
                "state_wages": {k: float(v) for k, v in extracted.state_wages.items()},
                "state_tax_withheld": {k: float(v) for k, v in extracted.state_tax_withheld.items()},
                "tax_year": extracted.tax_year
            },
            "confidence": extracted.ocr_confidence
        }

    except Exception as e:
        logger.error(f"W-2 processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process W-2: {str(e)}")


# =============================================================================
# 1099 PROCESSING
# =============================================================================

@router.post("/studies/{study_id}/documents/1099/upload")
async def upload_and_process_1099(
    study_id: UUID,
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process a 1099 document using AI-powered OCR.

    Extracts contractor payment information for R&D credit documentation.
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    content = await file.read()
    invoice_service = get_invoice_service(request)

    try:
        extracted = await invoice_service.process_1099(content, file.filename or "1099.pdf")

        # Save document record
        document = RDDocument(
            study_id=study_id,
            filename=file.filename,
            file_type=file.content_type,
            document_type="1099",
            file_size=len(content),
            processing_status="completed",
            storage_path=f"uploads/{study_id}/{file.filename}",
            extracted_data={
                "form_type": extracted.form_type,
                "recipient_name": extracted.recipient_name,
                "payer_name": extracted.payer_name,
                "payer_state": extracted.payer_state,
                "compensation": float(extracted.nonemployee_compensation),
                "ocr_confidence": extracted.ocr_confidence
            }
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        return {
            "success": True,
            "document_id": str(document.id),
            "form_1099_data": {
                "form_type": extracted.form_type,
                "recipient_name": extracted.recipient_name,
                "recipient_tin_last4": extracted.recipient_tin_last4,
                "payer_name": extracted.payer_name,
                "payer_tin": extracted.payer_tin,
                "payer_state": extracted.payer_state,
                "nonemployee_compensation": float(extracted.nonemployee_compensation),
                "other_income": float(extracted.other_income),
                "state_income": {k: float(v) for k, v in extracted.state_income.items()},
                "tax_year": extracted.tax_year
            },
            "confidence": extracted.ocr_confidence
        }

    except Exception as e:
        logger.error(f"1099 processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process 1099: {str(e)}")


# =============================================================================
# PA DOCUMENT PACKAGE
# =============================================================================

@router.post("/studies/{study_id}/documents/pa-package")
async def create_pa_document_package(
    study_id: UUID,
    w2_files: List[UploadFile] = File(default=[]),
    form_1099_files: List[UploadFile] = File(default=[]),
    invoice_files: List[UploadFile] = File(default=[]),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Pennsylvania R&D tax credit documentation package.

    Processes all uploaded W-2s, 1099s, and invoices, then creates
    a reconciliation report comparing documented amounts to the
    R&D credit calculation.

    PA requires:
    - PA W-2s for employee wages allocated to PA
    - PA 1099s for contractor payments
    - Invoices for supplies and other R&D expenses
    - Reconciliation to the R&D credit calculation
    """
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    invoice_service = get_invoice_service(request)
    pa_service = PADocumentPackageService(invoice_service)

    # Read all file contents
    w2_contents = [await f.read() for f in w2_files]
    form_1099_contents = [await f.read() for f in form_1099_files]
    invoice_contents = [await f.read() for f in invoice_files]

    # Get calculation summary from study
    # This should be calculated from the actual study data
    employees_result = await db.execute(
        select(QualifiedResearchExpense).where(
            QualifiedResearchExpense.study_id == study_id
        )
    )
    qres = employees_result.scalars().all()

    # Calculate PA-specific amounts (simplified - would need actual PA allocation logic)
    calculation_summary = {
        "pa_qre_wages": float(study.qre_wages or 0) * 0.1,  # Assume 10% PA allocation
        "pa_qre_contractor": sum(
            float(q.qualified_amount or 0)
            for q in qres
            if q.category == QRECategory.CONTRACT_RESEARCH
        ) * 0.1,
        "pa_qre_supplies": sum(
            float(q.qualified_amount or 0)
            for q in qres
            if q.category == QRECategory.SUPPLIES
        ) * 0.1,
    }

    try:
        package = await pa_service.create_pa_package(
            study_id=study_id,
            w2s=w2_contents,
            form_1099s=form_1099_contents,
            invoices=invoice_contents,
            calculation_summary=calculation_summary
        )

        # Store package in study
        if not study.ai_suggested_areas:
            study.ai_suggested_areas = {}
        study.ai_suggested_areas["pa_document_package"] = package

        await db.commit()

        return {
            "success": True,
            "package": package
        }

    except Exception as e:
        logger.error(f"PA package creation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create PA package: {str(e)}")


@router.get("/studies/{study_id}/documents/pa-package")
async def get_pa_document_package(
    study_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the PA document package for a study if it exists."""
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    package = None
    if study.ai_suggested_areas:
        package = study.ai_suggested_areas.get("pa_document_package")

    if not package:
        raise HTTPException(status_code=404, detail="PA package not found. Upload documents first.")

    return {
        "success": True,
        "package": package
    }


# =============================================================================
# DOCUMENT ANALYSIS SUMMARY
# =============================================================================

@router.get("/studies/{study_id}/documents/summary")
async def get_document_processing_summary(
    study_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get summary of all processed documents for a study."""
    study = await db.get(RDStudy, study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get all documents
    docs_result = await db.execute(
        select(RDDocument).where(RDDocument.study_id == study_id)
    )
    documents = docs_result.scalars().all()

    # Categorize documents
    summary = {
        "total_documents": len(documents),
        "by_type": {},
        "total_extracted_amount": 0.0,
        "total_qualified_amount": 0.0,
        "processing_status": {
            "completed": 0,
            "pending": 0,
            "failed": 0
        }
    }

    for doc in documents:
        doc_type = doc.document_type or "other"
        if doc_type not in summary["by_type"]:
            summary["by_type"][doc_type] = {
                "count": 0,
                "total_amount": 0.0,
                "qualified_amount": 0.0
            }

        summary["by_type"][doc_type]["count"] += 1

        if doc.extracted_data:
            amount = doc.extracted_data.get("total_amount", 0)
            qualified = doc.extracted_data.get("qualified_amount", 0)
            summary["by_type"][doc_type]["total_amount"] += amount
            summary["by_type"][doc_type]["qualified_amount"] += qualified
            summary["total_extracted_amount"] += amount
            summary["total_qualified_amount"] += qualified

        status = doc.processing_status or "pending"
        if status in summary["processing_status"]:
            summary["processing_status"][status] += 1

    return {
        "success": True,
        "study_id": str(study_id),
        "summary": summary
    }
