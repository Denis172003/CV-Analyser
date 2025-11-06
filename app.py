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
    
    /* Modern header */
    .modern-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(46, 134, 171, 0.3);
    }
    
    .modern-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .modern-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0;
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
    
    /* Responsive design */
    @media (max-width: 768px) {
        .modern-header h1 {
            font-size: 2rem;
        }
        
        .step-card {
            padding: 1.5rem;
        }
        
        .upload-area {
            padding: 2rem 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def create_modern_header():
    """Create a modern, attractive header."""
    st.markdown("""
    <div class="modern-header">
        <h1>🤖 AI Resume Analyzer</h1>
        <p>Transform your resume with AI-powered insights and personalized video pitches</p>
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
    
    # Step 6: View History
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


def display_history_step():
    """Display the history step."""
    st.markdown(f"""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">6</div>
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
    
    # Create modern header
    create_modern_header()
    
    # Check API keys and show warnings
    display_api_key_warnings()
    
    # Main workflow - step-by-step process
    display_workflow_steps()


if __name__ == "__main__":
    main()