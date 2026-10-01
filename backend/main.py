import os

from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from langgraph.types import Command

from backend.database import engine, SessionLocal
from backend.models import (
    Base,
    Clause,
    RiskFlag,
    ReviewDecision
)
from backend.crud import (
    create_document,
    get_documents,
    update_document,
    get_next_analysis_run_id,
    create_clause,
    create_risk_flag,
    create_review_decision
)

from graph.graph import graph
from graph.nodes import analysis_progress, document_qa


app = FastAPI(
    title = "Tata AI Legal Document Intelligence API",
    version = "1.0.0"
)

# ----------------------------------------------
# Request Models
# ----------------------------------------------

class GraphRequest(BaseModel):
    document_id: int
    document_path: str
    user_query: str
    thread_id: str


class ReviewRequest(BaseModel):
    decision: str
    thread_id: str

class DocumentQARequest(BaseModel):
    document_vector_store_path: str
    user_question: str

# ----------------------------------------------
# Create Database Tables
# ----------------------------------------------

Base.metadata.create_all(bind = engine)

# ----------------------------------------------
# Basic API Routing
# ----------------------------------------------

@app.get("/")
def read_root():

    return {
        "message": "Welcome to the Tata AI Legal Document Intelligence API"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }

# ----------------------------------------------
# Document Q&A
# ----------------------------------------------

@app.post("/document-qa")
def ask_document_question(
    request: DocumentQARequest
):

    answer = document_qa(
        request.document_vector_store_path,
        request.user_question
    )

    return {
        "answer": answer
    }

# ----------------------------------------------
# Analysis Progress
# ----------------------------------------------

@app.get("/analysis-progress/{thread_id}")
def get_analysis_progress(thread_id: str):

    return {
        "thread_id": thread_id,
        "stage": analysis_progress.get(
            thread_id,
            "starting"
        )
    }

# ----------------------------------------------
# Database session
# ----------------------------------------------

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# ----------------------------------------------
# Upload Document
# ----------------------------------------------

@app.post("/documents")
def add_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Make sure the uploads folder exists
    os.makedirs("uploads", exist_ok=True)

    # Create the path where the uploaded file will be saved
    file_path = os.path.join(
        "uploads",
        file.filename
    )

    # Save the uploaded file
    with open(file_path, "wb") as output_file:

        output_file.write(
            file.file.read()
        )

    # Create a database record
    document = create_document(
        db,
        file.filename,
        file_path
    )

    return {
        "id": document.id,
        "file_name": document.file_name,
        "status": document.status,
        "file_path": file_path
    }

# ----------------------------------------------
# Get All Documents
# ----------------------------------------------

@app.get("/documents")
def read_documents(
    db: Session = Depends(get_db)
):

    documents = get_documents(db)

    return [
        {
            "id": document.id,
            "file_name": document.file_name,
            "document_type": document.document_type,
            "status": document.status,
            "final_summary": document.final_summary,
            "uploaded_at": document.uploaded_at
        }
        for document in documents
    ]

# ----------------------------------------------
# Get All Clauses
# ----------------------------------------------

@app.get("/clauses")
def read_clauses(
    db: Session = Depends(get_db)
):

    clauses = db.query(Clause).all()

    return [
        {
            "id": clause.id,
            "document_id": clause.document_id,
            "analysis_run_id": clause.analysis_run_id,
            "clause_type": clause.clause_type,
            "clause_text": clause.clause_text
        }
        for clause in clauses
    ]

# ----------------------------------------------
# Get All Risk Flags
# ----------------------------------------------

@app.get("/risk-flags")
def read_risk_flags(
    db: Session = Depends(get_db)
):

    risk_flags = db.query(RiskFlag).all()

    return [
        {
            "id": risk.id,
            "document_id": risk.document_id,
            "analysis_run_id": risk.analysis_run_id,
            "severity": risk.severity,
            "risk_type": risk.risk_type,
            "affected_clause": risk.affected_clause,
            "rationale": risk.rationale,
            "source_location": risk.source_location,
            "recommended_action": risk.recommended_action,
            "confidence": risk.confidence
        }
        for risk in risk_flags
    ]

