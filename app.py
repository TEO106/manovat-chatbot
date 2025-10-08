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

# Configurazione pagina con palette personalizzata
st.set_page_config(
    page_title="MANOVAT - AI Solutions Consultant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# CSS personalizzato con palette di colori
st.markdown("""
<style>
    /* Nascondi elementi Streamlit di default */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* IMPEDISCI CHIUSURA SIDEBAR */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    section[data-testid="stSidebar"] {
        width: 300px !important;
        min-width: 300px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        width: 300px !important;
        min-width: 300px !important;
    }
    
    /* Palette colori della landing page */
    :root {
        --primary-navy: #0B3C5D;
        --secondary-teal: #00A7B5;
        --accent-coral: #FF6B57;
        --background-snow: #F7F9FB;
        --text-charcoal: #2E3842;
    }
    
    /* Sfondo globale */
    .stApp {
        background-color: #F7F9FB;
    }
    
    /* Sidebar styling - SEMPRE VISIBILE */
    [data-testid="stSidebar"] {
        background-color: #0B3C5D !important;
        min-width: 300px !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #F7F9FB !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #F7F9FB !important;
    }
    
    /* Titolo principale - COLORE NAVY */
    h1 {
        color: #0B3C5D !important;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sottotitoli - COLORE TEAL */
    h2, h3 {
        color: #00A7B5 !important;
    }
    
    /* Tagline - COLORE TEAL */
    .tagline {
        color: #00A7B5 !important;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Messaggi chat */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(11, 60, 93, 0.1);
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #2E3842 !important;
    }
    
    /* Input utente */
    .stChatInput {
        border-color: #00A7B5 !important;
    }
    
    .stChatInput input {
        color: #2E3842 !important;
    }
    
    /* BOTTONI - COLORE CORAL */
    .stButton > button {
        background-color: #FF6B57 !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #e55a47 !important;
        box-shadow: 0 4px 8px rgba(255, 107, 87, 0.3);
        transform: translateY(-2px);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #FF6B57 !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    
    .stDownloadButton > button:hover {
        background-color: #e55a47 !important;
    }
    
    /* Progress bar - COLORE TEAL */
    .stProgress > div > div {
        background-color: #00A7B5 !important;
    }
    
    /* Testo principale - CHARCOAL */
    p, li, span, div {
        color: #2E3842 !important;
    }
    
    /* Spinner - COLORE TEAL */
    .stSpinner > div {
        border-top-color: #00A7B5 !important;
    }
    
    /* Success message - TEAL */
    .stSuccess {
        background-color: rgba(0, 167, 181, 0.1) !important;
        color: #0B3C5D !important;
        border-left: 4px solid #00A7B5 !important;
    }
    
    /* Info message - NAVY */
    .stInfo {
        background-color: rgba(11, 60, 93, 0.1) !important;
        color: #0B3C5D !important;
        border-left: 4px solid #0B3C5D !important;
    }
    
    /* Text input per password */
    .stTextInput input {
        background-color: white !important;
        color: #2E3842 !important;
        border: 2px solid #00A7B5 !important;
    }
    
    .stTextInput input:focus {
        border-color: #0B3C5D !important;
        box-shadow: 0 0 0 0.2rem rgba(0, 167, 181, 0.25) !important;
    }
    
    /* Chat input specifico */
    [data-testid="stChatInput"] {
        border-color: #00A7B5 !important;
    }
    
    /* Sidebar card styling */
    [data-testid="stSidebar"] .element-container {
        background-color: rgba(247, 249, 251, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Password di accesso
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #0B3C5D;'>🔐 MANOVAT Access</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00A7B5; font-size: 1.1rem;'>Enter your access code to continue</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Access Code:", type="password", key="password_input")
        
        if password == "Lussemburgo2023":
            st.session_state.authenticated = True
            st.rerun()
        elif password:
            st.error("Invalid access code. Please try again.")
    st.stop()

# Inizializza OpenAI con chiave dai secrets
if 'openai_api_key' not in st.session_state:
    try:
        st.session_state.openai_api_key = st.secrets["OPENAI_API_KEY"]
    except:
        st.session_state.openai_api_key = ""

# Stati della conversazione
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
    FINAL_REPORT = "final_report"
    COMPLETE = "complete"

# Inizializza session state
if 'state' not in st.session_state:
    st.session_state.state = ConversationState.WELCOME
    st.session_state.messages = []
    st.session_state.data = {
        'problem_statement': '',
        'success_criteria': '',
        'solution': '',
        'is_small_biz': False,
        'dataset_needed': False,
        'dataset_sufficient': False,
        'dataset_info': {},
        'tech_requirements': '',
        'human_factors_detailed': False,
        'human_factors_info': {},
        'timeline': '',
        'current_dataset_question': 0,
        'current_hf_question': 0,
        'total_questions_asked': 0
    }

def call_gpt(system_prompt: str, user_message: str, temperature: float = 0.5, max_tokens: int = 1024) -> str:
    """Chiama GPT-4o-mini con gestione errori"""
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
        return f"Error in API call: {str(e)}"

def add_message(role: str, content: str, show_to_user: bool = True):
    """Aggiungi messaggio alla cronologia"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "show_to_user": show_to_user
    })

