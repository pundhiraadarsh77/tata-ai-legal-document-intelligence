import os
import io
import zipfile
import numpy as np

from pypdf import PdfReader # For reading Pdf files
from docx import Document as DocxDocument
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from odf import text
from odf.opendocument import load
from odf.teletype import extractText

from dotenv import load_dotenv # For accessing API Keys
from pydantic import BaseModel, Field # For structured LLM output
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.types import interrupt

from graph.state import Legal_Document_State
from rag.kb_retriever import get_kb_retriever
from rag.tools import document_evidence_search, evidence_verification

load_dotenv()

# ----------------------------------------------
# Analysis Progress Tracking
# ----------------------------------------------

analysis_progress = {}

def update_progress(thread_id, stage):

    if thread_id:
        analysis_progress[thread_id] = stage

# ----------------------------------------------
# LLM Configuration
# ----------------------------------------------

GROQ_MODEL = "openai/gpt-oss-120b"

GEMINI_MODEL = "gemini-3.8-flash"

groq_llm = ChatGroq(
    model = GROQ_MODEL,
    api_key = os.getenv("GROQ_API_KEY")
)

gemini_llm = ChatGoogleGenerativeAI(
    model = GEMINI_MODEL,
    google_api_key = os.getenv("GEMINI_API_KEY")
)

# ----------------------------------------------
# LLM Invoke with structured output support
# ----------------------------------------------

def invoke_structured_with_fallback(schema, prompt):

    # ----------------------------------------------
    # Try Groq first
    # ----------------------------------------------

    try:

        structured_llm = groq_llm.with_structured_output(
            schema
        )

        result = structured_llm.invoke(prompt)

        return result

    except Exception:

        pass

    # ----------------------------------------------
    # Try Gemini if Groq fails
    # ----------------------------------------------

    try:

        structured_llm = gemini_llm.with_structured_output(
            schema
        )

        result = structured_llm.invoke(prompt)

        return result

    except Exception as gemini_error:

        raise RuntimeError(
            "LLM service unavailable"
        ) from gemini_error

# ----------------------------------------------
# LLM Invoke without structured output support
# ----------------------------------------------

def invoke_with_fallback(prompt):

    # -----------------------------------------
    # Try Groq first
    # -----------------------------------------

    try:

        return groq_llm.invoke(prompt)

    except Exception:

        pass

    # -----------------------------------------
    # Try Gemini if Groq fails
    # -----------------------------------------

    try:

        return gemini_llm.invoke(prompt)

    except Exception as gemini_error:
        
        raise RuntimeError(
            "LLM service unavailable"
        ) from gemini_error

# ----------------------------------------------
# LLM Invoke with tools support
# ----------------------------------------------

def invoke_with_tools_fallback(tools, messages):

    # ----------------------------------------------
    # Try Groq first
    # ----------------------------------------------

    try:
        llm_with_tools = groq_llm.bind_tools(tools)

        return llm_with_tools.invoke(messages)

    except Exception:

        pass

    # ----------------------------------------------
    # Try Gemini
    # ----------------------------------------------

    try:
        llm_with_tools = gemini_llm.bind_tools(tools)

        return llm_with_tools.invoke(messages)

    except Exception as gemini_error:

        raise RuntimeError(
            "LLM service unavailable"
        ) from gemini_error

# ----------------------------------------------
# Query Guardrail
# ----------------------------------------------