# ----------------------------------------------
# Get All Review Decisions
# ----------------------------------------------

@app.get("/review-decisions")
def read_review_decisions(
    db: Session = Depends(get_db)
):

    review_decisions = db.query(ReviewDecision).all()

    return [
        {
            "id": review.id,
            "document_id": review.document_id,
            "analysis_run_id": review.analysis_run_id,
            "decision": review.decision,
            "reviewed_at": review.reviewed_at
        }
        for review in review_decisions
    ]

# ----------------------------------------------
# Update Document Status
# ----------------------------------------------

@app.put("/documents/{document_id}/status")
def change_document_status(
    document_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    document = update_document(
        db = db,
        document_id = document_id,
        status = status
    )

    if document is None:

        return {
            "message": "Document not found"
        }

    return {
        "id": document.id,
        "file_name": document.file_name,
        "status": document.status
    }

# ----------------------------------------------
# Helper: Save Clauses
# ----------------------------------------------

def save_clauses(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    clauses: list
):
    """
    Save every extracted clause as a separate database row.
    """

    if not clauses:
        return

    for clause in clauses:

        # Handle dictionary output
        if isinstance(clause, dict):

            clause_name = clause.get("clause_name")
            clause_text = clause.get("clause_text")

        # Handle Pydantic model output
        else:

            clause_name = getattr(
                clause,
                "clause_name",
                None
            )

            clause_text = getattr(
                clause,
                "clause_text",
                None
            )

        clause_type = clause_name

        create_clause(
            db = db,
            document_id = document_id,
            analysis_run_id = analysis_run_id,
            clause_type = clause_type,
            clause_text = clause_text
        )

# ----------------------------------------------
# Helper: Save Risk Flags
# ----------------------------------------------

def save_risk_flags(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    risk_flags: list
):
    """
    Save every risk flag as a separate database row.
    """

    if not risk_flags:
        return

    for risk in risk_flags:

        # Handle dictionary output
        if isinstance(risk, dict):

            severity = risk.get("severity")
            risk_type = risk.get("risk_type")
            affected_clause = risk.get("affected_clause")
            rationale = risk.get("rationale")
            source_location = risk.get("source_location")
            recommended_action = risk.get("recommended_action")
            confidence = risk.get("confidence")

        # Handle Pydantic model output
        else:

            severity = getattr(risk, "severity", None)
            risk_type = getattr(risk, "risk_type", None)
            affected_clause = getattr(risk, "affected_clause", None)
            rationale = getattr(risk, "rationale", None)
            source_location = getattr(risk, "source_location", None)
            recommended_action = getattr(
                risk,
                "recommended_action",
                None
            )
            confidence = getattr(
                risk,
                "confidence",
                None
            )

        create_risk_flag(
            db = db,
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

# ----------------------------------------------
# Run Legal Document Analysis
# ----------------------------------------------

@app.post("/run-analysis")
def run_analysis(
    request: GraphRequest,
    db: Session = Depends(get_db)
):

    # Create a new analysis run for this document
    analysis_run_id = get_next_analysis_run_id(
        db,
        request.document_id
    )

    initial_state = {
        "document_path": request.document_path,
        "user_query": request.user_query,
        "analysis_run_id": analysis_run_id,
        "thread_id": request.thread_id
    }

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    # Update document status
    update_document(
        db = db,
        document_id = request.document_id,
        status = "analyzing"
    )

    result = graph.invoke(
        initial_state,
        config = config
    )

    # --------------------------------------------------
    # Detect LangGraph interrupt
    # --------------------------------------------------

    if "__interrupt__" in result:

        interrupt_payload = result["__interrupt__"][0].value

        # Save extracted clauses for this analysis run
        save_clauses(
            db = db,
            document_id = request.document_id,
            analysis_run_id = analysis_run_id,
            clauses = result.get("clauses", [])
        )

        # Save risk flags for this analysis run
        save_risk_flags(
            db = db,
            document_id = request.document_id,
            analysis_run_id = analysis_run_id,
            risk_flags = result.get("risk_flags", [])
        )

        update_document(
            db = db,
            document_id = request.document_id,
            status = "awaiting_human_review",
            document_type = result.get("document_type")
        )

        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "document_type": result.get("document_type"),
            "document_vector_store_path": result.get("document_vector_store_path"),
            "clauses": result.get("clauses"),
            "risk_flags": result.get("risk_flags"),
            "human_review_status": "pending",
            "human_review_request": interrupt_payload,
            "final_summary": None
        }

    # --------------------------------------------------
    # Handle Early Exit Outcomes
    # --------------------------------------------------

    # ----------------------------------------------
    # Query rejected
    # ----------------------------------------------

    if result.get("query_allowed") is False:

        update_document(
            db = db,
            document_id = request.document_id,
            status = "rejected"
        )

        return {
                "document_id": request.document_id,
                "thread_id": request.thread_id,
                "analysis_run_id": analysis_run_id,
                "status": "rejected",
                "message": result.get(
                    "query_guardrail_message",
                    "The request is outside the supported scope."
                ),
                "document_type": None,
                "clauses": [],
                "risk_flags": [],
                "human_review_status": None,
                "human_review_request": None,
                "final_summary": None
    }

    # ----------------------------------------------
    # Parsing failed
    # ----------------------------------------------

    if result.get("parsing_error") is True:

        update_document(
            db = db,
            document_id = request.document_id,
            status = "failed"
        )

        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "status": "failed",
            "message": result.get(
                "parsing_error_message",
                "The document could not be processed."
            ),
            "document_type": None,
            "clauses": [],
            "risk_flags": [],
            "human_review_status": None,
            "human_review_request": None,
            "final_summary": None
        }

    # ----------------------------------------------
    # Insufficient information
    # ----------------------------------------------

    if result.get("is_sufficient") is False:

        update_document(
            db = db,
            document_id = request.document_id,
            status = "insufficient_information"
        )

        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "status": "insufficient_information",
            "message": "The document does not contain enough information for the requested review.",
            "missing_information": result.get("missing_information", []),
            "reasoning": result.get("reasoning", ""),
            "document_type": None,
            "clauses": result.get("clauses", []),
            "risk_flags": [],
            "human_review_status": None,
            "human_review_request": None,
            "final_summary": None
        }

    # --------------------------------------------------
    # Normal completion
    # --------------------------------------------------

    save_clauses(
        db = db,
        document_id = request.document_id,
        analysis_run_id = analysis_run_id,
        clauses = result.get("clauses", [])
    )

    save_risk_flags(
        db = db,
        document_id = request.document_id,
        analysis_run_id = analysis_run_id,
        risk_flags = result.get("risk_flags", [])
    )

    update_document(
        db = db,
        document_id = request.document_id,
        status = "completed",
        document_type = result.get("document_type"),
        final_summary = result.get("final_summary")
    )

    return {
        "document_id": request.document_id,
        "thread_id": request.thread_id,
        "analysis_run_id": analysis_run_id,
        "status": "completed",
        "document_type": result.get("document_type"),
        "document_vector_store_path": result.get("document_vector_store_path"),
        "clauses": result.get("clauses"),
        "risk_flags": result.get("risk_flags"),
        "human_review_status": result.get("human_review_status"),
        "human_review_request": None,
        "final_summary": result.get("final_summary")
    }

