import streamlit as st
import openai
from typing import Dict, List, Optional
import json
from datetime import datetime
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from io import BytesIO

# Configurazione pagina
st.set_page_config(
    page_title="MANOVAT - AI Solutions Consultant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS personalizzato
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="collapsedControl"] {display: none !important;}
    section[data-testid="stSidebar"] {width: 300px !important; min-width: 300px !important;}
    section[data-testid="stSidebar"] > div {width: 300px !important; min-width: 300px !important;}
    .stApp {background-color: #F7F9FB;}
    [data-testid="stSidebar"] {background-color: #0B3C5D !important; min-width: 300px !important;}
    [data-testid="stSidebar"] * {color: #F7F9FB !important;}
    [data-testid="stSidebar"] .stMarkdown {color: #F7F9FB !important;}
    h1 {color: #0B3C5D !important; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;}
    h2, h3 {color: #00A7B5 !important;}
    .tagline {color: #00A7B5 !important; font-size: 1.2rem; font-weight: 400; margin-bottom: 2rem; font-style: italic;}
    .stChatMessage {background-color: white; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(11, 60, 93, 0.1);}
    .stChatMessage [data-testid="stMarkdownContainer"] p {color: #2E3842 !important;}
    .stChatInput {border-color: #00A7B5 !important;}
    .stChatInput input {color: #2E3842 !important;}
    .stButton > button {background-color: #FF6B57 !important; color: white !important; border: none; border-radius: 8px; padding: 0.5rem 2rem; font-weight: 600; transition: all 0.3s ease;}
    .stButton > button:hover {background-color: #e55a47 !important; box-shadow: 0 4px 8px rgba(255, 107, 87, 0.3); transform: translateY(-2px);}
    .stDownloadButton > button {background-color: #FF6B57 !important; color: white !important; border: none; border-radius: 8px; padding: 0.5rem 2rem; font-weight: 600;}
    .stDownloadButton > button:hover {background-color: #e55a47 !important;}
    .stProgress > div > div {background-color: #00A7B5 !important;}
    p, li, span, div {color: #2E3842 !important;}
    .stSpinner > div {border-top-color: #00A7B5 !important;}
    .stSuccess {background-color: rgba(0, 167, 181, 0.1) !important; color: #0B3C5D !important; border-left: 4px solid #00A7B5 !important;}
    .stInfo {background-color: rgba(11, 60, 93, 0.1) !important; color: #0B3C5D !important; border-left: 4px solid #0B3C5D !important;}
    .stTextInput input {background-color: white !important; color: #2E3842 !important; border: 2px solid #00A7B5 !important;}
    .stTextInput input:focus {border-color: #0B3C5D !important; box-shadow: 0 0 0 0.2rem rgba(0, 167, 181, 0.25) !important;}
    [data-testid="stChatInput"] {border-color: #00A7B5 !important;}
    [data-testid="stSidebar"] .element-container {background-color: rgba(247, 249, 251, 0.1); border-radius: 8px; padding: 0.5rem; margin-bottom: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# Password
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #0B3C5D;'>🔐 MANOVAT Access</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00A7B5; font-size: 1.1rem;'>Enter your access code to continue</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Access Code:", type="password", key="password_input")
        if password == "demo_2025":
            st.session_state.authenticated = True
            st.rerun()
        elif password:
            st.error("Invalid access code. Please try again.")
    st.stop()

# OpenAI
if 'openai_api_key' not in st.session_state:
    try:
        st.session_state.openai_api_key = st.secrets["OPENAI_API_KEY"]
    except:
        st.session_state.openai_api_key = ""

# Stati
class ConversationState:
    WELCOME = "welcome"
    PROBLEM_UNDERSTANDING = "problem_understanding"
    SUCCESS_CRITERIA = "success_criteria"
    ANALYZING_SOLUTION = "analyzing_solution"
    SMALL_BIZ_CHECK = "small_biz_check"
    SMALL_BIZ_QUESTION = "small_biz_question"
    DATASET_CHECK = "dataset_check"
    DATASET_QUESTIONS = "dataset_questions"
    DATASET_SUFFICIENCY_CHECK = "dataset_sufficiency_check"
    TECH_ANALYSIS = "tech_analysis"
    HUMAN_FACTORS_CHECK = "human_factors_check"
    HUMAN_FACTORS_QUESTIONS = "human_factors_questions"
    TIMELINE = "timeline"
    COMPLETE = "complete"

# Init session state
if 'state' not in st.session_state:
    st.session_state.state = ConversationState.WELCOME
    st.session_state.messages = []
    st.session_state.data = {
        'problem_statement': '', 'success_criteria': '', 'solution': '',
        'is_small_biz': False, 'dataset_needed': False, 'dataset_sufficient': False,
        'dataset_info': {}, 'tech_requirements': '', 'human_factors_detailed': False,
        'human_factors_info': {}, 'timeline': '', 'current_dataset_question': 0,
        'current_hf_question': 0, 'total_questions_asked': 0
    }

def call_gpt(system_prompt: str, user_message: str, temperature: float = 0.5, max_tokens: int = 1024) -> str:
    if not st.session_state.openai_api_key:
        return "Error: API Key not configured."
    try:
        client = openai.OpenAI(api_key=st.session_state.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def add_message(role: str, content: str, show_to_user: bool = True):
    st.session_state.messages.append({
        "role": role, "content": content,
        "timestamp": datetime.now().isoformat(),
        "show_to_user": show_to_user
    })

def simulate_analysis(duration: float = 0.4):
    time.sleep(duration)

def analyze_problem_and_solution():
    system_prompt = """You are an AI Solutions Consultant with deep expertise in business strategy and AI/ML technologies.

Output Requirements:
1. Business Challenge Summary - Restate the user's problem
2. Artificial Intelligence Driven Solution - Suggest AI solution with DL/ML specifics
   Subtitle: How it Works - Explain operation details
3. Success Metrics and Targets - Propose metrics and targets
4. Assumptions - State any assumptions

Use clear sections with bullet points. Be professional and concise. Only answer if certain. Avoid generic statements."""

    user_message = f"""Business Problem: {st.session_state.data['problem_statement']}
Success Criteria: {st.session_state.data['success_criteria']}"""
    return call_gpt(system_prompt, user_message, 0.5, 1024)

def check_small_business():
    system_prompt = """Does the problem originate from a micro business or a freelancer?
If yes, output only 'y'. If no, produce no output."""
    response = call_gpt(system_prompt, st.session_state.data['solution'], 0.2, 1024)
    return response.strip().lower() == 'y'

def analyze_small_biz_human_factors(answer: str):
    system_prompt = """You are an expert Human Factors engineer. Analyze requirements for SOLUTION focusing on Procedures, Roles and Responsibilities.
Make comprehensive requirement list. No introduction/conclusion. Only answer if certain. Answer with 250 tokens."""
    user_message = f"""Q: Which internal teams are responsible?
A: {answer}
SOLUTION: {st.session_state.data['solution']}"""
    return call_gpt(system_prompt, user_message, 0.5, 1024)

def check_dataset_needed():
    system_prompt = """Does the solution require a dataset for development? If yes, print only 'y'. If no, produce no output."""
    response = call_gpt(system_prompt, st.session_state.data['solution'], 0.2, 1024)
    return response.strip().lower() == 'y'

def check_dataset_sufficiency():
    dataset_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.data['dataset_info'].items()])
    system_prompt = """Is the available data sufficient? If adequate, output 'y'. If insufficient, produce no output."""
    user_message = f"""SOLUTION: {st.session_state.data['solution']}
DATASET: {dataset_text}"""
    response = call_gpt(system_prompt, user_message, 0.2, 1024)
    return response.strip().lower() == 'y'

def check_human_factors_detailed():
    system_prompt = """Does the job involve significant physical activity or critical safety decisions? If any apply, output only 'y'; otherwise, output nothing."""
    response = call_gpt(system_prompt, st.session_state.data['solution'], 0.2, 1024)
    return response.strip().lower() == 'y'

def get_dataset_questions() -> List[str]:
    return [
        "Which datasets are available? Provide detailed description.",
        "How large is each dataset?",
        "Are datasets structured, unstructured, or both?",
        "Were data collected consistently?",
        "Who is responsible for data management?",
        "What is the data quality?"
    ]

def analyze_tech_requirements(dataset_info: Optional[str] = None, data_sufficient: bool = True):
    if dataset_info:
        if data_sufficient:
            system_prompt = """Analyze AI-based SOLUTION feasibility. Cover: 1) Model & Architecture, 2) Infrastructure & Tools, 3) Skill Sets, 4) Testing. No introduction/conclusion. 400 tokens."""
        else:
            system_prompt = """Analyze AI-based SOLUTION feasibility. Cover: 1) Model & Architecture, 2) Infrastructure & Tools, 3) Skill Sets, 4) Testing, 5) Data Assessment (more data needed, duration, quality improvements, divisions involved). 400 tokens."""
        user_message = f"""DATASET: {dataset_info}
SOLUTION: {st.session_state.data['solution']}"""
    else:
        system_prompt = """Analyze AI-based SOLUTION feasibility. Cover: 1) Model & Architecture, 2) Infrastructure & Tools, 3) Skill Sets, 4) Testing. 400 tokens."""
        user_message = f"""No dataset available.
SOLUTION: {st.session_state.data['solution']}"""
    return call_gpt(system_prompt, user_message, 0.5, 1024)

def get_human_factors_questions(detailed: bool) -> List[str]:
    if detailed:
        return [
            "How is your problem currently being solved?",
            "Which internal teams are responsible?",
            "Do teams need to interact or collaborate?",
            "What procedures do they follow?",
            "What information do they need?",
            "What tools and equipment are used?",
            "What competencies are required?",
            "What training is available?",
            "What is the current workplace?",
            "How many workstations?",
            "What is the division of tasks?",
            "What is the shift pattern?"
        ]
    else:
        return [
            "Which internal teams are responsible?",
            "Do teams need to interact or collaborate?",
            "What procedures do they follow?"
        ]

def analyze_human_factors(answers: Dict[str, str], detailed: bool):
    answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])
    if detailed:
        system_prompt = """Analyze human factors for SOLUTION. Domains: 1) Teams and Communication, 2) Procedures/Roles, 3) Human Machine Interaction, 4) Skills and Training, 5) Organisation of Work, 6) Environment. 250 tokens per domain."""
    else:
        system_prompt = """Analyze human factors for SOLUTION. Domains: 1) Teams and Communication, 2) Procedures/Roles, 3) Human Machine Interaction, 4) Skills and Training. 250 tokens per domain."""
    user_message = f"""Human Factors: {answers_text}
SOLUTION: {st.session_state.data['solution']}"""
    return call_gpt(system_prompt, user_message, 0.5, 1024)

def generate_timeline(solution: str, tech_req: str, hf_req: str, user_timeline: str):
    system_prompt = """Generate two timelines: 1) Rapid (No Procurement Delays), 2) Extended (With Procurement Delays). Break down into phases. 200 tokens."""
    user_message = f"""SOLUTION: {solution}
TECH: {tech_req}
HF: {hf_req}
USER TIMELINE: {user_timeline}"""
    return call_gpt(system_prompt, user_message, 0.2, 4096)

def generate_pdf_report() -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', fontSize=24, spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='CustomHeading', fontSize=16, spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='CustomBody', fontSize=11, spaceAfter=12, alignment=TA_JUSTIFY))
    story = []
    story.append(Paragraph("MANOVAT Analysis Report", styles['CustomTitle']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['CustomBody']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("1. PROBLEM UNDERSTANDING", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['problem_statement'], styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Success Criteria:", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['success_criteria'], styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("2. AI SOLUTION", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['solution'], styles['CustomBody']))
    story.append(PageBreak())
    story.append(Paragraph("3. TECHNICAL REQUIREMENTS", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['tech_requirements'], styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    if st.session_state.data.get('human_factors_analysis'):
        story.append(Paragraph("4. HUMAN FACTORS", styles['CustomHeading']))
        story.append(Paragraph(st.session_state.data['human_factors_analysis'], styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("5. PROJECT TIMELINE", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['timeline'], styles['CustomBody']))
    doc.build(story)
    buffer.seek(0)
    return buffer

# UI
st.markdown("<h1 style='text-align: center;'>MANOVAT</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline' style='text-align: center;'>Transform Business Challenges into AI-Powered Solutions</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Progress Tracker")
    progress_steps = {
        ConversationState.WELCOME: 0, ConversationState.PROBLEM_UNDERSTANDING: 10,
        ConversationState.SUCCESS_CRITERIA: 20, ConversationState.ANALYZING_SOLUTION: 25,
        ConversationState.SMALL_BIZ_CHECK: 30, ConversationState.SMALL_BIZ_QUESTION: 40,
        ConversationState.DATASET_CHECK: 45, ConversationState.DATASET_QUESTIONS: 55,
        ConversationState.DATASET_SUFFICIENCY_CHECK: 60, ConversationState.TECH_ANALYSIS: 70,
        ConversationState.HUMAN_FACTORS_CHECK: 75, ConversationState.HUMAN_FACTORS_QUESTIONS: 85,
        ConversationState.TIMELINE: 95, ConversationState.COMPLETE: 100
    }
    current_progress = progress_steps.get(st.session_state.state, 0)
    st.progress(current_progress / 100)
    st.caption(f"{current_progress}% Complete")
    st.markdown("---")
    if st.button("Reset Analysis", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'authenticated':
                del st.session_state[key]
        st.rerun()

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg.get("show_to_user", True):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# State machine
if st.session_state.state == ConversationState.WELCOME:
    if not st.session_state.messages:
        welcome_msg = """Welcome to MANOVAT!

I'll guide you through designing a comprehensive AI/ML solution.

Let's begin! **What is your specific business problem?**"""
        add_message("assistant", welcome_msg)
        st.rerun()
    user_input = st.chat_input("Describe your business problem...")
    if user_input:
        add_message("user", user_input)
        st.session_state.data['problem_statement'] = user_input
        st.session_state.data['total_questions_asked'] += 1
        st.session_state.state = ConversationState.SUCCESS_CRITERIA
        with st.spinner("Analyzing..."):
            simulate_analysis()
        st.rerun()

elif st.session_state.state == ConversationState.SUCCESS_CRITERIA:
    if st.session_state.messages[-1]["role"] != "assistant":
        add_message("assistant", "**What are your success criteria for this project?**")
        st.rerun()
    user_input = st.chat_input("Describe your success criteria...")
    if user_input:
        add_message("user", user_input)
        st.session_state.data['success_criteria'] = user_input
        st.session_state.data['total_questions_asked'] += 1
        st.session_state.state = ConversationState.ANALYZING_SOLUTION
        with st.spinner("Analyzing..."):
            simulate_analysis()
        st.rerun()

elif st.session_state.state == ConversationState.ANALYZING_SOLUTION:
    with st.spinner("Analyzing your requirements..."):
        solution = analyze_problem_and_solution()
        st.session_state.data['solution'] = solution
        add_message("assistant", "Analysis complete. Evaluating business context...", show_to_user=False)
        st.session_state.state = ConversationState.SMALL_BIZ_CHECK
    st.rerun()

elif st.session_state.state == ConversationState.SMALL_BIZ_CHECK:
    with st.spinner("Analyzing..."):
        is_small_biz = check_small_business()
        st.session_state.data['is_small_biz'] = is_small_biz
        if is_small_biz:
            add_message("assistant", "I need to understand your current operational context.")
            st.session_state.state = ConversationState.SMALL_BIZ_QUESTION
        else:
            add_message("assistant", "Proceeding with technical evaluation...", show_to_user=False)
            st.session_state.state = ConversationState.DATASET_CHECK
    st.rerun()

elif st.session_state.state == ConversationState.SMALL_BIZ_QUESTION:
    if st.session_state.messages[-1]["role"] != "assistant" or "?" not in st.session_state.messages[-1]["content"]:
        st.session_state.data['total_questions_asked'] += 1
        add_message("assistant", f"**Question {st.session_state.data['total_questions_asked']}:** Which internal teams are responsible for executing the activities?")
        st.rerun()
    user_input = st.chat_input("Your answer...")
    if user_input:
        add_message("user", user_input)
        with st.spinner("Generating analysis..."):
            hf_analysis = analyze_small_biz_human_factors(user_input)
            st.session_state.data['human_factors_analysis'] = hf_analysis
            st.session_state.data['tech_requirements'] = "Simplified analysis for small business context."
            add_message("assistant", "Analysis complete. Moving to timeline planning...", show_to_user=False)
            st.session_state.state = ConversationState.TIMELINE
        st.rerun()

elif st.session_state.state == ConversationState.DATASET_CHECK:
    with st.spinner("Analyzing..."):
        needs_dataset = check_dataset_needed()
        st.session_state.data['dataset_needed'] = needs_dataset
        if needs_dataset:
            add_message("assistant", "I need to understand your data availability.")
            st.session_state.state = ConversationState.DATASET_QUESTIONS
        else:
            add_message("assistant", "Proceeding with technical analysis...", show_to_user=False)
            st.session_state.state = ConversationState.TECH_ANALYSIS
    st.rerun()

elif st.session_state.state == ConversationState.DATASET_QUESTIONS:
    questions = get_dataset_questions()
    current_q = st.session_state.data['current_dataset_question']
    if current_q < len(questions):
        if st.session_state.messages[-1]["role"] != "assistant" or "?" not in st.session_state.messages[-1]["content"]:
            st.session_state.data['total_questions_asked'] += 1
            add_message("assistant", f"**Question {st.session_state.data['total_questions_asked']}:** {questions[current_q]}")
            st.rerun()
        user_input = st.chat_input("Your answer...")
        if user_input:
            add_message("user", user_input)
            st.session_state.data['dataset_info'][questions[current_q]] = user_input
            st.session_state.data['current_dataset_question'] += 1
            with st.spinner("Analyzing..."):
                simulate_analysis()
            st.rerun()
    else:
        st.session_state.state = ConversationState.DATASET_SUFFICIENCY_CHECK
        st.rerun()

elif st.session_state.state == ConversationState.DATASET_SUFFICIENCY_CHECK:
    with st.spinner("Evaluating data sufficiency..."):
        data_sufficient = check_dataset_sufficiency()
        st.session_state.data['dataset_sufficient'] = data_sufficient
        add_message("assistant", "Data assessment complete...", show_to_user=False)
        st.session_state.state = ConversationState.TECH_ANALYSIS
    st.rerun()

elif st.session_state.state == ConversationState.TECH_ANALYSIS:
    with st.spinner("Conducting technical analysis..."):
        dataset_text = None
        data_sufficient = True
        if st.session_state.data['dataset_needed']:
            dataset_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.data['dataset_info'].items()])
            data_sufficient = st.session_state.data['dataset_sufficient']
        tech_req = analyze_tech_requirements(dataset_text, data_sufficient)
        st.session_state.data['tech_requirements'] = tech_req
        add_message("assistant", "Technical analysis complete...", show_to_user=False)
        st.session_state.state = ConversationState.HUMAN_FACTORS_CHECK
    st.rerun()

elif st.session_state.state == ConversationState.HUMAN_FACTORS_CHECK:
    with st.spinner("Analyzing..."):
        needs_detailed_hf = check_human_factors_detailed()
        st.session_state.data['human_factors_detailed'] = needs_detailed_hf
        add_message("assistant", "I need to understand your current operations.")
        st.session_state.state = ConversationState.HUMAN_FACTORS_QUESTIONS
    st.rerun()

elif st.session_state.state == ConversationState.HUMAN_FACTORS_QUESTIONS:
    detailed = st.session_state.data['human_factors_detailed']
    questions = get_human_factors_questions(detailed)
    current_q = st.session_state.data['current_hf_question']
    if current_q < len(questions):
        if st.session_state.messages[-1]["role"] != "assistant" or "?" not in st.session_state.messages[-1]["content"]:
            st.session_state.data['total_questions_asked'] += 1
            add_message("assistant", f"**Question {st.session_state.data['total_questions_asked']}:** {questions[current_q]}")
            st.rerun()
        user_input = st.chat_input("Your answer...")
        if user_input:
            add_message("user", user_input)
            st.session_state.data['human_factors_info'][questions[current_q]] = user_input
            st.session_state.data['current_hf_question'] += 1
            with st.spinner("Analyzing..."):
                simulate_analysis()
            st.rerun()
    else:
        with st.spinner("Completing human factors analysis..."):
            hf_analysis = analyze_human_factors(st.session_state.data['human_factors_info'], detailed)
            st.session_state.data['human_factors_analysis'] = hf_analysis
            add_message("assistant", "Human factors analysis complete...", show_to_user=False)
            st.session_state.state = ConversationState.TIMELINE
        st.rerun()

elif st.session_state.state == ConversationState.TIMELINE:
    if st.session_state.messages[-1]["role"] != "assistant" or "timeline" not in st.session_state.messages[-1]["content"].lower():
        st.session_state.data['total_questions_asked'] += 1
        timeline_msg = f"**Question {st.session_state.data['total_questions_asked']}:** What is your planned timeline from project ideation to deployment?"
        add_message("assistant", timeline_msg)
        st.rerun()
    user_input = st.chat_input("Describe your timeline...")
    if user_input:
        add_message("user", user_input)
        with st.spinner("Generating timeline..."):
            hf_req = st.session_state.data.get('human_factors_analysis', 'Not applicable')
            timeline = generate_timeline(
                st.session_state.data['solution'],
                st.session_state.data['tech_requirements'],
                hf_req, user_input
            )
            st.session_state.data['timeline'] = timeline
            add_message("assistant", "Analysis complete! Your comprehensive MANOVAT report is ready.")
            st.session_state.state = ConversationState.COMPLETE
        st.rerun()

elif st.session_state.state == ConversationState.COMPLETE:
    st.success("✅ Analysis completed successfully!")
    col1, col2 = st.columns(2)
    with col1:
        pdf_buffer = generate_pdf_report()
        st.download_button(
            label="📄 Download Report (PDF)",
            data=pdf_buffer,
            file_name=f"manovat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col2:
        if st.button("🔄 Start New Analysis", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'authenticated':
                    del st.session_state[key]
            st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #00A7B5;'>MANOVAT - Powered by Advanced AI</p>", unsafe_allow_html=True)
