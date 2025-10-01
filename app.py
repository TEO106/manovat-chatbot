import streamlit as st
import openai
from typing import Dict, List, Optional
import json
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="MANOVAT - AI Solutions Consultant",
    page_icon="🤖",
    layout="wide"
)

# Usa la chiave API dal secrets (nascosta)
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
    DATASET_CHECK = "dataset_check"
    DATASET_QUESTIONS = "dataset_questions"
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
        'dataset_needed': False,
        'dataset_info': {},
        'tech_requirements': '',
        'human_factors_needed': False,
        'human_factors_info': {},
        'timeline': '',
        'current_dataset_question': 0,
        'current_hf_question': 0
    }

def call_gpt(system_prompt: str, user_message: str, temperature: float = 0.5, max_tokens: int = 1024) -> str:
    """Chiama GPT-4o-mini con gestione errori"""
    if not st.session_state.openai_api_key:
        return "⚠️ Per favore inserisci la tua OpenAI API Key nella sidebar."
    
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
        return f"❌ Errore nella chiamata API: {str(e)}"

def add_message(role: str, content: str):
    """Aggiungi messaggio alla cronologia"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

def analyze_problem_and_solution():
    """Fase 1: Analisi problema e generazione soluzione"""
    system_prompt = """You are an AI Solutions Consultant with deep expertise in business strategy and AI/ML technologies. You excel at understanding client business challenges and identifying the best technological solutions based on Artificial Intelligence, both traditional and generative.

A user has provided one or more business problems. Your job is to propose one unified, AI-driven solution that addresses all the problems effectively and efficiently—integrating them into a single, coherent strategy when possible.

Output Requirements:
1. Title: "Business Challenge Summary"
   - Restate the user's business problem(s) in your own words to ensure full understanding.

2. Title: "Artificial Intelligence Driven Solution"
   - Suggest the one best, single, and cohesive AI solution (traditional and/or generative), with all its DL/ML specifics (e.g., supervised ML model, recommender system, deep neural network, chatbot, LLM Agents, etc.).
   - Describe what those specifics are (e.g., "A Random Forest is a machine learning algorithm that uses multiple decision trees to make predictions and classifications.")
   
   Subtitle: "How it Works"
   - Clearly explain in details how the solution will work in operation.

3. Title: "Success Metrics and Targets"
   - Propose specific metrics and targets (e.g., accuracy, precision, recall, ROI, reduction in churn rate, etc.) to measure the solution's performance.
   - Explain how these metrics will validate the effectiveness of the solution.

4. Title: "Assumptions"
   - Clearly state any assumptions (e.g., "customer data has been collected for at least 12 months").

Presentation Format:
- Use clear, structured sections with bullet points, lists, and subheadings.
- Maintain a professional and concise writing style.

Important:
- For each section, only provide an answer if you are certain; if unsure about any part, explicitly note your uncertainty.
- Do not include any additional text such as introductions or conclusions beyond the structured solution.
- Avoid generic statements.
- Think through your answer carefully before responding."""

    user_message = f"""Business Problem: {st.session_state.data['problem_statement']}

Success Criteria: {st.session_state.data['success_criteria']}"""

    return call_gpt(system_prompt, user_message, temperature=0.5, max_tokens=1024)

def check_dataset_needed():
    """Controlla se serve un dataset"""
    system_prompt = """Does the proposed solution require a dataset (e.g., a structured or semi-structured collection of data needing processes like data collection, preparation, and transformation) for its development or implementation? Examples include training or fine-tuning machine learning models, creating custom analytics, or similar tasks. If yes, print only 'y'.

If no dataset is required (e.g., solutions relying solely on integrating APIs like ChatGPT without additional data collection or preparation), produce absolutely no output"""

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

def analyze_tech_requirements(dataset_info: Optional[str] = None):
    """Analizza i requisiti tecnici"""
    if dataset_info:
        system_prompt = """You are a very expert AI Engineer and Business Consultant. You must thoroughly analyze the feasibility of developing the AI-based SOLUTION described below, based on both DATASET AVAILABILITY and all other essential technical components (e.g., infrastructure, model design, tooling, skill sets). Your analysis should comprehensively cover the following points:

1) Model & Architecture - Which AI/ML model or approach is suitable for this SOLUTION? Go deep into details. Is there a need for specialized frameworks, libraries, or hardware? Are there any constraints or requirements specific to model scalability, performance, or interpretability?

2) Infrastructure & Tools - What infrastructure (e.g., cloud platform, on-prem servers) is required to train, deploy, and maintain the model? Which DevOps or MLOps tools and pipelines are necessary?

3) Skill Sets & Team Requirements - Which roles or expertise are needed to implement, manage, and maintain the SOLUTION? What kind of specialized training for existing staff is required?

4) Testing & Validation - How should testing be conducted to validate model accuracy and performance? Are there any required metrics or acceptance criteria?

5) Data Assessment - Is a larger amount of data required to initiate the project? If yes, specify whether it should be new, more of the same, or qualitatively different. What should be the required duration for additional data collection? How could data quality be improved? What other business divisions should be involved?

For each aspect, describe what the technical elements are (e.g., "A Random Forest is...", "AWS is..."). Provide comprehensive requirement lists, with no introduction or conclusion. Only answer if certain. Avoid generic statements. Answer with 400 tokens."""
        
        user_message = f"""Information about DATASET AVAILABILITY:
{dataset_info}

The SOLUTION identified:
{st.session_state.data['solution']}"""
    else:
        system_prompt = """You are a very expert AI Engineer and Business Consultant. Analyze the feasibility of developing the AI-based SOLUTION, focusing on technical components (infrastructure, model design, tooling, skill sets). Cover:

1) Model & Architecture
2) Infrastructure & Tools  
3) Skill Sets & Team Requirements
4) Testing & Validation

For each aspect, provide comprehensive requirements. No introduction/conclusion. Only answer if certain. Avoid generic statements. Answer with 400 tokens."""

        user_message = f"""No dataset available.

The SOLUTION identified:
{st.session_state.data['solution']}"""

    return call_gpt(system_prompt, user_message, temperature=0.5, max_tokens=1024)

def check_human_factors_needed():
    """Controlla se servono considerazioni sui fattori umani"""
    system_prompt = """Does the job involve significant physical activity or critical safety decisions? For instance, does it include factors such as physical strain (e.g., heavy lifting, awkward postures), challenging environmental conditions (e.g., poor lighting, extreme temperatures), notable hazards (e.g., dangerous machinery, hazardous substances), mandatory protective gear, or unpredictable work settings?

If any apply, output only y; otherwise, output nothing."""

    response = call_gpt(system_prompt, st.session_state.data['solution'], temperature=0.2, max_tokens=1024)
    return response.strip().lower() == 'y'

def get_human_factors_questions(detailed: bool) -> List[str]:
    """Ritorna le domande sui fattori umani"""
    basic_questions = [
        "How is your problem currently being solved? Clearly describe the current technical solutions and/or ongoing activities.",
        "Which internal teams or departments are currently responsible for executing the activities?",
        "Do internal teams need to interact or collaborate to execute the activities? If so, how often and what methods are currently used?",
        "What specific procedures do they follow to perform the activities?",
        "What information do they typically need to perform the task?",
        "What tools and equipment are currently used to perform the tasks?",
        "What competencies (both soft and technical skills) are required to perform the tasks?",
        "What training is currently available?"
    ]
    
    detailed_questions = basic_questions + [
        "What is the current workplace?",
        "How many workstations are there?",
        "What is the current division of tasks and responsibilities?",
        "What is the current shift pattern?"
    ]
    
    return detailed_questions if detailed else basic_questions

def analyze_human_factors(answers: Dict[str, str], detailed: bool):
    """Analizza i fattori umani"""
    answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])
    
    base_prompt = """You are an expert Human Factors engineer and Business Consultant. Analyze the human factors requirements for the SOLUTION. Make comprehensive requirement lists addressing internal personnel and development teams, with no introduction or conclusion. Only answer if certain. Avoid generic statements. Answer with 250 tokens per domain.

