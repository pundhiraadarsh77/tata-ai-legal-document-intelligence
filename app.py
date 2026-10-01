import os
import requests
import threading
import time
import streamlit as st

# ----------------------------------------------
# BACKEND URL
# ----------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

# ----------------------------------------------
# Page Configuration
# ----------------------------------------------

st.set_page_config(
    page_title = "Tata AI Chatbot Assistant",
    page_icon = "⚖️",
    layout = "wide"
)

# ----------------------------------------------
# Create Chat Title
# ----------------------------------------------

def create_chat_title(filename):
    """
    Creates a clean chat title from the uploaded document filename.
    """

    # Remove the file extension
    title = os.path.splitext(filename)[0]

    # Replace underscores and hyphens with spaces
    title = title.replace("_", " ").replace("-", " ")

    # Convert the title into readable capitalization
    chat_title = title.title()

    return chat_title

# ----------------------------------------------
# Session Management
# ----------------------------------------------

# Store the current chat session
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = 1

# Store all chat sessions
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

# ----------------------------------------------
# LangGraph Thread Management
# ----------------------------------------------

if "thread_ids" not in st.session_state:
    st.session_state.thread_ids = {}

# ----------------------------------------------
# Sidebar - Chat History
# ----------------------------------------------

with st.sidebar:

    st.title("💬 Tata AI Assistant")

    # Start a completely new chat session
    new_chat = st.button(
        "➕ New Chat",
        use_container_width=True
    )

    if new_chat:

        # Create a new unique session ID
        st.session_state.current_session_id += 1

        # Start with an empty conversation for the new session
        st.session_state.sessions[
            st.session_state.current_session_id
        ] = {
            "title": "New Chat",
            "messages": [],
            "documents": [],
            "user_query": "",
            "analysis_result": None,
            "human_review_status": None,
            "final_summary": None,
            "human_review_request": None,
            "document_qa_history": []
        }

        st.rerun()

    st.divider()

    st.subheader("🗂️ Chat History")

    if len(st.session_state.sessions) == 0:

        st.caption("No previous conversations")

    else:

        for session_id, session_data in st.session_state.sessions.items():

            if st.button(
                session_data["title"],
                key = f"session_{session_id}",
                use_container_width = True
            ):

                # Switch to the selected chat session
                st.session_state.current_session_id = session_id

                st.rerun()

# ----------------------------------------------
# Get Current Chat Session
# ----------------------------------------------

current_session = st.session_state.sessions.get(
    st.session_state.current_session_id
)

# ----------------------------------------------
# Application Header
# ----------------------------------------------

st.title("⚖️ Tata AI Legal Document Intelligence")
st.write(
    "AI-assisted legal document review for faster and "
    "evidence grounded first-pass analysis."
)

st.divider()

# ----------------------------------------------
# Document Upload
# ----------------------------------------------

# ----------------------------------------------
# Current Chat / Document Area
# ----------------------------------------------