def check_query_guardrail(state: Legal_Document_State):

    user_query = state.get("user_query", "").strip()

    if not user_query:

        user_query = "Perform a comprehensive legal review of this document."

    prompt = f"""
You are a safety and scope checker for a legal document review system.

Determine whether the user's request is appropriate for an AI-assisted
legal document review.

ALLOW requests such as:
- reviewing legal or compliance risks
- identifying important clauses
- identifying ambiguous language
- reviewing contractual obligations
- finding missing information
- summarizing or explaining document provisions

DO NOT ALLOW requests that ask the system to:
- fabricate or falsify information
- hide or conceal legal or compliance violations
- evade laws or regulatory requirements
- manipulate evidence or findings
- intentionally produce a misleading legal review

USER REQUEST:
{user_query}

Return ONLY valid JSON in exactly this format:

{{
    "query_allowed": true,
    "message": "short explanation for the user"
}}

Rules:
- query_allowed must be either true or false.
- message must be a short explanation.
- Do not include markdown.
- Do not include any text outside the JSON object.
"""

    response = invoke_with_fallback(prompt)

    result = response.content

    if isinstance(result, list):
        result = result[0]["text"]

    result = result.strip()

    import json

    data = json.loads(result)

    return {
        "query_allowed": data["query_allowed"],
        "query_guardrail_message": data["message"]
    }

# ----------------------------------------------
# Load OCR Engine
# ----------------------------------------------

ocr_engine = None

def get_ocr_engine():

    global ocr_engine

    # Load OCR engine only when it is actually needed
    if ocr_engine is None:

        ocr_engine = RapidOCR()

    return ocr_engine

# ----------------------------------------------
# OCR Helper
# ----------------------------------------------

def extract_text_from_image(image):

    # Convert PIL image into NumPy array
    image_array = np.array(image)

    result, _ = get_ocr_engine()(image_array)

    raw_text = ""

    if result:

        for line in result:

            raw_text += line[1] + "\n"

    return raw_text

# ----------------------------------------------
# PDF Parsing
# ----------------------------------------------

def parse_pdf(document_path):

    reader = PdfReader(document_path) # Open the file
    
    raw_text = ""
    
    for page in reader.pages: 
        text = page.extract_text() # Extracts the text from each page
    
        if text:
            raw_text += text + "\n"

        # Extract embedded images from the PDF
        try:

            for image in page.images:

                image_bytes = image.data

                # Convert image bytes into a PIL image
                image_object = Image.open(
                    io.BytesIO(image_bytes)
                )

                # OCR the embedded image
                image_text = extract_text_from_image(
                    image_object
                )

                if image_text.strip():

                    raw_text += "\n[OCR IMAGE TEXT]\n"
                    raw_text += image_text

        except Exception as e:

            raise ValueError(
                "Image processing failed. "
                "Please update and upload the document again."
            ) from e

    return raw_text    

# ----------------------------------------------
# DOCX Parsing
# ----------------------------------------------

def parse_docx(document_path):

    document = DocxDocument(document_path)

    raw_text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            raw_text += paragraph.text + "\n"

     # Extract embedded images from DOCX
    try:

        with zipfile.ZipFile(document_path, "r") as docx_zip:

            for file_name in docx_zip.namelist():

                if file_name.startswith("word/media/"):

                    image_bytes = docx_zip.read(file_name)

                    image_object = Image.open(
                        io.BytesIO(image_bytes)
                    )

                    # OCR the embedded image
                    image_text = extract_text_from_image(
                        image_object
                    )

                    if image_text.strip():

                        raw_text += "\n[OCR IMAGE TEXT]\n"
                        raw_text += image_text

    except Exception as e:

            raise ValueError(
                "Image processing failed. "
                "Please update and upload the document again."
            ) from e

    return raw_text

# ----------------------------------------------
# Image OCR Parsing
# ----------------------------------------------

def parse_image(document_path):

    image = Image.open(document_path)

    # Run OCR directly on the image
    raw_text = extract_text_from_image(image)

    if not raw_text.strip():

        raise ValueError(
            "Image text could not be extracted. "
            "The image may be unclear or unreadable."
        )

    return raw_text

# ----------------------------------------------
# ODT Parsing
# ----------------------------------------------

