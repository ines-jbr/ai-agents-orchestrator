from langchain_groq import ChatGroq
import os

def get_llm():
    """
    LLM via Groq — gratuit et rapide
    Modèle : llama-3.3-70b-versatile
    """
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0,
    )