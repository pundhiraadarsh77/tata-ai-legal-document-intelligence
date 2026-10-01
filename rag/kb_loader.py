# ========================================================================================
# Chunk loader for TATA AI Legal Assistant
# ========================================================================================

# Reads all Markdown knowledge base files
# Converts each Legal guidance entry into a LangChain document
# Adds metadata for traceability during retrieval.

from pathlib import Path
from langchain_core.documents import Document

def load_knowledge_base(knowledge_base_path = "knowledge_base"):
    documents = []

    # Loop through every .md file
    for file_path in Path(knowledge_base_path).glob("*.md"):

        with open(file_path, "r", encoding= "utf-8") as file:
            content = file.read()

        # Split markdown enteries using separator
        entries = content.split("---")

        for entry in entries:

            if entry.strip() == "":
                continue

            metadata = {}
            guidance_text = ""

            # Read line by line
            for line in entry.split("\n"):

                if line.startswith("TITLE:"):
                    metadata["title"] =  line.replace("TITLE:", "").strip()

                elif line.startswith("CATEGORY:"):
                    metadata["category"] = line.replace("CATEGORY:", "").strip()

                elif line.startswith("REFERENCE_ID:"):
                    metadata["reference_id"] = line.replace("REFERENCE_ID:", "").strip()

                elif line.startswith("JURISDICTION:"):
                    metadata["jurisdiction"] = line.replace("JURISDICTION:", "").strip()

                elif line.startswith("GUIDANCE:"):
                    guidance_text = line.replace("GUIDANCE:", "").strip()

                else:
                    guidance_text += "\n" + line.strip()

            # Store file_name as metadata
            metadata["source_file"] = file_path.name

            # Create LangChain Document
            document = Document(
                page_content= guidance_text,
                metadata= metadata
            )

            documents.append(document)

    return documents