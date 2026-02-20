import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv() #loads the PI Key from .env

api_key = os.getenv("GROK_API_KEY")

client = Groq(api_key=api_key) #initialize the client

def get_ai_feedback(question, user_answer): #setting up conversation history and protocols for the AI Interviewer
    messages = [
        {
            "role": "system",
            "content": "You are a senior software engineer conducting a technical interview. Keep your feedback concise, constructive and strictly focus on technical accuracy."
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
        max_tokens=200
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