Domains to analyze:
1) Teams and Communication - Impact on intra-organizational interactions during development
2) Procedures, Roles and Responsibilities - How working procedures, roles and responsibilities are impacted
3) Human Machine Interaction - Impact on internal technical teams' interactions with equipment
4) Skills and Training - How skills and competences are impacted"""

    if detailed:
        base_prompt += "\n5) Organisation of Work - How the organisation of work is impacted\n6) Environment - How the human-environment relation is impacted"

    user_message = f"""Information about Human Factors features:
{answers_text}

The SOLUTION identified:
{st.session_state.data['solution']}"""

    return call_gpt(base_prompt, user_message, temperature=0.5, max_tokens=1024)

def generate_timeline(solution: str, tech_req: str, hf_req: str, user_timeline: str):
    """Genera la timeline del progetto"""
    system_prompt = """You are an AI agent designed to generate development timelines for a project based on a provided technical solution description, requirements, and user's expected timeline.

Propose two effective timelines:

1. **Rapid Timeline (No Procurement/Business Delays):**
   - Assume no need for procurement or business decision delays
   - Project can commence as soon as tomorrow
   - Break down into key phases with detailed durations

2. **Extended Timeline (With Procurement/Business Delays):**
   - Include extra time for procurement and business decisions
   - State these periods occur before T0 (project kickstart)
   - Similar phase breakdown with added procurement time

Ensure timelines are aligned with the technical solution and requirements. Explain rationale, outline assumptions, and detail time allocations. Use clear sections with headers and bullet points. Answer with 200 tokens."""

    user_message = f"""SOLUTION:
{solution}

TECHNICAL REQUIREMENTS:
{tech_req}

HUMAN FACTORS REQUIREMENTS:
{hf_req}

USER'S EXPECTED TIMELINE:
{user_timeline}"""

    return call_gpt(system_prompt, user_message, temperature=0.2, max_tokens=4096)

# UI Layout
st.title("🤖 MANOVAT - AI Solutions Consultant")
st.markdown("*Virtual consultant for AI/ML solution design*")

# Sidebar per API Key e info
with st.sidebar:
    st.header("⚙️ About")
    st.info("💡 Free demo powered by AI")
    st.caption("No API key required!")
    
    st.markdown("---")
    st.header("📊 Progress")
    
    progress_steps = {
        ConversationState.WELCOME: 0,
        ConversationState.PROBLEM_UNDERSTANDING: 10,
        ConversationState.SUCCESS_CRITERIA: 20,
        ConversationState.ANALYZING_SOLUTION: 30,
        ConversationState.DATASET_CHECK: 40,
        ConversationState.DATASET_QUESTIONS: 50,
        ConversationState.TECH_ANALYSIS: 60,
        ConversationState.HUMAN_FACTORS_CHECK: 70,
        ConversationState.HUMAN_FACTORS_QUESTIONS: 80,
        ConversationState.TIMELINE: 90,
        ConversationState.COMPLETE: 100
    }
    
    current_progress = progress_steps.get(st.session_state.state, 0)
    st.progress(current_progress / 100)
    st.caption(f"{current_progress}% Complete")
    
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main conversation area
chat_container = st.container()

with chat_container:
    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# State machine logic
if st.session_state.state == ConversationState.WELCOME:
    if not st.session_state.messages:
        welcome_msg = """👋 Welcome to MANOVAT!

I'm your AI Solutions Consultant. I'll help you design a comprehensive AI/ML solution for your business challenge.

We'll go through several steps:
1. **Understanding your problem** and success criteria
2. **Designing an AI solution** tailored to your needs
3. **Analyzing technical requirements** (data, infrastructure, skills)
4. **Evaluating human factors** (if applicable)
5. **Creating a project timeline**

Let's start! **What is your specific business problem?**