def parse_odt(document_path):

    document = load(document_path)

    raw_text = ""

    paragraphs = document.getElementsByType(text.P)

    for paragraph in paragraphs:

        extracted = extractText(paragraph)

        if extracted.strip():

            raw_text += extracted + "\n"

    # Extract text from headings as well
    headings = document.getElementsByType(text.H)

    for heading in headings:

        extracted = extractText(heading)

        if extracted.strip():

            raw_text += extracted + "\n"

    # Extract embedded images from ODT
    try:

        with zipfile.ZipFile(document_path, "r") as odt_zip:

            for file_name in odt_zip.namelist():

                if file_name.startswith("media/"):

                    image_bytes = odt_zip.read(file_name)

                    image_object = Image.open(
                        io.BytesIO(image_bytes)
                    )

                    # OCR the embedded image
                    image_text = extract_text_from_image(
                        image_object
                    )

                    if image_text.strip():

                        raw_text += "\n[OCR IMAGE TEXT]\n"
                        raw_text += image_text

    except Exception as e:

            raise ValueError(
                "Image processing failed. "
                "Please update and upload the document again."
            ) from e

    return raw_text

# ----------------------------------------------
# Multi-Format Document Parsing
# ----------------------------------------------

def parse_document(state: Legal_Document_State):

    document_path = state["document_path"]

    extension = os.path.splitext(
        document_path
    )[1].lower()

    try:

        if extension == ".pdf":

            raw_text = parse_pdf(document_path)

        elif extension == ".docx":

            raw_text = parse_docx(document_path)

        elif extension in [".png", ".jpg", ".jpeg"]:

            raw_text = parse_image(document_path)

        elif extension == ".odt":

            raw_text = parse_odt(document_path)

        else:

            raise ValueError(
                f"Unsupported document format: {extension}"
            )

         # Mark document parsing as completed
        update_progress(
            state.get("thread_id"),
            "document_parsing"
        )

        return {
            "raw_text": raw_text,
            "parsing_error": False,
            "parsing_error_message": ""
        }

    except ValueError as e:

        return {
            "parsing_error": True,
            "parsing_error_message": str(e)
        }

# ----------------------------------------------
# Clause Extraction Model Structure
# ----------------------------------------------

class Clause(BaseModel):
    clause_name : str
    clause_text : str

class Clause_Extraction(BaseModel):
    clauses : list[Clause]

# ----------------------------------------------
# Extracting Clauses
# ----------------------------------------------

def extract_clauses(state: Legal_Document_State):

    raw_text = state["raw_text"]

    prompt = f"""
You are a legal document analysis assistant.

Your task is to identify the important clauses present in the provided document.

Identify clauses based on their meaning and context, not only exact keyword matches.

For every clause:
- Give a clear clause name.
- Extract the actual clause text from the document.
- Do not invent or rewrite the clause.
- Only include clauses that are actually present in the document.

Document text: 

{raw_text}
"""
    result = invoke_structured_with_fallback(Clause_Extraction, prompt)

    # Mark clause extraction as completed
    update_progress(
        state.get("thread_id"),
        "clause_extraction"
    )

    return {
        "clauses": result.clauses  
    }

# ----------------------------------------------
# Sufficiency Check Model Structure
# ----------------------------------------------

class Sufficiency_Check(BaseModel):
    is_sufficient: bool
    missing_information: list[str]
    reasoning: str

# ----------------------------------------------
# Checking Sufficient Information
# ----------------------------------------------

