import pandas as pd
import json
import streamlit as st
from groq import Groq
from utils.ai_helpers import clean_and_parse_json

def generate_insights(client, df):
    """
    Generate insights for the given DataFrame using the Groq API.
    
    Parameters:
        client (object): Initialized Groq API client.
        df (DataFrame): DataFrame containing the uploaded data.
    
    Returns:
        dict: Insights response as JSON or None if an error occurs.
    """
    if not isinstance(client, Groq):
        st.error("The provided client is not a valid Groq client.")
        return None
    
    if not isinstance(df, pd.DataFrame):
        st.error("Invalid dataset provided. Expected a pandas DataFrame.")
        return None
    
    # Create a prompt with strict JSON formatting
    prompt = f"""
    Analyze this dataset and provide insights in JSON format:
    Columns: {list(df.columns)}
    First 5 Rows: {df.head().to_dict(orient='records')}
    
    Respond strictly in this JSON format:
    {{
        "key_insights": [
            {{
                "title": "Main observation",
                "description": "Detailed explanation",
                "importance": "Business impact"
            }}
        ],
        "trends": [
            {{
                "pattern": "Identified pattern",
                "explanation": "Pattern meaning"
            }}
        ],
        "visualization_suggestions": [
            {{
                "type": "Visualization type",
                "reason": "Why this visualization works"
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        # Access content directly as a property
        response_content = response.choices[0].message.content
        # st.write("Debug: Raw API Response", response_content)  # Log response content for debugging
        
        return clean_and_parse_json(response_content)
    except json.JSONDecodeError as e:
        st.error(f"JSON decoding error: {e}")
        return None
    except Exception as e:
        st.error(f"Error interacting with Groq API: {e}")
        return None

def display_insights(insights):
    """
    Display insights in Streamlit.

    Parameters:
        insights (dict): Parsed insights JSON object.
    """
    if not insights:
        st.error("No insights to display.")
        return

    st.write("### Key Insights:")
    key_insights = insights.get("key_insights", [])
    for insight in key_insights:
        st.write(f"- **{insight['title']}**: {insight['description']} (Impact: {insight['importance']})")

    st.write("### Trends:")
    trends = insights.get("trends", [])
    for trend in trends:
        st.write(f"- **Pattern**: {trend['pattern']} — {trend['explanation']}")

    st.write("### Visualization Suggestions:")
    visualizations = insights.get("visualization_suggestions", [])
    for viz in visualizations:
        st.write(f"- **Type**: {viz['type']} — {viz['reason']}")
