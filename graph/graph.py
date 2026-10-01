from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from graph.state import Legal_Document_State
from graph.nodes import (
    parse_document, 
    extract_clauses, 
    check_query_guardrail,
    check_sufficient_information, 
    document_classification, 
    retrieve_legal_guidance, 
    legal_review_agent,
    risk_analysis,
    human_review,
    generate_final_summary
)

from rag.tools import (
    document_evidence_search,
    evidence_verification
)
from rag.document_retriever import create_document_vector_store

# ----------------------------------------------
# Routing after Document Parsing
# ----------------------------------------------

def route_after_parsing(state: Legal_Document_State):

    if state.get("parsing_error", False):
        return "end"

    return "create_document_vector_store"

# ----------------------------------------------
# Routing after Query Guardrail
# ----------------------------------------------

def route_after_query_guardrail(state: Legal_Document_State):

    if state.get("query_allowed", False):
        return "continue"

    return "end"

# ----------------------------------------------
# Routing after Sufficiency Check
# ----------------------------------------------

def route_after_sufficiency(state: Legal_Document_State):
    
    if state["is_sufficient"]:
        return "document_classification"
    else:
        return "end"

# ----------------------------------------------
# Routing after Tool call
# ----------------------------------------------

def route_after_agent(state: Legal_Document_State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return "risk_analysis"

# ----------------------------------------------
# Routing after Human Review
# ----------------------------------------------

def route_after_human(state: Legal_Document_State):

    status = state["human_review_status"]

    if status == "approve":
        return "final_summary"

    elif status == "re-analyze":
        return "retrieve_legal_guidance"

    elif status == "wrong_classification":
        return "document_classification"

    elif status == "escalate":
        return "end"

    return "end"

# ----------------------------------------------
# Building the Graph
# ----------------------------------------------

graph_builder = StateGraph(Legal_Document_State)

# ----------------------------------------------
# Adding tool nodes
# ----------------------------------------------

tool_node = ToolNode([
    document_evidence_search,
    evidence_verification
])

# ----------------------------------------------
# Adding nodes to the Graph
# ----------------------------------------------

graph_builder.add_node("check_query_guardrail", check_query_guardrail)
graph_builder.add_node("parse_document", parse_document)
graph_builder.add_node("create_document_vector_store", create_document_vector_store)
graph_builder.add_node("extract_clauses", extract_clauses)
graph_builder.add_node("check_sufficient_information", check_sufficient_information)
graph_builder.add_node("document_classification", document_classification)
graph_builder.add_node("retrieve_legal_guidance", retrieve_legal_guidance)
graph_builder.add_node("legal_review_agent", legal_review_agent)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("risk_analysis", risk_analysis)
graph_builder.add_node("human_review", human_review)
graph_builder.add_node("final_summary", generate_final_summary)

# ----------------------------------------------
# Adding edges to the Graph
# ----------------------------------------------

graph_builder.add_edge(START, "check_query_guardrail")

graph_builder.add_conditional_edges(
    "check_query_guardrail",
    route_after_query_guardrail,
    {
        "continue": "parse_document",
        "end": END
    }
)

graph_builder.add_conditional_edges(
    "parse_document",
    route_after_parsing,
    {
        "create_document_vector_store": "create_document_vector_store",
        "end": END
    }
)

graph_builder.add_edge("create_document_vector_store", "extract_clauses")
graph_builder.add_edge("extract_clauses", "check_sufficient_information")

graph_builder.add_conditional_edges(
    "check_sufficient_information",
    route_after_sufficiency,
    {
        "document_classification": "document_classification",
        "end": END
    }
)

graph_builder.add_edge("document_classification", "retrieve_legal_guidance")
graph_builder.add_edge("retrieve_legal_guidance", "legal_review_agent")

graph_builder.add_conditional_edges(
    "legal_review_agent",
    route_after_agent,
    {
        "tools": "tools",
        "risk_analysis": "risk_analysis"
    }
)

graph_builder.add_edge("tools", "legal_review_agent")
graph_builder.add_edge("risk_analysis", "human_review")

graph_builder.add_conditional_edges(
    "human_review",
    route_after_human,
    {
        "final_summary" : "final_summary",
        "retrieve_legal_guidance" : "retrieve_legal_guidance",
        "document_classification" : "document_classification",
        "end" : END 
    }
)

graph_builder.add_edge("final_summary", END)

# ----------------------------------------------
# Memory Checkpointer
# ----------------------------------------------

memory = MemorySaver()

# ----------------------------------------------
# Compiling the Graph for complete workflow
# ----------------------------------------------

graph = graph_builder.compile(
    checkpointer= memory
)