def simulate_analysis(duration: float = 0.4):
    """Simula analisi con spinner"""
    time.sleep(duration)

def analyze_problem_and_solution():
    """Fase 1: Analisi problema e generazione soluzione"""
    system_prompt = """You are an AI Solutions Consultant with deep expertise in business strategy and AI/ML technologies. You excel at understanding client business challenges and identifying the best technological solutions based on Artificial Intelligence, both traditional and generative.

A user has provided one or more business problems. Your job is to propose one unified, AI-driven solution that addresses all the problems effectively and efficiently—integrating them into a single, coherent strategy when possible.

Output Requirements:
1. Title: "Business Challenge Summary"
   - Restate the user's business problem(s) in your own words to ensure full understanding.

2. Title: "Artificial Intelligence Driven Solution"
   - Suggest the one best, single, and cohesive AI solution (traditional and/or generative), with all its DL/ML specifics.
   - Describe what those specifics are.
   
   Subtitle: "How it Works"
   - Clearly explain in details how the solution will work in operation.

3. Title: "Success Metrics and Targets"
   - Propose specific metrics and targets to measure the solution's performance.
   - Explain how these metrics will validate the effectiveness of the solution.

4. Title: "Assumptions"
   - Clearly state any assumptions.

Presentation Format:
- Use clear, structured sections with bullet points, lists, and subheadings.
- Maintain a professional and concise writing style.

Important:
- For each section, only provide an answer if you are certain.
- Do not include any additional text such as introductions or conclusions.
- Avoid generic statements."""

    user_message = f"""Business Problem: {st.session_state.data['problem_statement']}

Success Criteria: {st.session_state.data['success_criteria']}"""

    return call_gpt(system_prompt, user_message, temperature=0.5, max_tokens=1024)

def check_small_business():
    """FORK 1: Controlla se è una piccola impresa o freelancer"""
    system_prompt = """Does the problem originate from a micro business or a freelancer?

If yes, output only the character y (without quotes).
If no, produce no output at all."""

    response = call_gpt(system_prompt, st.session_state.data['solution'], temperature=0.2, max_tokens=1024)
    return response.strip().lower() == 'y'

def analyze_small_biz_human_factors(answer: str):
    """Analisi HF semplificata per small business"""
    system_prompt = """You are an expert Human Factors engineer and Business Consultant tasked with analyzing the human factors requirements for a specific business project ("SOLUTION"). Your analysis must be specific, detailed, and unambiguous.

Domain:
Procedures, Roles and Responsibilities - How the working procedures, roles and responsibilities are impacted

Questions:
1) Do any existing internal development or operational procedures need modification to support the solution's implementation?
2) Will the solution's development introduce new tasks or responsibilities for internal team members?
3) Are there internal tasks or procedures that will become obsolete or redundant during the solution's integration?
4) Will the solution necessitate significant changes in roles or responsibilities among internal personnel?
5) Are new specialized internal roles or expertise required to effectively develop, integrate, and maintain the solution?

Make only a comprehensive requirement list addressing the internal personnel and development teams, with no introduction or conclusion. Do not repeat the questions.
Title: Procedures, Roles and Responsibilities

Only answer if you know the answer with certainty; if you're unsure about something, it's ok to not confidently assess it.
Avoid generic statements. Think about your answer first before you respond.
Answer with 250 tokens"""

    user_message = f"""Information about Human Factors features:
Q: Which internal teams or departments are currently responsible for executing the activities?
A: {answer}

The SOLUTION identified:
{st.session_state.data['solution']}"""

    return call_gpt(system_prompt, user_message, temperature=0.5, max_tokens=1024)

