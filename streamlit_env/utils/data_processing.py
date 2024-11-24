import pandas as pd
import plotly.express as px

def load_data(file):
    """
    Load data from a CSV file.
    
    Parameters:
        file (str or file-like): The path or file object of the CSV file.
        
    Returns:
        pd.DataFrame: Loaded DataFrame, or None if an error occurs.
    """
    try:
        return pd.read_csv(file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_visualization(df, viz_type, config):
    """
    Create a visualization based on the specified type and configuration.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame
        viz_type (str): The type of visualization (e.g., "basic_bar", "pie").
        config (dict): Configuration parameters, including columns and title.
    
    Returns:
        plotly.graph_objects.Figure: The generated visualization, or None if unsupported.
    """
    try:
        if viz_type == "basic_bar":
            return px.bar(
                df,
                x=config["x"],
                y=config["y"],
                title=config["title"],
                labels={config["x"]: config["x"].title(), config["y"]: config["y"].title()}
            )
        elif viz_type == "stacked_bar":
            return px.bar(
                df,
                x=config["x"],
                y=config["y"],
                color=config["color"],
                title=config["title"],
                labels={config["x"]: config["x"].title(), config["y"]: config["y"].title()},
                barmode="stack"
            )
        elif viz_type == "grouped_bar":
            return px.bar(
                df,
                x=config["x"],
                y=config["y"],
                color=config["color"],
                title=config["title"],
                labels={config["x"]: config["x"].title(), config["y"]: config["y"].title()},
                barmode="group"
            )
        elif viz_type == "line":
            return px.line(
                df,
                x=config["x"],
                y=config["y"],
                title=config["title"],
                labels={config["x"]: config["x"].title(), config["y"]: config["y"].title()}
            )
        elif viz_type == "scatter":
            return px.scatter(
                df,
                x=config["x"],
                y=config["y"],
                title=config["title"],
                labels={config["x"]: config["x"].title(), config["y"]: config["y"].title()}
            )
        elif viz_type == "pie":
            return px.pie(
                df,
                names=config["x"],
                values=config["y"],
                title=config["title"],
                labels={config["x"]: config["x"].title(), config["y"]: config["y"].title()}
            )
        else:
            print(f"Unsupported visualization type: {viz_type}")
            return None
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None