Please provide:
- Organization size and context
- Key challenges you're facing
- Your objectives
- Potential business impact"""
        add_message("assistant", welcome_msg)
        st.rerun()
    
    user_input = st.chat_input("Describe your business problem...")
    if user_input:
        add_message("user", user_input)
        st.session_state.data['problem_statement'] = user_input
        st.session_state.state = ConversationState.SUCCESS_CRITERIA
        st.rerun()

elif st.session_state.state == ConversationState.SUCCESS_CRITERIA:
    if st.session_state.messages[-1]["role"] != "assistant":
        criteria_msg = """Great! Now, **what are your success criteria for this project?**

For instance:
- Specific percentage reduction in customer churn?
- Defined improvement in sales conversions?
- Target timeframe for achieving results?
- ROI expectations?

Be as specific as possible with metrics and targets."""
        add_message("assistant", criteria_msg)
        st.rerun()
    
    user_input = st.chat_input("Describe your success criteria...")
    if user_input:
        add_message("user", user_input)
        st.session_state.data['success_criteria'] = user_input
        st.session_state.state = ConversationState.ANALYZING_SOLUTION
        st.rerun()

elif st.session_state.state == ConversationState.ANALYZING_SOLUTION:
    with st.spinner("🧠 Analyzing your problem and designing AI solution..."):
        solution = analyze_problem_and_solution()
        st.session_state.data['solution'] = solution
        add_message("assistant", f"📋 **AI Solution Analysis Complete!**\n\n{solution}")
        st.session_state.state = ConversationState.DATASET_CHECK
    st.rerun()

elif st.session_state.state == ConversationState.DATASET_CHECK:
    with st.spinner("🔍 Checking if dataset is needed..."):
        needs_dataset = check_dataset_needed()
        st.session_state.data['dataset_needed'] = needs_dataset
        
        if needs_dataset:
            msg = "📊 This solution requires a dataset. Let me ask you some questions about data availability."
            add_message("assistant", msg)
            st.session_state.state = ConversationState.DATASET_QUESTIONS
        else:
            msg = "✅ This solution doesn't require a custom dataset. Moving to technical analysis..."
            add_message("assistant", msg)
            st.session_state.state = ConversationState.TECH_ANALYSIS
    st.rerun()

elif st.session_state.state == ConversationState.DATASET_QUESTIONS:
    questions = get_dataset_questions()
    current_q = st.session_state.data['current_dataset_question']
    
    if current_q < len(questions):
        if st.session_state.messages[-1]["role"] != "assistant" or "Q" not in st.session_state.messages[-1]["content"]:
            add_message("assistant", f"**Question {current_q + 1}/{len(questions)}:**\n\n{questions[current_q]}")
            st.rerun()
        
        user_input = st.chat_input(f"Answer question {current_q + 1}...")
        if user_input:
            add_message("user", user_input)
            st.session_state.data['dataset_info'][questions[current_q]] = user_input
            st.session_state.data['current_dataset_question'] += 1
            st.rerun()
    else:
        st.session_state.state = ConversationState.TECH_ANALYSIS
        st.rerun()

elif st.session_state.state == ConversationState.TECH_ANALYSIS:
    with st.spinner("🔧 Analyzing technical requirements..."):
        dataset_text = None
        if st.session_state.data['dataset_needed']:
            dataset_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.data['dataset_info'].items()])
        
        tech_req = analyze_tech_requirements(dataset_text)
        st.session_state.data['tech_requirements'] = tech_req
        add_message("assistant", f"⚙️ **Technical Requirements Analysis:**\n\n{tech_req}")
        st.session_state.state = ConversationState.HUMAN_FACTORS_CHECK
    st.rerun()

elif st.session_state.state == ConversationState.HUMAN_FACTORS_CHECK:
    with st.spinner("👥 Checking human factors requirements..."):
        needs_hf = check_human_factors_needed()
        st.session_state.data['human_factors_needed'] = needs_hf
        
        if needs_hf:
            msg = "👥 This solution requires human factors analysis. I'll ask you some questions about current operations."
            add_message("assistant", msg)
            st.session_state.state = ConversationState.HUMAN_FACTORS_QUESTIONS
        else:
            msg = "✅ Basic human factors analysis will be sufficient. Moving to timeline planning..."
            add_message("assistant", msg)
            st.session_state.state = ConversationState.TIMELINE
    st.rerun()

elif st.session_state.state == ConversationState.HUMAN_FACTORS_QUESTIONS:
    detailed = st.session_state.data['human_factors_needed']
    questions = get_human_factors_questions(detailed)
    current_q = st.session_state.data['current_hf_question']
    
    if current_q < len(questions):
        if st.session_state.messages[-1]["role"] != "assistant" or "Question" not in st.session_state.messages[-1]["content"]:
            add_message("assistant", f"**Question {current_q + 1}/{len(questions)}:**\n\n{questions[current_q]}")
            st.rerun()
        
        user_input = st.chat_input(f"Answer question {current_q + 1}...")
        if user_input:
            add_message("user", user_input)
            st.session_state.data['human_factors_info'][questions[current_q]] = user_input
            st.session_state.data['current_hf_question'] += 1
            st.rerun()
    else:
        with st.spinner("👥 Analyzing human factors..."):
            hf_analysis = analyze_human_factors(
                st.session_state.data['human_factors_info'],
                detailed
            )
            st.session_state.data['human_factors_analysis'] = hf_analysis
            add_message("assistant", f"👥 **Human Factors Analysis:**\n\n{hf_analysis}")
            st.session_state.state = ConversationState.TIMELINE
        st.rerun()

elif st.session_state.state == ConversationState.TIMELINE:
    if st.session_state.messages[-1]["role"] != "assistant" or "timeline" not in st.session_state.messages[-1]["content"].lower():
        timeline_msg = """📅 **Final step!**

