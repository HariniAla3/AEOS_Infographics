# InfographX AI Studio
 AI-Powered Dynamic Infographic Generation for Data Storytelling
## Overview
The **InfographX AI Studio** is a Streamlit-based application designed to simplify data exploration, visualization, and storytelling. It enables users to upload datasets, generate insights, and create dynamic visualizations with ease. Additionally, the app produces animated infographics for data-driven storytelling.

---

## Features

### 1. **Data Input Options**
- **File Upload**: Users can upload CSV files containing structured data.
- **Structured Survey Text Input**: Enter plain-text data in a structured, descriptive format.  
  Example:  
  _Smartphone sales (in millions) for the top five brands in 2023: Brand A (300M), Brand B (250M), Brand C (200M), Brand D (150M), Others (100M)._

### 2. **AI-Powered Insights**
- Extracts trends, key insights, and patterns from uploaded datasets.
- Provides AI-generated visualization suggestions based on the nature of the data.

### 3. **Dynamic Visualizations**
- Generates various types of visualizations, including:
  - Basic Bar Charts
  - Stacked/Grouped Bar Charts
  - Line Graphs
  - Pie Charts
  - Scatter Plots

### 4. **Animated Infographics**
- Creates animated visualizations with transitions for storytelling.
- Animations can be downloaded as MP4 video files.

### 5. **Data Profiling**
- Automatically generates a comprehensive data profiling report.
- Provides an overview of dataset features, including numerical and categorical summaries.

---

## Setup Instructions

### **Prerequisites**
- **Python**
- **Groq API Key**

### **Installation Steps**
- Follow the app's installation guide to set up the environment.

  ![Install](https://github.com/user-attachments/assets/5434a774-2486-42a8-b48e-54c958694804)

---

## Usage Instructions

### **Step 1: Data Upload**
- **Option 1**: Upload a CSV file via the file uploader.
- **Option 2**: Input structured survey text in the text area provided.

### **Step 2: Select Tab for Analysis**
- **Visualization**: Create custom visualizations for exploring data patterns.
- **Insights**: View AI-generated insights about the dataset.
- **Data Profile**: Generate a detailed report on data distributions and relationships.
- **Animation**: Design and download animated infographic videos.

### **Step 3: Customize and Download Outputs**
- Customize parameters like chart type, labels, and animation duration.
- Download visualizations as PNG and infographic videos as MP4 files.

---

## Example Workflow

### **Input**
- Upload a CSV file with sales data.  
- Enter structured survey text, e.g.,  
  _"20% of users prefer product A, 50% prefer product B."_

### **Output**
- Generates a bar chart for sales performance.
- Downloads an animated pie chart MP4 video showing user preferences.

![chart1](https://github.com/user-attachments/assets/ed33c63e-ff8e-4311-9326-efa9a54b1935)
---

## API Integration

### **Groq AI API**
The app utilizes the Groq AI API for:
1. **Natural Language Processing**: Extracts data insights and column information from structured text.
2. **Visualization Recommendations**: Suggests suitable visualizations for data storytelling.

---

## Supported Technologies

### **Frontend**
- **Streamlit**: Interactive UI.

### **Backend**
- **Data Processing**: Pandas, NumPy  
- **Visualization**: Plotly  
- **Profiling**: YData Profiling  
- **Animation and Video Rendering**: OpenCV, Plotly  

---

## Sample Test Cases

| **Input**                        | **Expected Output**                       |
|----------------------------------|-------------------------------------------|
| Text: "20% of users prefer A, 80% B" | Pie chart animation showing distribution. |
| CSV: File with time-series data   | Line graph with smooth animations.        |
| CSV: Sales performance data       | Bar chart highlighting product sales.     |

---

## Performance Metrics
- **Average Visualization Generation Time**: 2 seconds  
- **Animation Export Time**: 10 seconds per minute of video  

---

## Supported Platforms
- ✅ **Web** (via modern browsers)  
- ⬜ **Android**  
- ⬜ **iOS**  
- ⬜ **macOS**




























