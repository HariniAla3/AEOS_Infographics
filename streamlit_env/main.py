import streamlit as st
import pandas as pd
import json
import re
from pathlib import Path
from components.visualization import visualize_data
from components.insights import generate_insights, display_insights
from components.profiling import generate_profile_report, display_profile_report
from components.presentation_animator import add_animation_interface
from utils.data_processing import load_data
from components.groq_client import init_groq_client
import io


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Visualization"
    if 'insights' not in st.session_state:
        st.session_state.insights = None


def cleanup_temp_files():
    """Clean up temporary files created during the session"""
    try:
        temp_file = Path("temp_report.html")
        if temp_file.exists():
            temp_file.unlink()

        temp_paths = [
            Path("temp_frames"),
            Path("visualization.mp4")
        ]

        for path in temp_paths:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                for file in path.glob("*"):
                    file.unlink()
                path.rmdir()

    except Exception as e:
        st.warning(f"Warning: Could not clean up temporary files: {e}")


def infer_columns_and_data_with_ai(client, text):
    """
    Use Groq's `mixtral-8x7b-32768` model to infer column names and data from structured text.
    
    Parameters:
        client: The Groq AI client instance.
        text (str): Input text containing structured data.
    
    Returns:
        dict: Parsed JSON object containing column names and rows.
    """
    try:
        prompt = f"""
        You are an AI assistant. Analyze the following text to extract structured data.
        Identify column names and corresponding rows of data.

        Input text:
        "{text}"

        Respond strictly in this JSON format:
        {{
            "columns": ["Column1", "Column2", ...],
            "data": [
                ["Row1Col1", "Row1Col2", ...],
                ["Row2Col1", "Row2Col2", ...],
                ...
            ]
        }}
        """

        # Send the prompt to the Groq API using the `mixtral-8x7b-32768` model
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        # Parse AI response
        response_content = response.choices[0].message.content
        structured_data = json.loads(response_content)

        if "columns" in structured_data and "data" in structured_data:
            return structured_data
        else:
            raise ValueError("AI response missing required keys: 'columns' or 'data'.")

    except Exception as e:
        st.error(f"Error communicating with the Groq API: {e}")
    return None


def text_to_dataframe_with_ai(client, text):
    """
    Convert structured text into a DataFrame using Groq's `mixtral-8x7b-32768` model.
    
    Parameters:
        client: The Groq AI client instance.
        text (str): Input text containing structured data.
    
    Returns:
        pd.DataFrame: Generated DataFrame from the text.
    """
    try:
        structured_data = infer_columns_and_data_with_ai(client, text)

        if structured_data:
            df = pd.DataFrame(structured_data["data"], columns=structured_data["columns"])

            # Attempt to convert numerical columns to appropriate types
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors="ignore")
                except ValueError:
                    pass

            return df
        else:
            st.error("Failed to infer structured data from text.")
            return None
    except Exception as e:
        st.error(f"Error generating DataFrame: {e}")
        return None


def main():
    st.set_page_config(
        page_title="Data Visualization & Insights Studio",
        page_icon="📊",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    st.title("📊 Advanced Data Visualization & Insights Studio")

    # Initialize Groq client
    client = init_groq_client()
    if not client:
        st.error("Groq Client initialization failed. Please check your API key and connection.")
        return

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        tabs = {
            "Visualization": "📈",
            "Insights": "🔍",
            "Data Profile": "📋",
            "Animation": "🎬"
        }
        for tab, icon in tabs.items():
            button_type = "primary" if tab == st.session_state.active_tab else "secondary"
            if st.button(
                f"{icon} {tab}",
                type=button_type,
                disabled=not st.session_state.data_loaded,
                use_container_width=True
            ):
                st.session_state.active_tab = tab
                st.rerun()

        # Display current dataset information in sidebar
        if st.session_state.data_loaded:
            st.divider()
            st.write("### Current Dataset")
            st.info(f"Loaded data with {st.session_state.df.shape[0]} rows and {st.session_state.df.shape[1]} columns")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Numeric Columns",
                          len(st.session_state.df.select_dtypes(include=['int64', 'float64']).columns))
            with col2:
                st.metric("Categorical Columns",
                          len(st.session_state.df.select_dtypes(include=['object', 'category']).columns))

    # Handle data loading and input types
    if not st.session_state.data_loaded:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.header("Upload, Paste, or Enter Survey Data")

            # File upload
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

            # Structured survey text input
            st.write("Or enter structured survey text below:")
            survey_text_input = st.text_area("Enter Survey Text Here", height=200)

            # Process File Upload
            if st.button("Process File Upload") and uploaded_file:
                try:
                    df = load_data(uploaded_file)
                    if df is not None and not df.empty:
                        st.session_state.df = df
                        st.session_state.data_loaded = True
                        with st.spinner("Analyzing your data..."):
                            st.session_state.insights = generate_insights(client, df)
                        st.success("File uploaded successfully!")
                        st.rerun()
                    else:
                        st.error("Uploaded file is empty or invalid.")
                except Exception as e:
                    st.error(f"Error loading the file: {e}")

            # Process Survey Text with AI
            elif st.button("Process Survey Text with AI") and survey_text_input.strip():
                try:
                    df = text_to_dataframe_with_ai(client, survey_text_input)
                    if df is not None and not df.empty:
                        st.session_state.df = df
                        st.session_state.data_loaded = True
                        with st.spinner("Analyzing your data..."):
                            st.session_state.insights = generate_insights(client, df)
                        st.success("Survey text successfully processed!")
                        st.rerun()
                    else:
                        st.error("Survey text is empty or invalid.")
                except Exception as e:
                    st.error(f"Error processing the survey text: {str(e)}")

    # Workflow continues after data is loaded
    else:
        if st.session_state.active_tab == "Visualization":
            visualize_data(st.session_state.df, client)
        elif st.session_state.active_tab == "Insights":
            st.header("Data Insights")
            if st.session_state.insights:
                display_insights(st.session_state.insights)
        elif st.session_state.active_tab == "Data Profile":
            st.header("Data Profiling Report")
            try:
                with st.spinner("Generating the profiling report..."):
                    profile_report = generate_profile_report(st.session_state.df)
                    display_profile_report(profile_report)
            except Exception as e:
                st.error(f"An error occurred while generating the profiling report: {str(e)}")
        elif st.session_state.active_tab == "Animation":
            if st.session_state.df is not None:
                add_animation_interface(
                    st.session_state.df,
                    st.session_state.insights
                )
            else:
                st.error("Please load data first before creating animations.")

    # Cleanup temporary files
    cleanup_temp_files()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        cleanup_temp_files()