What is your planned timeline from project ideation to deployment?

Please include:
- Key milestones you envision
- Any specific deadlines
- Expected deliverables along the way"""
        add_message("assistant", timeline_msg)
        st.rerun()
    
    user_input = st.chat_input("Describe your timeline expectations...")
    if user_input:
        add_message("user", user_input)
        
        with st.spinner("📅 Generating project timeline..."):
            hf_req = st.session_state.data.get('human_factors_analysis', 'Not applicable')
            timeline = generate_timeline(
                st.session_state.data['solution'],
                st.session_state.data['tech_requirements'],
                hf_req,
                user_input
            )
            st.session_state.data['timeline'] = timeline
            
            final_msg = f"""🎉 **Analysis Complete!**

{timeline}

---

**📥 Download Complete Report**

Your complete MANOVAT analysis is ready. Would you like me to generate a summary document?"""
            add_message("assistant", final_msg)
            st.session_state.state = ConversationState.COMPLETE
        st.rerun()

elif st.session_state.state == ConversationState.COMPLETE:
    st.success("✅ Analysis completed successfully!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Full Report", use_container_width=True):
            report = f"""# MANOVAT - AI Solution Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. PROBLEM UNDERSTANDING
{st.session_state.data['problem_statement']}

### Success Criteria
{st.session_state.data['success_criteria']}

---

## 2. AI SOLUTION
{st.session_state.data['solution']}

---

## 3. TECHNICAL REQUIREMENTS
{st.session_state.data['tech_requirements']}

---

## 4. HUMAN FACTORS
{st.session_state.data.get('human_factors_analysis', 'Not applicable')}

---

## 5. PROJECT TIMELINE
{st.session_state.data['timeline']}

---

## 6. DATASET INFORMATION
{'Dataset required: YES' if st.session_state.data['dataset_needed'] else 'Dataset required: NO'}

"""
            if st.session_state.data['dataset_needed']:
                report += "\n### Dataset Details\n"
                for q, a in st.session_state.data['dataset_info'].items():
                    report += f"\n**Q:** {q}\n**A:** {a}\n"
            
            st.download_button(
                label="💾 Download Report (Markdown)",
                data=report,
                file_name=f"manovat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with col2:
        if st.button("🔄 Start New Analysis", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Footer
st.markdown("---")
st.caption("MANOVAT - Virtual AI Solutions Consultant")
