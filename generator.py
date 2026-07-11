import google.generativeai as genai
import PyPDF2
import os
import json
import re
from datetime import datetime

BOOKS_FOLDER = "../books"
OUTPUT_FOLDER = "../output"
_model = None


def setup_ai(api_key):
    global _model
    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel('gemini-flash-latest')
    return _model


def scan_books():
    books = {"biology": [], "physics": [], "chemistry": [], "pyq": [], "other": []}
    if not os.path.exists(BOOKS_FOLDER):
        return books
    for f in os.listdir(BOOKS_FOLDER):
        if not f.endswith(".pdf"):
            continue
        fl = f.lower()
        if "pyq" in fl or "neet_20" in fl:
            books["pyq"].append(f)
        elif "bio" in fl:
            books["biology"].append(f)
        elif "phy" in fl:
            books["physics"].append(f)
        elif "chem" in fl:
            books["chemistry"].append(f)
        else:
            books["other"].append(f)
    for k in books:
        books[k].sort()
    return books


def get_chapter_name(filename):
    name = filename.replace(".pdf", "").replace("ncert_", "").replace("_", " ")
    name = re.sub(r'(bio|phy|chem)(11|12)\s*ch\d+\s*', '', name)
    return name.strip().title()


def read_pdf(pdf_path):
    try:
        pdf = PyPDF2.PdfReader(pdf_path)
        text = ""
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t
        return text
    except:
        return ""


def search_pyqs(topic, pyq_files):
    if not pyq_files or not topic:
        return ""
    matches = []
    for pf in pyq_files[:3]:
        content = read_pdf(os.path.join(BOOKS_FOLDER, pf))
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if topic.lower() in line.lower():
                start = max(0, i - 2)
                end = min(len(lines), i + 5)
                matches.append('\n'.join(lines[start:end]))
                if len(matches) >= 5:
                    break
    return '\n---\n'.join(matches[:5])


def clean_text(text):
    if not text:
        return text
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    for i, s in enumerate("₀₁₂₃₄₅₆₇₈₉"):
        text = text.replace(s, str(i))
    for i, s in enumerate("⁰¹²³⁴⁵⁶⁷⁸⁹"):
        text = text.replace(s, str(i))
    return text.strip()


