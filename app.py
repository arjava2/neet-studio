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
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background-color: #09090b;
        color: #fafafa;
    }
    
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
        color: #fafafa !important;
    }
    
    footer, .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }
    
    header[data-testid="stHeader"] {
        background-color: rgba(9, 9, 11, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #27272a !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
        background: #18181b !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 8px !important;
        padding: 8px !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        transition: all 0.15s ease !important;
    }
    
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: #27272a !important;
        border-color: #52525b !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] svg {
        color: #a1a1aa !important;
        width: 20px !important;
        height: 20px !important;
    }
    
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #09090b !important;
        border-right: 1px solid #27272a !important;
        width: 280px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 1.5rem 1rem;
    }
    
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #18181b !important;
        color: #fafafa !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
    }
    
    .stSelectbox > div > div {
        background-color: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
    
    .stButton > button {
        background-color: #18181b !important;
        color: #fafafa !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #27272a !important;
        border-color: #3f3f46 !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 10px rgba(99,102,241,0.25) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 16px rgba(99,102,241,0.4) !important;
    }
    
    .stDownloadButton > button {
        background-color: #18181b !important;
        color: #fafafa !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stMetric"] {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #71717a !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    [data-testid="stMetricValue"] {
        color: #fafafa !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    .streamlit-expanderHeader {
        background-color: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        color: #fafafa !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3f3f46 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #0f0f12 !important;
        border: 1px solid #27272a !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 16px !important;
    }
    
    .stAlert, div[data-baseweb="notification"] {
        background-color: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #27272a !important;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #71717a !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        border: none !important;
        border-radius: 0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fafafa !important;
        border-bottom: 2px solid #6366f1 !important;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    }
    
    hr { border-color: #27272a !important; }
    
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #09090b; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
    
    .stImage img {
        border-radius: 8px !important;
        border: 1px solid #27272a !important;
    }
    
    .stFileUploader > div {
        background-color: #18181b !important;
        border: 1px dashed #3f3f46 !important;
        border-radius: 10px !important;
    }
    
    .brand { font-size: 20px; font-weight: 800; letter-spacing: -0.03em; background: linear-gradient(135deg, #818cf8, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .brand-sub { font-size: 12px; color: #52525b; margin-top: 2px; }
    .sec-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #52525b; margin: 20px 0 8px 0; }
    .card { background: #18181b; border: 1px solid #27272a; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
    .row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; border-bottom: 1px solid #1c1c1f; }
    .row:last-child { border: none; }
    .row-label { color: #71717a; }
    .row-value { color: #fafafa; font-weight: 500; }
    .pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .pill-on { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: #22c55e; }
    .pill-off { background: rgba(113,113,122,0.1); border: 1px solid rgba(113,113,122,0.3); color: #71717a; }
    .dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .dot-g { background: #22c55e; animation: blink 2s infinite; }
    .dot-r { background: #71717a; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.5} }
    .opt { padding: 10px 14px; margin: 4px 0; background: #18181b; border: 1px solid #27272a; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 14px; }
    .opt-ok { background: rgba(34,197,94,0.06); border-color: rgba(34,197,94,0.3); }
    .mark { width: 22px; height: 22px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }
    .mark-ok { background: #22c55e; color: white; }
    .mark-no { background: #27272a; color: #71717a; }
    .tag { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin-right: 4px; }
    .tag-e { background: rgba(34,197,94,0.12); color: #22c55e; }
    .tag-m { background: rgba(234,179,8,0.12); color: #eab308; }
    .tag-h { background: rgba(239,68,68,0.12); color: #ef4444; }
    .tag-t { background: rgba(99,102,241,0.12); color: #818cf8; }
    .empty { text-align: center; padding: 50px 20px; background: #18181b; border: 1px dashed #27272a; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

if "generated" not in st.session_state:
    st.session_state.generated = None
if "ai_ready" not in st.session_state:
    st.session_state.ai_ready = False
if "verify_results" not in st.session_state:
    st.session_state.verify_results = {}

with st.sidebar:
    st.markdown('<div class="brand">◆ NEET Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Question generation platform</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sec-label">API Key</div>', unsafe_allow_html=True)
    
    api_key = st.text_input("key", type="password", placeholder="Paste Gemini API key", label_visibility="collapsed")
    
    if st.button("Connect", type="primary", use_container_width=True):
        if api_key:
            try:
                setup_ai(api_key)
                st.session_state.ai_ready = True
                st.success("Connected")
            except:
                st.error("Failed")
        else:
            st.error("Key required")
    
    if st.session_state.ai_ready:
        st.markdown('<div class="pill pill-on"><span class="dot dot-g"></span>Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill pill-off"><span class="dot dot-r"></span>Offline</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sec-label">Library</div>', unsafe_allow_html=True)
    
    books = scan_books()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Bio", len(books['biology']))
        st.metric("Chem", len(books['chemistry']))
    with c2:
        st.metric("Phy", len(books['physics']))
        st.metric("PYQ", len(books['pyq']))
    
    total = sum(len(v) for v in books.values())
    st.caption(f"Total: {total} files")
    
    st.markdown('<div class="sec-label">Links</div>', unsafe_allow_html=True)
    st.markdown("[🔑 Get API Key](https://aistudio.google.com/apikey)")
    st.markdown("[📖 NCERT PDFs](https://ncert.nic.in/textbook.php)")
    st.caption("v6.0 · Free forever")

st.markdown("# NEET Question Studio")
st.caption("Generate NEET-level questions from NCERT PDFs using AI")

if not st.session_state.ai_ready:
    st.info("👋 Tap the ☰ menu button (top-left) to open sidebar and add your API key.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><div style="font-size:24px;margin-bottom:8px;">⚡</div><div style="font-weight:600;font-size:14px;">Fast</div><div style="color:#71717a;font-size:12px;margin-top:4px;">30 questions in 60 seconds</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div style="font-size:24px;margin-bottom:8px;">🎯</div><div style="font-weight:600;font-size:14px;">Verified</div><div style="color:#71717a;font-size:12px;margin-top:4px;">AI double-checks every answer</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><div style="font-size:24px;margin-bottom:8px;">🌐</div><div style="font-weight:600;font-size:14px;">Bilingual</div><div style="color:#71717a;font-size:12px;margin-top:4px;">English + Hindi output</div></div>', unsafe_allow_html=True)
    
    st.markdown("### How to use")
    st.markdown("1. Get free API key → [aistudio.google.com/apikey](https://aistudio.google.com/apikey)")
    st.markdown("2. Open sidebar (☰ top-left) → paste key → Connect")
    st.markdown("3. Upload PDFs or use pre-loaded library")
    st.markdown("4. Select chapter → Generate!")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Generate", "Upload", "History", "Diagrams"])

with tab1:
    if total == 0:
        st.markdown('<div class="empty"><div style="font-size:40px;margin-bottom:12px;">📚</div><h3>No PDFs yet</h3><p style="color:#71717a;">Go to Upload tab to add NCERT books</p></div>', unsafe_allow_html=True)
        st.stop()
    
    c_l, c_r = st.columns([1, 1], gap="large")
    
    with c_l:
        st.markdown('<div class="sec-label">Parameters</div>', unsafe_allow_html=True)
        
        avail = [s.title() for s in ["biology", "physics", "chemistry"] if books[s]]
        if not avail:
            st.error("No PDFs. Upload first.")
            st.stop()
        
        subject = st.selectbox("Subject", avail)
        pdfs = books[subject.lower()]
        
        ch_opts = [f"{i+1}. {get_chapter_name(p)}" for i, p in enumerate(pdfs)]
        ch_pick = st.selectbox("Chapter", ch_opts)
        ch_idx = int(ch_pick.split(".")[0]) - 1
        pdf_file = pdfs[ch_idx]
        ch_name = get_chapter_name(pdf_file)
        
        topic = st.text_input("Topic (optional)", placeholder="e.g. photosynthesis")
        
        qtype = st.selectbox("Type", ["General MCQ", "Assertion & Reason", "Statement Based", "Match the Following", "Image Question", "Graphical"])
        
        ca, cb = st.columns(2)
        with ca:
            diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        with cb:
            num_q = st.number_input("Count", 1, 30, 10)
        
        use_pyq = False
        if books["pyq"] and topic:
            use_pyq = st.checkbox(f"Use PYQs ({len(books['pyq'])})")
    
    with c_r:
        st.markdown('<div class="sec-label">Summary</div>', unsafe_allow_html=True)
        
        d_class = f"tag-{diff[0].lower()}"
        
        st.markdown(f"""
        <div class="card">
            <div style="margin-bottom:12px;"><span class="tag {d_class}">{diff}</span><span class="tag tag-t">{qtype}</span></div>
            <div class="row"><span class="row-label">Subject</span><span class="row-value">{subject}</span></div>
            <div class="row"><span class="row-label">Chapter</span><span class="row-value">{ch_name[:25]}</span></div>
            <div class="row"><span class="row-label">Topic</span><span class="row-value">{topic if topic else 'Full chapter'}</span></div>
            <div class="row"><span class="row-label">Count</span><span class="row-value">{num_q}</span></div>
            <div class="row"><span class="row-label">PYQ</span><span class="row-value">{'Yes' if use_pyq else 'No'}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Generate", type="primary", use_container_width=True):
            with st.spinner("Generating questions..."):
                res = generate_questions(pdf_file, ch_name, qtype, diff, num_q, topic, use_pyq)
            if res.get("success"):
                st.session_state.generated = res["data"]
                st.session_state.verify_results = {}
                st.success(f"✅ {res['count']} questions generated")
            else:
                st.error(f"❌ {res.get('error')}")
    
    if st.session_state.generated:
        st.markdown("---")
        
        qs = st.session_state.generated.get("questions", [])
        vc = sum(1 for i in range(len(qs)) if st.session_state.verify_results.get(i, {}).get("matches"))
        
        h1, h2 = st.columns([3, 1])
        with h1:
            st.markdown("### Results")
            st.caption(f"{len(qs)} questions · {vc} verified")
        with h2:
            st.metric("Verified", f"{vc}/{len(qs)}")
        
        for i, q in enumerate(qs):
            vd = st.session_state.verify_results.get(i, {})
            icon = ""
            if vd.get("matches") and vd.get("confidence", 0) >= 80:
                icon = "✅ "
            elif vd.get("verified") and not vd.get("matches"):
                icon = "⚠️ "
            
            with st.expander(f"{icon}Q{i+1} · {q.get('question_english','')[:70]}..."):
                t1, t2 = st.tabs(["English", "हिन्दी"])
                
                with t1:
                    st.markdown(f"**{q.get('question_english','')}**")
                    correct = q.get('correct_answer', '')
                    for opt, key in zip(['A','B','C','D'], ['option_a_english','option_b_english','option_c_english','option_d_english']):
                        ok = opt == correct
                        rc = "opt opt-ok" if ok else "opt"
                        mc = "mark mark-ok" if ok else "mark mark-no"
                        st.markdown(f'<div class="{rc}"><span class="{mc}">{opt}</span><span>{q.get(key,"")}</span></div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.info(f"💡 {q.get('explanation_english','')}")
                
                with t2:
                    st.markdown(f"**{q.get('question_hindi','')}**")
                    for opt, key in zip(['A','B','C','D'], ['option_a_hindi','option_b_hindi','option_c_hindi','option_d_hindi']):
                        ok = opt == correct
                        rc = "opt opt-ok" if ok else "opt"
                        mc = "mark mark-ok" if ok else "mark mark-no"
                        st.markdown(f'<div class="{rc}"><span class="{mc}">{opt}</span><span>{q.get(key,"")}</span></div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.info(f"💡 {q.get('explanation_hindi','')}")
                
                st.markdown("---")
                
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("🔍 Verify", key=f"v_{i}", use_container_width=True):
                        with st.spinner("..."):
                            r = verify_answer(q)
                            st.session_state.verify_results[i] = r
                        st.rerun()
                with b2:
                    if st.button("✍️ Humanize", key=f"h_{i}", use_container_width=True):
                        with st.spinner("..."):
                            h = humanize_question(q)
                            st.session_state.generated["questions"][i] = h
                        st.rerun()
                with b3:
                    if st.button("ℹ️ Meta", key=f"m_{i}", use_container_width=True):
                        st.session_state[f"sm_{i}"] = not st.session_state.get(f"sm_{i}", False)
                
                if vd:
                    cf = vd.get("confidence", 0)
                    if vd.get("matches") and cf >= 80:
                        st.success(f"✅ Verified · {cf}% confidence")
                    elif vd.get("matches") and cf >= 60:
                        st.warning(f"⚠️ Likely correct · {cf}%")
                    elif vd.get("verified"):
                        st.error(f"❌ Mismatch · AI says: {vd.get('ai_answer')}")
                
                if st.session_state.get(f"sm_{i}", False):
                    st.caption(f"Topic: {q.get('topic','')} · Subtopic: {q.get('subtopic','')}")
                    st.caption(f"NCERT: {q.get('ncert_reference','')} · Mistake: {q.get('common_mistake','')}")
                
                st.markdown("---")
                st.markdown("**Copy for TrackPrep**")
                e1, e2 = st.columns(2)
                with e1:
                    et = f"Q: {q.get('question_english','')}\nA) {q.get('option_a_english','')}\nB) {q.get('option_b_english','')}\nC) {q.get('option_c_english','')}\nD) {q.get('option_d_english','')}\nAnswer: {q.get('correct_answer','')}\nExplanation: {q.get('explanation_english','')}"
                    st.text_area("EN", et, height=160, key=f"e_{i}", label_visibility="collapsed")
                with e2:
                    ht = f"प्रश्न: {q.get('question_hindi','')}\nA) {q.get('option_a_hindi','')}\nB) {q.get('option_b_hindi','')}\nC) {q.get('option_c_hindi','')}\nD) {q.get('option_d_hindi','')}\nउत्तर: {q.get('correct_answer','')}\nव्याख्या: {q.get('explanation_hindi','')}"
                    st.text_area("HI", ht, height=160, key=f"hi_{i}", label_visibility="collapsed")

with tab2:
    st.markdown("### Upload PDFs")
    st.caption("Add NCERT books to your library")
    
    cat = st.selectbox("Category", ["biology", "physics", "chemistry", "pyq", "other"])
    
    files = st.file_uploader("Choose PDFs", type=["pdf"], accept_multiple_files=True)
    
    if files:
        if st.button("📤 Upload", type="primary", use_container_width=True):
            ok = 0
            for f in files:
                try:
                    save_uploaded_pdf(f, cat)
                    ok += 1
                except:
                    st.error(f"Failed: {f.name}")
            if ok:
                st.success(f"✅ Uploaded {ok} file(s)")
                st.rerun()
    
    st.markdown("---")
    st.markdown("### Your Library")
    
    bk = scan_books()
    if sum(len(v) for v in bk.values()) == 0:
        st.markdown('<div class="empty"><div style="font-size:40px;margin-bottom:12px;">📁</div><h3>Empty</h3><p style="color:#71717a;">Upload PDFs above</p></div>', unsafe_allow_html=True)
    else:
        for cat_name, pdf_list in bk.items():
            if pdf_list:
                st.markdown(f"**{cat_name.title()}** ({len(pdf_list)})")
                for p in pdf_list:
                    p1, p2 = st.columns([5, 1])
                    with p1:
                        st.caption(f"📄 {p}")
                    with p2:
                        if st.button("✕", key=f"d_{p}"):
                            delete_pdf(p)
                            st.rerun()

with tab3:
    st.markdown("### History")
    st.caption("Previous question sets")
    
    odir = "output"
    if os.path.exists(odir):
        fl = sorted([f for f in os.listdir(odir) if f.endswith(".json")], reverse=True)
        if not fl:
            st.info("No history yet. Generate some questions first.")
        else:
            sf = st.selectbox("File", fl)
            if sf:
                fp = os.path.join(odir, sf)
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                qs = data.get("questions", [])
                
                x1, x2 = st.columns([2, 1])
                with x1:
                    st.success(f"{len(qs)} questions")
                with x2:
                    with open(fp, "r", encoding="utf-8") as f:
                        st.download_button("💾 Download", f.read(), file_name=sf, use_container_width=True)
                
                for i, q in enumerate(qs):
                    with st.expander(f"Q{i+1} · {q.get('question_english','')[:60]}..."):
                        st.markdown(f"**{q.get('question_english','')}**")
                        correct = q.get('correct_answer', '')
                        for opt, key in zip(['A','B','C','D'], ['option_a_english','option_b_english','option_c_english','option_d_english']):
                            ok = opt == correct
                            rc = "opt opt-ok" if ok else "opt"
                            mc = "mark mark-ok" if ok else "mark mark-no"
                            st.markdown(f'<div class="{rc}"><span class="{mc}">{opt}</span><span>{q.get(key,"")}</span></div>', unsafe_allow_html=True)
                        st.info(q.get('explanation_english', ''))
    else:
        st.info("Generate questions first.")

with tab4:
    st.markdown("### Diagrams")
    st.caption("Extract figures from NCERT PDFs")
    
    if total == 0:
        st.markdown('<div class="empty"><div style="font-size:40px;margin-bottom:12px;">🖼️</div><h3>No PDFs</h3><p style="color:#71717a;">Upload PDFs first</p></div>', unsafe_allow_html=True)
    else:
        tb, ti = get_all_extracted_count()
        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Books", tb)
        with d2:
            st.metric("Images", ti)
        with d3:
            if st.button("🔄 Extract All", type="primary", use_container_width=True):
                with st.spinner("Extracting..."):
                    pb = st.progress(0)
                    sx = st.empty()
                    def upd(c, t, n):
                        pb.progress(c / t)
                        sx.caption(f"{c}/{t}: {n}")
                    r = extract_all_books(progress_callback=upd)
                    tot = sum(len(v) for v in r.values())
                    st.success(f"✅ {tot} diagrams from {len(r)} books")
                    st.rerun()
        
        st.markdown("---")
        ext = get_extracted_books()
        
        if not ext:
            st.info("Click 'Extract All' above to begin.")
        else:
            bd = {b: b.replace("ncert_","").replace("_"," ").title() for b in ext}
            sb = st.selectbox("Book", ext, format_func=lambda x: bd[x])
            
            if sb:
                imgs = get_book_images(sb)
                if imgs:
                    pr = st.selectbox("Grid", [2, 3, 4], index=1)
                    st.caption(f"{len(imgs)} diagrams")
                    
                    for rs in range(0, len(imgs), pr):
                        cols = st.columns(pr)
                        for j, col in enumerate(cols):
                            idx = rs + j
                            if idx < len(imgs):
                                im = imgs[idx]
                                with col:
                                    try:
                                        st.image(im["path"], caption=f"P{im['page']}")
                                        with open(im["path"], "rb") as f:
                                            st.download_button("↓", f.read(), file_name=im["filename"], mime="image/jpeg", key=f"dl_{idx}", use_container_width=True)
                                    except:
                                        st.caption("Error")
                else:
                    st.info("No images found")
