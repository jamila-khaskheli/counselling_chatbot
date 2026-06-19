# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# ChromaDB needs sqlite3 >= 3.35, but Streamlit Cloud's system sqlite is older.
# Swap in the bundled pysqlite3 BEFORE anything imports chromadb. Locally (where
# sqlite3 is new enough) pysqlite3 may be absent — that's fine, we skip it.
# --------------------------------------------------------------------------
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os
import re
import html
import streamlit as st
from riasec import CODE_TO_NAME, compute_holland

# Load .env for local dev so OPENAI_API_KEY is picked up. On Streamlit Cloud the
# key comes from st.secrets instead (see load_rag_components).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

#%% Chatbot Configration
# --------------------------------------------------------------------------
OPENAI_MODEL = "gpt-4.1-mini"
TEST_PAGE = "pages/1_RIASEC_Career_Pathway_Test.py"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # must match rag_setup.py
PERSIST_DIR = "chroma_store"

CODE_TO_NAME = {
    "R": "Realistic", "I": "Investigative", "A": "Artistic",
    "S": "Social", "E": "Enterprising", "C": "Conventional",
}

PROMPT_TEMPLATE = """You are Rahnuma, a warm and encouraging AI career counsellor for 
The Citizens Foundation (TCF), a non-profit school network in Pakistan. You are speaking 
with a student who has just completed an interest assessment and is deciding what to study after Intermediate.

ABOUT THIS STUDENT
- RIASEC code: {holland_code}
- Strongest interest types: {top_names_full}
- Intermediate background: {background}

HOW TO ANSWER
1. Ground every fact in the context below, which comes from TCF's curated career resources. Any specific claim — a university or programme name, an admission requirement, a scholarship, an entry test, a fee, a date, or any number MUST come from the context. If the context does not contain what is needed, say so plainly (e.g., "I don't have specific information on that in my resources") and suggest the student check with a TCF counsellor. Never invent specifics, and never name an institution the context does not mention.
2. You can still be a supportive guide. General encouragement, and helping the student think through their interests and options in relation to their question, is welcome, as long as you do not state specific facts that are not in the context.
3. Keep it clear and friendly. Write in simple, accessible English or roman Urdu suitable for a 16–18 year old who may be the first in their family to consider university. Be concise: a few short paragraphs at most. Avoid jargon, and briefly explain any term you must use.
4. Use the student's profile only when it genuinely helps. The RIASEC profile is more important than the student's Intermediate background when discussing career fit. Treat the Intermediate background as past study history, not as a recommended future career path. Where their RIASEC interests are relevant, refer to them naturally; where they are not, just answer the question without forcing a connection.
5. Finish with exactly two follow-up questions the student might naturally want to ask next, written from the student's point of view and about topics you can help with. Put them under a short heading "You could also ask:" with each question on its own line.

Context:
{context}

Student's question: {question}

Your answer:"""

