import pandas as pd
import plotly.express as px

def load_data(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        return None

def create_visualization(df, viz_type, config):
    if viz_type == "basic_bar":
        return px.bar(df, x=config["x"], y=config["y"], title=config["title"])
    elif viz_type == "line":
        return px.line(df, x=config["x"], y=config["y"], title=config["title"])
    # Add other visualization types as needed
    return None
