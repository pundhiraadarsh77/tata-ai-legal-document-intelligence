# --------------------------------------------------
# Functional Workflow Tests
# --------------------------------------------------

def test_project_modules_import():

    from graph.graph import graph
    from graph.nodes import parse_document
    from rag.document_retriever import create_document_vector_store
    from rag.kb_retriever import get_kb_retriever

    assert graph is not None
    assert parse_document is not None
    assert create_document_vector_store is not None
    assert get_kb_retriever is not None