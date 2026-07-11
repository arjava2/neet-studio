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
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', -apple-system, sans-serif !important; box-sizing: border-box; }
    
    .stApp { background: #09090b; color: #fafafa; }
    
    h1 { font-size: 26px !important; font-weight: 800 !important; letter-spacing: -0.03em !important; color: #fafafa !important; }
    h2 { font-size: 20px !important; font-weight: 700 !important; color: #fafafa !important; }
    h3 { font-size: 16px !important; font-weight: 700 !important; color: #fafafa !important; }
    
    footer, .stDeployButton, #MainMenu { display: none !important; visibility: hidden !important; }
    
    header[data-testid="stHeader"] { background: rgba(9,9,11,0.9) !important; backdrop-filter: blur(12px); border-bottom: 1px solid #18181b; }
    
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="headerNoPadding"],
    [data-testid="stBaseButton-headerNoPadding"] {
        background: #18181b !important; border: 1px solid #27272a !important;
        border-radius: 8px !important; padding: 6px 10px !important;
    }
    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stSidebarCollapseButton"] *,
    button[kind="headerNoPadding"] *,
    [data-testid="stBaseButton-headerNoPadding"] * {
        font-size: 0px !important; color: #a1a1aa !important;
    }
    [data-testid="stSidebarCollapsedControl"] *::before,
    [data-testid="stSidebarCollapseButton"] *::before {
        content: "☰" !important; font-size: 16px !important; color: #a1a1aa !important;
    }
    
    section[data-testid="stSidebar"] { background: #09090b !important; border-right: 1px solid #18181b !important; }
    section[data-testid="stSidebar"] > div { padding: 20px 14px; }
    
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: #18181b !important; color: #fafafa !important;
        border: 1px solid #27272a !important; border-radius: 8px !important;
        padding: 10px 12px !important; font-size: 14px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.12) !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #52525b !important; }
    
    .stSelectbox > div > div { background: #18181b !important; border: 1px solid #27272a !important; border-radius: 8px !important; }
    
    .stButton > button {
        background: #18181b !important; color: #fafafa !important;
        border: 1px solid #27272a !important; border-radius: 8px !important;
        padding: 10px 16px !important; font-size: 13px !important; font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover { background: #27272a !important; border-color: #3f3f46 !important; }
    .stButton > button:active { transform: scale(0.98); }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important; color: white !important; font-weight: 600 !important;
        box-shadow: 0 2px 12px rgba(99,102,241,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover { box-shadow: 0 4px 20px rgba(99,102,241,0.5) !important; transform: translateY(-1px); }
    .stButton > button[kind="primary"]:active { transform: scale(0.98) translateY(0); }
    
    .stDownloadButton > button {
        background: #18181b !important; color: #fafafa !important;
        border: 1px solid #27272a !important; border-radius: 8px !important;
    }
    
    [data-testid="stMetric"] {
        background: #18181b !important; border: 1px solid #27272a !important;
        border-radius: 10px !important; padding: 14px !important;
        transition: border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover { border-color: #3f3f46 !important; }
    [data-testid="stMetricLabel"] { color: #71717a !important; font-size: 10px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.08em; }
    [data-testid="stMetricValue"] { color: #fafafa !important; font-size: 24px !important; font-weight: 700 !important; }
    
    .streamlit-expanderHeader {
        background: #18181b !important; border: 1px solid #27272a !important;
        border-radius: 8px !important; color: #fafafa !important;
        font-weight: 500 !important; font-size: 13px !important;
        transition: all 0.2s ease;
    }
    .streamlit-expanderHeader:hover { border-color: #6366f1 !important; background: #1c1c1f !important; }
    .streamlit-expanderContent {
        background: #0f0f12 !important; border: 1px solid #27272a !important;
        border-top: none !important; border-radius: 0 0 8px 8px !important; padding: 16px !important;
    }
    
    .stAlert, div[data-baseweb="notification"] { background: #18181b !important; border: 1px solid #27272a !important; border-radius: 8px !important; }
    
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #27272a !important; gap: 0; }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: #52525b !important;
        font-weight: 500 !important; font-size: 13px !important;
        padding: 10px 14px !important; transition: color 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #a1a1aa !important; }
    .stTabs [aria-selected="true"] { color: #fafafa !important; border-bottom: 2px solid #6366f1 !important; }
    
    .stProgress > div > div { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; border-radius: 4px; }
    .stProgress > div { background: #18181b !important; border-radius: 4px; }
    hr { border-color: #1c1c1f !important; }
    
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
    
    .stImage img { border-radius: 8px !important; border: 1px solid #27272a !important; }
    .stFileUploader > div { background: #18181b !important; border: 1px dashed #3f3f46 !important; border-radius: 10px !important; }
    .stCheckbox label span { color: #a1a1aa !important; }
    
    .brand { font-size: 20px; font-weight: 800; background: linear-gradient(135deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub { font-size: 11px; color: #52525b; margin-top: 2px; }
    .lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3f3f46; margin: 20px 0 8px 0; }
    
    .crd { background: #18181b; border: 1px solid #27272a; border-radius: 10px; padding: 16px; margin-bottom: 12px; transition: border-color 0.2s ease; }
    .crd:hover { border-color: #3f3f46; }
    .rw { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; border-bottom: 1px solid #1c1c1f; }
    .rw:last-child { border: none; }
    .rl { color: #52525b; font-weight: 500; }
    .rv { color: #e4e4e7; font-weight: 500; }
    
    .pl { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
    .pl-on { background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2); color: #22c55e; }
    .pl-off { background: rgba(113,113,122,0.08); border: 1px solid rgba(113,113,122,0.2); color: #71717a; }
    .dt { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .dg { background: #22c55e; animation: bl 2s infinite; }
    .dr { background: #52525b; }
    @keyframes bl { 0%,100%{opacity:1} 50%{opacity:.4} }
    
    .op { padding: 10px 14px; margin: 4px 0; background: #18181b; border: 1px solid #27272a; border-radius: 8px; display: flex; align-items: center; gap: 10px; font-size: 13px; color: #d4d4d8; transition: border-color 0.15s ease; }
    .op:hover { border-color: #3f3f46; }
    .op-ok { background: rgba(34,197,94,0.05); border-color: rgba(34,197,94,0.25); }
    .mk { width: 22px; height: 22px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; }
    .mk-ok { background: #22c55e; color: white; }
    .mk-no { background: #27272a; color: #52525b; }
    
    .tg { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; margin-right: 4px; }
    .tg-e { background: rgba(34,197,94,0.1); color: #22c55e; }
    .tg-m { background: rgba(234,179,8,0.1); color: #eab308; }
    .tg-h { background: rgba(239,68,68,0.1); color: #ef4444; }
    .tg-t { background: rgba(99,102,241,0.1); color: #818cf8; }
    
    .emp { text-align: center; padding: 50px 20px; background: #18181b; border: 1px dashed #27272a; border-radius: 10px; color: #fafafa; }
    .emp p { color: #52525b !important; margin-top: 8px; }
    
    .install-btn {
        display: none;
        position: fixed; bottom: 20px; right: 20px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white; border: none; border-radius: 12px;
        padding: 12px 20px; font-size: 14px; font-weight: 600;
        cursor: pointer; z-index: 99999;
        box-shadow: 0 4px 20px rgba(99,102,241,0.4);
        font-family: 'Inter', sans-serif;
        animation: slideUp 0.5s ease;
    }
    .install-btn:hover { box-shadow: 0 6px 28px rgba(99,102,241,0.6); transform: translateY(-2px); }
    @keyframes slideUp { from { transform: translateY(100px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    
    @media (max-width: 768px) {
        h1 { font-size: 22px !important; }
        .crd { padding: 12px; }
        .op { font-size: 12px; padding: 8px 10px; }
    }
</style>

<script>
    // PWA Install
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        const btn = document.getElementById('installBtn');
        if (btn) btn.style.display = 'block';
    });
    
    function installApp() {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((result) => {
                deferredPrompt = null;
                const btn = document.getElementById('installBtn');
                if (btn) btn.style.display = 'none';
            });
        }
    }
</script>

<button id="installBtn" class="install-btn" onclick="installApp()">
    📲 Install App
</button>
""", unsafe_allow_html=True)

if "generated" not in st.session_state:
    st.session_state.generated = None
if "ai_ready" not in st.session_state:
    st.session_state.ai_ready = False
if "verify_results" not in st.session_state:
    st.session_state.verify_results = {}

with st.sidebar:
    st.markdown('<div class="brand">◆ NEET Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">AI-powered question generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="lbl">API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("key", type="password", placeholder="Paste Gemini API key", label_visibility="collapsed")
    if st.button("Connect", type="primary", use_container_width=True):
        if api_key:
            try:
                setup_ai(api_key)
                st.session_state.ai_ready = True
                st.success("Connected successfully")
            except:
                st.error("Connection failed")
        else:
            st.error("API key required")
    if st.session_state.ai_ready:
        st.markdown('<div class="pl pl-on"><span class="dt dg"></span>Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pl pl-off"><span class="dt dr"></span>Offline</div>', unsafe_allow_html=True)
    st.markdown('<div class="lbl">Library</div>', unsafe_allow_html=True)
    books = scan_books()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Bio", len(books['biology']))
        st.metric("Chem", len(books['chemistry']))
    with c2:
        st.metric("Phy", len(books['physics']))
        st.metric("PYQ", len(books['pyq']))
    total = sum(len(v) for v in books.values())
    st.caption(f"Total: {total} files indexed")
    st.markdown('<div class="lbl">Links</div>', unsafe_allow_html=True)
    st.markdown("[Get API Key](https://aistudio.google.com/apikey)")
    st.markdown("[NCERT PDFs](https://ncert.nic.in/textbook.php)")
    st.markdown("---")
    st.caption("v6.0 · Free forever")
    st.caption("Add to home screen for app experience")

st.markdown("# NEET Question Studio")
st.caption("Generate NEET-level questions from NCERT PDFs using AI")

if not st.session_state.ai_ready:
    st.info("Add your free Gemini API key in the sidebar to get started.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="crd"><div style="font-size:24px;margin-bottom:8px;">⚡</div><div style="font-weight:600;font-size:14px;">Fast</div><p style="color:#71717a;font-size:12px;margin:4px 0 0 0;">30 questions in 60 seconds</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="crd"><div style="font-size:24px;margin-bottom:8px;">🎯</div><div style="font-weight:600;font-size:14px;">Verified</div><p style="color:#71717a;font-size:12px;margin:4px 0 0 0;">AI double-checks answers</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="crd"><div style="font-size:24px;margin-bottom:8px;">🌐</div><div style="font-weight:600;font-size:14px;">Bilingual</div><p style="color:#71717a;font-size:12px;margin:4px 0 0 0;">English + Hindi output</p></div>', unsafe_allow_html=True)
    st.markdown("### How to use")
    st.markdown("""
1. Get free API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Paste key in sidebar and click **Connect**
3. Upload PDFs or use pre-loaded library
4. Select chapter and click **Generate**
    """)
    st.markdown("---")
    st.caption("📲 Tip: On mobile, tap browser menu > 'Add to Home Screen' to install as app")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Generate", "Upload", "History", "Diagrams"])

with tab1:
    if total == 0:
        st.markdown('<div class="emp"><div style="font-size:40px;margin-bottom:12px;">📚</div><h3>No PDFs yet</h3><p>Go to Upload tab to add books</p></div>', unsafe_allow_html=True)
        st.stop()
    cl, cr = st.columns([1, 1], gap="large")
    with cl:
        st.markdown('<div class="lbl">Parameters</div>', unsafe_allow_html=True)
        avail = [s.title() for s in ["biology", "physics", "chemistry"] if books[s]]
        if not avail:
            st.error("No PDFs available. Upload first.")
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
    with cr:
        st.markdown('<div class="lbl">Summary</div>', unsafe_allow_html=True)
        dc = f"tg-{diff[0].lower()}"
        st.markdown(f'<div class="crd"><div style="margin-bottom:12px;"><span class="tg {dc}">{diff}</span><span class="tg tg-t">{qtype}</span></div><div class="rw"><span class="rl">Subject</span><span class="rv">{subject}</span></div><div class="rw"><span class="rl">Chapter</span><span class="rv">{ch_name[:30]}</span></div><div class="rw"><span class="rl">Topic</span><span class="rv">{topic if topic else "Full chapter"}</span></div><div class="rw"><span class="rl">Count</span><span class="rv">{num_q}</span></div><div class="rw"><span class="rl">PYQ</span><span class="rv">{"Yes" if use_pyq else "No"}</span></div></div>', unsafe_allow_html=True)
        if st.button("Generate Questions", type="primary", use_container_width=True):
            with st.spinner("Generating questions..."):
                res = generate_questions(pdf_file, ch_name, qtype, diff, num_q, topic, use_pyq)
            if res.get("success"):
                st.session_state.generated = res["data"]
                st.session_state.verify_results = {}
                st.success(f"{res['count']} questions generated")
            else:
                st.error(res.get("error", "Generation failed"))
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
            with st.expander(f"{icon}Q{i+1} - {q.get('question_english','')[:65]}..."):
                t1, t2 = st.tabs(["English", "Hindi"])
                correct = q.get('correct_answer', '')
                en_keys = [('A','option_a_english'),('B','option_b_english'),('C','option_c_english'),('D','option_d_english')]
                hi_keys = [('A','option_a_hindi'),('B','option_b_hindi'),('C','option_c_hindi'),('D','option_d_hindi')]
                with t1:
                    st.markdown(f"**{q.get('question_english','')}**")
                    for o, k in en_keys:
                        ok = o == correct
                        st.markdown(f'<div class="op{" op-ok" if ok else ""}"><span class="mk{" mk-ok" if ok else " mk-no"}">{o}</span><span>{q.get(k,"")}</span></div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.info(q.get('explanation_english', ''))
                with t2:
                    st.markdown(f"**{q.get('question_hindi','')}**")
                    for o, k in hi_keys:
                        ok = o == correct
                        st.markdown(f'<div class="op{" op-ok" if ok else ""}"><span class="mk{" mk-ok" if ok else " mk-no"}">{o}</span><span>{q.get(k,"")}</span></div>', unsafe_allow_html=True)
                    st.markdown("")
                    st.info(q.get('explanation_hindi', ''))
                st.markdown("---")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("Verify", key=f"v_{i}", use_container_width=True):
                        with st.spinner("Verifying..."):
                            r = verify_answer(q)
                            st.session_state.verify_results[i] = r
                        st.rerun()
                with b2:
                    if st.button("Humanize", key=f"h_{i}", use_container_width=True):
                        with st.spinner("Rewriting..."):
                            hq = humanize_question(q)
                            st.session_state.generated["questions"][i] = hq
                        st.rerun()
                with b3:
                    if st.button("Details", key=f"m_{i}", use_container_width=True):
                        st.session_state[f"sm_{i}"] = not st.session_state.get(f"sm_{i}", False)
                if vd:
                    cf = vd.get("confidence", 0)
                    if vd.get("matches") and cf >= 80:
                        st.success(f"Verified · {cf}% confidence · Safe to use")
                    elif vd.get("matches") and cf >= 60:
                        st.warning(f"Likely correct · {cf}% · Manual check recommended")
                    elif vd.get("verified"):
                        st.error(f"Answer mismatch · AI suggests: {vd.get('ai_answer')}")
                if st.session_state.get(f"sm_{i}", False):
                    st.markdown(f'<div class="crd"><div class="rw"><span class="rl">Topic</span><span class="rv">{q.get("topic","")}</span></div><div class="rw"><span class="rl">Subtopic</span><span class="rv">{q.get("subtopic","")}</span></div><div class="rw"><span class="rl">NCERT Ref</span><span class="rv">{q.get("ncert_reference","")}</span></div><div class="rw"><span class="rl">Common Mistake</span><span class="rv">{q.get("common_mistake","")}</span></div></div>', unsafe_allow_html=True)
                st.markdown("---")
                st.markdown("**Copy for TrackPrep**")
                e1, e2 = st.columns(2)
                with e1:
                    et = f"Q: {q.get('question_english','')}\nA) {q.get('option_a_english','')}\nB) {q.get('option_b_english','')}\nC) {q.get('option_c_english','')}\nD) {q.get('option_d_english','')}\nAnswer: {q.get('correct_answer','')}\nExplanation: {q.get('explanation_english','')}"
                    st.text_area("en", et, height=150, key=f"e_{i}", label_visibility="collapsed")
                with e2:
                    ht = f"Q: {q.get('question_hindi','')}\nA) {q.get('option_a_hindi','')}\nB) {q.get('option_b_hindi','')}\nC) {q.get('option_c_hindi','')}\nD) {q.get('option_d_hindi','')}\nAnswer: {q.get('correct_answer','')}\nExplanation: {q.get('explanation_hindi','')}"
                    st.text_area("hi", ht, height=150, key=f"hi_{i}", label_visibility="collapsed")

with tab2:
    st.markdown("### Upload PDFs")
    st.caption("Add NCERT books to your library")
    cat = st.selectbox("Category", ["biology", "physics", "chemistry", "pyq", "other"])
    files = st.file_uploader("Choose PDFs", type=["pdf"], accept_multiple_files=True)
    if files:
        if st.button("Upload All", type="primary", use_container_width=True):
            ok = 0
            for f in files:
                try:
                    save_uploaded_pdf(f, cat)
                    ok += 1
                except:
                    st.error(f"Failed: {f.name}")
            if ok:
                st.success(f"Uploaded {ok} file(s)")
                st.rerun()
    st.markdown("---")
    st.markdown("### Library")
    bk = scan_books()
    if sum(len(v) for v in bk.values()) == 0:
        st.markdown('<div class="emp"><div style="font-size:40px;margin-bottom:12px;">📁</div><h3>Empty</h3><p>Upload PDFs above</p></div>', unsafe_allow_html=True)
    else:
        for cn, pl in bk.items():
            if pl:
                st.markdown(f"**{cn.title()}** ({len(pl)})")
                for p in pl:
                    p1, p2 = st.columns([5, 1])
                    with p1:
                        st.caption(p)
                    with p2:
                        if st.button("x", key=f"d_{p}"):
                            delete_pdf(p)
                            st.rerun()

with tab3:
    st.markdown("### History")
    st.caption("Previously generated question sets")
    odir = "output"
    if os.path.exists(odir):
        fl = sorted([f for f in os.listdir(odir) if f.endswith(".json")], reverse=True)
        if not fl:
            st.info("No history yet. Generate some questions first.")
        else:
            sf = st.selectbox("Select file", fl)
            if sf:
                fp = os.path.join(odir, sf)
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                qs = data.get("questions", [])
                x1, x2 = st.columns([2, 1])
                with x1:
                    st.success(f"{len(qs)} questions loaded")
                with x2:
                    with open(fp, "r", encoding="utf-8") as f:
                        st.download_button("Download", f.read(), file_name=sf, use_container_width=True)
                for i, q in enumerate(qs):
                    with st.expander(f"Q{i+1} - {q.get('question_english','')[:60]}..."):
                        st.markdown(f"**{q.get('question_english','')}**")
                        correct = q.get('correct_answer', '')
                        for o, k in [('A','option_a_english'),('B','option_b_english'),('C','option_c_english'),('D','option_d_english')]:
                            ok = o == correct
                            st.markdown(f'<div class="op{" op-ok" if ok else ""}"><span class="mk{" mk-ok" if ok else " mk-no"}">{o}</span><span>{q.get(k,"")}</span></div>', unsafe_allow_html=True)
                        st.info(q.get('explanation_english', ''))
    else:
        st.info("Generate questions first to see history.")

with tab4:
    st.markdown("### Diagrams")
    st.caption("Extract figures from NCERT PDFs")
    if total == 0:
        st.markdown('<div class="emp"><div style="font-size:40px;margin-bottom:12px;">🖼</div><h3>No PDFs</h3><p>Upload PDFs first</p></div>', unsafe_allow_html=True)
    else:
        tb, ti = get_all_extracted_count()
        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Books", tb)
        with d2:
            st.metric("Images", ti)
        with d3:
            if st.button("Extract All", type="primary", use_container_width=True):
                with st.spinner("Extracting diagrams..."):
                    pb = st.progress(0)
                    sx = st.empty()
                    def upd(c, t, n):
                        pb.progress(c / t)
                        sx.caption(f"{c}/{t}: {n}")
                    r = extract_all_books(progress_callback=upd)
                    tot = sum(len(v) for v in r.values())
                    st.success(f"{tot} diagrams extracted")
                    st.rerun()
        st.markdown("---")
        ext = get_extracted_books()
        if not ext:
            st.info("Click 'Extract All' to extract diagrams from your PDFs.")
        else:
            bd = {b: b.replace("ncert_","").replace("_"," ").title() for b in ext}
            sb = st.selectbox("Book", ext, format_func=lambda x: bd[x])
            if sb:
                imgs = get_book_images(sb)
                if imgs:
                    pr = st.selectbox("Grid columns", [2, 3, 4], index=1)
                    st.caption(f"{len(imgs)} diagrams found")
                    for rs in range(0, len(imgs), pr):
                        cols = st.columns(pr)
                        for j, col in enumerate(cols):
                            idx = rs + j
                            if idx < len(imgs):
                                im = imgs[idx]
                                with col:
                                    try:
                                        st.image(im["path"], caption=f"Page {im['page']}")
                                        with open(im["path"], "rb") as f:
                                            st.download_button("Save", f.read(), file_name=im["filename"], mime="image/jpeg", key=f"dl_{idx}", use_container_width=True)
                                    except:
                                        st.caption("Error loading")
                else:
                    st.info("No diagrams in this book")
