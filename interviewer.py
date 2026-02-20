import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv() #loads the PI Key from .env

api_key = os.getenv("GROK_API_KEY")

client = Groq(api_key=api_key) #initialize the client

def get_ai_feedback(question, user_answer): #set up conversation history and protocols for the AI Interviewer
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
        model="llama3-8b--8192",
        messages=messages,
        max_tokens=200
    )
    
    #return the feedback
    return response.choices[0].message.content