def check_dataset_needed():
    """FORK 2: Controlla se serve un dataset"""
    system_prompt = """Does the proposed solution require a dataset (e.g., a structured or semi-structured collection of data needing processes like data collection, preparation, and transformation) for its development or implementation? Examples include training or fine-tuning machine learning models, creating custom analytics, or similar tasks. If yes, print only 'y'.

If no dataset is required (e.g., solutions relying solely on integrating APIs like ChatGPT without additional data collection or preparation), produce absolutely no output"""
    
    response = call_gpt(system_prompt, st.session_state.data['solution'], temperature=0.2, max_tokens=1024)
    return response.strip().lower() == 'y'

def check_dataset_sufficiency():
    """FORK 3: Controlla se i dati raccolti sono sufficienti"""
    dataset_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.data['dataset_info'].items()])
    
    system_prompt = """Analyze the following description of a technological solution. Determine if the available data provided is sufficient for developing the solution.

If the data is adequate, output exactly the letter "y" (with no additional text or explanation).
If the data is insufficient, incomplete, or unclear, produce no output at all."""

    user_message = f"""SOLUTION:
{st.session_state.data['solution']}

DATASET INFORMATION:
{dataset_text}"""

    response = call_gpt(system_prompt, user_message, temperature=0.2, max_tokens=1024)
    return response.strip().lower() == 'y'

def check_human_factors_detailed():
    """FORK 4: Controlla se servono domande dettagliate sui fattori umani"""
    system_prompt = """Does the job involve significant physical activity or critical safety decisions? For instance, does it include factors such as physical strain (e.g., heavy lifting, awkward postures), challenging environmental conditions (e.g., poor lighting, extreme temperatures), notable hazards (e.g., dangerous machinery, hazardous substances), mandatory protective gear, or unpredictable work settings?

If any apply, output only y; otherwise, output nothing."""

    response = call_gpt(system_prompt, st.session_state.data['solution'], temperature=0.2, max_tokens=1024)
    return response.strip().lower() == 'y'

def get_dataset_questions() -> List[str]:
    """Ritorna le domande sul dataset in sequenza"""
    return [
        "Which datasets are available for this project? Provide a detailed description of each dataset's content, format, and source.",
        "How large is each dataset, and how many records or data points does it contain?",
        "Are the datasets structured, unstructured, or a combination of both? Specify formats, data types, and organization.",
        "Were the data collected consistently over time and across all relevant contexts? Describe the data collection methods, frequency, and any variations.",
        "Who is responsible for gathering and managing the data? Specify any teams or individuals involved, including their roles and responsibilities.",
        "What is the current quality of the data? Detail any known issues such as missing values, inconsistencies, outliers, or biases."
    ]

