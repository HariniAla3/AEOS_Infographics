import streamlit as st
from ydata_profiling import ProfileReport

def generate_profile_report(df):
    """
    Generates a profile report for a given DataFrame.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame to profile.
    
    Returns:
        ProfileReport: The generated profile report object.
    """
    return ProfileReport(df, title="Data Profile Report", minimal=True)

def display_profile_report(profile_report):
    """
    Displays the profile report in Streamlit.
    
    Parameters:
        profile_report (ProfileReport): The generated profile report object.
    """
    if profile_report:
        # Save the profile report as an HTML file
        profile_report.to_file("temp_report.html")
        
        # Read the HTML file and embed it in Streamlit
        with open("temp_report.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Display the report using an iframe
        st.components.v1.html(html_content, height=800, scrolling=True)
