import json
import streamlit as st

def clean_and_parse_json(response_content):
    """
    Clean and parse the AI response to extract valid JSON.

    Parameters:
        response_content (str): Raw string from the AI response.

    Returns:
        dict: Parsed JSON object.
    """
    try:
        # Extract JSON block by identifying the first '{' and last '}'
        start_idx = response_content.find("{")
        end_idx = response_content.rfind("}")
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON object found in the response content.")

        json_str = response_content[start_idx:end_idx + 1]
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decoding failed: {e}")

def get_ai_suggestions(client, data, chart_type):
    """
    Fetch AI suggestions for creating a specific type of chart based on the dataset.
    
    Parameters:
        client (object): The AI client instance.
        data (DataFrame): The dataset for which suggestions are needed.
        chart_type (str): The type of chart (e.g., 'bar', 'line').
        
    Returns:
        dict: A JSON object containing chart parameters or None if an error occurs.
    """
    prompt = f"""
    You are a helpful assistant. Always respond with valid JSON format only.
    Suggest how to best create a {chart_type} visualization.
    Dataset columns: {list(data.columns)}
    Respond strictly in the following JSON format:
    {{
        "parameters": {{
            "x": "column_name",
            "y": "column_name",
            "title": "Chart Title"
        }}
    }}
    """
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        response_content = response.choices[0].message.content

        # Clean and parse the response
        suggestion = clean_and_parse_json(response_content)
        if "parameters" not in suggestion:
            raise ValueError("Missing 'parameters' in AI response.")
        return suggestion
    except Exception as e:
        st.error(f"Error fetching AI suggestions: {e}")
    return None

def generate_data_insights(client, df):
    """
    Generate insights for a dataset using the AI client.
    
    Parameters:
        client (object): The AI client instance.
        df (DataFrame): The dataset to analyze.
        
    Returns:
        dict: A JSON object containing insights or None if an error occurs.
    """
    prompt = (
        "You are a helpful assistant. Always respond with valid JSON format only. "
        "Provide insights for the following dataset: " + df.head().to_json()
    )
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        response_content = response.choices[0].message.content

        # Clean and parse the response
        insights = clean_and_parse_json(response_content)
        if not isinstance(insights, dict):
            raise ValueError("Expected a JSON object as the AI response.")
        return insights
    except Exception as e:
        st.error(f"Error generating insights: {e}")
    return None
