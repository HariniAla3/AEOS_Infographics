# visualization.py

import streamlit as st
import plotly.express as px
from utils.ai_helpers import get_ai_suggestions
from utils.data_processing import create_visualization

def get_compatible_columns(df, viz_type):
    """
    Get columns compatible with the selected visualization type.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame
        viz_type (str): The type of visualization
    
    Returns:
        tuple: (numeric_cols, categorical_cols)
    """
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    if viz_type in ['scatter', 'line']:
        return numeric_cols + date_cols, numeric_cols
    elif viz_type in ['basic_bar', 'stacked_bar', 'grouped_bar']:
        return categorical_cols + date_cols, numeric_cols
    return df.columns.tolist(), df.columns.tolist()

def create_advanced_visualization(df, viz_type, config):
    """
    Create a visualization based on the specified type and configuration.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame
        viz_type (str): The type of visualization
        config (dict): Configuration parameters
        
    Returns:
        plotly.graph_objs._figure.Figure: The generated visualization
    """
    try:
        if viz_type == "basic_bar":
            return px.bar(df, x=config["x"], y=config["y"], 
                         title=config["title"],
                         labels={config["x"]: config["x"].title(), 
                                config["y"]: config["y"].title()})
        
        elif viz_type == "stacked_bar":
            color_col = config.get("color")
            if color_col:
                return px.bar(df, x=config["x"], y=config["y"],
                            color=color_col,
                            title=config["title"],
                            labels={config["x"]: config["x"].title(), 
                                   config["y"]: config["y"].title()})
            return px.bar(df, x=config["x"], y=config["y"],
                         title=config["title"])
        
        elif viz_type == "grouped_bar":
            color_col = config.get("color")
            if color_col:
                return px.bar(df, x=config["x"], y=config["y"],
                            color=color_col, barmode="group",
                            title=config["title"],
                            labels={config["x"]: config["x"].title(), 
                                   config["y"]: config["y"].title()})
            return px.bar(df, x=config["x"], y=config["y"],
                         title=config["title"])
        
        elif viz_type == "line":
            return px.line(df, x=config["x"], y=config["y"],
                          title=config["title"],
                          labels={config["x"]: config["x"].title(), 
                                 config["y"]: config["y"].title()})
        
        elif viz_type == "scatter":
            return px.scatter(df, x=config["x"], y=config["y"],
                            title=config["title"],
                            labels={config["x"]: config["x"].title(), 
                                   config["y"]: config["y"].title()})
        
        else:
            st.error(f"Unsupported visualization type: {viz_type}")
            return None
            
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None

def visualize_data(df, client):
    """
    Main function for data visualization interface.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame
        client: The AI client for getting suggestions
    """
    st.write("## Data Visualization")
    
    # Create columns for better layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        viz_type = st.selectbox("Select Visualization Type", [
            "basic_bar", "stacked_bar", "grouped_bar", "line", "scatter"
        ])
        
        # Get compatible columns for the selected visualization
        x_cols, y_cols = get_compatible_columns(df, viz_type)
        
        config = {}
        config["x"] = st.selectbox("X-axis", x_cols)
        config["y"] = st.selectbox("Y-axis", y_cols)
        
        # Add color option for bar charts
        if viz_type in ['stacked_bar', 'grouped_bar']:
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            config["color"] = st.selectbox("Color by", ['None'] + categorical_cols)
            if config["color"] == 'None':
                config.pop("color")
        
        config["title"] = st.text_input("Title", "")
        
        if st.button("Generate Visualization"):
            with col2:
                fig = create_advanced_visualization(df, viz_type, config)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        if st.button("Get AI Suggestions"):
            with st.spinner("Getting AI suggestions..."):
                suggestions = get_ai_suggestions(client, df, viz_type)
                if suggestions:
                    with col2:
                        st.write("### AI Suggestions")
                        st.json(suggestions)
                        config = suggestions["parameters"]
                        fig = create_advanced_visualization(df, viz_type, config)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)