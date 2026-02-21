import os
import streamlit as st
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

#Streamlit UI
st.title("AI Interviewer")
st.divider()

#setting up the question
question = "Can you explain the difference between an Interface and an Abstract Class in Java?"
st.markdown(f"**Interviewer**: {question}")

#Creates a text box for user to answer
user_answer = st.text_area("Your Answer: ", height=150)

#Creating a submit button
if st.button("Submit Answer"):
    if user_answer: #checks if typed or not
        with st.spinner("Analyzing your answer..."):
            feedback = get_ai_feedback(question, user_answer) #Calls the feedback funstion
            st.subheader("**Feedback**:")
            st.write(feedback) #Displays the feedback
    else:
        st.warning("Please enter your answer before submitting!")