if current_session is not None and current_session["documents"]:

    # ------------------------------------------
    # Existing Chat Session
    # ------------------------------------------

    st.header("📄 Current Document")

    for document in current_session["documents"]:

        st.info(f"📎 {document['name']}")

    st.divider()

    # ------------------------------------------
    # Show Previous User Query
    # ------------------------------------------

    if current_session["user_query"]:

        st.chat_message("user").write(
            current_session["user_query"]
        )

    else:

        st.chat_message("user").write(
            "Perform a comprehensive legal review of this document."
        )

    # -------------------------------------------
    # Human Review UI
    # -------------------------------------------

    if current_session["human_review_request"] is not None:

        review_request = current_session["human_review_request"]

        # ------------------------------------------
        # Legal Risk Analysis
        # ------------------------------------------

        risk_flags = current_session["analysis_result"].get(
            "risk_flags", []
        )

        st.subheader("⚠️ Legal Risk Analysis")

        if risk_flags:

            for index, risk in enumerate(risk_flags, start=1):

                risk_type = risk.get('risk_type', 'N/A')
                severity = risk.get('severity', 'N/A')
                affected_clause = risk.get('affected_clause', 'N/A')
                rationale = risk.get('rationale', 'N/A')
                source_location = risk.get('source_location', 'N/A')
                recommended_action = risk.get('recommended_action', 'N/A')
                confidence = risk.get('confidence', 0)
                st.warning(
                    f"### Risk {index}: {risk_type}\n\n"
                    f"**Severity:** {severity}\n\n"
                    f"**Affected Clause:** {affected_clause}\n\n"
                    f"**Rationale:** {rationale}\n\n"
                    f"**Evidence / Source:** {source_location}\n\n"
                    f"**Recommended Action:** {recommended_action}\n\n"
                    f"**Confidence:** {confidence:.0f}%"
                )

        else:

            st.success(
                "🟢 No supported legal or compliance risks were "
                "identified in the analyzed document."
            )

            st.info(
                "Human review is still required before finalization."
            )

        st.divider()

        # ------------------------------------------
        # Human Review Required
        # ------------------------------------------

        st.subheader("👤 Human Review Required")

        st.info(
            "The AI legal review is paused and requires "
            "human review before the document can be finalized."
        )

        # ------------------------------------------
        # Human Review Options
        # ------------------------------------------

        review_options = (
            review_request.get("options")
            if isinstance(review_request, dict)
            else None
        ) or [
            "approve",
            "re-analyze",
            "wrong_classification",
            "escalate"
        ]

        selected_review = st.radio(
            "Select a review decision:",
            review_options,
            format_func = lambda option: option.replace(
            "_", " "
            ).title(),
            key = f"review_{st.session_state.current_session_id}"
        )

        # ------------------------------------------
        # Submit Human Review
        # ------------------------------------------

        submit_review = st.button(
            "Submit Review",
            type = "primary"
        )

        if submit_review:

            thread_id = st.session_state.thread_ids[
                st.session_state.current_session_id
            ]

            document_id = current_session["documents"][0]["document_id"]

            review_payload = {
                "decision": selected_review,
                "thread_id": thread_id
            }

            # ------------------------------------------
            # Re-analysis Progress Stages
            # ------------------------------------------

            if selected_review == "wrong_classification":

                review_progress_stages = [
                    ("document_classification", "Document Classification"),
                    ("legal_guidance_retrieval", "Legal Guidance Retrieval"),
                    ("legal_agent_review", "Legal Agent Review"),
                    ("risk_analysis", "Risk Analysis")
                ]

            elif selected_review == "re-analyze":

                review_progress_stages = [
                    ("legal_guidance_retrieval", "Legal Guidance Retrieval"),
                    ("legal_agent_review", "Legal Agent Review"),
                    ("risk_analysis", "Risk Analysis")
                ]

            else:

                review_progress_stages = []

            # ------------------------------------------
            # Handle Re-analysis / Re-classification
            # ------------------------------------------

            if selected_review in [
                "re-analyze",
                "wrong_classification"
            ]:

                review_result_holder = {}

                def submit_review_request():

                    try:

                        response = requests.post(
                            f"{BACKEND_URL}/documents/{document_id}/review",
                            json=review_payload
                        )

                        response.raise_for_status()

                        review_result_holder["response"] = response

                    except Exception as error:

                        review_result_holder["error"] = error

                review_thread = threading.Thread(
                    target = submit_review_request
                )

                review_thread.start()

                progress_placeholder = st.empty()

                # ------------------------------------------
                # Poll Re-analysis Progress
                # ------------------------------------------

                with st.spinner("Re-analyzing document..."):

                    while review_thread.is_alive():

                        try:

                            progress_response = requests.get(
                                f"{BACKEND_URL}/analysis-progress/{thread_id}"
                            )

                            progress_response.raise_for_status()

                            current_stage = progress_response.json().get(
                                "stage",
                                "starting"
                            )

                        except Exception:

                            current_stage = "starting"

                        current_index = -1

                        for index, (stage_key, _) in enumerate(
                            review_progress_stages
                        ):

                            if stage_key == current_stage:

                                current_index = index

                                break

                        progress_lines = [
                            "### 🔄 Re-analysis in progress..."
                        ]

                        for index, (_, stage_name) in enumerate(
                            review_progress_stages
                        ):

                            if index <= current_index:

                                progress_lines.append(
                                    f"✅ {stage_name} completed successfully"
                                )

                        progress_placeholder.markdown(
                            "\n\n".join(progress_lines)
                        )

                        time.sleep(0.5)

                # ------------------------------------------
                # Wait for Review Response
                # ------------------------------------------

                review_thread.join()

                # ------------------------------------------
                # Handle Review Error
                # ------------------------------------------

                if "error" in review_result_holder:

                    st.error(
                        "❌ Problem with the LLM. "
                        "Please try again after some time."
                    )

                    st.stop()

                review_response = review_result_holder["response"]

                # ------------------------------------------
                # Show Final Re-analysis Progress
                # ------------------------------------------

                try:

                    final_progress_response = requests.get(
                        f"{BACKEND_URL}/analysis-progress/{thread_id}"
                    )

                    final_progress_response.raise_for_status()

                    final_stage = final_progress_response.json().get(
                        "stage",
                        "starting"
                    )

                except Exception:

                    final_stage = "starting"

                if final_stage == "human_review_required":

                    progress_lines = [
                        "### 🔄 Re-analysis in progress..."
                    ]

                    for _, stage_name in review_progress_stages:

                        progress_lines.append(
                            f"✅ {stage_name} completed successfully"
                        )

                    progress_lines.append(
                        "👤 Human Review Required"
                    )

                    progress_placeholder.markdown(
                        "\n\n".join(progress_lines)
                    )

            # ------------------------------------------
            # Handle Approve / Escalate
            # ------------------------------------------

            else:

                try:

                    with st.spinner("Submitting review..."):

                        review_response = requests.post(
                            f"{BACKEND_URL}/documents/{document_id}/review",
                            json=review_payload
                        )

                    review_response.raise_for_status()

                except Exception:

                    st.error(
                        "❌ Problem with the LLM. "
                        "Please try again after some time."
                    )

                    st.stop()

            result = review_response.json()

            new_vector_store_path = result.get(
                "document_vector_store_path"
            )

            if new_vector_store_path:

                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["document_vector_store_path"] = new_vector_store_path

            # Save latest workflow result
            st.session_state.sessions[
                st.session_state.current_session_id
            ]["analysis_result"] = result

            # Save human decision (source of truth is backend response)
            st.session_state.sessions[
                st.session_state.current_session_id
            ]["human_review_status"] = result.get("human_review_status")

            # --------------------------------------
            # Human Review Interrupt Handling
            # --------------------------------------

            if result.get("human_review_status") == "awaiting_human_review":

                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["human_review_request"] = result.get("human_review_request")

            else:

                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["human_review_request"] = None

            # --------------------------------------
            # Save Final Summary if generated
            # --------------------------------------

            if result.get("final_summary"):

                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["final_summary"] = result["final_summary"]

            st.rerun()

    elif current_session["final_summary"] is not None:

        st.success("✅ Document review finalized.")

        st.divider()

        st.subheader("📄 Final Legal Document Review")

        final_summary = current_session["final_summary"]

        # LLM may return the response content as a list of text blocks.
        # Extract the actual text before displaying it in Streamlit.
        if isinstance(final_summary, list):

            final_summary_text = ""

            for block in final_summary:

                if isinstance(block, dict) and block.get("type") == "text":

                    final_summary_text += block.get("text", "")

                elif isinstance(block, str):

                    final_summary_text += block

        else:

            final_summary_text = final_summary

        st.markdown(final_summary_text)

        st.divider()

        st.subheader("💬 Ask About This Document")

        if "document_qa_history" not in current_session:
            current_session["document_qa_history"] = []

        # Show previous document Q&A
        for qa in current_session["document_qa_history"]:

            st.chat_message("user").write(qa["question"])
            st.chat_message("assistant").write(qa["answer"])

        user_question = st.text_input(
            "Ask a follow-up question about the uploaded document:"
        )

        if st.button("Ask", key="document_qa_button"):

            if not user_question.strip():
                st.warning("Please enter a question.")

            else:

                try:

                    with st.spinner("Searching the document..."):

                        response = requests.post(
                            f"{BACKEND_URL}/document-qa",
                            json={
                                "document_vector_store_path": current_session["document_vector_store_path"],
                                "user_question": user_question.strip()
                            }
                        )

                        response.raise_for_status()

                        answer = response.json()["answer"]

                        # Save Q&A in current chat history
                        current_session["document_qa_history"].append(
                            {
                                "question": user_question.strip(),
                                "answer": answer
                            }
                        )

                        st.rerun()

                except Exception:
    
                    st.error(
                        "❌ Problem with the LLM. "
                        "Please try again after some time."
                    )

    else:

        st.info(
            "🔄 Document analysis has not been completed yet."
        )

