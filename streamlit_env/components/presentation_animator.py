import os
import base64
import cv2
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np
from pathlib import Path
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def easing_function(t):
    """Ease-in-out cubic easing function."""
    return t**3 if t < 0.5 else 1 - (-2 * t + 2)**3 / 2

def create_animated_visualization(df, viz_config, duration=30, fps=30):
    """
    Create an animated visualization with smooth transitions and effects.
    
    Parameters:
        df (DataFrame): Input data
        viz_config (dict): Visualization configuration
        duration (int): Duration of animation in seconds
        fps (int): Frames per second
        
    Returns:
        list: List of frames for the animation
    """
    frames = []
    total_frames = duration * fps

    try:
        easing_values = np.array([easing_function(i / total_frames) for i in range(total_frames)])

        if viz_config['type'] == 'basic_bar':
            y_data = df[viz_config['y']].values
            x_data = df[viz_config['x']].values
            colors = px.colors.sequential.Blues

            for i in range(total_frames):
                progress = easing_values[i]
                current_y = y_data * progress
                color_idx = int(progress * (len(colors) - 1))
                current_color = colors[color_idx]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=x_data,
                        y=current_y,
                        marker=dict(color=[current_color] * len(x_data), line=dict(width=0)),
                        opacity=min(1.0, progress * 1.2)
                    )
                ])
                fig.update_layout(
                    title=viz_config['title'],
                    xaxis_title=viz_config['x'],
                    yaxis=dict(range=[0, max(y_data) * 1.1]),
                    plot_bgcolor='white',
                )
                frames.append(fig)

        elif viz_config['type'] == 'stacked_bar':
            categories = df[viz_config['x']].unique()
            stack_cols = viz_config['stack_columns']

            for i in range(total_frames):
                progress = easing_values[i]
                data = [
                    go.Bar(name=col, x=categories, y=df[col] * progress, opacity=min(1.0, progress * 1.2))
                    for col in stack_cols
                ]
                fig = go.Figure(data=data)
                fig.update_layout(
                    barmode='stack',
                    title=viz_config['title'],
                    xaxis_title=viz_config['x'],
                    yaxis=dict(range=[0, df[stack_cols].sum(axis=1).max() * 1.1]),
                    plot_bgcolor='white',
                )
                frames.append(fig)

        elif viz_config['type'] == 'grouped_bar':
            categories = df[viz_config['x']].unique()
            group_cols = viz_config['group_columns']

            for i in range(total_frames):
                progress = easing_values[i]
                data = [
                    go.Bar(name=col, x=categories, y=df[col] * progress, opacity=min(1.0, progress * 1.2))
                    for col in group_cols
                ]
                fig = go.Figure(data=data)
                fig.update_layout(
                    barmode='group',
                    title=viz_config['title'],
                    xaxis_title=viz_config['x'],
                    yaxis=dict(range=[0, df[group_cols].max().max() * 1.1]),
                    plot_bgcolor='white',
                )
                frames.append(fig)

        elif viz_config['type'] == 'line':
            x_data = df[viz_config['x']].values
            y_data = df[viz_config['y']].values

            for i in range(total_frames):
                progress = easing_values[i]
                points_to_show = max(2, int(len(x_data) * progress))
                fig = go.Figure(data=[
                    go.Scatter(
                        x=x_data[:points_to_show],
                        y=y_data[:points_to_show],
                        mode='lines+markers',
                        line=dict(width=2),
                        marker=dict(size=8, opacity=progress)
                    )
                ])
                fig.update_layout(
                    title=viz_config['title'],
                    xaxis_title=viz_config['x'],
                    yaxis=dict(range=[0, max(y_data) * 1.1]),
                    plot_bgcolor='white',
                )
                frames.append(fig)

        elif viz_config['type'] == 'scatter':
            x_data = df[viz_config['x']].values
            y_data = df[viz_config['y']].values

            for i in range(total_frames):
                progress = easing_values[i]
                points_to_show = max(2, int(len(x_data) * progress))
                fig = go.Figure(data=[
                    go.Scatter(
                        x=x_data[:points_to_show],
                        y=y_data[:points_to_show],
                        mode='markers',
                        marker=dict(size=10, opacity=progress)
                    )
                ])
                fig.update_layout(
                    title=viz_config['title'],
                    xaxis_title=viz_config['x'],
                    yaxis=dict(range=[0, max(y_data) * 1.1]),
                    plot_bgcolor='white',
                )
                frames.append(fig)

        elif viz_config['type'] == 'pie':
            values = df[viz_config['values']].values
            labels = df[viz_config['labels']].values
            colors = px.colors.qualitative.Set2
            frame_step = np.cumsum(values) / total_frames

            for i in range(total_frames):
                cumulative_values = np.minimum(values, frame_step * (i + 1))
                fig = go.Figure(data=[
                    go.Pie(
                        labels=labels,
                        values=cumulative_values,
                        textinfo="none" if i < total_frames * 0.8 else "label+percent",
                        marker=dict(colors=colors, line=dict(color="white", width=1)),
                        hole=0.3
                    )
                ])
                fig.update_layout(title=viz_config['title'], plot_bgcolor='white')
                frames.append(fig)

        return frames
    except Exception as e:
        logger.error(f"Error creating animated visualization: {str(e)}")
        return []

