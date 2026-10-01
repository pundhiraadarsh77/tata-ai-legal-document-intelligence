# ========================================================================================================
# File to create chunks - Small parts of the whole document for better retrieval and summary generation.
# ========================================================================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_chunks(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 700,
        chunk_overlap = 150
    )

    chunks = splitter.split_text(text)

    return chunks