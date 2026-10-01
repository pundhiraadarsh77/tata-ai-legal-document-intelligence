from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --------------------------------------------------
# Cached Embedding Model
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
# Create Knowledge Base Retriever
# --------------------------------------------------

def get_kb_retriever():

    # Reuse the already loaded embedding model
    embedding_model = get_embeddings()

    # Load the existing ChromaDB
    vector_store = Chroma(
        persist_directory = "vector_store/chroma_db",
        embedding_function = embedding_model
    )

    # Create a retriever for semantic search
    retriever = vector_store.as_retriever(
        search_kwargs = {"k": 3}
    )

    return retriever