def generate_video_from_frames(frames, output_path=None, fps=30):
    """
    Generate a video file from Plotly frames.

    Parameters:
        frames (list): List of Plotly figures (frames) for the animation
        output_path (str, optional): Path where the video should be saved
        fps (int): Frames per second for the video

    Returns:
        str: Path to the generated video file
    """
    try:
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "visualization.mp4")
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"Created temporary directory: {temp_dir}")
            image_files = []
            for i, fig in enumerate(frames):
                image_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                try:
                    fig.write_image(image_path, format="png")
                    image_files.append(image_path)
                except Exception as e:
                    logger.error(f"Error saving frame {i}: {str(e)}")
                    continue
            
            if not image_files:
                logger.error("No frames were successfully saved")
                return None
            
            first_frame = cv2.imread(image_files[0])
            if first_frame is None:
                logger.error("Failed to read first frame")
                return None
            
            height, width, layers = first_frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frames_written = 0
            for image_file in image_files:
                frame = cv2.imread(image_file)
                if frame is not None:
                    video.write(frame)
                    frames_written += 1
                else:
                    logger.warning(f"Failed to read frame: {image_file}")
            
            video.release()
            logger.info(f"Video creation completed. Wrote {frames_written} frames to {output_path}")
            return output_path
    except Exception as e:
        logger.error(f"Error in generate_video_from_frames: {str(e)}")
        return None

def add_animation_interface(df, insights):
    """
    Add interface for creating and downloading animated visualizations.
    """
    st.write("## 🎬 Animated Visualization")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        viz_type = st.selectbox(
            "Select Visualization Type",
            ["basic_bar", "stacked_bar", "grouped_bar", "line", "scatter", "pie"]
        )
        
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        viz_config = {
            "type": viz_type,
            "title": st.text_input("Title", "Animated Visualization")
        }

        if viz_type in ['basic_bar', 'line', 'scatter']:
            viz_config.update({
                "x": st.selectbox("X-axis", categorical_cols if viz_type == 'basic_bar' else numeric_cols),
                "y": st.selectbox("Y-axis", numeric_cols)
            })
        elif viz_type == 'pie':
            viz_config.update({
                "labels": st.selectbox("Labels (Categorical)", categorical_cols),
                "values": st.selectbox("Values (Numeric)", numeric_cols)
            })
        elif viz_type in ['stacked_bar', 'grouped_bar']:
            viz_config.update({
                "x": st.selectbox("Category (X-axis)", categorical_cols),
                f"{'stack' if viz_type == 'stacked_bar' else 'group'}_columns": 
                    st.multiselect("Select columns to stack/group", numeric_cols)
            })

        duration = st.slider("Animation Duration (seconds)", 1, 10, 5)
        fps = st.slider("Frames per Second", 24, 60, 30)
        st.info("Higher FPS will result in smoother animations but longer generation time.")

    if st.button("Generate Animation", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Creating animation frames...")
            frames = create_animated_visualization(df, viz_config, duration, fps)
            progress_bar.progress(0.5)
            
            if frames:
                status_text.text("Generating video...")
                video_path = generate_video_from_frames(frames, fps=fps)
                progress_bar.progress(0.9)
                
                if video_path and os.path.exists(video_path):
                    progress_bar.progress(1.0)
                    status_text.text("Animation complete!")
                    st.success("Animation generated successfully!")
                    
                    with open(video_path, "rb") as file:
                        video_bytes = file.read()
                        if video_bytes:
                            b64 = base64.b64encode(video_bytes).decode()
                            href = f'<a href="data:video/mp4;base64,{b64}" download="visualization.mp4">Download Animation</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        else:
                            st.error("Failed to read video file for playback")
                else:
                    st.error("Failed to generate animation video")
            else:
                st.error("Failed to create animation frames")
                
        except Exception as e:
            logger.error(f"Error in animation generation: {str(e)}")
            st.error(f"Error generating animation: {str(e)}")
            
        finally:
            progress_bar.empty()
            status_text.empty()


__all__ = ['create_animated_visualization', 'generate_video_from_frames', 'add_animation_interface']
