from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load the same embedding model used to create the vector store
embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

# Load the existing ChromaDB
vector_store = Chroma(
    persist_directory = "vector_store/chroma_db",
    embedding_function= embeddings
)

# Create a retriever for semantic search
retriever = vector_store.as_retriever(
    search_kwargs = {"k":3} # Gives top 3 similar results with the query
)