#%% Page configration
st.set_page_config(
    page_title="TCF Rahnuma: AI Counsellor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

#%% Custom Design
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")

#%% Navigation
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-brand">
            <div class="topbar-brand-icon">R</div>
            <span>TCF Rahnuma</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

#%% Chatbot only answer when the test is performed
if "riasec_scores" not in st.session_state:
    st.markdown(
        """
        <div class="empty-state">
            <div style="font-size:3rem;">🧭</div>
            <h1>Take the test first</h1>
            <p>To personalise advice, the counsellor needs to know your RIASEC Code.
            Take the 7-minute RIASEC test — then come back here.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([2, 1.2, 2])
    with c2:
        if st.button("Go to the test  →", type="primary", width="stretch"):
            st.switch_page(TEST_PAGE)
    st.stop()

# Profile state — READ from what the test page saved (no recompute = no drift)

scores = st.session_state["riasec_scores"]                 # {full_name: score}
holland_code = st.session_state.get("holland_code")
holland_letters = st.session_state.get("holland_letters")

if not holland_code or not holland_letters:
    name_to_code = {v: k for k, v in CODE_TO_NAME.items()}
    scores_code = {name_to_code[name]: s for name, s in scores.items()}
    holland_letters, holland_code = compute_holland(scores_code)

top_names = [CODE_TO_NAME[c] for c in holland_letters]

student_info = st.session_state.get("student_info", {})
student_name = student_info.get("name", "Student").strip().capitalize()
background = student_info.get("background", "")
first_name = student_name.split()[0] if student_name.split() else "there"


#%% Custom Fundtions
def humanize_source(metadata: dict) -> str:
    """Turn a raw filename into a readable citation label.
    Prefers metadata['display_name'] (set in rag_setup.py), then 'title',
    then a prettified filename."""
    for key in ("display_name", "title"):
        if metadata.get(key):
            return str(metadata[key]).strip()

    src = metadata.get("source") or metadata.get("file_path") or "TCF document"
    name = os.path.splitext(os.path.basename(str(src)))[0]
    name = re.sub(r"[_\-\.]+", " ", name).strip()
    if not name:
        return "TCF document"
    parts = []
    for token in name.split():
        if (token.isupper() and len(token) <= 4) or token.isdigit():
            parts.append(token)
        else:
            parts.append(token.capitalize())
    return " ".join(parts)


def starter_questions(holland_code, top_names, background):
    """Suggested first questions, mildly tailored to the profile/background."""
    suggestions = [
        f"What universities in Pakistan are strongest for {top_names[0].lower()}-leaning students?",
        "What scholarships might I be eligible for?",
    ]
    if background and background not in ("Select faculty", "Other"):
        suggestions.append(f"What entrance tests should a {background} student prepare for?")
    else:
        suggestions.append("What entrance tests should I prepare for?")
    return suggestions


def render_user_message(content: str):
    safe = html.escape(content).replace("\n", "<br>")
    st.markdown(
        f'<div class="chat-row from-user">'
        f'<div class="chat-bubble chat-bubble-user">{safe}</div></div>',
        unsafe_allow_html=True,
    )


def render_ai_message(content: str, sources=None):
    # Minimal markdown -> HTML: bold **x** and paragraph/line breaks.
    safe = html.escape(content)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = safe.replace("\n\n", "</p><p>").replace("\n", "<br>")
    safe = f"<p>{safe}</p>"

    sources_html = ""
    if sources:
        items = " · ".join(html.escape(s) for s in sources)
        sources_html = (
            '<div class="chat-sources">'
            '<span class="chat-sources-label">📎 Sources:</span>'
            f"{items}</div>"
        )

    st.markdown(
        f'<div class="chat-row">'
        f'<div class="chat-avatar">R</div>'
        f'<div class="chat-bubble chat-bubble-ai">{safe}{sources_html}</div></div>',
        unsafe_allow_html=True,
    )


def render_feedback(msg_idx: int):
    """Native thumbs feedback under an AI reply."""
    existing = st.session_state.feedback.get(msg_idx)
    if existing is not None:
        label = "Thanks for the feedback!" if existing == "up" else "Thanks — we'll improve."
        st.caption(f"✓ {label}")
        return
    
    sentiment = st.feedback("thumbs", key=f"fb_{msg_idx}")
    if sentiment is not None:
        rating = "up" if sentiment == 1 else "down"
        st.session_state.feedback[msg_idx] = rating

        answer = st.session_state.messages[msg_idx]["content"]
        question = ""
        if msg_idx > 0 and st.session_state.messages[msg_idx - 1]["role"] == "user":
            question = st.session_state.messages[msg_idx - 1]["content"]

        try:
            from db import save_feedback
            save_feedback(student_name, holland_code, msg_idx, rating, question, answer)
        except Exception as e:
            print("feedback save failed:", e)  # log, don't crash the UI

        st.rerun()


#%% App architecture - RAG components (local embeddings + ChromaDB retrieval, OpenAI generation)

@st.cache_resource(show_spinner=False)
def load_rag_components():
    """Build retriever + LLM. Returns (components, status_message).
    status_message is None on success, else a user-facing reason."""
    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        return None, (f"Missing package: <code>{e.name}</code>. "
                      f"Run <code>pip install -r requirements.txt</code>.")

    if not os.path.isdir(PERSIST_DIR):
        return None, ("Knowledge base not found. Build it with "
                      "<code>python rag_setup.py</code> and commit "
                      "<code>chroma_store/</code> to the repo.")

    # OpenAI key: Streamlit Cloud secrets first, then env var (local .env).
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        openai_key = None
    openai_key = openai_key or os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        return None, ("<code>OPENAI_API_KEY</code> is not set. On Streamlit Cloud "
                      "add it under app → Settings → Secrets; locally add it to "
                      "<code>.streamlit/secrets.toml</code> or a <code>.env</code> file.")

    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
        vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
        retriever = vectordb.as_retriever(search_kwargs={"k": 6})

        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=openai_key,
            temperature=0.3,
            max_tokens=512,
        )
        return {"retriever": retriever, "llm": llm}, None
    except Exception as e:
        return None, f"Failed to initialise components: <code>{html.escape(str(e))}</code>"


def get_response(user_query: str, holland_code: str, top_names: list):
    """Returns dict: {content, sources, error}."""
    components, status = load_rag_components()
    if components is None:
        return {
            "content": (
                "I can't reach my knowledge base right now. Once it's connected, "
                f"I'll be able to answer this for your **{holland_code}** profile.\n\n"
                f"Your question: *{user_query}*"
            ),
            "sources": [],
            "error": status,
        }

    retriever = components["retriever"]
    llm = components["llm"]

    try:
        # 1. Retrieve with the CLEAN question (profile goes into the prompt only).
        docs = retriever.invoke(user_query)
        context = "\n\n".join(d.page_content for d in docs) if docs else ""

        # 2. Generate with the profile-aware prompt (this is the OpenAI call).
        prompt = PROMPT_TEMPLATE.format(
            holland_code=holland_code,
            top_names_full=", ".join(top_names),
            background=bg_line,
            context=context,
            question=user_query,
        )
        raw = llm.invoke(prompt)
        answer = (raw.content if hasattr(raw, "content") else str(raw)).strip()

        # 3. Humanised, deduplicated sources.
        sources, seen = [], set()
        for d in docs[:3]:
            label = humanize_source(d.metadata or {})
            if label not in seen:
                sources.append(label)
                seen.add(label)

        if not answer:
            answer = ("I couldn't find relevant guidance in TCF's resources for that "
                      "question. Try rephrasing, or ask a TCF counsellor directly.")
            sources = []

        return {"content": answer, "sources": sources, "error": None}

    except Exception as e:
        import traceback
        traceback.print_exc()          # full error in your terminal
        return {
            "content": f"⚠️ DEBUG — {type(e).__name__}: {e},Something went wrong while looking that up. Please try again in a moment.",
            "sources": [],
            "error": str(e),
        }


def handle_turn(user_text: str):
    """Append the user message, get a grounded reply, append it."""
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.spinner("Looking that up in TCF's resources..."):
        response = get_response(user_text, holland_code, top_names)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["content"],
        "sources": response.get("sources", []),
    })


# --------------------------------------------------------------------------
# Session state init
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            f"Hi {first_name}! 👋 Your results suggest that you're strongest in "
            f"**{', '.join(top_names)}**. Let's explore discipline/program, university, "
            f"scholarships, and career paths that could be a great fit for you."
            f"\n\nPick a question below, or ask me anything!"
        ),
        "sources": [],
    }]

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# --------------------------------------------------------------------------
# Page content
# --------------------------------------------------------------------------
st.markdown('<div class="page-wrap page-wrap-chat">', unsafe_allow_html=True)

# ----- Profile card -----
bg_line = (
    f'<span class="profile-card-meta-item"><strong>Background:</strong> '
    f'{html.escape(background)}</span>'
    if background and background != "Select faculty" else ""
)
st.markdown(
    f"""
    <div class="profile-card">
        <div class="profile-card-top">
            <div>
                <div class="profile-card-greeting">Talking with</div>
                <h2 class="profile-card-name">{html.escape(student_name)}</h2>
            </div>
            <div class="profile-card-code-block">
                <div class="profile-card-code-label">RIASEC Code</div>
                <div class="profile-card-code">{html.escape(holland_code)}</div>
            </div>
        </div>
        <div class="profile-card-meta">
            <span class="profile-card-meta-item"><strong>Top types:</strong> {', '.join(top_names)}</span>
            {bg_line}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----- Status banner if RAG unavailable -----
_, _status = load_rag_components()
if _status:
    st.markdown(
        f'<div class="status-banner"><strong>Heads up:</strong> the knowledge base '
        f"isn't fully connected yet — {_status} Answers will be limited until that's fixed.</div>",
        unsafe_allow_html=True,
    )

# ----- Process a pending prompt from a starter-chip click -----
if st.session_state.pending_prompt:
    pending = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    handle_turn(pending)

# ----- Render chat history -----
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        render_ai_message(msg["content"], msg.get("sources"))
        if idx > 0:                       # no feedback on the opening welcome
            render_feedback(idx)

# ----- Starter chips (only before any real conversation) -----
if len(st.session_state.messages) == 1:
    st.markdown(
        '<p class="starters-label">Try one of these to start</p>',
        unsafe_allow_html=True,
    )
    # st.container(key=...) renders a <div class="st-key-starters_grid"> whose
    # children ARE nested in the DOM, so style.css can style these buttons as
    # chips via `.st-key-starters_grid div.stButton > button` — no JS hack.
    with st.container(key="starters_grid"):
        cols = st.columns(2, gap="small")
        for i, q in enumerate(starter_questions(holland_code, top_names, background)):
            with cols[i % 2]:
                if st.button(q, key=f"starter_{i}", width="stretch"):
                    st.session_state.pending_prompt = q
                    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Chat input (sticks to the bottom)
# --------------------------------------------------------------------------
if prompt := st.chat_input("Ask about universities, scholarships, fields of study..."):
    handle_turn(prompt)
    st.rerun()


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Your Profile")
    st.markdown(f"**{student_name}**")
    if background and background != "Select faculty":
        st.caption(background)
    st.markdown(f"RIASEC Code: **`{holland_code}`**")
    st.caption(", ".join(top_names))

    st.divider()
    st.markdown("### Conversation")
    if st.button("Clear chat", width="stretch"):
        welcome = st.session_state.messages[0] if st.session_state.messages else None
        st.session_state.messages = [welcome] if welcome else []
        st.session_state.feedback = {}
        st.rerun()
    if st.button("Back to results", width="stretch"):
        st.session_state.wizard_step = 3
        st.switch_page(TEST_PAGE)

    st.divider()
    st.caption(f"Model: `{OPENAI_MODEL}`")
