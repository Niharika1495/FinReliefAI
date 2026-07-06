from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.report_service import ReportService
from app.utils.exceptions import FinReliefException
from app.services.audit_service import AuditService

reports_router = APIRouter()

@reports_router.get(
    "/{report_type}/pdf",
    summary="Download PDF Report",
    response_class=FileResponse
)
def get_pdf_report(
    report_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compiles report data and downloads a beautifully styled PDF document.
    """
    file_path = ReportService.generate_report_file(
        db=db,
        user=current_user,
        report_type=report_type.lower(),
        file_format="pdf"
    )
    
    # Audit log
    AuditService.create_log(
        db=db,
        user_id=current_user.id,
        action=f"Generate PDF report: {report_type}"
    )

    if not os.path.exists(file_path):
        raise FinReliefException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PDF_GENERATION_FAILED",
            message="The requested PDF report could not be created."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=os.path.basename(file_path)
    )

@reports_router.get(
    "/{report_type}/csv",
    summary="Download CSV Report",
    response_class=FileResponse
)
def get_csv_report(
    report_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compiles report data and downloads tabular data in CSV format.
    """
    file_path = ReportService.generate_report_file(
        db=db,
        user=current_user,
        report_type=report_type.lower(),
        file_format="csv"
    )
    
    # Audit log
    AuditService.create_log(
        db=db,
        user_id=current_user.id,
        action=f"Generate CSV report: {report_type}"
    )

    if not os.path.exists(file_path):
        raise FinReliefException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CSV_GENERATION_FAILED",
            message="The requested CSV report could not be created."
        )

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=os.path.basename(file_path)
    )
