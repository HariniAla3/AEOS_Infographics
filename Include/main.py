import streamlit as st
import pandas as pd
import os
from pathlib import Path
from components.visualization import visualize_data
from components.insights import generate_insights, display_insights
from components.profiling import generate_profile_report, display_profile_report
from components.presentation_animator import add_animation_interface, generate_video_from_slides
from utils.data_processing import load_data
from components.groq_client import init_groq_client
import base64


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
    if 'visualizations' not in st.session_state:
        st.session_state.visualizations = []


def cleanup_temp_files():
    """Clean up temporary files created during the session"""
    try:
        temp_file = Path("temp_report.html")
        if temp_file.exists():
            temp_file.unlink()

        temp_dir = Path("temp_animations")
        if temp_dir.exists():
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()
    except Exception as e:
        st.warning(f"Warning: Could not clean up temporary files: {e}")


def download_video(video_path):
    """Generate a download link for the MP4 video."""
    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()
        b64 = base64.b64encode(video_bytes).decode()
        href = f'<a href="data:video/mp4;base64,{b64}" download="presentation.mp4">Download MP4 Video</a>'
        return href


def main():
    st.set_page_config(
        page_title="Data Visualization & Insights Studio",
        page_icon="📊",
        layout="wide"
    )

    initialize_session_state()

    st.title("📊 Advanced Data Visualization & Insights Studio")

    # Initialize Groq client
    client = init_groq_client()
    if not client:
        st.error("Groq Client initialization failed. Please check your API key and connection.")
        return

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

    if not st.session_state.data_loaded:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.header("Upload Your Data")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file:
                try:
                    df = load_data(uploaded_file)
                    if df is not None and not df.empty:
                        st.session_state.df = df
                        st.session_state.data_loaded = True
                        with st.spinner("Analyzing your data..."):
                            st.session_state.insights = generate_insights(client, df)
                        st.session_state.visualizations = [
                            {"type": "basic_bar", "x": df.columns[0], "y": df.columns[1], "title": "Sample Bar Chart"},
                            {"type": "line", "x": df.columns[0], "y": df.columns[1], "title": "Sample Line Chart"}
                        ]
                        st.success("File uploaded successfully!")
                        st.rerun()
                    else:
                        st.error("Uploaded file is empty or invalid. Please check the format.")
                except Exception as e:
                    st.error(f"Error loading the file: {str(e)}")
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
            st.header("Create Animated Presentation")
            if st.session_state.insights and st.session_state.visualizations:
                if st.button("Generate Video"):
                    with st.spinner("Creating video..."):
                        slides = add_animation_interface(st.session_state.df, st.session_state.insights, st.session_state.visualizations)
                        if slides:
                            video_path = generate_video_from_slides(slides, frame_duration=2)
                            if video_path:
                                st.success("Video generated successfully!")
                                st.markdown(download_video(video_path), unsafe_allow_html=True)
                        else:
                            st.error("Failed to generate slides. Ensure insights and visualizations are defined.")
            else:
                st.error("Insights or visualizations are missing. Please try again.")


    cleanup_temp_files()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        cleanup_temp_files()
