from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class Legal_Document_State(TypedDict, total = False):
    document_path : str # Uploaded Document Path
    user_query : str # User's question/instruction
    thread_id : str # Represents the same session thread id
    query_allowed: bool # Is User Query Valid
    query_guardrail_message: str # Message generated for invalid User Message
    raw_text : str # Raw Document Text
    parsing_error : bool # Whether document/image processing failed
    parsing_error_message : str # User-friendly parsing error message
    document_vector_store_path : str # Temporary vector store location for uploaded document
    analysis_run_id: int  # Identifies the current analysis/re-analysis run
    clauses : list # Clauses Identification
    is_sufficient : bool # Whether enough information is available
    missing_information : list # Missing information identified
    reasoning : str # Reason for sufficiency decision
    document_type : str # Document Classification
    retrieved_guidance : list # Retrieval guidance 
    messages : Annotated[list, add_messages] # Messages exchanged between agent and tools
    agent_findings : str # Grounded findings produced by the Legal Review Agent
    risk_flags : list # Risk Flags identified in the document
    human_review_status : str # Status of human review
    final_summary : str # Final legal summary of the uploaded document