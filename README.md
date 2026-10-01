# ⚖️ Tata AI Legal Document Intelligence

An AI-assisted legal document review system that analyzes legal documents using **Generative AI, RAG, LangGraph, document evidence retrieval, and Human-in-the-Loop review**.

The system extracts important clauses, checks whether sufficient information is available, classifies the document, retrieves relevant legal guidance, performs evidence-grounded review, identifies potential risks, and allows a human reviewer to review the findings before the final summary is generated.

---

## 🌐 Live Application

**[Open Tata AI Legal Document Intelligence](YOUR_DEPLOYED_APP_URL)**

The application is deployed and can be accessed directly through the link above.

### 📂 Source Code

The complete source code, project structure, documentation, and configuration are available in this GitHub repository.

---

## 🚀 Overview

Legal document review often requires manually reading lengthy documents, identifying important clauses, checking for missing information, finding potentially risky provisions, and supporting findings with evidence from the document.

**Tata AI Legal Document Intelligence** automates the initial review process while keeping a human reviewer involved before the final result is generated.

The application supports multiple document formats and combines:

* Generative AI
* Retrieval-Augmented Generation (RAG)
* Vector databases
* LangGraph workflow orchestration
* Tool-based document evidence search
* Structured LLM outputs
* Human-in-the-Loop review

The system is designed to **assist legal document review, not replace professional legal judgment**.

---

## ✨ Key Features

### 📄 Multi-Format Document Processing

Supports:

* PDF
* DOCX
* ODT
* PNG
* JPG / JPEG

The application can extract text from native documents and use OCR when text needs to be extracted from images.

---

### 🔍 Clause Extraction

The system uses an LLM with structured output to identify important clauses from the uploaded document.

For each clause, the system extracts:

* Clause name
* Actual clause text

The extraction process is designed to use only information present in the uploaded document.

---

### ✅ Sufficiency Check

Before continuing with the legal review, the system checks whether the available document information is sufficient for the requested analysis.

If important information is missing, the workflow stops and displays the missing information instead of generating a risk analysis.

```text
Document
   ↓
Sufficiency Check
   ↓
Insufficient Information
   ↓
Show Missing Information
   ↓
Stop Review
```

---

### 🏷️ Document Classification

The system classifies documents into supported categories such as:

* `vendor_agreement`
* `service_agreement`
* `policy_document`
* `regulatory_filing`
* `other_legal_document`

Classification is based on the document's purpose and content.

---

### 📚 Legal Knowledge Base + RAG

The project contains a structured legal knowledge base with guidance for different clause categories.

The current knowledge base contains:

* 11 Markdown files
* 88 knowledge entries

It covers areas such as:

* Audit Rights
* Compliance Obligations
* Confidentiality
* Data Protection
* Dispute Resolution
* Governing Law
* Indemnity
* Liability
* Payment Terms
* Renewal
* Termination

The retrieval layer uses:

* HuggingFace `all-MiniLM-L6-v2` embeddings
* ChromaDB
* Semantic similarity search
* Top-k retrieval

Relevant guidance is retrieved based on the clauses identified in the uploaded document.

---

## 🤖 Legal Review Agent

The legal review stage uses a **LangGraph-based agent** to analyze the document using:

* Extracted clauses
* Retrieved legal guidance
* Document evidence
* Evidence verification

The entire application is **not made agentic**.

LangGraph controls the overall workflow, while the agent is specifically used for the legal review stage where document evidence may need to be searched and verified.

---

## 🛠️ Document Analysis Tools

The Legal Review Agent can use two document-level tools.

### Document Evidence Search

Searches the temporary vector store created from the uploaded document.

This allows the agent to retrieve relevant sections of the actual document when additional evidence is required.

### Evidence Verification

Verifies retrieved evidence and checks for potentially conflicting information or obligations within the document.

These tools help ground the review in the uploaded document rather than relying only on the model's general knowledge.

---

## ⚠️ Risk Analysis

After the legal review stage, the system performs structured risk analysis.

Supported risk types include:

* Missing Information
* Ambiguous Language
* Non-standard Wording
* Conflicting Obligations
* High-risk Provision

Risk findings can include:

* Severity
* Risk type
* Affected clause
* Rationale
* Source location
* Recommended action
* Confidence

Risk-analysis results are structured using Pydantic models.

---

## 👤 Human-in-the-Loop Review

The workflow pauses after risk analysis and requires human review before generating the final summary.

The reviewer can choose:

### Approve

Continues the workflow and generates the final summary.

### Re-analyze

Retrieves the relevant legal guidance again and sends the workflow back to the Legal Review Agent.

### Wrong Classification

Sends the document through classification again before continuing the review workflow.

### Escalate

Stops the automated workflow without generating the final summary.

This keeps the final review decision under human control.

---

## 📄 Final Legal Document Summary

After the human reviewer approves the analysis, the system generates a structured final summary of the document.

The final summary includes:

* Document type
* Executive summary
* Key clauses
* Identified risks
* Risk severity
* Supporting reasoning
* Relevant document evidence