def check_sufficient_information(state: Legal_Document_State):

    raw_text = state["raw_text"]
    clauses = state["clauses"]

    user_query = state.get("user_query", "").strip()

    if not user_query:
        user_query = "Perform a comprehensive legal review of this document."

    clause_text = ""

    for clause in clauses:
        clause_text += f"""
Clause Name: {clause.clause_name}
Clause Text: {clause.clause_text}
"""

    prompt = f"""
You are a legal document sufficiency assessment assistant.

Your task is to determine whether the available information in the
document is sufficient to perform the requested legal document review.

USER QUERY:
{user_query}

EXTRACTED CLAUSES:
{clause_text}

DOCUMENT TEXT:
{raw_text}

Rules:

1. Consider the user's query when determining sufficiency.

2. Determine whether the document contains enough actual information
to perform a meaningful review of the requested document.

3. Do not assume that information exists if it is not present in the document.

4. Set is_sufficient to false ONLY when the document is too incomplete,
unreadable, corrupted, or lacks enough actual content to perform a
meaningful review.

5. The absence of individual legal clauses or provisions does NOT by itself
make the document insufficient.

6. Missing provisions such as indemnity, force majeure, insurance,
intellectual property, audit rights, dispute resolution, warranties,
assignment, or other legal clauses should NOT automatically cause
is_sufficient to be false. These can instead be identified later as
potential risks or missing provisions during legal review and risk analysis.

7. If the document contains substantial readable legal content and enough
information to analyze at least some of its clauses, set is_sufficient to true.

8. Only identify missing information that prevents the requested review
from being meaningfully performed.

9. Do not invent missing information.

10. Explain the reasoning behind the decision.

Return the result using the required structured format.
"""

    result = invoke_structured_with_fallback(Sufficiency_Check, prompt)

    # Mark sufficiency check as completed
    update_progress(
        state.get("thread_id"),
        "sufficiency_check"
    )

    return {
        "is_sufficient": result.is_sufficient,
        "missing_information": result.missing_information,
        "reasoning": result.reasoning
    }

# ----------------------------------------------
# Document Classification
# ----------------------------------------------

def document_classification(state: Legal_Document_State):

    raw_text = state["raw_text"]

    prompt = f"""
You are a document classification assistant for a legal document intelligence system.

Classify the provided document into exactly ONE of these categories:

- vendor_agreement
- service_agreement
- policy_document
- regulatory_filing
- other_legal_document

Rules:
- Return exactly ONE category from the allowed categories.
- If the document does not reasonably fit any of the first four categories,
  classify it as other_legal_document.
- Never invent a category outside the allowed categories and do not invent any information out of the context.

Document text:

{raw_text}
"""

    result = invoke_with_fallback(prompt)

    document_type = result.content

    if isinstance(document_type, list):
        document_type = document_type[0]["text"]

    document_type = document_type.strip()

    # Mark document classification as completed
    update_progress(
        state.get("thread_id"),
        "document_classification"
    )

    return {
        "document_type": document_type
    }

# ----------------------------------------------
# Retrieving Legal Guidance
# ----------------------------------------------

def retrieve_legal_guidance(state: Legal_Document_State):

    """Retrieve relevant legal guidance from the approved knowledge base."""

    retrieved_guidance = []

    retriever = get_kb_retriever()

    # Search the knowledge base using the extracted clause
    for clause in state["clauses"]:
        query = clause.clause_text

        results = retriever.invoke(query)

        for document in results:
            retrieved_guidance.append({
                "content" : document.page_content,
                "metadata" : document.metadata
            })

    # Mark legal guidance retrieval as completed
    update_progress(
        state.get("thread_id"),
        "legal_guidance_retrieval"
    )

    return {
        "retrieved_guidance" : retrieved_guidance
    }

# --------------------------------------------------
# Legal Review Agent Model Structure
# --------------------------------------------------

class Legal_Review_Output(BaseModel):
    findings: List[str]
    reasoning: str

# --------------------------------------------------
# Legal Review Agent
# --------------------------------------------------

