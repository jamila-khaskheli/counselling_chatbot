
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from db import init_db, save_test_result
from riasec import CODE_TO_NAME, compute_holland, QUESTIONS, DESCRIPTIONS, DISCIPLINE_MAP, RELATED_PATHWAYS, BACKGROUND_OPTIONS

init_db()

#%% Page Configration 
st.set_page_config(
    page_title="TCF Rahnuma: Career Assessment",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
#%% State init
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1

if "answers" not in st.session_state:
    st.session_state.answers = {}  # {q_index: bool}

if "test_completed" not in st.session_state:
    st.session_state.test_completed = False

#%% Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

#%% Navigation Bar
def navbar():
    st.markdown(
        """
        <div class="navbar">
            <div class="navbar-brand">
                <div class="navbar-brand-icon">🎓</div>
                <span>TCF Rahnuma</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_indicator(current: int):
    def cls(step_num):
        if step_num < current:
            return "step-dot complete"
        if step_num == current:
            return "step-dot active"
        return "step-dot"

    def line_cls(after_step):
        return "step-line complete" if after_step < current else "step-line"

    st.markdown(
        f"""
        <div class="step-indicator">
            <div class="{cls(1)}">1</div>
            <div class="{line_cls(1)}"></div>
            <div class="{cls(2)}">2</div>
            <div class="{line_cls(2)}"></div>
            <div class="{cls(3)}">{'✓' if current > 3 else '3'}</div>
        </div>
        <div class="step-labels">
            <span class="step-label {'active' if current == 1 else ''}">Questions</span>
            <span class="step-label {'active' if current == 2 else ''}">Your info</span>
            <span class="step-label {'active' if current == 3 else ''}">Your results</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tally_scores():
    """Compute per-type scores from current st.session_state.answers."""
    scores_code = {c: 0 for c in CODE_TO_NAME}
    for idx, (_, code) in enumerate(QUESTIONS):
        if st.session_state.answers.get(idx, False):
            scores_code[code] += 1
    return scores_code

def validate_cnic(cnic: str) -> bool:
    """Loose Pakistani CNIC validation: 13 digits, optionally formatted as 5-7-1."""
    digits = "".join(ch for ch in cnic if ch.isdigit())
    return len(digits) == 13


# ==============================================================================
# Step 1 — Questions
# ==============================================================================
def render_step_questions():
    render_step_indicator(1)

    st.markdown('<p class="page-eyebrow">Step 1 of 3</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Tick the statements that sound like you</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Read each one. Tick the ones that genuinely describe you and '
        "not the ones that sound impressive. There are no right or wrong answers.</p>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    with st.form("questions_form", clear_on_submit=False):
        st.markdown(
            f'<p class="question-form-helper">'
            f'<strong>{len(QUESTIONS)} statements</strong> · '
            f'Tick as many as feel true · Takes about 5–7 minutes</p>',
            unsafe_allow_html=True,
        )

        # Render in two columns
        col_a, col_b = st.columns(2, gap="small")
        half = (len(QUESTIONS) + 1) // 2
        for index, (text, _) in enumerate(QUESTIONS):
            target = col_a if index < half else col_b
            with target:
                # Preserve prior selection if revisiting
                default = st.session_state.answers.get(index, False)
                checked = st.checkbox(
                    f"{index + 1}. {text}",
                    key=f"q_{index}",
                    value=default,
                )
                # Update session state inline so going Back preserves answers
                st.session_state.answers[index] = checked

        st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("Continue →", type="primary", width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        # Save final state from form
        for index in range(len(QUESTIONS)):
            st.session_state.answers[index] = st.session_state.get(f"q_{index}", False)

        selected = sum(1 for v in st.session_state.answers.values() if v)
        if selected == 0:
            st.error("Please tick at least a few statements that resonate with you before continuing.")
        else:
            st.session_state.wizard_step = 2
            st.rerun()


# ==============================================================================
# Step 2 — Your info
# ==============================================================================
def render_step_info():
    render_step_indicator(2)

    st.markdown('<p class="page-eyebrow">Step 2 of 3</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Almost there — just a few details</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">So we can save your result and a TCF counsellor can follow up '
        "if you want them to.</p>",
        unsafe_allow_html=True,
    )

    # Use columns to center the form
    _, mid, _ = st.columns([1, 4, 1])
    with mid:
        st.markdown('<div>', unsafe_allow_html=True)
        with st.form("info_form"):
            student_name = st.text_input(
                "Your name *",
                value=st.session_state.get("student_info", {}).get("name", ""),
                placeholder="e.g. Jamila",
            )

            background = st.selectbox(
                "Academic background *",
                BACKGROUND_OPTIONS,
                index=BACKGROUND_OPTIONS.index(
                    st.session_state.get("student_info", {}).get("background", "Select faculty")
                ) if st.session_state.get("student_info", {}).get("background") in BACKGROUND_OPTIONS else 0,
                help="Pick the Intermediate field you're studying or just completed.",
            )
            student_id = st.text_input(
                "B form / CNIC",
                value=st.session_state.get("student_info", {}).get("id", ""),
                placeholder="13 digits, e.g. 3520212345678",
                help="3520212345678",
            )

            st.markdown('<div style="height: 0.75rem;"></div>', unsafe_allow_html=True)
            col_back, col_next = st.columns(2)
            with col_back:
                back = st.form_submit_button("← Back", width="stretch")
            with col_next:
                submit = st.form_submit_button("See my results →", type="primary", width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    if back:
        st.session_state.wizard_step = 1
        st.rerun()

    if submit:
        errors = []
        if not student_name.strip():
            errors.append("Please enter your name.")
        if background == "Select faculty":
            errors.append("Please select your academic background.")
        if not student_id.strip():
            errors.append("Please enter your B-form or CNIC.")
        if student_id.strip() and not validate_cnic(student_id):
            errors.append("CNIC should be 13 digits (e.g. 3520212345678). ")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Score and persist
            scores_code = tally_scores()
            holland_letters, holland_code = compute_holland(scores_code)

            st.session_state.student_info = {
                "name": student_name.strip(),
                "id": student_id.strip(),
                "background": background,
                "share_cnic": bool(student_id.strip()),
            }
            st.session_state.riasec_scores_code = scores_code
            st.session_state.riasec_scores = {
                CODE_TO_NAME[c]: v for c, v in scores_code.items()
            }
            st.session_state.holland_code = holland_code
            st.session_state.holland_letters = holland_letters
            st.session_state.test_completed = True

            try:
                st.session_state.result_id = save_test_result(
                    result_id=st.session_state.get("result_id"),
                    name=student_name.strip(),
                    cnic=student_id.strip() or None,
                    background=background,
                    holland_code=holland_code,
                    scores=scores_code,
                    answers={str(k): v for k, v in st.session_state.answers.items()},
                    consent_followup=bool(student_id.strip()),
                )
            except Exception as e:
                st.session_state.save_error = str(e)

            st.session_state.wizard_step = 3
            st.rerun()


# ==============================================================================
# Step 3 — Results
# ==============================================================================
def render_score_chart(scores_code, holland_letters):
    """Horizontal bar chart, teal palette, highlighting top-3."""
    type_order = list(CODE_TO_NAME.keys())  # R, I, A, S, E, C
    df = pd.DataFrame({
        "Type": [CODE_TO_NAME[c] for c in type_order],
        "Score": [scores_code[c] for c in type_order],
        "Code": type_order,
    })

    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = ["#0F766E" if c in holland_letters else "#CBD5E1" for c in type_order]
    bars = ax.barh(df["Type"], df["Score"], color=colors, height=0.65)
    ax.set_xlim(0, 7.5)
    ax.set_xticks(range(0, 8))
    ax.invert_yaxis()  # so Realistic appears on top
    ax.set_xlabel("Score (out of 7)", color="#64748B", fontsize=10)
    ax.tick_params(colors="#475569")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#E2E8F0")
    ax.spines["bottom"].set_color("#E2E8F0")
    ax.grid(axis="x", color="#F1F5F9", linewidth=1)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, df["Score"]):
        ax.text(value + 0.15, bar.get_y() + bar.get_height() / 2,
                str(value), va="center", fontweight="600", color="#0F172A", fontsize=10)

    fig.patch.set_facecolor("white")
    plt.tight_layout()
    return fig


def render_step_results():
    render_step_indicator(3)

    info = st.session_state.student_info
    scores_code = st.session_state.riasec_scores_code
    holland_letters = st.session_state.holland_letters
    holland_code = st.session_state.holland_code

    # ---- Holland code reveal ------------------------------------------------
    type_names = [CODE_TO_NAME[c] for c in holland_letters]
    names_html = '<span>·</span>'.join(f' {n} ' for n in type_names)
    st.markdown(
        f"""
        <div class="code-reveal">
            <p class="code-reveal-label">{info['name']}'s RIASEC Code</p>
            <h1 class="code-reveal-letters">{holland_code}</h1>
            <p class="code-reveal-names">{names_html}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Profile summary ----------------------------------------------------
    cnic_line = ""
    if info.get("share_cnic"):
        cnic_line = f"<br><strong>CNIC on file:</strong> {info['id']}"
    st.markdown(
        f"""
        <div class="profile-summary">
            <strong>Background:</strong> {info['background']}{cnic_line}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Confidence notices -------------------------------------------------
    top_score = scores_code[holland_letters[0]]
    second_score = scores_code[holland_letters[1]] if len(holland_letters) >= 2 else None
    third_score = scores_code[holland_letters[2]] if len(holland_letters) >= 3 else None
    selected_total = sum(scores_code.values())

    if top_score <= 2:
        st.markdown(
            f"""
            <div class="notice notice-warn">
              <strong>A note on confidence:</strong> your scores are quite low across the board
              ({selected_total} total selections). The Holland code below is your best-fit pattern,
              but it's based on relatively little signal. Consider retaking and ticking anything
              you're even mildly drawn to.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif top_score - third_score <= 1:
        st.markdown(
            f"""
            <div class="notice notice-info">
              <strong>Heads up:</strong> your top scores are very close together it suggests broad, multi-directional interests. Treat all
                directions as worth exploring.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Score breakdown ----------------------------------------------------
    st.markdown(
        '<h2 class="result-section-title">Your score across the six types</h2>',
        unsafe_allow_html=True,
    )
    st.pyplot(render_score_chart(scores_code, holland_letters), width="stretch")
    st.caption("Highlighted bars are your top interest types together they make your Holland code.")

    # ---- What it means ------------------------------------------------------
    st.markdown(
        '<h2 class="result-section-title">What this says about you</h2>',
        unsafe_allow_html=True,
    )
    for code in holland_letters:
        desc = DESCRIPTIONS[code]
        score = scores_code[code]
        st.markdown(
            f"""
            <div class="type-card">
                <div class="type-card-letter">{code}</div>
                <div class="type-card-body">
                    <div class="type-card-head">
                        <span class="type-card-name">{desc['title']}</span>
                        <span class="type-card-score">{score}</span>
                    </div>
                    <p class="type-card-text">{desc['desc_first_person']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Background-aware pathways -----------------------------------------
    st.markdown(
        '<h4>Want to continue in the same field you studied in Intermediate?</h4>'
        '<h2 class="result-section-title">Recommended Study Pathways for You</h2>',
        unsafe_allow_html=True,
    )

    bg_map = DISCIPLINE_MAP.get(info["background"])
    fallback_used = bg_map is None
    if fallback_used:
        bg_map = RELATED_PATHWAYS

    MIN_PRIMARY = 3
    MAX_BACKUP = 2

    # Distinct code letters, highest score first
    letters = []
    for code in holland_letters:
        if code in bg_map and code not in letters:
            letters.append(code)

    # Stable per-session seed: keeps suggestions fixed across Streamlit reruns,
    # but varies them between students/sessions.
    if "rec_seed" not in st.session_state:
        st.session_state["rec_seed"] = random.randrange(1_000_000)
    rng = random.Random(st.session_state["rec_seed"])

    # Shuffled working pool for each letter
    pools = {c: list(bg_map.get(c, [])) for c in letters}
    for c in pools:
        rng.shuffle(pools[c])

    used = set()

    def draw(n):
        """Round-robin: one programme per letter per pass, in priority order."""
        picked = []
        progress = True
        while len(picked) < n and progress:
            progress = False
            for c in letters:
                if len(picked) >= n:
                    break
                while pools[c] and pools[c][0] in used:   # skip anything already taken
                    pools[c].pop(0)
                if pools[c]:
                    opt = pools[c].pop(0)
                    picked.append((c, opt))
                    used.add(opt)
                    progress = True
        return picked

    # Primary: one from each code letter, but never fewer than MIN_PRIMARY
    target = max(MIN_PRIMARY, len(letters))
    primary = draw(target)

    # Fallback: a thin bucket left us short -> borrow from this stream's other letters
    if len(primary) < MIN_PRIMARY:
        for c in (x for x in "RIASEC" if x not in letters and bg_map.get(x)):
            for opt in bg_map[c]:
                if len(primary) >= MIN_PRIMARY:
                    break
                if opt not in used:
                    primary.append((c, opt))
                    used.add(opt)
            if len(primary) >= MIN_PRIMARY:
                break

    backup = draw(MAX_BACKUP)  # genuine second choices from the same code letters

    if not primary:
        st.warning("No matching disciplines found. Please consult a counsellor for manual guidance.")
    else:
        primary_pills = "".join(
            f'<span class="pathway-pill">{opt} · '
            f'<em style="opacity:0.7">{DESCRIPTIONS[c]["title"]}</em></span>'
            for c, opt in primary
        )

        backup_html = ""
        if backup:
            backup_label = "Backup option" if len(backup) == 1 else "Backup options"
            backup_pills = "".join(
                f'<span class="pathway-pill pathway-pill-secondary">{opt} · '
                f'<em style="opacity:0.7">{DESCRIPTIONS[c]["title"]}</em></span>'
                for c, opt in backup
            )
            backup_html = (
                '<div class="pathway-group">'
                f'<div class="pathway-group-label">{backup_label}</div>'
                f'{backup_pills}'
                '</div>'
            )

        fallback_note = ""
        if fallback_used:
            fallback_note = (
                '<div class="notice notice-info" style="margin-bottom:1.25rem;">'
                "Your background isn't mapped to a specific track yet, so these are "
                "general recommendations. A counsellor can help personalise further."
                "</div>"
            )

        st.markdown(
            f"""
            {fallback_note}
            <div class="pathways-card">
                <div class="pathway-group">
                    <div class="pathway-group-label">Primary pathways</div>
                    {primary_pills}
                </div>
                {backup_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    # ---- Career families ----------------------------------------------------
    st.markdown(
        f'<h2 class="result-section-title">Based on your interests and strengths, you might explore...</h2>',
        unsafe_allow_html=True,
    )
    for code in holland_letters:
        desc = DESCRIPTIONS[code]
        majors = " · ".join(desc["majors"])
        st.markdown(
            f"""
            <div class="career-family">
                <div class="career-family-label">{desc['title']}</div>
                <div class="career-family-list">{majors}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(f"""
        <div class="career-family">
            <div class="type-card-body">
                <div class="type-card-head">
                    <span class="type-card-name">Congratulations!!</span>
                </div>
                <p class="type-card-text">You have completed your personality assessment. This is your starting point; not your finishing point. It is designed to give you a clear overview of the fields available to you and the programs you can study.</p>
            </div>
        </div>
        <div class="type-card">
            <div class="type-card-body">
                <div class="type-card-head">
                    <span class="type-card-name">STEP 1 — Start here</span>
                </div>
                <p class="type-card-text"><strong>Ask yourself:</strong> Does this feel like something I could see myself doing?</p>
            </div>
            <div class="type-card-body">
                <div class="type-card-head">
                    <span class="type-card-name">STEP 2 — Go deeper with university websites</span>
                </div>
                <p class="type-card-text">Once you have a shortlist of fields, visit the official websites of the universities listed under 'Universities on Policy'. Read about their specific programs, and admission requirements.</p>
            </div>            
            <div class="type-card-body">
                <div class="type-card-head">
                    <span class="type-card-name">STEP 3 — Talk to AI Counsellor</span>
                </div>
                <p class="type-card-text">Use AI Counsellor to ask follow-up questions and explore further. It can help explain concepts in simple language</p>
        </div>
        """, unsafe_allow_html=True,)

    # ---- Actions ------------------------------------------------------------
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("← Review my answers", width="stretch"):
            st.session_state.wizard_step = 1
            st.rerun()
    with col2:
        if st.button("Retake from scratch", width="stretch"):
            for k in list(st.session_state.keys()):
                if k.startswith("q_") or k in {
                    "answers", "wizard_step", "test_completed",
                    "riasec_scores", "riasec_scores_code",
                    "holland_code", "holland_letters", "student_info",
                }:
                    del st.session_state[k]
            st.rerun()
    with col3:
        if st.button("Universities on Policy →", type="primary", width="stretch"):
            st.switch_page("pages/3_Universities_on_Policy.py")
    with col4:
        if st.button("Talk to AI counsellor →", type="primary", width="stretch"):
            st.switch_page("pages/2_Career_Counsellor_Chat.py")

    st.markdown(
        '<p class="footer-note">Your result is saved. You can come back to this page any time.</p>',
        unsafe_allow_html=True,
    )


# ==============================================================================
# Main
# ==============================================================================
navbar()

st.markdown('<div class="page-wrap page-wrap-wide">', unsafe_allow_html=True)

# If results already exist and they're not actively editing, skip to step 3
if st.session_state.test_completed and st.session_state.wizard_step < 3:
    st.session_state.wizard_step = 3

if st.session_state.wizard_step == 1:
    render_step_questions()
elif st.session_state.wizard_step == 2:
    render_step_info()
else:
    render_step_results()

st.markdown('</div>', unsafe_allow_html=True)