The final output provides a consolidated view of the approved analysis.

---

## 🔄 System Workflow

                         Document Upload
                                │
                                ↓
                       Document Parsing
                                │
                                ↓
                 Temporary Document Vector Store
                                │
                                ↓
                       Clause Extraction
                                │
                                ↓
                       Sufficiency Check
                         /             \
                        /               \
              Insufficient           Sufficient
                  │                      │
                  ↓                      ↓
       Show Missing Information   Document Classification
                  │                      │
                  ↓                      ↓
                 END             Knowledge Base Retrieval
                                         │
                                         ↓
                                  Legal Review Agent
                                    /           \
                                   ↓             ↓
                         Document Evidence   Evidence
                              Search         Verification
                                   \           /
                                    \         /
                                     ↓       ↓
                                    Legal Findings
                                          │
                                          ↓
                                    Risk Analysis
                                          │
                                          ↓
                                    Human Review
                                          │
              ┌───────────────────┬───────┼───────────────┐
              ↓                   ↓       ↓               ↓
           Approve            Re-analyze  Wrong        Escalate
                                      Classification
              │                   │       │               │
              │                   ↓       ↓               ↓
              │             Retrieve   Reclassify       END
              │             Guidance      │
              │                   │       │
              │                   ↓       │
              │             Legal Review │
              │                Agent ◄────┘
              │
              ↓
       Final Legal Document
             Summary

---

## 🏗️ Application Architecture

                 ┌─────────────────────┐
                 │     Streamlit UI    │
                 └──────────┬──────────┘
                            │
                            ↓
                 ┌─────────────────────┐
                 │    FastAPI Backend  │
                 └──────────┬──────────┘
                            │
                            ↓
                 ┌─────────────────────┐
                 │     LangGraph       │
                 │      Workflow       │
                 │    Orchestration    │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
        LLM Layer       RAG Layer      Document Tools
             │              │              │
       Groq / Gemini     ChromaDB      Evidence Search
                                      Evidence Verification
             │              │              │
             └──────────────┼──────────────┘
                            ↓
                     Human Review
                            ↓
                 Final Document Summary

---

## 🗄️ Application Database

The backend uses **SQLite with SQLAlchemy** for application data.

The database stores application-level information such as:

* Uploaded document records
* Analysis information
* Review decisions
* Status information
* Timestamps

The application database is separate from the vector databases used for document and knowledge-base retrieval.

---

## 🧩 Technology Stack

| Technology             | Purpose                         |
| ---------------------- | ------------------------------- |
| Python                 | Core programming language       |
| Streamlit              | Frontend and user interface     |
| FastAPI                | Backend API                     |
| LangGraph              | Workflow orchestration          |
| LangChain              | LLM and retrieval integrations  |
| Groq / Google Gemini   | Generative AI                   |
| ChromaDB               | Vector database                 |
| HuggingFace Embeddings | Semantic embeddings             |
| Pydantic               | Structured data and LLM outputs |
| SQLAlchemy             | Database ORM                    |
| SQLite                 | Application database            |
| PyPDF                  | PDF processing                  |
| python-docx            | DOCX processing                 |
| RapidOCR               | OCR                             |
| Pillow                 | Image processing                |
| odfpy                  | ODT processing                  |

---

## 📁 Key Files

**`app.py`**
Streamlit frontend and user interaction.

**`backend/main.py`**
FastAPI application and API endpoints.

**`backend/database.py`**
SQLite database configuration and SQLAlchemy setup.

**`backend/models.py`**
Database models.

**`graph/graph.py`**
LangGraph workflow, routing, tools, and human-review flow.

**`graph/state.py`**
Shared state used throughout the workflow.

**`graph/nodes.py`**
Document processing, clause extraction, sufficiency check, classification, legal review, risk analysis, human review, and final summary logic.

**`rag/kb_retriever.py`**
Knowledge-base retrieval.

**`rag/tools.py`**
Document evidence search and evidence verification tools.

**`rag/document_retriever.py`**
Temporary vector store creation and document retrieval.

---

## 🔐 Data & Security

* API keys are stored in environment variables.
* `.env` files are excluded from Git.
* Local SQLite database files are excluded from Git.
* Local vector databases are excluded from Git.
* Uploaded documents are excluded from Git.
* Users interact with the application through the frontend/API rather than directly accessing the backend database.

---

## ⚖️ Disclaimer

Tata AI Legal Document Intelligence is an **AI-assisted legal document review system** developed as an educational and portfolio project.

It is intended to assist with initial document analysis and should not be considered a substitute for professional legal advice, legal counsel, or formal legal review.

AI-generated findings may contain errors and should be reviewed by a qualified human professional.

---

## 👨‍💻 Author

**Aadarsh Pundhir**

Built to demonstrate practical applications of:

* Generative AI
* Prompt Engineering
* LLM APIs
* LangGraph
* Retrieval-Augmented Generation
* Vector Databases
* Tool-based AI Agents
* Human-in-the-Loop AI
* Streamlit
* FastAPI