def legal_review_agent(state: Legal_Document_State):

    # Tools available to the Legal Review Agent
    tools = [document_evidence_search, evidence_verification]

    clause_text = ""

    for clause in state["clauses"]:
        clause_text += f"""
Clause Name: {clause.clause_name}
Clause Text: {clause.clause_text}
"""

    guidance_text = ""

    for guidance in state["retrieved_guidance"]:
        guidance_text += f"""
Guidance: {guidance["content"]}
Reference: {guidance["metadata"]}
"""

    user_query = state.get("user_query", "")
    messages = state.get("messages", [])

    prompt = f"""
You are the Legal Review Agent in a legal document intelligence system.

Your task is to review the document using the extracted clauses and the 
approved knowledge base guidance.

DOCUMENT TYPE:
{state["document_type"]}

EXTRACTED CLAUSES:
{clause_text}

APPROVED KNOWLEDGE BASE GUIDANCE:
{guidance_text}

Instructions:

1. Analyze the document only using the extracted clauses and 
approved knowledge base guidance.

2. Treat the knowledge base guidance as supporting reference, not as 
evidence from the document.

3. If the available clauses are not enough to support an important finding, 
use the document_evidence_search tool to retrieve additional evidence from 
the uploaded document.

4. Decide yourself whether using the tool is necessary.

5. When using the tool, generate a semantic search query describing the evidence you need.

6. Do not invent facts, clauses, obligations, laws, or legal requirements.

7. Every finding must be grounded in the document and/or approved knowledge base guidance.

8. Do not assign severity, confidence, or final risk labels. That will be 
handled in the Risk Analysis stage.

9. Produce concise grounded findings and reasoning that can be passed to the 
Risk Analysis stage.
"""

    if user_query:
        current_request = user_query
    else:
        current_request = "Perform a comprehensive legal review of this document."

    # Check whether the agent is continuing after a tool call
    is_tool_continuation = (
        messages
        and isinstance(messages[-1], ToolMessage)
    )

    # Human review requested a fresh analysis
    is_fresh_human_review = (
        state.get("human_review_status") in [
            "re-analyze",
            "wrong_classification"
        ]
        and not is_tool_continuation
    )

    # Start a fresh review for the first analysis
    # or after a human-requested re-analysis/classification correction
    if not messages or is_fresh_human_review:

        user_message = HumanMessage(
            content = f"{prompt}\n\nUSER REQUEST:\n{current_request}"
        )

        result = invoke_with_tools_fallback(tools, [user_message])

        conversation = [user_message, result]

    # Continue the existing agent-tool conversation
    else:

        result = invoke_with_tools_fallback(tools, messages)

        conversation = [result]

    if result.tool_calls:
        return {
            "messages": conversation
        }

    # Mark legal agent review as completed
    update_progress(
        state.get("thread_id"),
        "legal_agent_review"
    )

    return {
        "messages": conversation,
        "agent_findings": result.content
    }

# ----------------------------------------------
# Risk Analysis Model Structure
# ----------------------------------------------

class RiskFlag(BaseModel):
    """
    Represents one legal/compliance risk identified in the document.
    """

    severity: str = Field(description="High, Medium, or Low severity.")

    risk_type: str = Field(
        description="Missing Information, Ambiguous Language, Non-standard Wording, Conflicting Obligations, or High-risk Provision."
    )

    affected_clause: str = Field(
        description="Clause where the risk was identified."
    )

    rationale: str = Field(
        description="Reason this clause is considered risky."
    )

    source_location: str = Field(
        description="Clause or section name in the document."
    )

    recommended_action: str = Field(
        description="Suggested action for the legal reviewer."
    )

    confidence: int = Field(
        description="Confidence score as a whole number percentage between 0 and 100."
    )

class RiskAnalysisOutput(BaseModel):
    """
    Structured response returned by Gemini for risk analysis.
    """

    risk_flags: List[RiskFlag]

# ----------------------------------------------
# Risk Analysis
# ----------------------------------------------

