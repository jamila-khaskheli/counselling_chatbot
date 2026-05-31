import streamlit as st

#%% Page Configration 
st.set_page_config(
    page_title="TCF Rahnuma: Find a career that fits you",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)
#%% Routing
TEST_PAGE = "pages/1_RIASEC_Career_Pathway_Test.py"
COUNSELLOR="pages/2_Career_Counsellor_Chat.py"

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
            <div class="navbar-links">
                <a href="#about">About RIASEC</a>
                <a href="#how">How it works</a>
                <a href="#counsellor">AI counsellor</a>
                <a href="#faq">FAQ</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
#%% Hero Section
def hero_section():
    st.markdown(
        """
         <div class="hero">
        <span class="hero-badge">🌱 Based on Holland's RIASEC Theory</span>
        <h1 class="hero-title">
            Not sure what degree to pursue <br/>
            <span class="accent">after Intermediate?</span>
        </h1>
        <p class="hero-subtitle">
            In about 7 minutes, find academic and career paths that 
            feel right for the way you think and work. Based on the research-backed RIASEC framework. 
        </p>
        <p class="hero-subtitle">
        After your results, you can ask follow-up questions to your AI career counsellor.
        </p>
    </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 1.2, 2])
    with c2:
        if st.button("Start my test  →", key="hero_cta", width="stretch", type="primary"):
            st.switch_page(TEST_PAGE)

    st.markdown(
        """
        <div style="text-align:center;">
            <div class="hero-trust">
                <span>⏱ <strong>About 7 minutes</strong></span>
                <span>🎓 <strong>For TCF Alumni </strong></span>
                <span>📍 Built for <strong>Pakistani students</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

#%%Quote
def quote_band():
    st.markdown(
        """
        <div class="quote-band">
            <p class="quote-band-title">You're not alone</p>
            <div class="quote-grid">
                <div class="quote-card">
                    <p class="quote-card-text">"Everyone is choosing a field, but how do I know what's right for me?"</p>
                    <div class="quote-card-author">— Pre-engineering student, Lahore</div>
                </div>
                <div class="quote-card">
                    <p class="quote-card-text">"My family wants me to do MBBS. But I'm not sure that's what I want."</p>
                    <div class="quote-card-author">— Pre-medical student, Karachi</div>
                </div>
                <div class="quote-card">
                    <p class="quote-card-text">"I'm worried! I'll pick the wrong degree and waste four years."</p>
                    <div class="quote-card-author">— ICS student, Islamabad</div>
                </div>
            </div>
            <p class="quote-band-closer">
                If any of this sounds like you, you don't have to figure it out by guessing.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
#%% About RIASEC
def about_riasec():
    st.markdown(
        """
        <div id="about">
            <div class="section-eyebrow">The Science</div>
            <h2 class="section-title">Built on the RIASEC framework</h2>
            <p class="section-sub">
                Developed by psychologist Dr. John Holland, RIASEC identifies six work personalities. Most people share traits across two or three. Your unique combination is your <strong>RIASEC Code</strong>. It's used by career counselors worldwide.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    riasec = [
    ("R", "Realistic", "🔧", "These people are often good at mechanical or athletic jobs.", "Engineering · Architecture · Agriculture"),
    ("I", "Investigative", "🔬", "These people like to watch, learn, analyze and solve problems.", "Medicine · Data Science · Research"),
    ("A", "Artistic", "🎨", "These people like to work in unstructured situations where they can use their creativity.", "Design · Media · Writing · Film"),
    ("S", "Social", "🤝", "These people like to work with other people, rather than things.", "Teaching · Psychology · Public Health"),
    ("E", "Enterprising", "💼", "These people like to work with others and enjoy persuading and performing.", "Business · Law · Entrepreneurship"),
    ("C", "Conventional", "📊", "These people are very detail oriented,organized  and like to work with data.", "Accounting · Finance · Administration"),]

    r_cols = st.columns(6, gap="small")
    for col, (letter, name, emoji, tagline, career) in zip(r_cols, riasec):
        with col:
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #e2e8f0;
                            border-radius: 14px; padding: 1.25rem 0.75rem;
                            text-align: center; transition: all 0.2s ease;">
                    <div style="font-size: 1.6rem; margin-bottom: 0.4rem;">{emoji}</div>
                    <div style="font-weight: 800; font-size: 1.4rem;
                                background: linear-gradient(90deg,#10b981,#3b82f6);
                                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                        {letter}
                    </div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.92rem;">
                        {name}
                    </div>
                    <div style="color: #64748b; font-size: 0.8rem; margin-top: 2px;">
                        {tagline}
                    </div>
                    <div class="riasec-careers" style="font-size: 0.7rem;">{career}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def how_it_works():
    steps = [
    ("1", "📝", "Answer 42 quick questions",
     "Honest reactions to everyday activities. No right or wrong answers."),
    ("2", "🧬", "Get your RIASEC code",
     "A 3-letter combination that captures how you naturally engage with work."),
    ("3", "🚀", "Explore suitable career paths",
     "See degrees, universities in Pakistan, and careers that fit your code."),
     ]
    st.markdown(
        """
        <div class="section-tinted" id="how">
            <div class="section-tinted-inner">
                <div class="section-eyebrow">Simple Process</div>
                <h2 class="section-title">How it works</h2>
                <p class="section-sub">Three steps. About 7 minutes. A clearer picture of what fits you.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st1, st2, st3 = st.columns(3, gap="small")
    for col, (num, emoji, title, text) in zip([st1, st2, st3], steps):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div class="step-num">{num}</div>
                    <div class="step-title" style="text-align: center">{title}</div>
                    <p class="step-desc" style="text-align: center">{text}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
def counsellor():
    st.markdown(
        """
        <div class="section" id="counsellor">
            <div class="section-eyebrow">After The Test</div>
            <h2 class="section-title">Got questions? Talk to our AI counsellor</h2>
            <p class="section-sub">
                Once you've got your RIASEC Code, ask follow-up questions about universities, scholarships, eligibility, or entrance prep. Our AI counsellor is trained on TCF's career resources, so answers stay grounded in what actually applies to Pakistani students.
            </p>
            <div class="counsellor-preview">
                <div class="chat-row from-user">
                    <div class="chat-bubble chat-bubble-user">
                        Which universities in Lahore are strongest for media studies?
                    </div>
                </div>
                <div class="chat-row">
                    <div class="chat-avatar">R</div>
                    <div class="chat-bubble chat-bubble-ai">
                        Based on your <strong>SAE</strong> code (Social–Artistic–Enterprising), three Lahore-based programs are worth looking at for media studies. Beaconhouse National University, FC College, and LUMS' Mushtaq Ahmad Gurmani School. Admission requirements differ; I can walk you through any of them.
                        <div class="chat-sources">📎 Sources: TCF Career Guide</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def faq():
    st.markdown(
        """
        <div id="faq">
            <div class="section-eyebrow">Questions</div>
            <h2 class="section-title">What students usually ask</h2>
            <p class="section-sub">If you're hesitating, you're probably not the only one. Here are the questions we get most.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        with st.expander("Is this test really accurate?"):
            st.markdown(
                "RIASEC has been studied for over 60 years and is one of the most validated career assessment frameworks in the world. It is used by university counselling centres globally. That said, no test decides your future. It's a starting point for thinking, not a prescription."
            )
        with st.expander("What information is stored, and who sees it?"):
            st.markdown(
                "Your test answers and RIASEC Code are saved securely so a TCF team can use the data for program improvement. Nothing is shared publicly, sold, or used for anything outside TCF."
            )
        with st.expander("How many questions, and how long does it take?"):
            st.markdown(
                "**42 statements**, organised as a simple tick-list. Most students finish in 5 to 7 minutes. There's no time pressure, answer at your own pace."
            )
        with st.expander("What if I disagree with my result?"):
            st.markdown(
                "That's important data too. The point isn't to label you. It's to give you a structured way to reflect. If a result surprises you, the 'why' is often where the real insight is. You can also chat with the AI counsellor afterward to explore directions the test didn't surface."
            )
        with st.expander("Is this only for science students?"):
            st.markdown(
                "No. The test works for any Intermediate field, e.g. pre-medical, pre-engineering, ICS, ICOM, FA, or general science. Recommendations are mapped to degrees available across Pakistani universities and adjusted for your selected background."
            )
        with st.expander("What is the AI counsellor, and is it accurate?"):
            st.markdown(
                "After the test, you can chat with an AI counsellor trained on TCF's curated career resources. It cites its sources on every answer, and it'll tell you plainly when something isn't covered in its materials rather than making things up. It's a guide, not a substitute for talking to a real counsellor."
            )


def final_cta():
    st.markdown(
        """
        <div class="final-cta">
            <h2>Your future starts with one question</h2>
            <p>Stop guessing. Take the test, get your RIASEC Code, and walk into your next decision with clarity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 1.2, 2])
    with c2:
        if st.button("Start my test  →", key="final_cta", width="stretch", type="primary"):
            st.switch_page(TEST_PAGE)


def footer():
    st.markdown(
    """
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem;
                margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
        For students figuring out their path · Based on Holland's RIASEC theory of Career Choice
    </div>
    """,
    unsafe_allow_html=True,
)



#%% Main
navbar()
hero_section()
quote_band()
about_riasec()
how_it_works()
counsellor()
faq()
final_cta()
footer()