import streamlit as st
from groq import Groq

def init_groq_client():
    try:
        # Read API key from Streamlit secrets
        api_key = st.secrets["groq"]["api_key"]
        return Groq(api_key=api_key)
    except KeyError:
        st.error("API key not found. Please configure it in Streamlit secrets.")
        return None
    except Exception as e:
        st.error(f"Error initializing Groq client: {e}")
        return None