def risk_analysis(state: Legal_Document_State):

    agent_findings = state.get("agent_findings", "")
    clauses = state["clauses"]
    retrieved_guidance = state["retrieved_guidance"]

    # Formatting extracted clauses into readable text for the llm
    clause_text = ""

    for clause in clauses:
        clause_text += f"""
Clause_name: {clause.clause_name}
Clause_text: {clause.clause_text}
"""

    # Formatting retrieved guidance into readable text for the llm
    guidance_text = ""

    for guidance in retrieved_guidance:
        guidance_text += f"""
Guidance: {guidance["content"]}
Reference: {guidance["metadata"]}
"""

    prompt = f"""
You are a legal document risk analysis assistant.

Your task is to identify potential legal or compliance risks
using the Legal Review Agent's findings, the actual clauses
from the document, and the approved legal guidance retrieved
from the knowledge base.

IMPORTANT RULES:

1. Only identify risks that are supported by the document text
and/or the retrieved approved guidance.

2. Do not invent facts, clauses, obligations, laws, or risks.

3. Do not provide legal advice or make a final legal decision.
Your output is only a preliminary risk assessment for human legal review.

4. If there is not enough evidence to support a risk, do not create a risk flag.

5. Use only these risk types:
    - Missing Information
    - Ambiguous Language
    - Non-standard Wording
    - Conflicting Obligations
    - High-risk Provision

6. The affected_clause must refer to a clause that actually exists in the document.

7. The rationale must explain the risk using evidence from the actual
clause and/or retrieved guidance.

8. The recommended_action should be an action for a human legal reviewer,
not a final legal conclusion.

9. Confidence must be a whole number between 0 and 100.

10. Return confidence as a numeric integer only. Do not write it as a word or decimal.

11. It is acceptable to return an empty list if no supported risks are identified.

LEGAL REVIEW AGENT FINDINGS:
{agent_findings}

DOCUMENT CLAUSES:
{clause_text}

APPROVED KNOWLEDGE BASE GUIDANCE:
{guidance_text}
"""

    result = invoke_structured_with_fallback(RiskAnalysisOutput, prompt)

    # Mark risk analysis as completed
    update_progress(
        state.get("thread_id"),
        "risk_analysis"
    )

    return {
        "risk_flags": result.risk_flags
    }

# ----------------------------------------------
# Human Review
# ----------------------------------------------

def human_review(state: Legal_Document_State):

    risk_flags = state.get("risk_flags", [])

    review_request = {
        "type": "human_review",
        "message": "Please review the AI-generated legal risk analysis.",
        "risk_flags": risk_flags,
        "options": [
            "approve",
            "re-analyze",
            "wrong_classification",
            "escalate"
        ]
    }

    # Analysis is now paused and waiting for human review
    update_progress(
        state.get("thread_id"),
        "human_review_required"
    )
    
    decision = interrupt(review_request)

    return {
        "human_review_status" : decision
    }

# ----------------------------------------------
# Final Legal Summary
# ----------------------------------------------

def generate_final_summary(state: Legal_Document_State):

    clauses = state["clauses"]
    agent_findings = state.get("agent_findings", "")
    risk_flags = state.get("risk_flags", [])
    human_review_status = state.get("human_review_status", "")

    # Formatting extracted clauses
    clause_text = ""

    for clause in clauses:
        clause_text += f"""
Clause Name: {clause.clause_name}
Clause Text: {clause.clause_text}
"""

    # Formatting risk flags
    risk_text = ""

    if risk_flags:

        for risk in risk_flags:
            risk_text += f"""
Risk Type: {risk.risk_type}
Severity: {risk.severity}
Affected Clause: {risk.affected_clause}
Rationale: {risk.rationale}
Source Location: {risk.source_location}
Recommended Action: {risk.recommended_action}
Confidence: {risk.confidence}
"""

    else:
        risk_text = "No supported legal or compliance risks were identified."

    prompt = f"""
You are the final legal document review summarization assistant.

Create a concise but comprehensive final legal document review summary
using ONLY the information provided below.

DOCUMENT TYPE:
{state["document_type"]}

EXTRACTED CLAUSES:
{clause_text}

LEGAL REVIEW AGENT FINDINGS:
{agent_findings}

IDENTIFIED RISKS:
{risk_text}

HUMAN REVIEW DECISION:
{human_review_status}

IMPORTANT RULES:

1. Do not invent facts, clauses, obligations, laws, or legal conclusions.

2. Use only information supported by the document clauses, agent findings,
and identified risk flags.

3. Clearly distinguish between facts from the document and preliminary
risk observations.

4. Do not provide final legal advice.

5. Preserve the source location and affected clause information for
identified risks.

6. If no risks were identified, explicitly state that no supported
legal or compliance risks were identified.

7. The human review decision must be reflected accurately.

8. Keep the summary professional, concise, and suitable for a legal
or compliance reviewer.

Use exactly this structure:

📄 FINAL LEGAL DOCUMENT REVIEW

Document Type:
[document type]

Executive Summary:
[concise summary of the document and its purpose]

Key Clauses:
• [important clause]
• [important clause]
• [important clause]

Identified Risks:
[risks with type, severity, affected clause, rationale,
source location, and recommended action]

Evidence & Sources:
[relevant document clauses and locations used during the review]

Human Review:
[human review decision]

Overall Review Status:
Finalized
"""
    
    result = invoke_with_fallback(prompt)

    return {
        "final_summary": result.content
    }

