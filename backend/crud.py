from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models import Clause, Document, ReviewDecision, RiskFlag

# ----------------------------------------------
# Document CRUD
# ----------------------------------------------

# Create a new document record
def create_document(db: Session, file_name: str, file_path: str = None):
    document = Document(
        file_name = file_name,
        file_path = file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

# Get all uploaded documents
def get_documents(db: Session):
    return db.query(Document).all()

# Update a document's fields.
def update_document(
    db: Session,
    document_id: int,
    status: str = None,
    document_type: str = None,
    final_summary: str = None,
    file_path: str = None
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document:

        if status is not None:
            document.status = status

        if document_type is not None:
            document.document_type = document_type

        if final_summary is not None:
            document.final_summary = final_summary

        if file_path is not None:
            document.file_path = file_path

        db.commit()
        db.refresh(document)

    return document

# ----------------------------------------------
# Analysis Run ID Helper
# ----------------------------------------------

def get_next_analysis_run_id(db: Session, document_id: int) -> int:

    # Find the highest analysis_run_id in each child table for this document
    max_clause = db.query(
        func.max(Clause.analysis_run_id)
    ).filter(Clause.document_id == document_id).scalar()

    max_risk = db.query(
        func.max(RiskFlag.analysis_run_id)
    ).filter(RiskFlag.document_id == document_id).scalar()

    max_review = db.query(
        func.max(ReviewDecision.analysis_run_id)
    ).filter(ReviewDecision.document_id == document_id).scalar()

    # Collect non-None values and find the overall maximum
    existing = [v for v in [max_clause, max_risk, max_review] if v is not None]

    if not existing:
        return 1

    return max(existing) + 1

# ----------------------------------------------
# Clause CRUD
# ----------------------------------------------

# Create a single clause record linked to a document and analysis run
def create_clause(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    clause_type: str,
    clause_text: str
):
    clause = Clause(
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        clause_type = clause_type,
        clause_text = clause_text
    )

    db.add(clause)
    db.commit()
    db.refresh(clause)

    return clause

# ----------------------------------------------
# RiskFlag CRUD
# ----------------------------------------------

# Create a single risk flag record linked to a document and analysis run
def create_risk_flag(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    severity: str,
    risk_type: str,
    affected_clause: str,
    rationale: str,
    source_location: str,
    recommended_action: str,
    confidence: int
):
    risk_flag = RiskFlag(
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        severity = severity,
        risk_type = risk_type,
        affected_clause = affected_clause,
        rationale = rationale,
        source_location = source_location,
        recommended_action = recommended_action,
        confidence = confidence
    )

    db.add(risk_flag)
    db.commit()
    db.refresh(risk_flag)

    return risk_flag

# ----------------------------------------------
# ReviewDecision CRUD
# ----------------------------------------------

# Create a single review decision record linked to a document and analysis run
def create_review_decision(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    decision: str
):
    review_decision = ReviewDecision(
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        decision = decision
    )

    db.add(review_decision)
    db.commit()
    db.refresh(review_decision)

    return review_decision