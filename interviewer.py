import os
import streamlit as st
import random
from dotenv import load_dotenv
from groq import Groq

load_dotenv(dotenv_path=".env") #loads the PI Key from .env

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API KEY NOT FOUND")
    st.stop()

client = Groq(api_key=api_key) #initialize the client

def get_next_question(topic, history):
    messages = [
        {"role": "system", "content": f"you are a technical interviewer for topic {topic}. Ask one specific question related to topic {topic}. Do not explain the history or give introductury text. Also don't explain while asking the questions. you just ask questions and at last give a score out of 10 on each questions. Use history to ask follow-ups"}
    ]
    #The memory loop
    for item in history:
        messages.append({"role": "assistant", "content": item["question"]})
        messages.append({"role": "user", "content": item["answer"]})
        
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=150    
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
    subject = st.selectbox("Choose a topic: ", ["Java", "Python", "Machine Learning", "Operating Systems", "DBMS", "Data Structures and Algorithms"])

    if st.button("Reset and change topic"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

#Interview Loop
if st.session_state.step <= 5:
    st.subheader(f"Question {st.session_state.step}")

    if not st.session_state.current_question:
        with st.spinner("Generating question..."):
            st.session_state.current_question = get_next_question(subject, st.session_state.chat_history)

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
    