# --------------------------------------------------
# Load Embedding Model for Document Q&A
# --------------------------------------------------

qa_embeddings = None

def get_qa_embeddings():

    global qa_embeddings

    # Load the embedding model only on first use
    if qa_embeddings is None:

        qa_embeddings = HuggingFaceEmbeddings(
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
        )

    return qa_embeddings

# --------------------------------------------------
# Document Follow-up Q&A
# --------------------------------------------------

def document_qa(document_vector_store_path, user_question):

    # Create retriever for the uploaded document
    retriever = Chroma(
        persist_directory = document_vector_store_path,
        embedding_function = get_qa_embeddings()
    ).as_retriever(
        search_kwargs = {"k": 3}
    )

    # Search the uploaded document
    results = retriever.invoke(user_question)

    # Collect relevant evidence
    evidence = []

    for result in results:
        evidence.append(
            f"""
Evidence:
{result.page_content}
"""
        )

    if evidence:

        evidence_text = "\n".join(evidence)

    else:

        evidence_text = "No relevant information was found in the uploaded document."   

    # Ask Gemini to answer using only retrieved evidence
    prompt = f"""
You are a legal document review assistant.

The user has already received a legal document review.
They are now asking a follow-up question about the same document.

Your task is to answer the user's question helpfully while
distinguishing between legal questions, document-specific questions,
and questions unrelated to the legal domain.

IMPORTANT RULES:

1. If the user asks a GENERAL legal-domain question, provide a
clear and simple general explanation using your general legal knowledge.

Example:
If the user asks:
"What is indemnity in general?"

First explain what indemnity generally means.

Then clearly state whether relevant information about indemnity
was found in the uploaded document.

2. If the user asks a DOCUMENT-SPECIFIC legal question, answer using
the retrieved evidence from the uploaded document.

3. If the question is BOTH general and document-specific:
   - First provide the general legal explanation.
   - Then explain what the uploaded document says about that topic,
     based only on the retrieved evidence.

4. If relevant information is NOT present in the uploaded document,
do not say that you cannot explain the legal concept.

Instead:
   - Provide the general legal explanation if the question is
     a general legal-domain question.
   - Then clearly state that the relevant information was not found
     in the uploaded document.

5. If the user asks a question unrelated to the legal domain or
unrelated to the uploaded document, do not attempt to answer it.

Respond clearly:
"I can only help with legal or uploaded-document-related questions."

6. Do not invent facts about the uploaded document.

7. When discussing the uploaded document, use only the retrieved
document evidence provided below.

8. Clearly distinguish general legal information from information
actually found in the uploaded document.

9. Do not provide personalized legal advice or make a final legal
decision.

10. Explain the answer clearly and simply.

DOCUMENT EVIDENCE:
{evidence_text}

USER QUESTION:
{user_question}
"""

    response = invoke_with_fallback(prompt)

    return response.content