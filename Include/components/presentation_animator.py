import os
import base64
import cv2
import plotly.io as pio
import plotly.graph_objects as go
import streamlit as st
from components.visualization import create_advanced_visualization


class PresentationAnimator:
    def __init__(self, df, insights, visualizations, duration=30):
        """
        Initialize the presentation animator.

        Parameters:
            df (pd.DataFrame): The dataset to visualize
            insights (dict): Generated insights from the analysis
            visualizations (list): List of visualization configurations
            duration (int): Total presentation duration in seconds
        """
        self.df = df
        self.insights = insights if isinstance(insights, dict) else {}
        self.visualizations = visualizations if isinstance(visualizations, list) else []
        self.duration = duration

    def create_insight_slide(self, insight):
        """
        Create a slide for a single insight using Plotly.

        Parameters:
            insight (dict): Single insight from the insights collection

        Returns:
            go.Figure: Plotly figure for the insight
        """
        fig = go.Figure()
        fig.add_annotation(
            text=insight.get("title", "Insight"),
            xref="paper", yref="paper",
            x=0.5, y=0.8, showarrow=False,
            font=dict(size=24, color="white"), align="center"
        )
        fig.add_annotation(
            text=insight.get("description", "No description available"),
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="white"), align="center"
        )
        fig.add_annotation(
            text=f"Business Impact: {insight.get('importance', 'N/A')}",
            xref="paper", yref="paper",
            x=0.5, y=0.2, showarrow=False,
            font=dict(size=16, color="lightblue"), align="center"
        )
        fig.update_layout(template="plotly_dark", height=600, showlegend=False)
        return fig

    def generate_presentation(self):
        """
        Generate the complete presentation as a sequence of Plotly figures.

        Returns:
            list: List of Plotly figures representing the presentation
        """
        slides = []

        # Add introduction
        intro_fig = go.Figure()
        intro_fig.add_annotation(
            text="Data Analysis Insights & Visualizations",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=32, color="white"), align="center"
        )
        intro_fig.update_layout(template="plotly_dark", height=600)
        slides.append(intro_fig)

        # Add key insights
        for insight in self.insights.get("key_insights", []):
            insight_slide = self.create_insight_slide(insight)
            if insight_slide:
                slides.append(insight_slide)

        # Add visualizations
        for viz_config in self.visualizations:
            viz_type = viz_config.get("type", "line")
            fig = create_advanced_visualization(self.df, viz_type, viz_config)
            if fig:
                slides.append(fig)

        # Add conclusion
        outro_fig = go.Figure()
        outro_fig.add_annotation(
            text="Thank you for viewing the presentation",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=32, color="white"), align="center"
        )
        outro_fig.update_layout(template="plotly_dark", height=600)
        slides.append(outro_fig)

        return slides


def generate_video_from_slides(slides, output_path="presentation.mp4", frame_duration=1):
    """
    Generate a video from slides using OpenCV.

    Parameters:
        slides (list): List of Plotly figures.
        output_path (str): Path to save the MP4 video.
        frame_duration (int): Duration of each frame in seconds.

    Returns:
        str: Path to the saved MP4 video.
    """
    temp_dir = "temp_slides"
    os.makedirs(temp_dir, exist_ok=True)

    image_paths = []
    try:
        # Save each slide as an image
        for i, slide in enumerate(slides):
            image_path = os.path.join(temp_dir, f"slide_{i}.png")
            slide.write_image(image_path, format="png", width=1920, height=1080)
            image_paths.append(image_path)

        # Determine video properties
        frame_size = (1920, 1080)
        fps = 1 / frame_duration

        # Create a VideoWriter object
        video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, frame_size)

        # Add images to video
        for image_path in image_paths:
            frame = cv2.imread(image_path)
            video_writer.write(frame)

        video_writer.release()
        return output_path
    finally:
        # Cleanup temporary images
        for image_path in image_paths:
            os.remove(image_path)
        os.rmdir(temp_dir)


def add_animation_interface(df, insights, visualizations):
    """
    Add animation interface to Streamlit app.

    Parameters:
        df (pd.DataFrame): The dataset
        insights (dict): Generated insights
        visualizations (list): List of visualization configurations
    """
    st.write("## 🎬 Interactive Presentation")

    if not isinstance(insights, dict):
        st.error("Invalid insights format. Expected a dictionary.")
        return

    duration = st.slider("Time per slide (seconds)", min_value=1, max_value=10, value=2, step=1)

    if st.button("Generate Presentation"):
        with st.spinner("Creating your presentation..."):
            animator = PresentationAnimator(df, insights, visualizations, duration)
            slides = animator.generate_presentation()

            if slides:
                st.success("Presentation generated successfully!")

                # Display slides
                for fig in slides:
                    st.plotly_chart(fig)

                # Generate MP4 video
                if st.button("Export as MP4 Video"):
                    with st.spinner("Generating video..."):
                        video_path = generate_video_from_slides(slides, frame_duration=duration)
                        if video_path:
                            st.success(f"Video saved at {video_path}")
                            with open(video_path, "rb") as file:
                                b64 = base64.b64encode(file.read()).decode()
                                href = f'<a href="data:video/mp4;base64,{b64}" download="presentation.mp4">Download MP4 Video</a>'
                                st.markdown(href, unsafe_allow_html=True)
                        else:
                            st.error("Failed to generate video. Please try again.")
            else:
                st.error("No slides were generated.")
