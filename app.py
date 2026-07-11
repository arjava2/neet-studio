import streamlit as st
import os
import json
from generator import (
    setup_ai, scan_books, get_chapter_name, generate_questions,
    verify_answer, humanize_question
)
from image_search import (
    extract_all_books, get_extracted_books, get_book_images,
    get_all_extracted_count, copy_image_to_output,
    save_uploaded_pdf, delete_pdf
)

st.set_page_config(
    page_title="NEET Studio",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp {
        background-color: #0a0a0a;
        color: #ededed;
    }
    
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: #ededed !important;
    }
    
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    
    /* Header bar with sidebar toggle */
    header[data-testid="stHeader"] {
        background-color: rgba(10, 10, 10, 0.95) !important;
        backdrop-filter: blur(10px);
        visibility: visible !important;
        height: auto !important;
        border-bottom: 1px solid #1f1f1f;
    }
    
    /* Sidebar toggle button - always visible */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        top: 12px !important;
        left: 12px !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.5) !important;
        z-index: 999999 !important;
        border: none !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] button {
        color: white !important;
        background: transparent !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] svg {
        color: white !important;
        fill: white !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        [data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            visibility: visible !important;
            position: fixed !important;
            top: 10px !important;
            left: 10px !important;
            padding: 8px 12px !important;
        }
        
        .brand-title { font-size: 20px !important; }
        h1 { font-size: 24px !important; }
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 1px solid #1f1f1f !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }
    
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #141414 !important;
        color: #ededed !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    .stSelectbox > div > div {
        background-color: #141414 !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
    }
    
    .stButton > button {
        background-color: #1a1a1a !important;
        color: #ededed !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #252525 !important;
        border-color: #3a3a3a !important;
        transform: translateY(-1px);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-2px);
    }
    
    .stDownloadButton > button {
        background-color: #1a1a1a !important;
        color: #ededed !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #141414 0%, #1a1a1a 100%) !important;
        border: 1px solid #262626 !important;
        border-radius: 10px !important;
        padding: 16px !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a1a1a1 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    [data-testid="stMetricValue"] {
        color: #ededed !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    .streamlit-expanderHeader {
        background-color: #141414 !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
        color: #ededed !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #6366f1 !important;
        background-color: #1a1a1a !important;
    }
    
    .streamlit-expanderContent {
        background-color: #0f0f0f !important;
        border: 1px solid #262626 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 20px !important;
    }
    
    .stAlert, div[data-baseweb="notification"] {
        background-color: #141414 !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border-color: #10b981 !important;
        color: #10b981 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border-color: #ef4444 !important;
        color: #ef4444 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%) !important;
        border-color: #f59e0b !important;
        color: #f59e0b !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%) !important;
        border-color: #6366f1 !important;
        color: #a5b4fc !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #262626 !important;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #737373 !important;
        font-weight: 500 !important;
        padding: 12px 20px !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #ededed !important;
        border-bottom: 2px solid #6366f1 !important;
        background-color: rgba(99, 102, 241, 0.05) !important;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
    }
    
    hr {
        border-color: #1f1f1f !important;
        margin: 24px 0 !important;
    }
    
    code {
        background-color: #1a1a1a !important;
        color: #a5b4fc !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0a0a0a; }
    ::-webkit-scrollbar-thumb { background: #262626; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }
    
    .stImage img {
        border-radius: 8px !important;
        border: 1px solid #262626 !important;
    }
    
    .brand-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .brand-tag {
        font-size: 12px;
        color: #737373;
        margin-top: -4px;
    }
    
    .section-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #737373;
        margin-bottom: 10px;
    }
    
    .info-card {
        background: linear-gradient(135deg, #141414 0%, #1a1a1a 100%);
        border: 1px solid #262626;
        border-radius: 10px;
        padding: 20px;
    }
    
    .info-row {
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: 12px;
        padding: 6px 0;
        font-size: 14px;
        border-bottom: 1px solid #1f1f1f;
    }
    
    .info-row:last-child { border-bottom: none; }
    .info-label { color: #737373; font-weight: 500; }
    .info-value { color: #ededed; font-weight: 500; }
    
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
    }
    
    .status-offline {
        background: rgba(115, 115, 115, 0.1);
        border: 1px solid rgba(115, 115, 115, 0.3);
        color: #737373;
    }
    
    .status-dot {
        width: 6px; height: 6px; border-radius: 50%;
    }
    
    .pulse-dot {
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.5); }
        50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    }
    
    .option-row {
        padding: 12px 16px;
        margin: 6px 0;
        background: #141414;
        border: 1px solid #262626;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .option-correct {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-color: #10b981;
    }
    
    .option-marker {
        width: 24px; height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
    }
    
    .marker-correct { background: #10b981; color: white; }
    .marker-normal { background: #262626; color: #a1a1a1; }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 6px;
    }
    
    .badge-easy { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .badge-medium { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .badge-hard { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .badge-verified { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #141414 0%, #1a1a1a 100%);
        border: 1px dashed #262626;
        border-radius: 12px;
    }
    
    .stFileUploader > div {
        background-color: #141414 !important;
        border: 2px dashed #6366f1 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    .stFileUploader label {
        color: #ededed !important;
    }
</style>
""", unsafe_allow_html=True)

if "generated" not in st.session_state:
    st.session_state.generated = None
if "ai_ready" not in st.session_state:
    st.session_state.ai_ready = False
if "verify_results" not in st.session_state:
    st.session_state.verify_results = {}

with st.sidebar:
    st.markdown('<div class="brand-title">◆ NEET Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tag">AI question generation</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)
    
    api_key = st.text_input(
        "API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        placeholder="Paste your Gemini API key",
        label_visibility="collapsed"
    )
    
    if st.button("Connect", type="primary", use_container_width=True):
        if api_key:
            try:
                setup_ai(api_key)
                st.session_state.ai_ready = True
                st.success("Connected")
            except Exception as e:
                st.error("Failed")
        else:
            st.error("Key required")
    
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    
    if st.session_state.ai_ready:
        st.markdown(
            '<div class="status-pill status-online"><span class="status-dot pulse-dot" style="background: #10b981;"></span>System Online</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-pill status-offline"><span class="status-dot" style="background: #737373;"></span>Offline</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">Library</div>', unsafe_allow_html=True)
    
    books = scan_books()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Biology", len(books['biology']))
        st.metric("Chemistry", len(books['chemistry']))
    with c2:
        st.metric("Physics", len(books['physics']))
        st.metric("PYQs", len(books['pyq']))
    
    total = sum(len(v) for v in books.values())
    st.markdown(f'<div style="text-align: center; margin-top: 12px; color: #737373; font-size: 12px;">Total: <span style="color: #ededed; font-weight: 600;">{total}</span> files indexed</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">Resources</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: #a1a1a1;">🔑 <a href="https://aistudio.google.com/apikey" style="color: #a5b4fc; text-decoration: none;" target="_blank">Get Free API Key</a></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: #a1a1a1; margin-top: 4px;">📖 <a href="https://ncert.nic.in/textbook.php" style="color: #a5b4fc; text-decoration: none;" target="_blank">Download NCERT PDFs</a></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: #a1a1a1; margin-top: 4px;">💡 Free tier: 1500 req/day</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 12px; color: #525252; margin-top: 16px;">Version 6.0</div>', unsafe_allow_html=True)

st.markdown("# NEET Question Studio")
st.markdown('<div style="color: #a1a1a1; font-size: 15px; margin-top: -8px;">Generate NEET-level questions from NCERT PDFs using AI</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

if not st.session_state.ai_ready:
    st.info("👋 Welcome! Please add your free Gemini API key in the sidebar to get started. Tap the ▶ button on top-left if sidebar is hidden.")
    
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="info-card">
            <div style="font-size: 28px; margin-bottom: 8px;">⚡</div>
            <div style="font-weight: 600; font-size: 15px; margin-bottom: 4px;">Fast Generation</div>
            <div style="color: #a1a1a1; font-size: 13px;">Generate up to 30 questions in under a minute</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <div style="font-size: 28px; margin-bottom: 8px;">🎯</div>
            <div style="font-weight: 600; font-size: 15px; margin-bottom: 4px;">Answer Verification</div>
            <div style="color: #a1a1a1; font-size: 13px;">Built-in AI verification for accuracy check</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="info-card">
            <div style="font-size: 28px; margin-bottom: 8px;">🌐</div>
            <div style="font-weight: 600; font-size: 15px; margin-bottom: 4px;">Bilingual Output</div>
            <div style="color: #a1a1a1; font-size: 13px;">Both English and Hindi versions included</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    st.markdown("### 🚀 Quick Start Guide")
    st.markdown("""
    1. **Get API Key** - Click the link in sidebar to get your free Gemini key
    2. **Connect** - Paste key and click Connect button
    3. **Select Chapter** - Choose from pre-loaded NCERT library
    4. **Generate** - Get NEET-level questions instantly!
    """)
    
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["✨ Generate", "📁 Upload PDFs", "📚 History", "🖼️ Diagrams"])

with tab1:
    if sum(len(v) for v in books.values()) == 0:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 48px; margin-bottom: 16px;">📚</div>
            <h3 style="margin: 0 0 8px 0;">No PDFs uploaded yet</h3>
            <p style="color: #a1a1a1; margin: 0;">Go to the <strong>Upload PDFs</strong> tab to add your NCERT books</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown('<div class="section-label">Parameters</div>', unsafe_allow_html=True)
        
        available_subjects = [s.title() for s in ["Biology", "Physics", "Chemistry"] if books[s.lower()]]
        
        if not available_subjects:
            st.error("No subject PDFs available. Please upload PDFs first.")
            st.stop()
        
        subject = st.selectbox("Subject", available_subjects)
        sub_key = subject.lower()
        pdfs = books[sub_key]
        
        chapter_options = [f"{i+1}. {get_chapter_name(p)}" for i, p in enumerate(pdfs)]
        chapter_choice = st.selectbox("Chapter", chapter_options)
        chapter_idx = int(chapter_choice.split(".")[0]) - 1
        pdf_file = pdfs[chapter_idx]
        chapter_name = get_chapter_name(pdf_file)
        
        topic = st.text_input("Topic", placeholder="e.g., photosynthesis (optional)")
        
        qtype = st.selectbox("Question Type", [
            "General MCQ", "Assertion & Reason", "Statement Based",
            "Match the Following", "Image Question", "Graphical"
        ])
        
        ca, cb = st.columns(2)
        with ca:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        with cb:
            num_q = st.number_input("Count", min_value=1, max_value=30, value=10)
        
        use_pyq = False
        if books["pyq"] and topic:
            use_pyq = st.checkbox(f"Include PYQ references ({len(books['pyq'])})")
        
        if qtype in ["Image Question", "Graphical"]:
            st.info("💡 Use the Diagrams tab to browse NCERT figures")
    
    with col_right:
        st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
        
        diff_badge = f'<span class="badge badge-{difficulty.lower()}">{difficulty}</span>'
        
        st.markdown(f"""
        <div class="info-card">
            <div style="margin-bottom: 16px;">{diff_badge}<span class="badge badge-verified">{qtype}</span></div>
            <div class="info-row"><div class="info-label">Subject</div><div class="info-value">{subject}</div></div>
            <div class="info-row"><div class="info-label">Chapter</div><div class="info-value">{chapter_name}</div></div>
            <div class="info-row"><div class="info-label">Topic</div><div class="info-value">{topic if topic else 'Full chapter'}</div></div>
            <div class="info-row"><div class="info-label">Quantity</div><div class="info-value">{num_q} questions</div></div>
            <div class="info-row"><div class="info-label">PYQ Ref</div><div class="info-value">{'Yes' if use_pyq else 'No'}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        
        if st.button("✨ Generate Questions", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is crafting your questions..."):
                result = generate_questions(pdf_file, chapter_name, qtype, difficulty, num_q, topic, use_pyq)
            
            if result.get("success"):
                st.session_state.generated = result["data"]
                st.session_state.verify_results = {}
                st.success(f"✅ Generated {result['count']} questions successfully")
            else:
                st.error(f"❌ {result.get('error')}")
    
    if st.session_state.generated:
        st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        questions = st.session_state.generated.get("questions", [])
        
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown(f"### Generated Results")
            st.caption(f"{len(questions)} questions ready. Verify each before using on TrackPrep.")
        with col_h2:
            verified_count = sum(1 for i in range(len(questions)) if st.session_state.verify_results.get(i, {}).get("matches"))
            st.metric("Verified", f"{verified_count}/{len(questions)}")
        
        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        
        for i, q in enumerate(questions):
            verify_data = st.session_state.verify_results.get(i, {})
            
            status_icon = ""
            if verify_data.get("matches") and verify_data.get("confidence", 0) >= 80:
                status_icon = "✅ "
            elif verify_data.get("verified") and not verify_data.get("matches"):
                status_icon = "⚠️ "
            
            with st.expander(f"{status_icon}Question {i+1}  ·  {q.get('question_english', '')[:75]}..."):
                
                lt1, lt2 = st.tabs(["🇬🇧 English", "🇮🇳 हिन्दी"])
                
                with lt1:
                    st.markdown(f"**{q.get('question_english', '')}**")
                    st.markdown("")
                    
                    correct = q.get('correct_answer', '')
                    options = ['A', 'B', 'C', 'D']
                    keys = ['option_a_english', 'option_b_english', 'option_c_english', 'option_d_english']
                    
                    for opt, key in zip(options, keys):
                        is_correct = opt == correct
                        row_class = "option-row option-correct" if is_correct else "option-row"
                        marker_class = "option-marker marker-correct" if is_correct else "option-marker marker-normal"
                        st.markdown(
                            f'<div class="{row_class}">'
                            f'<span class="{marker_class}">{opt}</span>'
                            f'<span>{q.get(key, "")}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("")
                    st.markdown("**💡 Explanation**")
                    st.markdown(q.get('explanation_english', ''))
                
                with lt2:
                    st.markdown(f"**{q.get('question_hindi', '')}**")
                    st.markdown("")
                    
                    keys_hi = ['option_a_hindi', 'option_b_hindi', 'option_c_hindi', 'option_d_hindi']
                    for opt, key in zip(options, keys_hi):
                        is_correct = opt == correct
                        row_class = "option-row option-correct" if is_correct else "option-row"
                        marker_class = "option-marker marker-correct" if is_correct else "option-marker marker-normal"
                        st.markdown(
                            f'<div class="{row_class}">'
                            f'<span class="{marker_class}">{opt}</span>'
                            f'<span>{q.get(key, "")}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("")
                    st.markdown("**💡 व्याख्या**")
                    st.markdown(q.get('explanation_hindi', ''))
                
                st.markdown("---")
                st.markdown("**🛠️ Quality Tools**")
                
                qc1, qc2, qc3 = st.columns(3)
                
                with qc1:
                    if st.button("🔍 Verify Answer", key=f"vrf_{i}", use_container_width=True):
                        with st.spinner("Verifying..."):
                            result = verify_answer(q)
                            st.session_state.verify_results[i] = result
                        st.rerun()
                
                with qc2:
                    if st.button("✍️ Humanize", key=f"hum_{i}", use_container_width=True):
                        with st.spinner("Rewriting..."):
                            humanized = humanize_question(q)
                            st.session_state.generated["questions"][i] = humanized
                        st.rerun()
                
                with qc3:
                    if st.button("📋 View Meta", key=f"mta_{i}", use_container_width=True):
                        st.session_state[f"show_meta_{i}"] = not st.session_state.get(f"show_meta_{i}", False)
                
                if verify_data:
                    conf = verify_data.get("confidence", 0)
                    if verify_data.get("matches") and conf >= 80:
                        st.success(f"✅ Verified · Confidence: {conf}% · Safe to use")
                    elif verify_data.get("matches") and conf >= 60:
                        st.warning(f"⚠️ Likely correct · Confidence: {conf}% · Manual check recommended")
                    elif verify_data.get("verified"):
                        st.error(f"❌ Answer mismatch · AI suggests: {verify_data.get('ai_answer')} · Not: {q.get('correct_answer')}")
                        if verify_data.get("notes"):
                            st.caption(f"Note: {verify_data.get('notes')}")
                    else:
                        st.error("Verification failed. Try again.")
                
                if st.session_state.get(f"show_meta_{i}", False):
                    st.markdown("")
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-row"><div class="info-label">Topic</div><div class="info-value">{q.get('topic', 'N/A')}</div></div>
                        <div class="info-row"><div class="info-label">Subtopic</div><div class="info-value">{q.get('subtopic', 'N/A')}</div></div>
                        <div class="info-row"><div class="info-label">NCERT Ref</div><div class="info-value">{q.get('ncert_reference', 'N/A')}</div></div>
                        <div class="info-row"><div class="info-label">Common Mistake</div><div class="info-value">{q.get('common_mistake', 'N/A')}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**📋 Copy for TrackPrep**")
                
                cc1, cc2 = st.columns(2)
                with cc1:
                    eng_text = f"""Q: {q.get('question_english', '')}
A) {q.get('option_a_english', '')}
B) {q.get('option_b_english', '')}
C) {q.get('option_c_english', '')}
D) {q.get('option_d_english', '')}
Answer: {q.get('correct_answer', '')}
Explanation: {q.get('explanation_english', '')}"""
                    st.text_area("English", eng_text, height=180, key=f"eng_{i}", label_visibility="collapsed")
                
                with cc2:
                    hin_text = f"""प्रश्न: {q.get('question_hindi', '')}
A) {q.get('option_a_hindi', '')}
B) {q.get('option_b_hindi', '')}
C) {q.get('option_c_hindi', '')}
D) {q.get('option_d_hindi', '')}
उत्तर: {q.get('correct_answer', '')}
व्याख्या: {q.get('explanation_hindi', '')}"""
                    st.text_area("Hindi", hin_text, height=180, key=f"hin_{i}", label_visibility="collapsed")

with tab2:
    st.markdown('<div class="section-label">Upload NCERT PDFs</div>', unsafe_allow_html=True)
    st.caption("Upload your NCERT PDFs to build your personal library")
    
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    
    st.info("💡 **Tip:** Name your files clearly (e.g., `ncert_bio11_ch01_living_world.pdf`) for better organization")
    
    category = st.selectbox(
        "PDF Category",
        ["biology", "physics", "chemistry", "pyq", "other"],
        help="Select the subject category for the PDF"
    )
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF files"
    )
    
    if uploaded_files:
        if st.button("📤 Upload All", type="primary", use_container_width=True):
            success_count = 0
            for uploaded_file in uploaded_files:
                try:
                    save_uploaded_pdf(uploaded_file, category)
                    success_count += 1
                except Exception as e:
                    st.error(f"Failed to upload {uploaded_file.name}: {e}")
            
            if success_count > 0:
                st.success(f"✅ Successfully uploaded {success_count} PDF(s)")
                st.rerun()
    
    st.markdown("---")
    
    st.markdown('<div class="section-label">Your Library</div>', unsafe_allow_html=True)
    
    books_current = scan_books()
    
    if sum(len(v) for v in books_current.values()) == 0:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 48px; margin-bottom: 16px;">📁</div>
            <h3 style="margin: 0 0 8px 0;">Library is empty</h3>
            <p style="color: #a1a1a1; margin: 0;">Upload some PDFs above to get started</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for cat, pdfs_list in books_current.items():
            if pdfs_list:
                st.markdown(f"**{cat.title()}** ({len(pdfs_list)} files)")
                for pdf in pdfs_list:
                    col_p1, col_p2 = st.columns([5, 1])
                    with col_p1:
                        st.markdown(f"📄 `{pdf}`")
                    with col_p2:
                        if st.button("🗑️", key=f"del_{pdf}", use_container_width=True):
                            delete_pdf(pdf)
                            st.rerun()
                st.markdown("")

with tab3:
    st.markdown('<div class="section-label">Question History</div>', unsafe_allow_html=True)
    st.caption("Browse and download previously generated question sets")
    
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    
    output_dir = "output"
    if os.path.exists(output_dir):
        files = sorted([f for f in os.listdir(output_dir) if f.endswith(".json")], reverse=True)
        
        if not files:
            st.info("📭 No question sets yet. Generate some in the Generate tab.")
        else:
            selected_file = st.selectbox("Select file", files)
            
            if selected_file:
                filepath = os.path.join(output_dir, selected_file)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                questions = data.get("questions", [])
                
                cl1, cl2, cl3 = st.columns([2, 1, 1])
                with cl1:
                    st.success(f"📄 {len(questions)} questions loaded")
                with cl2:
                    with open(filepath, "r", encoding="utf-8") as f:
                        st.download_button("💾 JSON", f.read(), file_name=selected_file, use_container_width=True)
                with cl3:
                    txt_file = filepath.replace(".json", ".txt")
                    if os.path.exists(txt_file):
                        with open(txt_file, "r", encoding="utf-8") as f:
                            st.download_button("📄 TXT", f.read(), file_name=selected_file.replace(".json", ".txt"), use_container_width=True)
                
                st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
                
                for i, q in enumerate(questions):
                    with st.expander(f"Q{i+1}  ·  {q.get('question_english', '')[:70]}..."):
                        st.markdown(f"**{q.get('question_english', '')}**")
                        st.markdown("")
                        
                        correct = q.get('correct_answer', '')
                        options = ['A', 'B', 'C', 'D']
                        keys = ['option_a_english', 'option_b_english', 'option_c_english', 'option_d_english']
                        
                        for opt, key in zip(options, keys):
                            is_correct = opt == correct
                            row_class = "option-row option-correct" if is_correct else "option-row"
                            marker_class = "option-marker marker-correct" if is_correct else "option-marker marker-normal"
                            st.markdown(
                                f'<div class="{row_class}">'
                                f'<span class="{marker_class}">{opt}</span>'
                                f'<span>{q.get(key, "")}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        
                        st.markdown("")
                        st.info(q.get('explanation_english', ''))
    else:
        st.info("📁 Generate some questions first to see them here.")

with tab4:
    st.markdown('<div class="section-label">NCERT Diagram Extractor</div>', unsafe_allow_html=True)
    st.caption("Extract and browse figures directly from your uploaded NCERT PDFs")
    
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    
    if sum(len(v) for v in books.values()) == 0:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 48px; margin-bottom: 16px;">📚</div>
            <h3 style="margin: 0 0 8px 0;">No PDFs to extract from</h3>
            <p style="color: #a1a1a1; margin: 0;">Upload PDFs first in the Upload PDFs tab</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_books, total_images = get_all_extracted_count()
        
        ds1, ds2, ds3 = st.columns([1, 1, 1])
        with ds1:
            st.metric("Books Indexed", total_books)
        with ds2:
            st.metric("Diagrams Available", total_images)
        with ds3:
            st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
            if st.button("🔄 Extract All PDFs", type="primary", use_container_width=True):
                with st.spinner("Processing PDFs..."):
                    progress_bar = st.progress(0)
                    status = st.empty()
                    
                    def update(current, total, name):
                        progress_bar.progress(current / total)
                        status.caption(f"⚙️ Processing {current}/{total}: {name}")
                    
                    result = extract_all_books(progress_callback=update)
                    total = sum(len(imgs) for imgs in result.values())
                    st.success(f"✅ Extracted {total} diagrams from {len(result)} books")
                    st.rerun()
        
        st.markdown("---")
        
        extracted = get_extracted_books()
        
        if not extracted:
            st.info("🎨 No diagrams extracted yet. Click 'Extract All PDFs' to begin.")
        else:
            book_display = {b: b.replace("ncert_", "").replace("_", " ").title() for b in extracted}
            
            db1, db2 = st.columns([2, 1])
            with db1:
                selected_book = st.selectbox("Book", options=extracted, format_func=lambda x: book_display[x])
            with db2:
                per_row = st.selectbox("Grid", [2, 3, 4, 5], index=1)
            
            if selected_book:
                images = get_book_images(selected_book)
                
                if images:
                    all_pages = sorted(set(img["page"] for img in images))
                    page_options = ["All pages"] + [f"Page {p}" for p in all_pages]
                    selected_page = st.selectbox("Filter by page", page_options)
                    
                    if selected_page != "All pages":
                        page_num = int(selected_page.replace("Page ", ""))
                        filtered = [img for img in images if img["page"] == page_num]
                    else:
                        filtered = images
                    
                    st.caption(f"Showing {len(filtered)} diagrams")
                    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
                    
                    for row_start in range(0, len(filtered), per_row):
                        cols = st.columns(per_row)
                        for i, col in enumerate(cols):
                            idx = row_start + i
                            if idx < len(filtered):
                                img = filtered[idx]
                                with col:
                                    try:
                                        st.image(img["path"], caption=f"Page {img['page']}")
                                        
                                        with open(img["path"], "rb") as f:
                                            st.download_button("↓ Download", f.read(), file_name=img["filename"], mime="image/jpeg", key=f"dl_{idx}", use_container_width=True)
                                    except:
                                        st.caption(f"Error: {img['filename']}")
                else:
                    st.info("No diagrams in this book")
