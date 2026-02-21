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

def get_ai_feedback(question, user_answer): #setting up conversation history and protocols for the AI Interviewer
    messages = [
        {
            "role": "system",
            "content": """You are an expert technical interviewer.
            Analyze the candidate's answer for:
            1. Technical accuracy.
            2. Completeness(what did they miss?).
            3. Clarity and communication style(was it a clear answer? was it professional?).
            Provide a 'Score' out of 10 and then give detailed 'Strengths' and 'Areas for Improvements'."""
        },
        {
            "role": "user",
            "content": f"Question asked: {question}\nCandidate's answer: {user_answer}\nPlease provide brief feedback on this answer, highlighting any technical inaccuracies and suggesting improvements."
       }
    ]
    #response from AI Interviewer
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=600,
        temperature=0.7
    )
    
    #returns the feedback
    return response.choices[0].message.content

#setting up the question
question = {
    "Java": [
        "Difference between Abstract Class and Interface",
        "Explain the 'fail-fast' vs 'fail-safe' iterator.",
        "How does garbage collection work in Java?" 
    ],
    "OS": [
        "Explain Paging vs Segmentation",
        "What are the four conditions for deadlocks?",
        "Difference between a Process and a Thread"
    ],
    "Machine Learning": [
        "Explain the bias-variance tradeoff.",
        "How does a Convolutional Neural Network(CNN) work?",
        "What is the difference between L1 and L2 regularization?"
    ]
}

#topic selection
with st.sidebar:
    st.title("Settings")
    topic = st.selectbox("Select Topic: ", question.keys())

    #resets the question
    if st.button("Generate New Question"):
        st.session_state.current_question = random.choice(question[topic])
        #clear previous feedback while getting a new question
        if "feedback" in st.session_state:
            del st.session_state.feedback

#initializing first question, if i doee'nt exist
if 'current_question' not in st.session_state:
    st.session_state.current_question = random.choice(question[topic])

st.subheader(f"Topic: {topic}")
st.info(f"Current Question: {st.session_state.current_question}")

#Streamlit UI
st.title("AI Interviewer")
st.divider()

#Creates a text box for user to answer
user_answer = st.text_area("Your Answer: ", height=150, placeholder="Type your answer here...")

#Creating a submit button
if st.button("Submit Answer"):
    if user_answer: #checks if typed or not
        with st.spinner("Analyzing your answer..."):
            feedback = get_ai_feedback(question, user_answer) #Calls the feedback funstion
            st.subheader("**Feedback**:")
            st.write(feedback) #Displays the feedback
    else:
        st.warning("Please enter your answer before submitting!")