def analyze_tech_requirements(dataset_info: Optional[str] = None, data_sufficient: bool = True):
    """Analizza i requisiti tecnici"""
    if dataset_info:
        if data_sufficient:
            # Dataset sufficiente - analisi standard
            system_prompt = """You are an expert AI Engineer and Business Consultant. Analyze the feasibility of developing the AI-based SOLUTION based on DATASET AVAILABILITY and technical components. Cover: 1) Model & Architecture, 2) Infrastructure & Tools, 3) Skill Sets & Team Requirements, 4) Testing & Validation. Provide comprehensive requirements. No introduction/conclusion. Only answer if certain. Avoid generic statements. Answer with 400 tokens."""
        else:
            # Dataset insufficiente - analisi con Data Assessment esteso
            system_prompt = """You are an expert AI Engineer and Business Consultant. Analyze the feasibility of developing the AI-based SOLUTION based on DATASET AVAILABILITY and technical components. Cover: 1) Model & Architecture, 2) Infrastructure & Tools, 3) Skill Sets & Team Requirements, 4) Testing & Validation, 5) Data Assessment (specify if more data needed, duration for collection, quality improvements needed, which business divisions should be involved). Provide comprehensive requirements. No introduction/conclusion. Only answer if certain. Avoid generic statements. Answer with 400 tokens."""
        
        user_message = f"""Information about DATASET AVAILABILITY:
{dataset_info}

The SOLUTION identified:
{st.session_state.data['solution']}"""
    else:
        # Nessun dataset necessario
        system_prompt = """You are an expert AI Engineer and Business Consultant. Analyze the feasibility of developing the AI-based SOLUTION, focusing on technical components. Cover: 1) Model & Architecture, 2) Infrastructure & Tools, 3) Skill Sets & Team Requirements, 4) Testing & Validation. Provide comprehensive requirements. No introduction/conclusion. Only answer if certain. Answer with 400 tokens."""
        
        user_message = f"""No dataset available.

The SOLUTION identified:
{st.session_state.data['solution']}"""

    return call_gpt(system_prompt, user_message, temperature=0.5, max_tokens=1024)

def get_human_factors_questions(detailed: bool) -> List[str]:
    """Ritorna le domande sui fattori umani - 3 se basic, 12 se detailed"""
    if detailed:
        # 12 domande per lavori fisici/safety-critical
        return [
            "How is your problem currently being solved? Clearly describe the current technical solutions and/or ongoing activities.",
            "Which internal teams or departments are currently responsible for executing the activities?",
            "Do internal teams need to interact or collaborate to execute the activities? If so, how often and what methods are currently used?",
            "What specific procedures do they follow to perform the activities?",
            "What information do they typically need to perform the task?",
            "What tools and equipment are currently used to perform the tasks?",
            "What competencies (both soft and technical skills) are required to perform the tasks?",
            "What training is currently available?",
            "What is the current workplace?",
            "How many workstations are there?",
            "What is the current division of tasks and responsibilities?",
            "What is the current shift pattern?"
        ]
    else:
        # 3 domande per lavori non fisici
        return [
            "Which internal teams or departments are currently responsible for executing the activities?",
            "Do internal teams need to interact or collaborate to execute the activities? If so, how often and what methods are currently used?",
            "What specific procedures do they follow to perform the activities?"
        ]

def analyze_human_factors(answers: Dict[str, str], detailed: bool):
    """Analizza i fattori umani - 4 domini se basic, 6 se detailed"""
    answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])
    
    if detailed:
        # 6 domini per lavori fisici/safety-critical
        system_prompt = """You are an expert Human Factors engineer and Business Consultant. Analyze the human factors requirements for the SOLUTION. Make comprehensive requirement lists. Only answer if certain. Avoid generic statements. Answer with 250 tokens per domain. 

Domains to analyze:
1) Teams and Communication - Impact on intra-organizational interactions
2) Procedures, Roles and Responsibilities - How working procedures, roles and responsibilities are impacted
3) Human Machine Interaction - Impact on internal technical teams' interactions with equipment
4) Skills and Training - How skills and competences are impacted
5) Organisation of Work - How the organisation of work is impacted (shifts, staffing, layout, change management)
6) Environment - How the human-environment relation is impacted (physical aspects and socio-cultural factors)"""
    else:
        # 4 domini per lavori non fisici
        system_prompt = """You are an expert Human Factors engineer and Business Consultant. Analyze the human factors requirements for the SOLUTION. Make comprehensive requirement lists. Only answer if certain. Avoid generic statements. Answer with 250 tokens per domain.

Domains to analyze:
1) Teams and Communication - Impact on intra-organizational interactions
2) Procedures, Roles and Responsibilities - How working procedures, roles and responsibilities are impacted
3) Human Machine Interaction - Impact on internal technical teams' interactions with equipment
4) Skills and Training - How skills and competences are impacted"""

    user_message = f"""Information about Human Factors features:
{answers_text}

The SOLUTION identified:
{st.session_state.data['solution']}"""

    return call_gpt(system_prompt, user_message, temperature=0.5, max_tokens=1024)