def clean_json(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def clean_data(data):
    if "questions" in data:
        for q in data["questions"]:
            for key in q:
                if isinstance(q[key], str):
                    q[key] = clean_text(q[key])
    return data


def build_prompt(content, chapter_name, qtype, difficulty, num_questions, topic, pyq_context=""):
    type_formats = {
        "General MCQ": "Simple direct MCQ with 4 options",
        "Assertion & Reason": "Assertion (A) and Reason (R) with standard 4 options",
        "Statement Based": "3-4 numbered statements with combination options",
        "Match the Following": "Two columns with 4 items each",
        "Image Question": "Include [IMAGE: description] tag",
        "Graphical": "Include [GRAPH: description] tag"
    }
    topic_line = f"FOCUS TOPIC: {topic}" if topic else "Cover important concepts"
    pyq_section = f"\n\nPYQ REFERENCES:\n{pyq_context[:3000]}\n" if pyq_context else ""
    
    prompt = f"""You are a SENIOR NEET EXAMINER with 20 years experience.
Generate {num_questions} authentic NEET-level questions.

CHAPTER: {chapter_name}
TYPE: {qtype}
DIFFICULTY: {difficulty}
{topic_line}

FORMAT: {type_formats[qtype]}

NCERT CONTENT:
{content[:10000]}
{pyq_section}

FORMATTING RULES:
1. NO LaTeX NO dollar signs NO backslash commands
2. Chemical formulas plain text: H2SO4 Fe2O3
3. Superscripts plain: Ca2+ Na+
4. NO markdown formatting
5. Write like human examiner not AI
6. Minimal punctuation natural flow
7. 100% accurate per NCERT
8. Controversial = NCERT view
9. Hinglish explanation teacher style
10. Cross verify each answer

OUTPUT (STRICT JSON):
{{
  "questions": [
    {{
      "question_english": "text",
      "question_hindi": "hindi text",
      "option_a_english": "A",
      "option_b_english": "B",
      "option_c_english": "C",
      "option_d_english": "D",
      "option_a_hindi": "A hindi",
      "option_b_hindi": "B hindi",
      "option_c_hindi": "C hindi",
      "option_d_hindi": "D hindi",
      "correct_answer": "A",
      "explanation_english": "80-120 words",
      "explanation_hindi": "hinglish",
      "topic": "topic",
      "subtopic": "subtopic",
      "ncert_reference": "ref",
      "image_description": "null OR desc",
      "common_mistake": "error"
    }}
  ]
}}

Return ONLY valid JSON."""
    return prompt


def generate_questions(pdf_file, chapter_name, qtype, difficulty, num_questions, topic="", use_pyq=False):
    global _model
    if not _model:
        return {"error": "AI not initialized"}
    pdf_path = os.path.join(BOOKS_FOLDER, pdf_file)
    if not os.path.exists(pdf_path):
        return {"error": f"PDF not found: {pdf_file}"}
    content = read_pdf(pdf_path)
    if not content:
        return {"error": "Could not read PDF"}
    pyq_context = ""
    if use_pyq and topic:
        books = scan_books()
        pyq_context = search_pyqs(topic, books["pyq"])
    prompt = build_prompt(content, chapter_name, qtype, difficulty, num_questions, topic, pyq_context)
    try:
        response = _model.generate_content(prompt)
        cleaned = clean_json(response.text)
        data = json.loads(cleaned)
        data = clean_data(data)
        save_output(data, chapter_name, qtype)
        return {"success": True, "data": data, "count": len(data.get("questions", []))}
    except json.JSONDecodeError as e:
        return {"error": f"JSON error: {str(e)}", "raw": response.text}
    except Exception as e:
        return {"error": str(e)}


def verify_answer(question_data):
    global _model
    if not _model:
        return {"verified": False, "confidence": 0}
    
    q = question_data
    verify_prompt = f"""You are a NEET expert reviewer. Independently solve this MCQ.

QUESTION: {q.get('question_english', '')}

OPTIONS:
A) {q.get('option_a_english', '')}
B) {q.get('option_b_english', '')}
C) {q.get('option_c_english', '')}
D) {q.get('option_d_english', '')}

CLAIMED ANSWER: {q.get('correct_answer', '')}

Solve independently and return JSON:
{{
  "correct_answer": "A/B/C/D",
  "matches_claimed": true/false,
  "confidence": 85,
  "notes": "brief note",
  "should_accept": true/false
}}

Return ONLY valid JSON."""
    
    try:
        response = _model.generate_content(verify_prompt)
        text = clean_json(response.text)
        result = json.loads(text)
        return {
            "verified": True,
            "confidence": result.get("confidence", 0),
            "matches": result.get("matches_claimed", False),
            "ai_answer": result.get("correct_answer", ""),
            "should_accept": result.get("should_accept", False),
            "notes": result.get("notes", "")
        }
    except Exception as e:
        return {"verified": False, "confidence": 0, "notes": str(e)}


def humanize_question(question_data):
    global _model
    if not _model:
        return question_data
    
    q = question_data
    humanize_prompt = f"""Rewrite this AI-generated question to sound completely human-written by a teacher.

ORIGINAL:
Q: {q.get('question_english', '')}
A) {q.get('option_a_english', '')}
B) {q.get('option_b_english', '')}
C) {q.get('option_c_english', '')}
D) {q.get('option_d_english', '')}
Explanation: {q.get('explanation_english', '')}

RULES:
1. Vary sentence structure naturally
2. Use conversational teacher tone
3. Change 30% of wording
4. Keep same meaning and answer
5. Reduce punctuation naturally
6. Sound like a real Indian teacher

Return JSON:
{{
  "question_english": "rewritten",
  "option_a_english": "text",
  "option_b_english": "text",
  "option_c_english": "text",
  "option_d_english": "text",
  "explanation_english": "humanized"
}}

Return ONLY valid JSON."""
    
    try:
        response = _model.generate_content(humanize_prompt)
        text = clean_json(response.text)
        humanized = json.loads(text)
        q.update({k: v for k, v in humanized.items() if v})
        return q
    except:
        return question_data


def save_output(data, chapter_name, qtype):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    ts = datetime.now().strftime("%m%d_%H%M")
    ch = re.sub(r'[^a-z0-9]+', '_', chapter_name.lower())[:25]
    qt = re.sub(r'[^a-z0-9]+', '_', qtype.lower())[:15]
    jf = f"{OUTPUT_FOLDER}/{ch}_{qt}_{ts}.json"
    with open(jf, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tf = f"{OUTPUT_FOLDER}/{ch}_{qt}_{ts}.txt"
    with open(tf, "w", encoding="utf-8") as f:
        f.write(f"CHAPTER: {chapter_name}\nTYPE: {qtype}\n")
        f.write(f"DATE: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n{'='*60}\n\n")
        for i, q in enumerate(data.get("questions", []), 1):
            f.write(f"{'='*60}\nQ{i}\n{'='*60}\n\n")
            f.write(f"[EN] {q.get('question_english', '')}\n\n")
            f.write(f"A) {q.get('option_a_english', '')}\nB) {q.get('option_b_english', '')}\n")
            f.write(f"C) {q.get('option_c_english', '')}\nD) {q.get('option_d_english', '')}\n\n")
            f.write(f"ANS: {q.get('correct_answer', '')}\n\n")
            f.write(f"EXP: {q.get('explanation_english', '')}\n\n")
            f.write(f"[HI] {q.get('question_hindi', '')}\n\n")
            f.write(f"A) {q.get('option_a_hindi', '')}\nB) {q.get('option_b_hindi', '')}\n")
            f.write(f"C) {q.get('option_c_hindi', '')}\nD) {q.get('option_d_hindi', '')}\n\n")
            f.write(f"EXP: {q.get('explanation_hindi', '')}\n")
            f.write(f"REF: {q.get('ncert_reference', '')}\n\n")
    return jf