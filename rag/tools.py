# ===================================================================================================
# Tools used by the Legal Review Agent to search and verify evidence from the uploaded document.
# ===================================================================================================

from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from graph.state import Legal_Document_State

# --------------------------------------------------
# Load Embedding Model
# --------------------------------------------------

embeddings = None

def get_embeddings():

    global embeddings

    # Load the embedding model only on first use
    if embeddings is None:

        embeddings = HuggingFaceEmbeddings(
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
        )

    return embeddings

def get_document_retriever(state: Legal_Document_State):

    vector_store = Chroma(
        persist_directory = state["document_vector_store_path"],
        embedding_function = get_embeddings()
    )

    return vector_store.as_retriever(
        search_kwargs = {"k": 3}
    )

# --------------------------------------------------
# Document Evidence Search Tool
# --------------------------------------------------

@tool
def document_evidence_search(
    query: str,
    state: Annotated[Legal_Document_State, InjectedState]) -> str:
    
    """
    Search the uploaded document for relevant evidence using semantic search.
    The agent should use this tool when additional document evidence is required.
    """

    # Create a semantic retriever for the current uploaded document
    retriever = get_document_retriever(state)

    # Search the document using the agent's query
    results = retriever.invoke(query)

    # If no relevant evidence is found
    if not results:
        return "No relevant evidence was found in the document."

    # Format the retrieved evidence
    evidence = []

    for result in results:
        evidence.append(
            f"""
Evidence:
{result.page_content}
"""
        )

    return "\n".join(evidence)

# --------------------------------------------------
# Evidence Verification Tool
# --------------------------------------------------

@tool
def evidence_verification(
    query: str,
    state: Annotated[Legal_Document_State, InjectedState]) -> str:

    """
    Verify evidence from the uploaded document and check for
    supporting or conflicting information.
    """

    retriever = get_document_retriever(state)

    results = retriever.invoke(query)

    if not results:
        return "No relevant evidence was found for verification."

    evidence = []

    for result in results:
        evidence.append(
            f"""
Evidence:
{result.page_content}
"""
        )

    return "\n".join(evidence)