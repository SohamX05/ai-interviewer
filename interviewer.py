import os
import streamlit as st
import random
from dotenv import load_dotenv
from groq import Groq
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

load_dotenv(dotenv_path=".env") #loads the PI Key from .env

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API KEY NOT FOUND")
    st.stop()

client = Groq(api_key=api_key) #initialize the client

def get_next_question(topic_or_resume, history, is_resume=False):
    if is_resume:
        system_task = f"""You are a recruiter interviewing a candidate based on their resume. 
        Resume Content: {topic_or_resume}
        Ask ONE specific technical question about their projects, skills, or experiences listed. 
        Make follow-up questions deeper based on their previous answers."""
    else:
        system_task = f"""Either You are a strict technical interviewer for {topic_or_resume}. 
            Your ONLY job is to ask the next question. 
            DO NOT give feedback on the previous answer. 
            DO NOT say 'Correct' or 'Good job'.
            If the candidate answered well, ask a harder follow-up. 
            If they struggled, ask a different fundamental question.
            ONLY output the question text."""

    messages = [
        {
            "role": "system", 
            "content": system_task
        }
    ]
    #The memory loop
    for item in history:
        messages.append({"role": "assistant", "content": item["question"]})
        messages.append({"role": "user", "content": item["answer"]})
        
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=350    
    )

    return response.choices[0].message.content

def get_final_evaluation(topic, history):
    transcript = ""
    for i, item in enumerate(history):
        transcript += f"Q{i+1}: {item['question']}\nA{i+1}: {item['answer']}\n\n"
    
    messages = [
        {
            "role": "system", 
            "content": f"You are a senior hiring manager. Evaluate this {topic} interview transcript. Provide a Score (out of 10), Strengths, and Areas for Improvement."
        },
        {"role": "user", "content": transcript}
    ]
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=850
    )
    return response.choices[0].message.content

#The Memory(Session State)
if 'step' not in st.session_state:
    st.session_state.step = 1       #Tracks the current no of question
    st.session_state.chat_history = []      #Stores History[{q1, a1}, {q2, a2}...]
    st.session_state.current_question = ""      #Stores the specific question text

#UI
with st.sidebar:
    st.title("Settings")

    mode = st.radio("Choose interview mode: ", ["Topic-Based", "Resume-Based"])

    if mode == "Topic-Based":
        subject = st.selectbox("Choose a topic: ", ["Java", "Python", "Machine Learning", "Operating Systems", "DBMS", "Data Structures and Algorithms"])
        
        if st.button("Reset and change topic"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
            
        if st.button("Restart Interview"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    else:
        uploaded_file = st.file_uploader("Upload your Resume/CV (PDF): ", type="pdf")
        if uploaded_file and 'resume_text' not in st.session_state:
            st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
            st.success("Resume Uploaded")

        if st.button("Restart Interview"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
#Interview Loop
total_questions = 10 if mode == "Resume-Based" else 5
if st.session_state.step <= total_questions:
    st.progress(st.session_state.step / total_questions)
    st.subheader(f"Question {st.session_state.step}")

    if not st.session_state.current_question:
        with st.spinner("Generating question..."):
            if mode == "Resume-based" and 'resume_text' in st.session_state:
                context = f"The candidate's resume: {st.session_state.resume_text}"
                st.session_state.current_question = get_next_question(context, st.session_state.chat_history, is_resume=True)
            else:
                st.session_state.current_question = get_next_question(subject, st.session_state.chat_history, is_resume=False)

    st.info(st.session_state.current_question)

    user_answer = st.text_area("Your Answer: ", key=f"answer_{st.session_state.step}")

    if st.button("Submit Answer"):
        if user_answer.strip():
            st.session_state.chat_history.append({"question": st.session_state.current_question, "answer": user_answer})
            st.session_state.current_question = ""
            st.session_state.step += 1
            st.rerun()
        else:
            st.warning("Please provide answer before submitting.")
else:
    st.header("Final Results: ")

    if st.session_state.chat_history:
        with st.spinner("Analyzing your performance accross all 5 questions..."):
            if mode == "Resume-Based":
                report = get_final_evaluation(st.session_state.resume_text, st.session_state.chat_history, is_resume=True)
            else:
                report = get_final_evaluation(subject, st.session_state.chat_history, is_resume=False)
            st.markdown(report)
            st.download_button("Download Report", str(st.session_state.chat_history))

    else:
        st.write("No interview data found. Please start a new session.")

    if st.button("Start New Interview"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
def get_final_evaluation(topic_or_resume, history, is_resume=False):
    transcript = ""
    for i, item in enumerate(history):
        transcript += f"Q{i+1}: {item['question']}\nA{i+1}: {item['answer']}\n\n"
    
    if is_resume:
        role_desc = "Evaluate if the candidate's answers back up the claims made in their resume."
    else:
        role_desc = f"Evaluate the candidate's technical knowledge of {topic_or_resume}."

    messages = [
        {
            "role": "system", 
            "content": f"You are a senior hiring manager. Evaluate this {role_desc} interview transcript. Provide a Score (out of 10), Strengths, and Areas for Improvement."
        },
        {
            "role": "user", 
            "content": transcript
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=850
    )
    return response.choices[0].message.content
