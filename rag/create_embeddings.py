from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from kb_loader import load_knowledge_base

documents = load_knowledge_base()

# Convert legal documents into numerical vectors
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Store documents, embeddings and metadata in ChromaDB
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="vector_store/chroma_db"
)