else:

    # ------------------------------------------
    # New Chat / Upload Area
    # ------------------------------------------

    st.header("📄 Upload Legal Document")

    uploaded_file = st.file_uploader(
        "Upload a legal document for analysis",
        type = ["pdf",
                "docx",
                "png",
                "jpg",
                "jpeg",
                "odt"
                ]
    )

    if uploaded_file is not None:

        st.success(f"Document uploaded: {uploaded_file.name}")

        st.subheader("📝 Review Request")

        user_query = st.text_area(
            "What would you like the AI to review?",
            placeholder = "Example: Review this document for legal and compliance risks.",
            height = 100
        )

        analyze_button = st.button(
            "🔍 Analyze Document",
            type = "primary"
        )

        if analyze_button:

            # Send the uploaded document to FastAPI
            response = requests.post(
                f"{BACKEND_URL}/documents",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }
            )

            # Check if upload was successful
            if response.status_code != 200:

                st.error(
                    "❌ Failed to upload document to backend."
                )

                st.stop()

            # Get response from FastAPI
            document_data = response.json()

            # Get document information
            document_id = document_data.get("id")
            document_path = document_data.get("file_path")
            file_name = document_data.get("file_name", uploaded_file.name)

            st.success("Document uploaded successfully.")

            st.info(f"🆔 Document ID: {document_id}")

            st.info("🔄 Document analysis started...")

            # Create a clean title from the uploaded document filename
            chat_title = create_chat_title(file_name)

            # Save the current session data
            st.session_state.sessions[
                st.session_state.current_session_id
            ] = {
                "title": chat_title,
                "documents": [
                    {
                        "document_id": document_id,
                        "name": file_name,
                        "path": document_path
                    }
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                "user_query": user_query,
                "analysis_result": None,
                "human_review_status": None,
                "final_summary": None,
                "human_review_request": None,
                "document_qa_history": []
            }

            # ----------------------------------------------
            # Create LangGraph Thread ID
            # ----------------------------------------------

            if st.session_state.current_session_id not in st.session_state.thread_ids:
                st.session_state.thread_ids[
                    st.session_state.current_session_id
                ] = f"legal-review-{st.session_state.current_session_id}"

            thread_id = st.session_state.thread_ids[st.session_state.current_session_id]

            # ----------------------------------------------
            # Run Analysis via FastAPI
            # ----------------------------------------------

            analysis_payload = {
                "document_id": document_id,
                "document_path": document_path,
                "user_query": user_query.strip(),
                "thread_id": thread_id
            }

            # ----------------------------------------------
            # Run Analysis in Background
            # ----------------------------------------------

            analysis_result_holder = {}

            def run_analysis_request():

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/run-analysis",
                        json=analysis_payload
                    )

                    response.raise_for_status()

                    analysis_result_holder["response"] = response

                except Exception as error:

                    analysis_result_holder["error"] = error

            analysis_thread = threading.Thread(
                target = run_analysis_request
            )

            analysis_thread.start()

            # ----------------------------------------------
            # Analysis Progress Stages
            # ----------------------------------------------

            progress_stages = [
                ("document_parsing", "Document Parsing"),
                ("clause_extraction", "Clause Extraction"),
                ("sufficiency_check", "Sufficiency Check"),
                ("document_classification", "Document Classification"),
                ("legal_guidance_retrieval", "Legal Guidance Retrieval"),
                ("legal_agent_review", "Legal Agent Review"),
                ("risk_analysis", "Risk Analysis")
            ]

            progress_placeholder = st.empty()

            # ----------------------------------------------
            # Poll Analysis Progress
            # ----------------------------------------------

            with st.spinner("Analyzing document..."):

                while analysis_thread.is_alive():

                    try:

                        progress_response = requests.get(
                            f"{BACKEND_URL}/analysis-progress/{thread_id}"
                        )

                        progress_response.raise_for_status()

                        current_stage = progress_response.json().get(
                            "stage",
                            "starting"
                        )

                    except Exception:

                        current_stage = "starting"

                    current_index = -1

                    for index, (stage_key, _) in enumerate(
                        progress_stages
                    ):

                        if stage_key == current_stage:

                            current_index = index

                            break

                    progress_lines = [
                        "### 🔄 Analysis in progress..."
                    ]

                    for index, (_, stage_name) in enumerate(
                        progress_stages
                    ):

                        if index <= current_index:

                            progress_lines.append(
                                f"✅ {stage_name} completed successfully"
                            )

                    progress_placeholder.markdown(
                        "\n\n".join(progress_lines)
                    )

                    time.sleep(0.5)

            # ----------------------------------------------
            # Wait for Final Analysis Response
            # ----------------------------------------------

            analysis_thread.join()

            # ----------------------------------------------
            # Handle Analysis Error
            # ----------------------------------------------

            if "error" in analysis_result_holder:

                st.error(
                    "❌ Problem with the LLM. "
                    "Please try again after some time."
                )

                st.stop()

            analysis_response = analysis_result_holder["response"]

            # ----------------------------------------------
            # Show Final Progress
            # ----------------------------------------------

            try:

                final_progress_response = requests.get(
                    f"{BACKEND_URL}/analysis-progress/{thread_id}"
                )

                final_progress_response.raise_for_status()

                final_stage = final_progress_response.json().get(
                    "stage",
                    "starting"
                )

            except Exception:

                final_stage = "starting"

            if final_stage == "human_review_required":

                progress_lines = [
                    "### 🔄 Analysis in progress..."
                ]

                for _, stage_name in progress_stages:

                    progress_lines.append(
                        f"✅ {stage_name} completed successfully"
                    )

                progress_lines.append(
                    "👤 Human Review Required"
                )

                progress_placeholder.markdown(
                    "\n\n".join(progress_lines)
                )

            # ----------------------------------------------
            # Handle Analysis Result
            # ----------------------------------------------
            
            analysis_data = analysis_response.json()

            st.session_state.sessions[
                st.session_state.current_session_id
            ]["analysis_result"] = analysis_data

            document_vector_store_path = analysis_data.get(
                "document_vector_store_path"
            )

            if document_vector_store_path:

                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["document_vector_store_path"] = document_vector_store_path

            if analysis_data.get("human_review_status") in ["awaiting_human_review", "pending"]:
                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["human_review_request"] = analysis_data.get("human_review_request")
            else:
                st.session_state.sessions[
                    st.session_state.current_session_id
                ]["final_summary"] = analysis_data.get("final_summary")

            st.rerun()