# ----------------------------------------------
# Human Review
# ----------------------------------------------

@app.post("/documents/{document_id}/review")
def submit_review(
    document_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db)
):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    # ----------------------------------------------
    # Get the current graph state
    # ----------------------------------------------

    current_state = graph.get_state(config).values

    current_run_id = current_state.get("analysis_run_id")

    if current_run_id is None:

        current_run_id = get_next_analysis_run_id(
            db,
            document_id
        )

    # ----------------------------------------------
    # Save the current human review decision
    # ----------------------------------------------

    create_review_decision(
        db = db,
        document_id = document_id,
        analysis_run_id = current_run_id,
        decision = request.decision
    )

    # ----------------------------------------------
    # Handle re-analysis decisions
    # ----------------------------------------------

    new_run_id = current_run_id

    if request.decision in [
        "re-analyze",
        "wrong_classification"
    ]:

        # Create a new analysis run
        new_run_id = get_next_analysis_run_id(
            db,
            document_id
        )

        # Update the LangGraph state with the new run ID
        graph.update_state(
            config,
            {
                "analysis_run_id": new_run_id
            }
        )

        # Reset progress for the new analysis run
        analysis_progress[request.thread_id] = "starting"

    # ----------------------------------------------
    # Resume the graph
    # ----------------------------------------------

    result = graph.invoke(
        Command(resume = request.decision),
        config = config
    )

    # ----------------------------------------------
    # If another human review is required
    # ----------------------------------------------

    if "__interrupt__" in result:

        interrupt_payload = result["__interrupt__"][0].value

        # Save clauses generated in the current run
        save_clauses(
            db = db,
            document_id = document_id,
            analysis_run_id = new_run_id,
            clauses = result.get("clauses", [])
        )

        # Save risks generated in the current run
        save_risk_flags(
            db = db,
            document_id = document_id,
            analysis_run_id = new_run_id,
            risk_flags = result.get("risk_flags", [])
        )

        update_document(
            db = db,
            document_id = document_id,
            status = "awaiting_human_review",
            document_type = result.get("document_type")
        )

        return {
            "document_id": document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": new_run_id,
            "decision": request.decision,
            "document_type": result.get("document_type"),
            "document_vector_store_path": result.get("document_vector_store_path"),
            "clauses": result.get("clauses"),
            "risk_flags": result.get("risk_flags"),
            "human_review_status": "pending",
            "human_review_request": interrupt_payload,
            "final_summary": None
        }

    # ----------------------------------------------
    # Handle Escalation
    # ----------------------------------------------

    if request.decision == "escalate":

        update_document(
            db = db,
            document_id = document_id,
            status = "escalated",
            document_type = result.get("document_type")
        )

        return {
            "document_id": document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": current_run_id,
            "decision": request.decision,
            "status": "escalated",
            "document_type": result.get("document_type"),
            "clauses": result.get("clauses"),
            "risk_flags": result.get("risk_flags"),
            "human_review_status": "escalated",
            "final_summary": None
        }

    # ----------------------------------------------
    # Final completion after human review
    # ----------------------------------------------

    if request.decision in [
        "re-analyze",
        "wrong_classification"
    ]:

        save_clauses(
            db = db,
            document_id = document_id,
            analysis_run_id = new_run_id,
            clauses = result.get("clauses", [])
        )

        save_risk_flags(
            db = db,
            document_id = document_id,
            analysis_run_id = new_run_id,
            risk_flags = result.get("risk_flags", [])
        )

    update_document(
        db = db,
        document_id = document_id,
        status = "completed",
        document_type = result.get("document_type"),
        final_summary = result.get("final_summary")
    )

    return {
        "document_id": document_id,
        "thread_id": request.thread_id,
        "analysis_run_id": new_run_id,
        "decision": request.decision,
        "document_type": result.get("document_type"),
        "document_vector_store_path": result.get("document_vector_store_path"),
        "clauses": result.get("clauses"),
        "risk_flags": result.get("risk_flags"),
        "human_review_status": result.get("human_review_status"),
        "final_summary": result.get("final_summary")
    }