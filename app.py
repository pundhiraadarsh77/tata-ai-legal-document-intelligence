import os
import requests
import threading
import time
import streamlit as st

# ============================================================
# BACKEND URL
# ============================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Tata AI Legal Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM UI STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    .stApp {
        background-color: #f5f7fb;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1, h2, h3 {
        color: #102a43;
    }

    p {
        color: #486581;
    }

    /* -------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0b1f3a 0%,
            #12355b 100%
        );
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    [data-testid="stSidebar"] .stButton button {
        background-color: rgba(255, 255, 255, 0.10);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 10px;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.18);
        border-color: rgba(255, 255, 255, 0.35);
    }

    /* -------------------------------------------------------
       BRAND
    ------------------------------------------------------- */

    .brand-card {
        background: linear-gradient(
            135deg,
            #12355b,
            #1f5f8b
        );
        padding: 22px;
        border-radius: 16px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }

    .brand-title {
        font-size: 21px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .brand-subtitle {
        font-size: 12px;
        color: #d9e7f5;
        line-height: 1.5;
    }

    /* -------------------------------------------------------
       HERO HEADER
    ------------------------------------------------------- */

    .hero {
        background: linear-gradient(
            135deg,
            #0b1f3a 0%,
            #12355b 55%,
            #1f6f9f 100%
        );
        padding: 34px 38px;
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px rgba(16, 42, 67, 0.18);
    }

    .hero-title {
        color: #ffffff;
        font-size: 32px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #d9e7f5;
        font-size: 15px;
        line-height: 1.6;
        max-width: 850px;
    }

    .hero-badge {
        display: inline-block;
        margin-top: 15px;
        padding: 6px 12px;
        border-radius: 20px;
        background-color: rgba(255,255,255,0.12);
        color: #ffffff;
        font-size: 12px;
        border: 1px solid rgba(255,255,255,0.20);
    }

    /* -------------------------------------------------------
       SECTION TITLES
    ------------------------------------------------------- */

    .section-title {
        color: #102a43;
        font-size: 22px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .section-subtitle {
        color: #627d98;
        font-size: 13px;
        margin-bottom: 18px;
    }

    /* -------------------------------------------------------
       DOCUMENT CARD
    ------------------------------------------------------- */

    .document-card {
        background-color: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 15px;
        padding: 18px 20px;
        box-shadow: 0 5px 18px rgba(16,42,67,0.06);
        margin-bottom: 18px;
    }

    .document-name {
        font-size: 16px;
        font-weight: 700;
        color: #102a43;
    }

    .document-meta {
        font-size: 12px;
        color: #829ab1;
        margin-top: 5px;
    }

    /* -------------------------------------------------------
       UPLOAD CARD
    ------------------------------------------------------- */

    .upload-card {
        background-color: #ffffff;
        border: 2px dashed #9fb3c8;
        border-radius: 18px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
    }

    .upload-icon {
        font-size: 38px;
        margin-bottom: 5px;
    }

    .upload-title {
        color: #102a43;
        font-size: 20px;
        font-weight: 700;
    }

    .upload-description {
        color: #627d98;
        font-size: 13px;
    }

    /* -------------------------------------------------------
       INFO CARDS
    ------------------------------------------------------- */

    .info-card {
        background-color: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 14px;
        padding: 17px;
        min-height: 100px;
        box-shadow: 0 4px 15px rgba(16,42,67,0.05);
    }

    .info-label {
        color: #829ab1;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 700;
    }

    .info-value {
        color: #102a43;
        font-size: 18px;
        font-weight: 700;
        margin-top: 7px;
    }

    /* -------------------------------------------------------
       WORKFLOW
    ------------------------------------------------------- */

    .workflow-container {
        background-color: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 5px 18px rgba(16,42,67,0.06);
        margin: 15px 0 25px 0;
    }

    .workflow-title {
        color: #102a43;
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 17px;
    }

    .workflow-step {
        display: flex;
        align-items: center;
        margin-bottom: 11px;
        padding: 9px 12px;
        border-radius: 9px;
        background-color: #f7f9fc;
    }

    .workflow-step.completed {
        background-color: #edf9f1;
    }

    .workflow-step.active {
        background-color: #eaf3ff;
        border: 1px solid #9fc5ed;
    }

    .workflow-icon {
        width: 27px;
        height: 27px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-size: 13px;
        font-weight: 700;
        background-color: #d9e2ec;
        color: #486581;
    }

    .completed .workflow-icon {
        background-color: #37a66a;
        color: white;
    }

    .active .workflow-icon {
        background-color: #2680c2;
        color: white;
    }

    .workflow-name {
        font-size: 13px;
        color: #334e68;
        font-weight: 600;
    }

    /* -------------------------------------------------------
       RISK CARDS
    ------------------------------------------------------- */

    .risk-card {
        background-color: #ffffff;
        border-radius: 15px;
        border: 1px solid #e0e6ed;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 5px 18px rgba(16,42,67,0.06);
    }

    .risk-header {
        font-size: 17px;
        font-weight: 700;
        color: #102a43;
        margin-bottom: 10px;
    }

    .risk-severity {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        background-color: #fff3cd;
        color: #856404;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .risk-label {
        color: #829ab1;
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    .risk-value {
        color: #334e68;
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 10px;
    }

    /* -------------------------------------------------------
       HUMAN REVIEW
    ------------------------------------------------------- */

    .review-card {
        background: linear-gradient(
            135deg,
            #fffaf0,
            #fffdf8
        );
        border: 1px solid #f0d9a6;
        border-radius: 17px;
        padding: 22px;
        margin: 20px 0;
        box-shadow: 0 5px 18px rgba(16,42,67,0.05);
    }

    .review-title {
        color: #7c5a12;
        font-size: 20px;
        font-weight: 700;
    }

    /* -------------------------------------------------------
    FINAL SUMMARY
    ------------------------------------------------------- */

    .st-key-final_summary_content .stMarkdown p,
    .st-key-final_summary_content .stMarkdown li,
    .st-key-final_summary_content .stMarkdown span,
    .st-key-final_summary_content .stMarkdown strong,
    .st-key-final_summary_content .stMarkdown em,
    .st-key-final_summary_content .stMarkdown h1,
    .st-key-final_summary_content .stMarkdown h2,
    .st-key-final_summary_content .stMarkdown h3,
    .st-key-final_summary_content .stMarkdown h4,
    .st-key-final_summary_content .stMarkdown h5,
    .st-key-final_summary_content .stMarkdown h6,
    .st-key-final_summary_content .stMarkdown td,
    .st-key-final_summary_content .stMarkdown th {
        color: #1f2937 !important;
    }

    .st-key-final_summary_content .stMarkdown table {
        color: #1f2937 !important;
    }

    .st-key-final_summary_content .stMarkdown table thead th,
    .st-key-final_summary_content .stMarkdown table tbody td {
        color: #1f2937 !important;
    }

    /* -------------------------------------------------------
       QA AREA
    ------------------------------------------------------- */

    .qa-header {
        background: linear-gradient(
            135deg,
            #eef6ff,
            #f7fbff
        );
        border: 1px solid #c9dff2;
        border-radius: 15px;
        padding: 18px 20px;
        margin-bottom: 15px;
    }

    .qa-title {
        color: #12355b;
        font-size: 19px;
        font-weight: 700;
    }

    /* Document Q&A - force readable dark text */
    .stChatMessage p,
    .stChatMessage li,
    .stChatMessage span,
    .stChatMessage strong,
    .stChatMessage em,
    .stChatMessage td,
    .stChatMessage th {
        color: #1f2937 !important;
    }

    /* -------------------------------------------------------
       STREAMLIT BUTTONS
    ------------------------------------------------------- */

    .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        min-height: 45px !important;
    }

    .stButton > button p {
        color: #ffffff !important;
    }

    .stButton > button span {
        color: #ffffff !important;
    }

    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }

    .stButton > button:hover p,
    .stButton > button:hover span {
        color: #ffffff !important;
    }

    /* -------------------------------------------------------
       INPUTS
    ------------------------------------------------------- */

    .stTextArea textarea,
    .stTextInput input {
        border-radius: 10px;
    }

    /* -------------------------------------------------------
       DIVIDER
    ------------------------------------------------------- */

    hr {
        border-color: #d9e2ec;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_chat_title(filename):
    """
    Creates a clean chat title from the uploaded document filename.
    """

    title = os.path.splitext(filename)[0]
    title = title.replace("_", " ").replace("-", " ")

    return title.title()

def display_workflow(
    progress_stages,
    current_stage,
    title="Analysis Workflow"
):
    """
    Displays the existing backend workflow as a visual UI.
    This function only changes how the workflow is displayed.
    """

    current_index = -1

    for index, (stage_key, _) in enumerate(progress_stages):

        if stage_key == current_stage:
            current_index = index
            break

    st.markdown(
    f"""
        <h3 style="
            color: #0f172a;
            margin-bottom: 20px;
            font-weight: 700;
        ">
            ⚙️ {title}
        </h3>
        """,
        unsafe_allow_html=True
    )

    for index, (_, stage_name) in enumerate(progress_stages):

        if index < current_index:

            icon = "🟢"
            status = "Completed"

        elif index == current_index:

            icon = "🔵"
            status = "In Progress"

        else:

            icon = "⚪"
            status = "Pending"

        col1, col2, col3 = st.columns(
            [0.08, 0.62, 0.30]
        )

        with col1:

            st.markdown(
                f"### {icon}"
            )

        with col2:

            st.markdown(
                f"**{stage_name}**"
            )

        with col3:

            if status == "Completed":

                st.success(
                    status,
                    icon="✅"
                )

            elif status == "In Progress":

                st.info(
                    status,
                    icon="🔵"
                )

            else:

                st.caption(
                    status
                )

        st.divider()

def display_document_card(document):
    """
    Displays uploaded document information.
    """

    st.markdown(
        f"""
        <div class="document-card">
        <div class="document-name">
        📄 {document["name"]}
        </div>
        <div class="document-meta">
        Legal document selected for AI-assisted review
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_risk_card(index, risk):
    """
    Displays one legal risk in a structured card.
    """

    risk_type = risk.get("risk_type", "N/A")
    severity = risk.get("severity", "N/A")
    affected_clause = risk.get("affected_clause", "N/A")
    rationale = risk.get("rationale", "N/A")
    source_location = risk.get("source_location", "N/A")
    recommended_action = risk.get("recommended_action", "N/A")
    confidence = risk.get("confidence", 0)

    try:
        confidence_text = f"{float(confidence):.0f}%"
    except Exception:
        confidence_text = str(confidence)

    st.markdown(
        f"""
        <div class="risk-card">
        <div class="risk-header">
        ⚠️ Risk {index}: {risk_type}
        </div>
        <div class="risk-severity">
        Severity: {severity}
        </div>
        <div class="risk-label">
        Affected Clause
        </div>
        <div class="risk-value">
        {affected_clause}
        </div>
        <div class="risk-label">
        Rationale
        </div>
        <div class="risk-value">
        {rationale}
        </div>
        <div class="risk-label">
        Evidence / Source
        </div>
        <div class="risk-value">
        {source_location}
        </div>
        <div class="risk-label">
        Recommended Action
        </div>
        <div class="risk-value">
        {recommended_action}
        </div>
        <div class="risk-label">
        Confidence
        </div>
        <div class="risk-value">
        {confidence_text}
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def extract_summary_text(final_summary):
    """
    Converts the final summary into displayable text.
    """

    if isinstance(final_summary, list):

        final_summary_text = ""

        for block in final_summary:

            if (
                isinstance(block, dict)
                and block.get("type") == "text"
            ):
                final_summary_text += block.get("text", "")

            elif isinstance(block, str):
                final_summary_text += block

        return final_summary_text

    return final_summary

# ============================================================
# SESSION MANAGEMENT
# ============================================================

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = 1

if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "thread_ids" not in st.session_state:
    st.session_state.thread_ids = {}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-card">
        <div class="brand-title">
        ⚖️ Tata AI Assistant
        </div>
        <div class="brand-subtitle">
        Legal Document Intelligence
        <br>
        AI-assisted first-pass legal review
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    new_chat = st.button(
        "➕  New Chat",
        use_container_width=True
    )

    if new_chat:

        st.session_state.current_session_id += 1

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

    st.markdown(
        """
        <div style="
        font-size:13px;
        font-weight:700;
        color:#d9e7f5;
        margin-bottom:10px;
        ">
        🗂️ CHAT HISTORY
        </div>
        """,
        unsafe_allow_html=True
    )

    if len(st.session_state.sessions) == 0:

        st.caption("No previous conversations")

    else:

        for session_id, session_data in st.session_state.sessions.items():

            if st.button(
                session_data["title"],
                key=f"session_{session_id}",
                use_container_width=True
            ):

                st.session_state.current_session_id = session_id

                st.rerun()

    st.divider()

    st.caption("Tata AI Legal Document Intelligence")

# ============================================================
# CURRENT SESSION
# ============================================================

current_session = st.session_state.sessions.get(
    st.session_state.current_session_id
)

# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
    <div style="background:#0f172a; color:white; padding:30px; border-radius:15px;">
    <h1>
    Tata AI Legal Document Intelligence
    </h1>
    <p>
    AI-assisted legal document review
    </p>
    <p style="font-size:13px; color:#cbd5e1;">
    🔐 Document Intelligence  •  🤖 AI Review  •  👤 Human-in-the-Loop
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# EXISTING CHAT SESSION
# ============================================================

if (
    current_session is not None
    and current_session["documents"]
):

    # --------------------------------------------------------
    # CURRENT DOCUMENT
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-title">
        📄 Current Document
        </div>
        <div class="section-subtitle">
        Document selected for legal analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    for document in current_session["documents"]:
        display_document_card(document)

    # --------------------------------------------------------
    # DOCUMENT INFORMATION
    # --------------------------------------------------------

    document = current_session["documents"][0]

    analysis_result = current_session.get(
        "analysis_result"
    ) or {}

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            f"""
            <div class="info-card">
            <div class="info-label">
            Document ID
            </div>
            <div class="info-value">
            {document.get("document_id", "N/A")}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        document_type = analysis_result.get(
            "document_type",
            "Pending"
        )

        st.markdown(
            f"""
            <div class="info-card">
            <div class="info-label">
            Document Type
            </div>
            <div class="info-value">
            {document_type}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        review_status = current_session.get(
            "human_review_status"
        )

        if review_status == "awaiting_human_review":
            status_text = "Human Review"
        elif current_session.get("final_summary") is not None:
            status_text = "Finalized"
        else:
            status_text = "Analysis"

        st.markdown(
            f"""
            <div class="info-card">
            <div class="info-label">
            Status
            </div>
            <div class="info-value">
            {status_text}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # --------------------------------------------------------
    # PREVIOUS USER REQUEST
    # --------------------------------------------------------

    if current_session["user_query"]:

        st.markdown(
            """
            <div class="section-title">
            💬 Review Request
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.chat_message("user"):
            st.write(current_session["user_query"])

    else:

        with st.chat_message("user"):
            st.write(
                "Perform a comprehensive legal review of this document."
            )

    # ========================================================
    # HUMAN REVIEW UI
    # ========================================================

    if current_session["human_review_request"] is not None:

        review_request = current_session[
            "human_review_request"
        ]

        # ----------------------------------------------------
        # LEGAL RISK ANALYSIS
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="section-title">
            ⚠️ Legal Risk Analysis
            </div>
            <div class="section-subtitle">
            AI-identified legal and compliance risks requiring review
            </div>
            """,
            unsafe_allow_html=True
        )

        analysis_result = current_session.get(
            "analysis_result"
        ) or {}

        risk_flags = analysis_result.get(
            "risk_flags",
            []
        )

        if risk_flags:

            for index, risk in enumerate(
                risk_flags,
                start=1
            ):
                display_risk_card(
                    index,
                    risk
                )

        else:

            st.success(
                "🟢 No supported legal or compliance risks "
                "were identified in the analyzed document."
            )

            st.info(
                "Human review is still required before finalization."
            )

        # ----------------------------------------------------
        # HUMAN REVIEW
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="review-card">
            <div class="review-title">
            👤 Human Review Required
            </div>
            <p style="color:#7c5a12; margin-top:8px;">
            The AI legal review is paused and requires
            human review before the document can be finalized.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

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
            format_func=lambda option: option.replace(
                "_",
                " "
            ).title(),
            key=f"review_{st.session_state.current_session_id}"
        )

        submit_review = st.button(
            "✓  Submit Review Decision",
            type="primary"
        )

        if submit_review:

            thread_id = st.session_state.thread_ids[
                st.session_state.current_session_id
            ]

            document_id = current_session[
                "documents"
            ][0]["document_id"]

            review_payload = {
                "decision": selected_review,
                "thread_id": thread_id
            }

            # ------------------------------------------------
            # RE-ANALYSIS PROGRESS STAGES
            # ------------------------------------------------

            if selected_review == "wrong_classification":

                review_progress_stages = [
                    (
                        "document_classification",
                        "Document Classification"
                    ),
                    (
                        "legal_guidance_retrieval",
                        "Legal Guidance Retrieval"
                    ),
                    (
                        "legal_agent_review",
                        "Legal Agent Review"
                    ),
                    (
                        "risk_analysis",
                        "Risk Analysis"
                    )
                ]

            elif selected_review == "re-analyze":

                review_progress_stages = [
                    (
                        "legal_guidance_retrieval",
                        "Legal Guidance Retrieval"
                    ),
                    (
                        "legal_agent_review",
                        "Legal Agent Review"
                    ),
                    (
                        "risk_analysis",
                        "Risk Analysis"
                    )
                ]

            else:

                review_progress_stages = []

            # ------------------------------------------------
            # HANDLE RE-ANALYSIS
            # ------------------------------------------------

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

                        review_result_holder[
                            "response"
                        ] = response

                    except Exception as error:

                        review_result_holder[
                            "error"
                        ] = error


                review_thread = threading.Thread(
                    target=submit_review_request
                )

                review_thread.start()

                progress_placeholder = st.empty()

                with st.spinner(
                    "Re-analyzing document..."
                ):

                    while review_thread.is_alive():

                        try:
                            
                            progress_response = requests.get(
                                f"{BACKEND_URL}/analysis-progress/{thread_id}",
                                timeout=5
                            )

                            if progress_response.status_code == 200:

                                progress_data = progress_response.json()

                                current_stage = progress_data.get(
                                    "stage",
                                    "starting"
                                )

                                progress_placeholder.empty()

                                with progress_placeholder.container():

                                    display_workflow(
                                        review_progress_stages,
                                        current_stage,
                                        "Re-analysis Workflow"
                                    )

                        except Exception:
                            
                            pass

                        time.sleep(0.5)

                review_thread.join()

                if "error" in review_result_holder:

                    st.error(
                        "❌ Problem with the LLM. "
                        "Please try again after some time."
                    )

                    st.stop()

                review_response = (
                    review_result_holder["response"]
                )

                # --------------------------------------------
                # FINAL RE-ANALYSIS PROGRESS
                # --------------------------------------------

                try:

                    final_progress_response = requests.get(
                        f"{BACKEND_URL}/analysis-progress/{thread_id}"
                    )

                    final_progress_response.raise_for_status()

                    final_stage = (
                        final_progress_response
                        .json()
                        .get(
                            "stage",
                            "starting"
                        )
                    )

                except Exception:

                    final_stage = "starting"


                if final_stage == "human_review_required":
                    
                    progress_placeholder.empty()

                    with progress_placeholder.container():
                    
                        display_workflow(
                            review_progress_stages,
                            "risk_analysis",
                            "Re-analysis Workflow"
                        )

                    st.info(
                        "👤 Re-analysis completed. "
                        "Human review is required again."
                    )

            # ------------------------------------------------
            # APPROVE / ESCALATE
            # ------------------------------------------------

            else:

                try:

                    with st.spinner(
                        "Submitting review..."
                    ):

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

            # ------------------------------------------------
            # SAVE REVIEW RESULT
            # ------------------------------------------------

            result = review_response.json()

            current_session = st.session_state.sessions[
                st.session_state.current_session_id
            ]

            # Save the complete latest analysis result.
            # This includes the latest risk_flags returned by the backend.
            current_session["analysis_result"] = result

            new_vector_store_path = result.get(
                "document_vector_store_path"
            )

            if new_vector_store_path:

                current_session[
                    "document_vector_store_path"
                ] = new_vector_store_path

            current_session[
                "human_review_status"
            ] = result.get(
                "human_review_status"
            )

            if result.get("human_review_status") in [
                "awaiting_human_review",
                "pending"
            ]:

                current_session[
                    "human_review_request"
                ] = result.get(
                    "human_review_request"
                )

                # Keep the latest risk analysis available
                # when the page reruns for another human review.
                current_session[
                    "analysis_result"
                ] = {
                    **result,
                    "risk_flags": result.get(
                        "risk_flags",
                        []
                    )
                }

            else:

                current_session[
                    "human_review_request"
                ] = None

                if result.get("final_summary"):

                    current_session[
                        "final_summary"
                    ] = result["final_summary"]

            st.rerun()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    elif current_session["final_summary"] is not None:

        st.success(
            "✅ Document review finalized."
        )

        st.markdown(
            """
            <div class="section-title">
            📁 Final Legal Document Summary
            </div>
            <div class="section-subtitle">
            Consolidated output from the AI-assisted legal review
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(key="final_summary_content"):
            final_summary_text = extract_summary_text(
                current_session["final_summary"]
            )

            st.markdown(final_summary_text)

        # ----------------------------------------------------
        # DOCUMENT Q&A
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="qa-header">
            <div class="qa-title">
            💬 Ask About This Document
            </div>
            <div style="
            color:#627d98;
            font-size:13px;
            margin-top:5px;
            ">
            Ask follow-up questions using the analyzed
            document as the knowledge source.
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if "document_qa_history" not in current_session:

            current_session[
                "document_qa_history"
            ] = []

        # ----------------------------------------------------
        # PREVIOUS DOCUMENT Q&A
        # ----------------------------------------------------

        for qa in current_session[
            "document_qa_history"
        ]:

            with st.chat_message("user"):
                st.write(
                    qa["question"]
                )

            with st.chat_message("assistant"):
                st.write(
                    qa["answer"]
                )

        user_question = st.text_input(
            "Ask a follow-up question:",
            placeholder="Example: What is the termination period in this agreement?"
        )

        if st.button(
            "🔍 Ask Document",
            key="document_qa_button",
            type="primary"
        ):

            if not user_question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                try:

                    with st.spinner(
                        "Searching the document..."
                    ):

                        response = requests.post(
                            f"{BACKEND_URL}/document-qa",
                            json={
                                "document_vector_store_path":
                                    current_session[
                                        "document_vector_store_path"
                                    ],
                                "user_question":
                                    user_question.strip()
                            }
                        )

                        response.raise_for_status()

                        answer = response.json()["answer"]

                        current_session[
                            "document_qa_history"
                        ].append(
                            {
                                "question":
                                    user_question.strip(),
                                "answer":
                                    answer
                            }
                        )

                        st.rerun()

                except Exception:

                    st.error(
                        "❌ Problem with the LLM. "
                        "Please try again after some time."
                    )

    # ========================================================
    # ANALYSIS NOT COMPLETED
    # ========================================================

    else:

        st.markdown(
            """
            <div class="section-title">
            🔄 Document Analysis
            </div>
            """,
            unsafe_allow_html=True
        )

        st.info(
            "Document analysis has not been completed yet."
        )

# ============================================================
# NEW CHAT / DOCUMENT UPLOAD
# ============================================================

else:

    # --------------------------------------------------------
    # UPLOAD HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-title">
        📄 Start a New Legal Document Review
        </div>
        <div class="section-subtitle">
        Upload a legal document and provide the type of
        review you want the AI assistant to perform.
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # UPLOAD CARD
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="upload-card">
        <div class="upload-icon">
        📂
        </div>
        <div class="upload-title">
        Upload your legal document
        </div>
        <div class="upload-description">
        PDF, DOCX, PNG, JPG, JPEG or ODT
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=[
            "pdf",
            "docx",
            "png",
            "jpg",
            "jpeg",
            "odt"
        ],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:

        st.success(
            f"✓ Document selected: {uploaded_file.name}"
        )

        st.markdown(
            """
            <div class="section-title">
            📝 Review Request
            </div>
            <div class="section-subtitle">
            Tell the AI assistant what you want it to focus on.
            </div>
            """,
            unsafe_allow_html=True
        )

        user_query = st.text_area(
            "Review request",
            placeholder=(
                "Example: Review this document for legal "
                "and compliance risks."
            ),
            height=110,
            label_visibility="collapsed"
        )

        analyze_button = st.button(
            "🔍  Analyze Document",
            type="primary",
            use_container_width=True
        )

        # ====================================================
        # START ANALYSIS
        # ====================================================

        if analyze_button:

            # ------------------------------------------------
            # UPLOAD DOCUMENT TO FASTAPI
            # ------------------------------------------------

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

            if response.status_code != 200:

                st.error(
                    "❌ Failed to upload document to backend."
                )

                st.stop()

            document_data = response.json()

            document_id = document_data.get(
                "id"
            )

            document_path = document_data.get(
                "file_path"
            )

            file_name = document_data.get(
                "file_name",
                uploaded_file.name
            )

            st.success(
                "✓ Document uploaded successfully."
            )

            # ------------------------------------------------
            # CREATE CHAT TITLE
            # ------------------------------------------------

            chat_title = create_chat_title(
                file_name
            )

            # ------------------------------------------------
            # SAVE SESSION DATA
            # ------------------------------------------------

            st.session_state.sessions[
                st.session_state.current_session_id
            ] = {

                "title":
                    chat_title,

                "documents": [
                    {
                        "document_id":
                            document_id,

                        "name":
                            file_name,

                        "path":
                            document_path
                    }
                ],

                "messages": [
                    {
                        "role":
                            "user",

                        "content":
                            user_query
                    }
                ],

                "user_query":
                    user_query,

                "analysis_result":
                    None,

                "human_review_status":
                    None,

                "final_summary":
                    None,

                "human_review_request":
                    None,

                "document_qa_history":
                    []
            }

            # ------------------------------------------------
            # CREATE LANGGRAPH THREAD ID
            # ------------------------------------------------

            if (
                st.session_state.current_session_id
                not in st.session_state.thread_ids
            ):

                st.session_state.thread_ids[
                    st.session_state.current_session_id
                ] = (
                    "legal-review-"
                    + str(
                        st.session_state.current_session_id
                    )
                )

            thread_id = (
                st.session_state.thread_ids[
                    st.session_state.current_session_id
                ]
            )

            # ------------------------------------------------
            # ANALYSIS PAYLOAD
            # ------------------------------------------------

            analysis_payload = {

                "document_id":
                    document_id,

                "document_path":
                    document_path,

                "user_query":
                    user_query.strip(),

                "thread_id":
                    thread_id
            }

            # ------------------------------------------------
            # RUN ANALYSIS IN BACKGROUND
            # ------------------------------------------------

            analysis_result_holder = {}

            def run_analysis_request():

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/run-analysis",
                        json=analysis_payload
                    )

                    response.raise_for_status()

                    analysis_result_holder[
                        "response"
                    ] = response

                except Exception as error:

                    analysis_result_holder[
                        "error"
                    ] = error

            analysis_thread = threading.Thread(
                target=run_analysis_request
            )

            analysis_thread.start()

            # ------------------------------------------------
            # ANALYSIS WORKFLOW
            # ------------------------------------------------

            progress_stages = [

                (
                    "document_parsing",
                    "Document Parsing"
                ),

                (
                    "clause_extraction",
                    "Clause Extraction"
                ),

                (
                    "sufficiency_check",
                    "Sufficiency Check"
                ),

                (
                    "document_classification",
                    "Document Classification"
                ),

                (
                    "legal_guidance_retrieval",
                    "Legal Guidance Retrieval"
                ),

                (
                    "legal_agent_review",
                    "Legal Agent Review"
                ),

                (
                    "risk_analysis",
                    "Risk Analysis"
                )
            ]

            progress_placeholder = st.empty()

            # ------------------------------------------------
            # POLL ANALYSIS PROGRESS
            # ------------------------------------------------

            with st.spinner(
                "Analyzing document..."
            ):

                while analysis_thread.is_alive():

                    try:

                        progress_response = requests.get(
                            f"{BACKEND_URL}/analysis-progress/{thread_id}"
                        )

                        progress_response.raise_for_status()

                        current_stage = (
                            progress_response
                            .json()
                            .get(
                                "stage",
                                "starting"
                            )
                        )

                    except Exception:

                        current_stage = "starting"

                    progress_placeholder.empty()

                    with progress_placeholder.container():

                        display_workflow(
                            progress_stages,
                            current_stage,
                            "AI Legal Review Workflow"
                        )

                    time.sleep(0.5)

            # ------------------------------------------------
            # WAIT FOR FINAL RESPONSE
            # ------------------------------------------------

            analysis_thread.join()

            # ------------------------------------------------
            # HANDLE ERROR
            # ------------------------------------------------

            if "error" in analysis_result_holder:

                st.error(
                    "❌ Problem with the LLM. "
                    "Please try again after some time."
                )

                st.stop()

            analysis_response = (
                analysis_result_holder[
                    "response"
                ]
            )

            # ------------------------------------------------
            # FINAL PROGRESS
            # ------------------------------------------------

            try:

                final_progress_response = requests.get(
                    f"{BACKEND_URL}/analysis-progress/{thread_id}"
                )

                final_progress_response.raise_for_status()

                final_stage = (
                    final_progress_response
                    .json()
                    .get(
                        "stage",
                        "starting"
                    )
                )

            except Exception:

                final_stage = "starting"

            if final_stage == "human_review_required":

                progress_placeholder.empty()

                with progress_placeholder.container():

                    display_workflow(
                        progress_stages,
                        "risk_analysis",
                        "AI Legal Review Workflow"
                    )

                st.info(
                    "👤 AI analysis completed. "
                    "Human review is required before finalization."
                )

            # ------------------------------------------------
            # ANALYSIS RESULT
            # ------------------------------------------------

            analysis_data = (
                analysis_response.json()
            )

            st.session_state.sessions[
                st.session_state.current_session_id
            ][
                "analysis_result"
            ] = analysis_data

            document_vector_store_path = (
                analysis_data.get(
                    "document_vector_store_path"
                )
            )

            if document_vector_store_path:

                st.session_state.sessions[
                    st.session_state.current_session_id
                ][
                    "document_vector_store_path"
                ] = document_vector_store_path

            if analysis_data.get(
                "human_review_status"
            ) in [
                "awaiting_human_review",
                "pending"
            ]:

                st.session_state.sessions[
                    st.session_state.current_session_id
                ][
                    "human_review_request"
                ] = analysis_data.get(
                    "human_review_request"
                )

            else:

                st.session_state.sessions[
                    st.session_state.current_session_id
                ][
                    "final_summary"
                ] = analysis_data.get(
                    "final_summary"
                )

            st.rerun()