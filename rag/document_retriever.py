# ==========================================================================================
# Creates a semantic retriever for the uploaded document.
# The parsed document text is chunked, embedded, and stored in a temporary vector store.
# This retriever will later be used by the Evidence Search and Verification tools.
# ==========================================================================================
import tempfile

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from graph.state import Legal_Document_State
from utils.chunking import create_chunks

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

# --------------------------------------------------
# Create Document Retriever
# --------------------------------------------------

def create_document_vector_store(state: Legal_Document_State):
    raw_text = state["raw_text"]

    # Split the already-parsed document text into smaller chunks
    chunks = create_chunks(raw_text)

    # Convert each chunk into a LangChain Document
    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content = chunk
            )
        )

    # Create a temporary directory for this uploaded document
    temp_directory = tempfile.mkdtemp()

    # Create Chroma vector store inside the temporary directory
    Chroma.from_documents(
        documents = documents,
        embedding = get_embeddings(),
        persist_directory = temp_directory
    )

    return {
        "document_vector_store_path": temp_directory
    }