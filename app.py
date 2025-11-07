"""
Modern Streamlit application for AI Resume Analyzer with improved UI/UX.

This module provides a modern, step-by-step interface for resume analysis,
eliminating the awkward sidebar layout and creating an intuitive workflow.
"""

import streamlit as st
import os
import logging
import tempfile
from typing import Optional, Dict, Any
from io import BytesIO

# Import our modules
import parsing
import ai_integration
import tts_video
import db  # SQLite database module

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar by default
    menu_items={
        'Get Help': 'https://github.com/Denis172003/CV-Analyser',
        'Report a bug': 'https://github.com/Denis172003/CV-Analyser/issues',
        'About': "AI Resume Analyzer - Transform your resume with AI-powered insights!"
    }
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'extracted_text': "",
        'analysis_results': None,
        'video_path': None,
        'processing_stage': "ready",
        'show_history': False,
        'selected_history_item': None,
        'job_description_text': "",
        'company_name': "",
        'job_title': "",
        'job_analysis_results': None,
        'current_step': 1,
        'uploaded_file': None,
        'extraction_method': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_modern_css():
    """Add modern CSS styling for improved UI/UX."""
    st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Modern color scheme */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --background-light: #F8F9FA;
        --text-dark: #2C3E50;
        --border-light: #E9ECEF;
        --shadow-light: rgba(0,0,0,0.1);
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 4rem 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 15px 40px rgba(46, 134, 171, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #ffffff, #f0f8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 3rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 2rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Features Overview */
    .features-overview {
        margin-bottom: 3rem;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid var(--border-light);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-card h3 {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 1rem;
    }
    
    .feature-card p {
        color: #666;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Quick Start Guide */
    .quick-start-guide {
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 1px solid var(--border-light);
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .quick-start-guide h2 {
        text-align: center;
        color: var(--text-dark);
        margin-bottom: 2rem;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .quick-start-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
    }
    
    .quick-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .quick-step:hover {
        transform: translateY(-3px);
    }
    
    .step-icon {
        font-size: 2rem;
        flex-shrink: 0;
    }
    
    .step-content h4 {
        color: var(--text-dark);
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .step-content p {
        color: #666;
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Step cards */
    .step-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px var(--shadow-light);
        border: 1px solid var(--border-light);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .step-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .step-card.active {
        border-left: 5px solid var(--primary-color);
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
    }
    
    .step-card.completed {
        border-left: 5px solid var(--success-color);
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
    }
    
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .step-number {
        background: var(--primary-color);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        font-size: 1.2rem;
    }
    
    .step-number.completed {
        background: var(--success-color);
    }
    
    .step-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #000000 !important;
        margin: 0;
    }
    
    /* Ensure all text in step cards is black */
    .step-card h3,
    .step-card p,
    .step-card div,
    .step-card span {
        color: #000000 !important;
    }
    
    /* Override Streamlit's default text colors */
    .step-card .stMarkdown,
    .step-card .stMarkdown p,
    .step-card .stMarkdown div {
        color: #000000 !important;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 2px dashed var(--primary-color);
        border-radius: 15px;
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: var(--secondary-color);
        background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4);
    }
    
    /* Progress indicators */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }
    
    /* Results styling */
    .results-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px var(--shadow-light);
    }
    
    .skill-tag {
        background: linear-gradient(135deg, #e1f5fe 0%, #f0f8ff 100%);
        color: var(--text-dark);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 500;
        border: 1px solid #b3e5fc;
    }
    
    /* Video container */
    .video-container {
        background: var(--background-light);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px var(--shadow-light);
        border: 1px solid var(--border-light);
        margin: 0.5rem 0;
    }
    
    /* Mock Interview Styling */
    .interview-question {
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
        border-left: 4px solid var(--primary-color);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .score-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid var(--border-light);
        margin: 0.5rem;
    }
    
    .score-excellent {
        border-left: 4px solid #28a745;
    }
    
    .score-good {
        border-left: 4px solid #ffc107;
    }
    
    .score-needs-improvement {
        border-left: 4px solid #dc3545;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .hero-stats {
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .features-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .step-card {
            padding: 1.5rem;
        }
        
        .upload-area {
            padding: 2rem 1rem;
        }
        
        .interview-question {
            padding: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .hero-section {
            padding: 3rem 1rem;
        }
        
        .hero-title {
            font-size: 2rem;
        }
        
        .stat-number {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def create_hero_dashboard():
    """Create a comprehensive hero dashboard with features overview."""
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">Present Your True Potential</h1>
            <p class="hero-subtitle">Transform your career with AI-powered resume analysis, job matching, and interview preparation</p>
            <div class="hero-stats">
                <div class="stat-item">
                    <div class="stat-number">10s</div>
                    <div class="stat-label">Video Generation</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">95%</div>
                    <div class="stat-label">Match Accuracy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Mock Questions</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="features-overview">
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <h3>Smart Analysis</h3>
                <p>AI-powered resume analysis with detailed insights, strengths identification, and improvement suggestions</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Job Matching</h3>
                <p>Compare your resume against job requirements with compatibility scoring and skill gap analysis</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎥</div>
                <h3>Video Pitches</h3>
                <p>Generate personalized 10-second video pitches using advanced AI and professional templates</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎤</div>
                <h3>Mock Interviews</h3>
                <p>Practice with AI-generated interview questions and receive detailed performance feedback</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h3>ATS Optimization</h3>
                <p>Optimize your resume for Applicant Tracking Systems with keyword recommendations</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Progress Tracking</h3>
                <p>Monitor your improvement over time with detailed analytics and performance metrics</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded file format and size."""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file extension
    file_extension = uploaded_file.name.lower().split('.')[-1]
    if file_extension not in ['pdf', 'docx']:
        return False, f"Unsupported file format: {file_extension}. Please upload PDF or DOCX files only."
    
    # Check file size (limit to 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        return False, "File size too large. Please upload files smaller than 10MB."
    
    return True, ""


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary location."""
    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save file with original name
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return temp_path


def extract_text_from_file(file_path: str) -> tuple[str, str]:
    """Extract text from uploaded file with error handling."""
    try:
        # Determine file type and extract text
        if file_path.lower().endswith('.pdf'):
            extracted_text = parsing.extract_text_pdf(file_path)
            method = "PDF extraction"
        elif file_path.lower().endswith('.docx'):
            extracted_text = parsing.extract_text_docx(file_path)
            method = "DOCX extraction"
        else:
            raise ValueError("Unsupported file format")
        
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return extracted_text, method
        
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        raise Exception(f"Failed to extract text: {str(e)}")


def generate_pitch_video(analysis_results: Dict[str, Any], video_type: str = "General Pitch", 
                        industry_style: str = "Professional", job_analysis: Dict = None) -> tuple[str, str]:
    """Generate personalized video pitch from analysis results."""
    try:
        # Generate script based on analysis
        script_data = ai_integration.generate_pitch_script(analysis_results)
        
        if not script_data:
            return "", "Failed to generate pitch script"
        
        # Create output directory
        output_dir = "temp"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate video using TTS and moviepy
        video_path = tts_video.generate_pitch_video(
            script_data=script_data,
            output_dir=output_dir,
            language="en",
            target_duration=10.0
        )
        
        if os.path.exists(video_path):
            return video_path, f"{video_type} generated successfully"
        else:
            return "", "Video file was not created"
            
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        return "", f"Video generation failed: {str(e)}"


def display_quick_start_guide():
    """Display a quick start guide for new users."""
    if not st.session_state.get('uploaded_file'):
        st.markdown("""
        <div class="quick-start-guide">
            <h2>🚀 Quick Start Guide</h2>
            <div class="quick-start-steps">
                <div class="quick-step">
                    <div class="step-icon">1️⃣</div>
                    <div class="step-content">
                        <h4>Upload Your Resume</h4>
                        <p>Drop your PDF or DOCX resume file to get started</p>
                    </div>
                </div>
                <div class="quick-step">
                    <div class="step-icon">2️⃣</div>
                    <div class="step-content">
                        <h4>Add Job Description</h4>
                        <p>Paste a job posting for personalized analysis</p>
                    </div>
                </div>
                <div class="quick-step">
                    <div class="step-icon">3️⃣</div>
                    <div class="step-content">
                        <h4>Get AI Insights</h4>
                        <p>Receive detailed analysis and improvement suggestions</p>
                    </div>
                </div>
                <div class="quick-step">
                    <div class="step-icon">4️⃣</div>
                    <div class="step-content">
                        <h4>Practice & Perfect</h4>
                        <p>Generate videos and practice mock interviews</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_workflow_steps():
    """Display the main workflow as interactive steps."""
    # Step 1: Upload Resume
    display_upload_step()
    
    # Step 2: Extract Text (if file uploaded)
    if st.session_state.get('uploaded_file') is not None:
        display_extraction_step()
    
    # Step 3: Add Job Description (optional)
    if st.session_state.get('extracted_text'):
        display_job_description_step()
    
    # Step 4: Analyze Resume
    if st.session_state.get('extracted_text'):
        display_analysis_step()
    
    # Step 5: Generate Video
    if st.session_state.get('analysis_results'):
        display_video_step()
    
    # Step 6: Mock Interview
    if st.session_state.get('analysis_results'):
        display_mock_interview_step()
    
    # Step 7: View History
    display_history_step()


def display_upload_step():
    """Display the file upload step with modern design."""
    step_status = "completed" if st.session_state.get('uploaded_file') else "active"
    
    st.markdown(f"""
    <div class="step-card {step_status}">
        <div class="step-header">
            <div class="step-number {'completed' if step_status == 'completed' else ''}">1</div>
            <h3 class="step-title">Upload Your Resume</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload area
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx'],
            help="Upload PDF or DOCX resume files (max 10MB)",
            key="resume_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_file is None:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h4 style="color: #2E86AB; margin-bottom: 1rem;">📄 Drop your resume here</h4>
                <p style="color: #6c757d;">Supports PDF and DOCX files up to 10MB</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Validate and store file
    if uploaded_file is not None:
        is_valid, error_msg = validate_file_upload(uploaded_file)
        if is_valid:
            st.session_state.uploaded_file = uploaded_file
            st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
            st.session_state.current_step = max(st.session_state.current_step, 2)
        else:
            st.error(f"❌ {error_msg}")


def display_extraction_step():
    """Display the text extraction step."""
    step_status = "completed" if st.session_state.get('extracted_text') else "active"
    
    st.markdown(f"""
    <div class="step-card {step_status}">
        <div class="step-header">
            <div class="step-number {'completed' if step_status == 'completed' else ''}">2</div>
            <h3 class="step-title">Extract Text from Resume</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('extracted_text'):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔍 Extract Text", key="extract_btn", use_container_width=True):
                with st.spinner("Extracting text from your resume..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = save_uploaded_file(st.session_state.uploaded_file)
                        
                        # Extract text
                        extracted_text, extraction_method = extract_text_from_file(temp_path)
                        
                        if extracted_text.strip():
                            st.session_state.extracted_text = extracted_text
                            st.session_state.extraction_method = extraction_method
                            st.session_state.current_step = max(st.session_state.current_step, 3)
                            st.rerun()
                        else:
                            st.error("❌ Could not extract text from the file. Please try a different file.")
                    
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {str(e)}")
    else:
        # Show extracted text preview
        with st.expander("📄 View Extracted Text", expanded=False):
            st.text_area(
                "Extracted Content",
                value=st.session_state.extracted_text,
                height=200,
                disabled=True,
                label_visibility="collapsed"
            )
            
            # Text statistics
            word_count = len(st.session_state.extracted_text.split())
            char_count = len(st.session_state.extracted_text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", word_count)
            with col2:
                st.metric("Characters", char_count)
            with col3:
                st.metric("Method", st.session_state.get('extraction_method', 'Unknown'))


def display_job_description_step():
    """Display the job description input step."""
    st.markdown(f"""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">3</div>
            <h3 class="step-title">Add Job Description (Optional)</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Adding a job description enables advanced features like skill gap analysis and job-specific optimization!")
    
    # Company and job title
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input(
            "Company Name",
            value=st.session_state.get('company_name', ''),
            placeholder="e.g., Google, Microsoft, Startup Inc.",
            key="company_input"
        )
        st.session_state.company_name = company_name
        
    with col2:
        job_title = st.text_input(
            "Job Title",
            value=st.session_state.get('job_title', ''),
            placeholder="e.g., Software Engineer, Data Scientist",
            key="job_title_input"
        )
        st.session_state.job_title = job_title
    
    # Job description
    job_description = st.text_area(
        "Job Description",
        value=st.session_state.get('job_description_text', ''),
        height=150,
        placeholder="Paste the complete job description here...\n\nInclude:\n• Job responsibilities\n• Required skills and qualifications\n• Company culture information",
        key="job_desc_input"
    )
    st.session_state.job_description_text = job_description
    
    # Show job description stats
    if job_description:
        word_count = len(job_description.split())
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", word_count)
        with col2:
            if word_count < 50:
                st.metric("Quality", "⚠️ Brief")
            elif word_count > 200:
                st.metric("Quality", "✅ Detailed")
            else:
                st.metric("Quality", "✅ Good")
        with col3:
            if company_name and job_title:
                st.metric("Status", "✅ Complete")
            else:
                st.metric("Status", "⚠️ Incomplete")


def display_analysis_step():
    """Display the analysis step."""
    step_status = "completed" if st.session_state.get('analysis_results') else "active"
    
    st.markdown(f"""
    <div class="step-card {step_status}">
        <div class="step-header">
            <div class="step-number {'completed' if step_status == 'completed' else ''}">4</div>
            <h3 class="step-title">AI Analysis & Insights</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('analysis_results'):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analysis_type = "Job-Specific Analysis" if st.session_state.get('job_description_text') else "General Analysis"
            
            if st.button(f"🤖 Start {analysis_type}", key="analyze_btn", use_container_width=True):
                with st.spinner("AI is analyzing your resume..."):
                    try:
                        # Perform basic analysis
                        job_desc = st.session_state.get('job_description_text', '')
                        analysis_results = ai_integration.call_gpt_analysis(
                            st.session_state.extracted_text, 
                            job_desc
                        )
                        
                        # If job description provided, add job matching analysis
                        if job_desc.strip():
                            with st.spinner("Analyzing job compatibility..."):
                                # Analyze job description
                                job_analysis = ai_integration.analyze_job_description(job_desc)
                                
                                # Generate CV optimization advice
                                optimization_advice = ai_integration.generate_cv_optimization_advice(
                                    analysis_results, job_analysis
                                )
                                
                                # Add job matching results to analysis
                                analysis_results['job_analysis'] = job_analysis
                                analysis_results['optimization_advice'] = optimization_advice
                                
                                # Calculate compatibility score
                                skill_gap = optimization_advice.get('skill_gap_analysis', {})
                                analysis_results['compatibility_score'] = skill_gap.get('compatibility_score', 0)
                                analysis_results['matching_skills'] = skill_gap.get('matching_skills', [])
                                analysis_results['missing_skills'] = skill_gap.get('missing_skills', [])
                                
                                # Generate interview questions
                                with st.spinner("Generating interview questions..."):
                                    interview_questions = ai_integration.generate_interview_questions(
                                        analysis_results, job_analysis
                                    )
                                    analysis_results['interview_questions'] = interview_questions
                        
                        st.session_state.analysis_results = analysis_results
                        st.session_state.current_step = max(st.session_state.current_step, 5)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
    else:
        # Display analysis results
        display_analysis_results()


def display_video_step():
    """Display the video generation step."""
    step_status = "completed" if st.session_state.get('video_path') else "active"
    
    st.markdown(f"""
    <div class="step-card {step_status}">
        <div class="step-header">
            <div class="step-number {'completed' if step_status == 'completed' else ''}">5</div>
            <h3 class="step-title">Generate Video Pitch</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('video_path'):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🎥 Generate Video Pitch", key="video_btn", use_container_width=True):
                with st.spinner("Creating your personalized video pitch..."):
                    try:
                        video_path, status_message = generate_pitch_video(
                            st.session_state.analysis_results,
                            "General Pitch",
                            "Professional"
                        )
                        
                        if video_path and os.path.exists(video_path):
                            st.session_state.video_path = video_path
                            st.success(f"✅ {status_message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {status_message}")
                            
                    except Exception as e:
                        st.error(f"❌ Video generation failed: {str(e)}")
    else:
        # Display video
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        st.video(st.session_state.video_path)
        
        # Download button
        with open(st.session_state.video_path, "rb") as video_file:
            st.download_button(
                label="📥 Download Video",
                data=video_file.read(),
                file_name="resume_pitch.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)


def display_mock_interview_step():
    """Display the mock interview step."""
    st.markdown(f"""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">6</div>
            <h3 class="step-title">Mock Interview Practice</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🎭 Practice your interview skills with AI-powered mock interviews!")
    
    # Initialize session state for mock interview
    if 'mock_interview_questions' not in st.session_state:
        st.session_state.mock_interview_questions = None
    if 'mock_interview_responses' not in st.session_state:
        st.session_state.mock_interview_responses = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'interview_completed' not in st.session_state:
        st.session_state.interview_completed = False
    if 'interview_evaluation' not in st.session_state:
        st.session_state.interview_evaluation = None
    
    # Start Mock Interview Button
    if not st.session_state.mock_interview_questions and not st.session_state.interview_completed:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🎭 Start Mock Interview", key="start_mock_interview", use_container_width=True):
                with st.spinner("Preparing your personalized mock interview..."):
                    try:
                        # Generate mock interview questions
                        job_analysis = st.session_state.analysis_results.get('job_analysis')
                        mock_interview = ai_integration.conduct_mock_interview(
                            st.session_state.analysis_results,
                            job_analysis
                        )
                        
                        st.session_state.mock_interview_questions = mock_interview
                        st.session_state.mock_interview_responses = []
                        st.session_state.current_question_index = 0
                        st.session_state.interview_completed = False
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to start mock interview: {str(e)}")
    
    # Display Mock Interview Questions
    elif st.session_state.mock_interview_questions and not st.session_state.interview_completed:
        display_mock_interview_questions()
    
    # Display Interview Results
    elif st.session_state.interview_completed and st.session_state.interview_evaluation:
        display_interview_evaluation()
    
    # Reset Interview Button
    if st.session_state.interview_completed:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Start New Mock Interview", key="restart_mock_interview", use_container_width=True):
                # Reset all interview state
                st.session_state.mock_interview_questions = None
                st.session_state.mock_interview_responses = []
                st.session_state.current_question_index = 0
                st.session_state.interview_completed = False
                st.session_state.interview_evaluation = None
                st.rerun()


def display_mock_interview_questions():
    """Display the mock interview questions one by one."""
    questions = st.session_state.mock_interview_questions.get('questions', [])
    current_index = st.session_state.current_question_index
    
    if current_index < len(questions):
        current_question = questions[current_index]
        
        # Interview context
        context = st.session_state.mock_interview_questions.get('interview_context', {})
        st.markdown(f"**Interview for:** {context.get('position', 'Position')} at {context.get('company', 'Company')}")
        
        # Progress indicator
        progress = (current_index + 1) / len(questions)
        st.progress(progress)
        st.markdown(f"**Question {current_index + 1} of {len(questions)}**")
        
        # Question details
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {current_question.get('question', '')}")
        with col2:
            difficulty_color = {
                'Easy': '🟢',
                'Medium': '🟡', 
                'Hard': '🔴'
            }
            difficulty = current_question.get('difficulty', 'Medium')
            st.markdown(f"**Difficulty:** {difficulty_color.get(difficulty, '🟡')} {difficulty}")
        
        # Category and tips
        st.markdown(f"**Category:** {current_question.get('category', 'General')}")
        
        with st.expander("💡 Tips for answering", expanded=False):
            st.markdown(f"**What we're looking for:** {current_question.get('evaluation_criteria', 'Clear and relevant response')}")
            if current_question.get('expected_elements'):
                st.markdown("**Try to include:**")
                for element in current_question['expected_elements']:
                    st.markdown(f"• {element}")
        
        # Response input
        response_key = f"response_{current_index}"
        user_response = st.text_area(
            "Your Answer:",
            height=150,
            placeholder="Take your time to provide a thoughtful response...",
            key=response_key
        )
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_index > 0:
                if st.button("⬅️ Previous Question", key="prev_question"):
                    st.session_state.current_question_index -= 1
                    st.rerun()
        
        with col3:
            if user_response.strip():
                if current_index < len(questions) - 1:
                    if st.button("Next Question ➡️", key="next_question"):
                        # Save current response
                        if len(st.session_state.mock_interview_responses) <= current_index:
                            st.session_state.mock_interview_responses.extend([''] * (current_index + 1 - len(st.session_state.mock_interview_responses)))
                        st.session_state.mock_interview_responses[current_index] = user_response
                        st.session_state.current_question_index += 1
                        st.rerun()
                else:
                    if st.button("🏁 Complete Interview", key="complete_interview"):
                        # Save final response and evaluate
                        if len(st.session_state.mock_interview_responses) <= current_index:
                            st.session_state.mock_interview_responses.extend([''] * (current_index + 1 - len(st.session_state.mock_interview_responses)))
                        st.session_state.mock_interview_responses[current_index] = user_response
                        
                        # Evaluate the interview
                        with st.spinner("Evaluating your interview performance..."):
                            try:
                                job_analysis = st.session_state.analysis_results.get('job_analysis')
                                evaluation = ai_integration.evaluate_interview_responses(
                                    questions,
                                    st.session_state.mock_interview_responses,
                                    st.session_state.analysis_results,
                                    job_analysis
                                )
                                
                                st.session_state.interview_evaluation = evaluation
                                st.session_state.interview_completed = True
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Failed to evaluate interview: {str(e)}")
            else:
                st.info("Please provide an answer to continue.")


def display_interview_evaluation():
    """Display the interview evaluation results."""
    evaluation = st.session_state.interview_evaluation
    questions = st.session_state.mock_interview_questions.get('questions', [])
    
    st.markdown("## 🎯 Interview Performance Report")
    
    # Overall Score
    overall_score = evaluation.get('overall_score', 0)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.progress(overall_score / 100)
        score_color = "🟢" if overall_score >= 80 else "🟡" if overall_score >= 60 else "🔴"
        st.markdown(f"### {score_color} Overall Score: {overall_score}/100")
        
        # Score interpretation
        if overall_score >= 90:
            st.success("🌟 Excellent performance! You're well-prepared for interviews.")
        elif overall_score >= 80:
            st.success("✅ Good performance! Minor improvements will make you even stronger.")
        elif overall_score >= 70:
            st.warning("⚠️ Decent performance, but there's room for improvement.")
        elif overall_score >= 60:
            st.warning("📈 You're on the right track, but need more practice.")
        else:
            st.error("📚 Consider more preparation and practice before your interview.")
    
    with col2:
        st.metric("Communication", f"{evaluation.get('interview_performance', {}).get('communication', 0)}/100")
    
    with col3:
        st.metric("Relevance", f"{evaluation.get('interview_performance', {}).get('relevance', 0)}/100")
    
    # Performance Breakdown
    st.markdown("### 📊 Performance Breakdown")
    performance = evaluation.get('interview_performance', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        comm_score = performance.get('communication', 0)
        st.metric("Communication", f"{comm_score}/100")
    with col2:
        rel_score = performance.get('relevance', 0)
        st.metric("Relevance", f"{rel_score}/100")
    with col3:
        conf_score = performance.get('confidence', 0)
        st.metric("Confidence", f"{conf_score}/100")
    with col4:
        spec_score = performance.get('specificity', 0)
        st.metric("Specificity", f"{spec_score}/100")
    
    # Individual Question Feedback
    st.markdown("### 📝 Question-by-Question Feedback")
    
    individual_scores = evaluation.get('individual_scores', [])
    for i, (question, score_data) in enumerate(zip(questions, individual_scores)):
        with st.expander(f"Q{i+1}: {question.get('question', '')[:60]}... - Score: {score_data.get('score', 0)}/100", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Your Response:**")
                response = st.session_state.mock_interview_responses[i] if i < len(st.session_state.mock_interview_responses) else ""
                st.markdown(f"*{response[:200]}{'...' if len(response) > 200 else ''}*")
                
                st.markdown("**Feedback:**")
                st.markdown(score_data.get('feedback', 'No feedback available'))
            
            with col2:
                st.markdown("**Strengths:**")
                for strength in score_data.get('strengths', []):
                    st.markdown(f"✅ {strength}")
                
                st.markdown("**Areas for Improvement:**")
                for improvement in score_data.get('improvements', []):
                    st.markdown(f"📈 {improvement}")
    
    # Overall Feedback
    st.markdown("### 💡 Overall Feedback")
    overall_feedback = evaluation.get('overall_feedback', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌟 Your Strengths:**")
        for strength in overall_feedback.get('strengths', []):
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("**📈 Areas for Improvement:**")
        for improvement in overall_feedback.get('areas_for_improvement', []):
            st.markdown(f"• {improvement}")
    
    # Recommendations
    st.markdown("### 🎯 Recommendations for Next Steps")
    for recommendation in overall_feedback.get('recommendations', []):
        st.markdown(f"🔹 {recommendation}")


def display_history_step():
    """Display the history step."""
    st.markdown(f"""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">7</div>
            <h3 class="step-title">View History & Progress</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📚 View Analysis History", key="history_btn", use_container_width=True):
            st.session_state.show_history = True
            st.rerun()
    
    if st.session_state.get('show_history'):
        display_history_content()


def display_analysis_results():
    """Display analysis results in a modern format."""
    results = st.session_state.analysis_results
    
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Job Compatibility Score (if job description was provided)
    if 'compatibility_score' in results and results['compatibility_score'] is not None:
        st.markdown("### 🎯 Job Compatibility Score")
        
        score = results['compatibility_score']
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Create a progress bar for the score
            st.progress(score / 100)
            st.markdown(f"**{score}% Match** with job requirements")
            
            # Color-coded interpretation
            if score >= 80:
                st.success("🟢 Excellent match! You're well-qualified for this position.")
            elif score >= 60:
                st.warning("🟡 Good match with some areas for improvement.")
            else:
                st.error("🔴 Significant skill gaps identified. Consider upskilling.")
        
        with col2:
            if 'matching_skills' in results and results['matching_skills']:
                st.metric("Matching Skills", len(results['matching_skills']))
        
        with col3:
            if 'missing_skills' in results and results['missing_skills']:
                st.metric("Missing Skills", len(results['missing_skills']))
        
        st.markdown("---")
    
    # Skills Comparison (if job matching was performed)
    if 'matching_skills' in results or 'missing_skills' in results:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'matching_skills' in results and results['matching_skills']:
                st.markdown("### ✅ Matching Skills")
                skills_html = ""
                for skill in results['matching_skills']:
                    skills_html += f'<span style="background-color: #d4edda; color: #155724; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px;">{skill}</span> '
                st.markdown(skills_html, unsafe_allow_html=True)
        
        with col2:
            if 'missing_skills' in results and results['missing_skills']:
                st.markdown("### ❌ Missing Skills")
                skills_html = ""
                for skill in results['missing_skills']:
                    skills_html += f'<span style="background-color: #f8d7da; color: #721c24; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px;">{skill}</span> '
                st.markdown(skills_html, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Top Skills
    if 'top_skills' in results and results['top_skills']:
        st.markdown("### 🎯 Top Skills")
        skills_html = ""
        for skill in results['top_skills']:
            skills_html += f'<span class="skill-tag">{skill}</span> '
        st.markdown(skills_html, unsafe_allow_html=True)
        st.markdown("---")
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Strengths")
        if 'strengths' in results:
            for strength in results['strengths']:
                st.markdown(f"**{strength.get('text', '')}**")
                if 'evidence' in strength:
                    st.markdown(f"*{strength['evidence']}*")
                st.markdown("")
    
    with col2:
        st.markdown("### ⚠️ Areas for Improvement")
        if 'weak_points' in results:
            for weakness in results['weak_points']:
                st.markdown(f"**{weakness.get('text', '')}**")
                if 'reason' in weakness:
                    st.markdown(f"*{weakness['reason']}*")
                st.markdown("")
    
    # CV Optimization Advice (if job matching was performed)
    if 'optimization_advice' in results:
        optimization = results['optimization_advice']
        
        # Keyword Optimization
        if 'keyword_optimization' in optimization:
            st.markdown("### 🔍 Keyword Optimization")
            keyword_data = optimization['keyword_optimization']
            
            # Missing industry keywords
            if 'missing_industry_keywords' in keyword_data and keyword_data['missing_industry_keywords']:
                st.markdown("**Add these keywords to your resume:**")
                keywords = keyword_data['missing_industry_keywords']
                keywords_html = ""
                for keyword in keywords:
                    keywords_html += f'<span style="background-color: #e1f5fe; color: #000000; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px;">{keyword}</span> '
                st.markdown(keywords_html, unsafe_allow_html=True)
            
            # Title optimization
            if 'title_optimization' in keyword_data:
                st.markdown("**Title Suggestions:**")
                st.write(keyword_data['title_optimization'])
            
            # ATS optimization tips
            if 'ats_optimization_tips' in keyword_data:
                st.markdown("**ATS Optimization Tips:**")
                for tip in keyword_data['ats_optimization_tips']:
                    st.write(f"• {tip}")
        
        st.markdown("---")
    
    # Interview Questions (if generated)
    if 'interview_questions' in results:
        st.markdown("### 🎤 Potential Interview Questions")
        st.info("💡 Practice these questions to prepare for your interview!")
        
        questions = results['interview_questions']
        
        # Create tabs for different difficulty levels
        easy_tab, medium_tab, hard_tab = st.tabs(["🟢 Easy", "🟡 Medium", "🔴 Hard"])
        
        with easy_tab:
            st.markdown("**Warm-up questions to get you comfortable:**")
            if 'easy_questions' in questions:
                for i, q in enumerate(questions['easy_questions'], 1):
                    with st.expander(f"Q{i}: {q.get('question', '')}", expanded=False):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown(f"**Category:** {q.get('category', 'General')}")
                            st.markdown(f"**Focus:** {q.get('focus', 'General assessment')}")
                        with col2:
                            st.markdown(f"**💡 Tip:** {q.get('tip', 'Be honest and specific')}")
        
        with medium_tab:
            st.markdown("**Questions about your experience and skills:**")
            if 'medium_questions' in questions:
                for i, q in enumerate(questions['medium_questions'], 1):
                    with st.expander(f"Q{i}: {q.get('question', '')}", expanded=False):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown(f"**Category:** {q.get('category', 'General')}")
                            st.markdown(f"**Focus:** {q.get('focus', 'General assessment')}")
                        with col2:
                            st.markdown(f"**💡 Tip:** {q.get('tip', 'Use specific examples')}")
        
        with hard_tab:
            st.markdown("**Challenging questions that test your problem-solving:**")
            if 'hard_questions' in questions:
                for i, q in enumerate(questions['hard_questions'], 1):
                    with st.expander(f"Q{i}: {q.get('question', '')}", expanded=False):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown(f"**Category:** {q.get('category', 'General')}")
                            st.markdown(f"**Focus:** {q.get('focus', 'General assessment')}")
                        with col2:
                            st.markdown(f"**💡 Tip:** {q.get('tip', 'Think through your approach step by step')}")
        
        st.markdown("---")
    
    # Suggestions
    if 'suggestions' in results and results['suggestions']:
        st.markdown("### 💡 Improvement Suggestions")
        for suggestion in results['suggestions']:
            st.markdown(f"• **{suggestion.get('for', '')}**: {suggestion.get('suggestion', '')}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_history_content():
    """Display history content."""
    st.markdown("### 📚 Analysis History")
    
    try:
        # Get analysis history from database
        records = db.get_analysis_history(limit=10)
        
        if records:
            st.success(f"Found {len(records)} previous analyses")
            
            for record in records[:5]:  # Show last 5 records
                with st.expander(f"📄 {record.get('filename', 'Unknown')} - {record.get('created_at', 'Unknown date')}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**File Info:**")
                        st.write(f"• Filename: {record.get('filename', 'N/A')}")
                        st.write(f"• Date: {record.get('created_at', 'N/A')}")
                        st.write(f"• File Type: {record.get('file_type', 'N/A')}")
                        st.write(f"• Language: {record.get('language', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Analysis Summary:**")
                        analysis = record.get('analysis', {})
                        if analysis:
                            top_skills = analysis.get('top_skills', [])
                            if top_skills:
                                st.write("• Top Skills: " + ", ".join(top_skills[:3]))
                            
                            strengths = analysis.get('strengths', [])
                            if strengths:
                                st.write(f"• Strengths: {len(strengths)}")
                            
                            suggestions = analysis.get('suggestions', [])
                            if suggestions:
                                st.write(f"• Suggestions: {len(suggestions)}")
                            
                            if analysis.get('compatibility_score'):
                                st.write(f"• Compatibility: {analysis['compatibility_score']}%")
                        else:
                            st.write("• No analysis data available")
        else:
            st.info("No previous analyses found. Upload and analyze a resume to get started!")
            
    except Exception as e:
        st.error(f"Failed to load history: {str(e)}")


def display_api_key_warnings():
    """Display warnings for missing API keys."""
    warnings = []
    
    if not os.getenv('OPENAI_API_KEY'):
        warnings.append("⚠️ OpenAI API key not configured. AI analysis will not work.")
    
    if warnings:
        for warning in warnings:
            st.warning(warning)
        
        st.info("💡 Please check your `.env` file and add the required API keys.")


def main():
    """Main application entry point with modern UI design."""
    # Initialize session state
    init_session_state()
    
    # Add modern CSS
    add_modern_css()
    
    # Create hero dashboard
    create_hero_dashboard()
    
    # Check API keys and show warnings
    display_api_key_warnings()
    
    # Quick start guide
    display_quick_start_guide()
    
    # Main workflow - step-by-step process
    display_workflow_steps()


if __name__ == "__main__":
    main()