import os
import streamlit as st
from groq import Groq

def init_groq_client():
    """
    Initialize the Groq client using an environment variable for the API key.
    
    Returns:
        Groq: An initialized Groq client object if successful.
        None: If the API key is missing or there is an initialization error.
    """
    try:
        # Fetch the API key from the environment variable
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("API key not found in environment variables. Ensure 'GROQ_API_KEY' is set.")
        
        # Initialize and return the Groq client
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Groq client: {e}")
        return None