def generate_timeline(solution: str, tech_req: str, hf_req: str, user_timeline: str):
    """Genera la timeline del progetto"""
    system_prompt = """You are an AI agent designed to generate development timelines. Propose two timelines: 1) Rapid Timeline (No Procurement Delays), 2) Extended Timeline (With Procurement Delays). Break down into phases with durations. Explain rationale and assumptions. Use clear sections. Answer with 200 tokens."""

    user_message = f"""SOLUTION: {solution}
TECHNICAL REQUIREMENTS: {tech_req}
HUMAN FACTORS REQUIREMENTS: {hf_req}
USER'S EXPECTED TIMELINE: {user_timeline}"""

    return call_gpt(system_prompt, user_message, temperature=0.2, max_tokens=4096)

def generate_pdf_report() -> BytesIO:
    """Genera report PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', fontSize=24, textColor='#0B3C5D', spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='CustomHeading', fontSize=16, textColor='#00A7B5', spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='CustomBody', fontSize=11, textColor='#2E3842', spaceAfter=12, alignment=TA_JUSTIFY))
    
    story = []
    
    # Title
    story.append(Paragraph("MANOVAT Analysis Report", styles['CustomTitle']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['CustomBody']))
    story.append(Spacer(1, 0.5*inch))
    
    # Problem Understanding
    story.append(Paragraph("1. PROBLEM UNDERSTANDING", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['problem_statement'], styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Success Criteria:", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['success_criteria'], styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    
    # AI Solution
    story.append(Paragraph("2. AI SOLUTION", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['solution'], styles['CustomBody']))
    story.append(PageBreak())
    
    # Technical Requirements
    story.append(Paragraph("3. TECHNICAL REQUIREMENTS", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['tech_requirements'], styles['CustomBody']))
    story.append(Spacer(1, 0.3*inch))
    
    # Human Factors
    if st.session_state.data.get('human_factors_analysis'):
        story.append(Paragraph("4. HUMAN FACTORS", styles['CustomHeading']))
        story.append(Paragraph(st.session_state.data['human_factors_analysis'], styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
    
    # Timeline
    story.append(Paragraph("5. PROJECT TIMELINE", styles['CustomHeading']))
    story.append(Paragraph(st.session_state.data['timeline'], styles['CustomBody']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# UI Layout
st.markdown("<h1 style='text-align: center;'>MANOVAT</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline' style='text-align: center;'>Transform Business Challenges into AI-Powered Solutions</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    st.markdown("### Progress Tracker")
    
    progress_steps = {
        ConversationState.WELCOME: 0,
        ConversationState.PROBLEM_UNDERSTANDING: 10,
        ConversationState.SUCCESS_CRITERIA: 20,
        ConversationState.ANALYZING_SOLUTION: 25,
        ConversationState.SMALL_BIZ_CHECK: 30,
        ConversationState.SMALL_BIZ_QUESTION: 40,
        ConversationState.DATASET_CHECK: 45,
        ConversationState.DATASET_QUESTIONS: 55,
        ConversationState.DATASET_SUFFICIENCY_CHECK: 60,
        ConversationState.TECH_ANALYSIS: 70,
        ConversationState.HUMAN_FACTORS_CHECK: 75,
        ConversationState.HUMAN_FACTORS_QUESTIONS: 85,
        ConversationState.TIMELINE: 95,
        ConversationState.COMPLETE: 100
    }
    
    current_progress = progress_steps.get(st.session_state.state, 0)
    st.progress(current_progress / 100)
    st.caption(f"{current_progress}% Complete")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("Reset Analysis", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'authenticated':
                del st.session_state[key]
        st.rerun()

# Main conversation area
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg.get("show_to_user", True):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# State machine logic
if st.session_state.state == ConversationState.WELCOME:
    if not st.session_state.messages:
        welcome_msg = """Welcome to MANOVAT!

I'll guide you through designing a comprehensive AI/ML solution for your business challenge.

We'll explore:
- Your business problem and objectives
- A tailored AI solution design
- Technical requirements analysis
- Human factors evaluation
- Project timeline planning

Let's begin! **What is your specific business problem?**

Please describe:
- Your organization and context
- Key challenges you face
- Your objectives
- Expected business impact"""
