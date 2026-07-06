from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.utils.response_utils import success_response

documents_router = APIRouter()

@documents_router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF or Image Document for OCR Parsing"
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads a financial statement, checks format and size, runs OCR parsing,
    stores metadata, and generates an audit log entry.
    """
    doc = DocumentService.upload_document(db=db, user=current_user, upload_file=file)
    return success_response(
        data=DocumentResponse.model_validate(doc),
        message="Document uploaded and processed successfully",
        status_code=status.HTTP_201_CREATED
    )

@documents_router.get(
    "",
    summary="List Uploaded Documents for User"
)
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all uploaded document metadata entries associated with the user.
    """
    docs = DocumentService.get_documents(db=db, user=current_user)
    return success_response(
        data=[DocumentResponse.model_validate(d) for d in docs],
        message="Documents retrieved successfully"
    )
