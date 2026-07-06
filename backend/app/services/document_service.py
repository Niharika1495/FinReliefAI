from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.document import DocumentMetadata
from app.models.user import User
from app.utils.file_handler import save_upload_file
from app.utils.ocr import extract_metadata_from_file
from app.services.audit_service import AuditService

class DocumentService:
    """
    Service layer coordinating document storage, OCR text parsing, 
    and database metadata indexing.
    """

    @staticmethod
    def upload_document(db: Session, user: User, upload_file: UploadFile) -> DocumentMetadata:
        # Save file to disk
        file_path = save_upload_file(upload_file)
        
        # Determine file type
        file_type = "pdf" if upload_file.content_type == "application/pdf" else "image"
        
        # Run OCR extraction
        ocr_details = extract_metadata_from_file(file_path)
        
        # Save metadata to DB
        doc_metadata = DocumentMetadata(
            user_id=user.id,
            filename=upload_file.filename,
            file_path=file_path,
            file_type=file_type,
            extracted_lender=ocr_details.get("extracted_lender"),
            extracted_amount=ocr_details.get("extracted_amount"),
            extracted_emi=ocr_details.get("extracted_emi"),
            extracted_interest_rate=ocr_details.get("extracted_interest_rate"),
            extracted_due_date=ocr_details.get("extracted_due_date"),
            extracted_loan_type=ocr_details.get("extracted_loan_type")
        )
        db.add(doc_metadata)
        db.commit()
        db.refresh(doc_metadata)
        
        # Audit log creation
        AuditService.create_log(
            db=db,
            user_id=user.id,
            action=f"Upload document: {upload_file.filename} (ID: {doc_metadata.id})"
        )
        
        return doc_metadata

    @staticmethod
    def get_documents(db: Session, user: User):
        """
        Retrieves all documents associated with the current user.
        """
        return db.query(DocumentMetadata).filter(DocumentMetadata.user_id == user.id).order_by(DocumentMetadata.created_at.desc()).all()
