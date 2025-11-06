"""
Main Streamlit application for AI Resume Analyzer.

This module provides the web interface for file uploads,
analysis display, and video generation.
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
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/ai-resume-analyzer',
        'Report a bug': 'https://github.com/your-repo/ai-resume-analyzer/issues',
        'About': "AI Resume Analyzer - Get instant insights and video pitches from your resume!"
    }
)

# Initialize session state
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'processing_stage' not in st.session_state:
    st.session_state.processing_stage = "ready"
if 'show_history' not in st.session_state:
    st.session_state.show_history = False
if 'selected_history_item' not in st.session_state:
    st.session_state.selected_history_item = None
if 'job_description_text' not in st.session_state:
    st.session_state.job_description_text = ""
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""
if 'job_title' not in st.session_state:
    st.session_state.job_title = ""
if 'job_analysis_results' not in st.session_state:
    st.session_state.job_analysis_results = None


def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """
    Validate uploaded file format and size.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
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
    """
    Save uploaded file to temporary location.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Path to saved temporary file
    """
    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save file with original name
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def check_api_keys() -> Dict[str, bool]:
    """Check if required API keys are configured."""
    return {
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'nutrient': bool(os.getenv('NUTRIENT_API_KEY'))
    }


def display_api_key_warnings():
    """Display warnings for missing API keys."""
    api_keys = check_api_keys()
    
    if not api_keys['openai']:
        st.error("⚠️ OpenAI API key not configured. AI analysis will not work. Please set OPENAI_API_KEY in your .env file.")
    
    if not api_keys['nutrient']:
        st.warning("⚠️ Nutrient API key not configured. OCR fallback will not be available for complex documents.")


def add_custom_css():
    """Add custom CSS for better responsive design."""
    st.markdown("""
    <style>
    /* Responsive design improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Better mobile experience */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.75rem;
            font-size: 0.9rem;
        }
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Error message styling */
    .stAlert > div {
        border-radius: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0.5rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    # Add custom CSS
    add_custom_css()
    
    st.title("🤖 AI-Powered Resume Analyzer")
    st.markdown("Upload your resume and get AI-powered analysis with personalized video pitch!")
    
    # Check API keys and show warnings
    display_api_key_warnings()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("📁 Upload & Settings")
        
        # File upload with validation
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx'],
            help="Upload PDF or DOCX resume files (max 10MB)",
            key="resume_uploader"
        )
        
        # Validate file if uploaded
        file_valid = False
        if uploaded_file is not None:
            is_valid, error_msg = validate_file_upload(uploaded_file)
            if is_valid:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                file_valid = True
            else:
                st.error(f"❌ {error_msg}")
        
        # Job description input interface
        st.header("💼 Job Description (Optional)")
        
        # Company and job title inputs
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input(
                "Company Name",
                value=st.session_state.company_name,
                placeholder="e.g., Google, Microsoft, Startup Inc.",
                help="Enter the company name for better context",
                key="company_name_input"
            )
            st.session_state.company_name = company_name
            
        with col2:
            job_title = st.text_input(
                "Job Title",
                value=st.session_state.job_title,
                placeholder="e.g., Software Engineer, Data Scientist",
                help="Enter the specific job title",
                key="job_title_input"
            )
            st.session_state.job_title = job_title
        
        # Job description text area with formatting options
        job_description = st.text_area(
            "Job Description",
            value=st.session_state.job_description_text,
            height=200,
            placeholder="Paste the complete job description here...\n\nInclude:\n• Job responsibilities\n• Required skills and qualifications\n• Company culture information\n• Benefits and perks",
            help="Adding a detailed job description provides better skill gap analysis and optimization suggestions",
            key="job_description_input"
        )
        st.session_state.job_description_text = job_description
        
        # Job description validation and preprocessing
        if job_description:
            # Character and word count
            char_count = len(job_description)
            word_count = len(job_description.split())
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"📊 {word_count} words, {char_count} characters")
            with col2:
                # Quality indicator
                if word_count < 50:
                    st.caption("⚠️ Consider adding more details")
                elif word_count > 500:
                    st.caption("✅ Comprehensive description")
                else:
                    st.caption("✅ Good length")
            
            # Save job description option
            if company_name and job_title:
                if st.button("💾 Save Job Description", help="Save this job description for future use"):
                    try:
                        import database
                        # Analyze job description
                        job_analysis = ai_integration.analyze_job_description(job_description)
                        
                        # Store job description
                        job_id = database.store_job_description(
                            job_text=job_description,
                            job_analysis=job_analysis,
                            metadata={
                                'company_name': company_name,
                                'job_title': job_title,
                                'source': 'manual_input'
                            }
                        )
                        
                        st.success(f"✅ Job description saved! ID: {job_id}")
                        
                    except Exception as e:
                        st.error(f"Failed to save job description: {str(e)}")
        
        # Load saved job descriptions
        with st.expander("📂 Load Saved Job Descriptions", expanded=False):
            try:
                import database
                saved_jobs = database.get_job_descriptions(limit=10)
                
                if saved_jobs:
                    st.success(f"Found {len(saved_jobs)} saved job descriptions")
                    for job in saved_jobs:
                        job_display = f"{job.get('company_name', 'Unknown')} - {job.get('job_title', 'Unknown Position')}"
                        if st.button(f"📋 {job_display}", key=f"load_job_{job['id']}"):
                            # Load job description into the text area
                            st.session_state.job_description_text = job['job_text']
                            st.session_state.company_name = job.get('company_name', '')
                            st.session_state.job_title = job.get('job_title', '')
                            st.success(f"Loaded job description: {job.get('job_title', 'Unknown')}")
                            st.rerun()
                else:
                    st.info("No saved job descriptions found")
                    
            except Exception as e:
                st.error(f"Error loading saved jobs: {str(e)}")
                logger.error(f"Failed to load saved job descriptions: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        # Action buttons
        st.header("🚀 Actions")
        
        # Extract text button
        extract_button = st.button(
            "📄 Extract Text", 
            disabled=not file_valid,
            help="Extract text from uploaded resume"
        )
        
        # Analyze button
        analyze_button = st.button(
            "📊 Analyze Resume", 
            type="primary",
            disabled=not file_valid or not st.session_state.extracted_text,
            help="Analyze resume with AI (requires text extraction first)"
        )
        
        # Generate video button
        generate_video_button = st.button(
            "🎥 Generate Pitch Video",
            disabled=not st.session_state.analysis_results,
            help="Generate personalized video pitch (requires analysis first)"
        )
        
        # Download section
        if st.session_state.analysis_results or st.session_state.video_path:
            st.header("💾 Downloads")
            
            # Download analysis results
            if st.session_state.analysis_results:
                analysis_text = format_analysis_for_download(st.session_state.analysis_results)
                st.download_button(
                    label="📄 Download Analysis",
                    data=analysis_text,
                    file_name="resume_analysis.txt",
                    mime="text/plain",
                    help="Download analysis results as text file"
                )
            
            # Download video
            if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                with open(st.session_state.video_path, 'rb') as video_file:
                    video_bytes = video_file.read()
                    st.download_button(
                        label="🎥 Download Video",
                        data=video_bytes,
                        file_name="pitch_video.mp4",
                        mime="video/mp4",
                        help="Download your personalized pitch video"
                    )
    
    # Main content area
    if uploaded_file is not None and file_valid:
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Extracted Text", "📊 Analysis Results", "🎥 Video Pitch", "📚 History"])
        
        with tab1:
            display_text_extraction_tab(uploaded_file, extract_button)
            
        with tab2:
            display_analysis_results_tab(analyze_button, job_description, uploaded_file)
            
        with tab3:
            display_video_generation_tab(generate_video_button)
            
        with tab4:
            display_history_tab()
    
    else:
        # Show history even without file upload
        tab1, tab2 = st.tabs(["🏠 Welcome", "📚 History"])
        
        with tab1:
            display_welcome_screen()
            
        with tab2:
            display_history_tab()


def display_welcome_screen():
    """Display welcome screen with feature information."""
    st.info("👆 Please upload a resume file to get started!")
    
    # Show sample information
    st.markdown("### 🌟 Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📄 Smart Text Extraction**
        - PDF and DOCX support
        - OCR fallback for scanned docs
        - Multi-language support (EN/RO)
        """)
        
    with col2:
        st.markdown("""
        **🤖 AI-Powered Analysis**
        - Strengths & weaknesses identification
        - Improvement suggestions
        - Skill gap analysis vs job descriptions
        """)
        
    with col3:
        st.markdown("""
        **🎥 Video Pitch Generation**
        - 10-second personalized pitch
        - Text-to-speech synthesis
        - Animated visual elements
        """)
    
    # Instructions
    st.markdown("### 📋 How to Use")
    st.markdown("""
    1. **Upload** your resume (PDF or DOCX format)
    2. **Extract** text from the document
    3. **Analyze** with AI to get insights and suggestions
    4. **Generate** a personalized video pitch
    5. **Download** results and video for your use
    
    💡 **Tip:** Add a job description for tailored analysis and skill gap insights!
    """)


def extract_text_from_file(file_path: str) -> tuple[str, str]:
    """
    Extract text from uploaded file with error handling.
    
    Args:
        file_path: Path to the uploaded file
        
    Returns:
        Tuple of (extracted_text, status_message)
    """
    try:
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            text = parsing.extract_text_pdf(file_path)
        elif file_extension == 'docx':
            text = parsing.extract_text_docx(file_path)
        else:
            return "", f"Unsupported file format: {file_extension}"
        
        if not text or len(text.strip()) < 50:
            return "", "Extracted text is too short or empty. The file might be corrupted or contain only images."
        
        # Check if OCR fallback is needed
        if hasattr(parsing, 'needs_nutrient_ocr') and parsing.needs_nutrient_ocr(text):
            try:
                # Try OCR fallback if available
                ocr_text = parsing.call_nutrient_ocr(file_path, os.getenv('NUTRIENT_API_KEY', ''))
                if ocr_text and len(ocr_text) > len(text):
                    return ocr_text, "Text extracted successfully using OCR fallback"
            except Exception as ocr_error:
                logger.warning(f"OCR fallback failed: {ocr_error}")
        
        return text, "Text extracted successfully"
        
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return "", f"Text extraction failed: {str(e)}"


def display_text_extraction_tab(uploaded_file, extract_button):
    """Display text extraction tab content with progress tracking."""
    st.header("📄 Extracted Text")
    
    if extract_button:
        # Show progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress with helpful messages
            progress_bar.progress(25)
            status_text.text("💾 Saving uploaded file...")
            
            # Save uploaded file
            file_path = save_uploaded_file(uploaded_file)
            
            # Update progress
            progress_bar.progress(50)
            status_text.text("📄 Extracting text from document... This may take a moment for large files.")
            
            # Extract text
            extracted_text, status_message = extract_text_from_file(file_path)
            
            # Update progress
            progress_bar.progress(75)
            status_text.text("🔍 Processing and validating extracted content...")
            
            if extracted_text:
                # Store in session state
                st.session_state.extracted_text = extracted_text
                
                # Update progress
                progress_bar.progress(100)
                status_text.text("✅ Text extraction completed successfully!")
                
                # Show success message with helpful info
                st.success(f"{status_message} 🎉")
                
                # Show text statistics with helpful context
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                st.info(f"📊 Extracted {word_count} words ({char_count} characters) - Ready for AI analysis!")
                
                # Helpful tip
                if word_count < 100:
                    st.warning("💡 Your resume seems quite short. Consider adding more details for better analysis.")
                elif word_count > 1000:
                    st.info("💡 Your resume is comprehensive! The AI will focus on the most relevant information.")
                
            else:
                progress_bar.progress(100)
                status_text.text("❌ Text extraction failed")
                st.error(f"{status_message}")
                
                # Provide helpful suggestions
                st.markdown("""
                **💡 Troubleshooting Tips:**
                - Ensure your file is not password-protected
                - Try converting to a different format (PDF ↔ DOCX)
                - Check if the file contains actual text (not just images)
                - For scanned documents, OCR processing may be needed
                """)
            
            # Clean up temporary file
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temp file: {cleanup_error}")
                
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Processing failed")
            st.error(f"An unexpected error occurred: {str(e)}")
            
            # Provide helpful error context
            st.markdown("""
            **🔧 What you can try:**
            - Refresh the page and try again
            - Check your internet connection
            - Try a different file format
            - Contact support if the problem persists
            """)
            
            logger.error(f"Text extraction process failed: {e}")
    
    # Display extracted text if available
    if st.session_state.extracted_text:
        with st.expander("📝 View Extracted Text", expanded=False):
            st.text_area(
                "Extracted content:",
                value=st.session_state.extracted_text,
                height=300,
                disabled=True,
                help="This is the text extracted from your resume. Review it to ensure accuracy."
            )
            
            # Add text quality indicators
            text = st.session_state.extracted_text
            word_count = len(text.split())
            line_count = len(text.split('\n'))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", word_count)
            with col2:
                st.metric("Lines", line_count)
            with col3:
                avg_words_per_line = round(word_count / max(line_count, 1), 1)
                st.metric("Avg Words/Line", avg_words_per_line)
                
    else:
        st.info("Click 'Extract Text' to process your resume and view the extracted content.")


def perform_resume_analysis(resume_text: str, job_description: str = "") -> tuple[Dict[str, Any], str]:
    """
    Perform AI analysis of resume text with enhanced job matching.
    
    Args:
        resume_text: Extracted resume text
        job_description: Optional job description for comparison
        
    Returns:
        Tuple of (analysis_results, status_message)
    """
    try:
        # Call AI analysis
        analysis_results = ai_integration.call_gpt_analysis(resume_text, job_description)
        
        if not analysis_results:
            return {}, "AI analysis returned empty results"
        
        # Validate required fields
        required_fields = ['strengths', 'weak_points', 'suggestions', 'top_skills', 'one_sentence_pitch']
        for field in required_fields:
            if field not in analysis_results:
                return {}, f"Analysis missing required field: {field}"
        
        # Enhanced job matching if job description provided
        if job_description.strip():
            try:
                # Analyze job description
                job_analysis = ai_integration.analyze_job_description(job_description)
                st.session_state.job_analysis_results = job_analysis
                
                # Generate CV optimization advice
                optimization_advice = ai_integration.generate_cv_optimization_advice(
                    analysis_results, job_analysis
                )
                analysis_results['optimization_advice'] = optimization_advice
                
                # Enhanced skill matching
                resume_skills = analysis_results.get('top_skills', [])
                job_skills = job_analysis.get('required_skills', [])
                
                skill_analysis = ai_integration.score_resume_vs_job(resume_skills, job_skills)
                
                # Update analysis results with enhanced matching
                analysis_results.update(skill_analysis)
                
                logger.info("Enhanced job matching analysis completed")
                
            except Exception as job_error:
                logger.warning(f"Job matching analysis failed: {job_error}")
                # Continue with basic analysis if job matching fails
        
        return analysis_results, "Analysis completed successfully"
        
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        return {}, f"Analysis failed: {str(e)}"


def display_analysis_results(analysis_results: Dict[str, Any], job_description: str = ""):
    """
    Display formatted analysis results.
    
    Args:
        analysis_results: Dictionary containing analysis data
        job_description: Optional job description for context
    """
    # Display one-sentence pitch prominently
    if 'one_sentence_pitch' in analysis_results:
        st.markdown("### 🎯 Your Elevator Pitch")
        st.info(f"💬 {analysis_results['one_sentence_pitch']}")
    
    # Create columns for strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Strengths")
        if 'strengths' in analysis_results and analysis_results['strengths']:
            for i, strength in enumerate(analysis_results['strengths'], 1):
                if isinstance(strength, dict):
                    st.markdown(f"**{i}.** {strength.get('text', strength)}")
                    if 'evidence' in strength:
                        st.caption(f"Evidence: {strength['evidence']}")
                else:
                    st.markdown(f"**{i}.** {strength}")
        else:
            st.info("No strengths identified")
    
    with col2:
        st.markdown("### ⚠️ Areas for Improvement")
        if 'weak_points' in analysis_results and analysis_results['weak_points']:
            for i, weakness in enumerate(analysis_results['weak_points'], 1):
                if isinstance(weakness, dict):
                    st.markdown(f"**{i}.** {weakness.get('text', weakness)}")
                    if 'reason' in weakness:
                        st.caption(f"Reason: {weakness['reason']}")
                else:
                    st.markdown(f"**{i}.** {weakness}")
        else:
            st.info("No major weaknesses identified")
    
    # Display suggestions
    st.markdown("### 💡 Improvement Suggestions")
    if 'suggestions' in analysis_results and analysis_results['suggestions']:
        for i, suggestion in enumerate(analysis_results['suggestions'], 1):
            if isinstance(suggestion, dict):
                st.markdown(f"**{i}.** {suggestion.get('suggestion', suggestion)}")
                if 'for' in suggestion:
                    st.caption(f"For: {suggestion['for']}")
            else:
                st.markdown(f"**{i}.** {suggestion}")
    else:
        st.info("No specific suggestions available")
    
    # Display top skills
    st.markdown("### 🛠️ Top Skills Identified")
    if 'top_skills' in analysis_results and analysis_results['top_skills']:
        # Display skills as tags
        skills_html = ""
        for skill in analysis_results['top_skills']:
            skills_html += f'<span style="background-color: #e1f5fe; color: #000000; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px;">{skill}</span> '
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.info("No skills identified")
    
    # Display job comparison if job description was provided
    if job_description and 'compatibility_score' in analysis_results:
        st.markdown("### 🎯 Job Match Analysis")
        
        # Compatibility score with enhanced visualization
        score = analysis_results.get('compatibility_score', 0)
        
        # Create score visualization with color coding
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.metric("Compatibility Score", f"{score}%", help="How well your resume matches the job requirements")
            
            # Color-coded progress bar
            if score >= 80:
                st.success("🎉 Excellent match!")
                progress_color = "success"
            elif score >= 60:
                st.info("👍 Good match with room for improvement")
                progress_color = "info"
            elif score >= 40:
                st.warning("⚠️ Moderate match - consider optimization")
                progress_color = "warning"
            else:
                st.error("❌ Low match - significant improvements needed")
                progress_color = "error"
            
            st.progress(score / 100)
        
        with col2:
            matching_count = len(analysis_results.get('matching_skills', []))
            st.metric("Matching Skills", matching_count, help="Number of skills that match job requirements")
        
        with col3:
            missing_count = len(analysis_results.get('missing_skills', []))
            st.metric("Missing Skills", missing_count, help="Number of critical skills you should develop")
        
        # Enhanced skills comparison with priority indicators
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Matching Skills")
            matching_skills = analysis_results.get('matching_skills', [])
            if matching_skills:
                for i, skill in enumerate(matching_skills, 1):
                    # Add priority indicator based on position
                    if i <= 3:
                        st.markdown(f"🔥 **{skill}** (High Priority)")
                    elif i <= 6:
                        st.markdown(f"⭐ **{skill}** (Medium Priority)")
                    else:
                        st.markdown(f"✅ {skill}")
            else:
                st.info("No matching skills identified")
        
        with col2:
            st.markdown("#### ❌ Missing Skills")
            missing_skills = analysis_results.get('missing_skills', [])
            if missing_skills:
                for i, skill in enumerate(missing_skills, 1):
                    # Add priority indicator for missing skills
                    if i <= 3:
                        st.markdown(f"🚨 **{skill}** (Critical)")
                    elif i <= 6:
                        st.markdown(f"⚠️ **{skill}** (Important)")
                    else:
                        st.markdown(f"💡 {skill} (Nice to have)")
            else:
                st.success("No critical skills missing!")
        
        # CV Optimization advice display
        if 'optimization_advice' in analysis_results:
            st.markdown("### 💡 CV Optimization Recommendations")
            
            optimization = analysis_results['optimization_advice']
            
            # Actionable items with checkboxes
            if 'actionable_items' in optimization:
                st.markdown("#### 📋 Action Items")
                for i, item in enumerate(optimization['actionable_items'], 1):
                    st.markdown(f"**{i}.** {item}")
            
            # Keyword optimization
            if 'keyword_optimization' in optimization:
                st.markdown("#### 🔍 Keyword Optimization")
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
                
                # Department keywords
                if 'department_keywords' in keyword_data:
                    st.markdown("**Department-specific keywords:**")
                    st.write(keyword_data['department_keywords'])
                
                # ATS optimization tips
                if 'ats_optimization_tips' in keyword_data:
                    st.markdown("**ATS Optimization Tips:**")
                    for tip in keyword_data['ats_optimization_tips']:
                        st.write(f"• {tip}")
            
            # Section-specific improvements
            if 'section_improvements' in optimization:
                st.markdown("#### 📝 Section-Specific Improvements")
                improvements = optimization['section_improvements']
                
                for section, advice in improvements.items():
                    with st.expander(f"📄 {section.title()} Section", expanded=False):
                        st.markdown(advice)


def display_analysis_results_tab(analyze_button, job_description, uploaded_file=None):
    """Display analysis results tab content with progress tracking."""
    st.header("📊 Analysis Results")
    
    if analyze_button and st.session_state.extracted_text:
        # Show progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress with helpful messages
            progress_bar.progress(25)
            status_text.text("🤖 Initializing AI analysis... Connecting to OpenAI...")
            
            # Prepare job description context
            job_context = job_description.strip() if job_description else ""
            if job_context:
                progress_bar.progress(40)
                status_text.text("🔍 Analyzing resume against job requirements... This provides better insights!")
            else:
                progress_bar.progress(40)
                status_text.text("🔍 Analyzing resume content... Consider adding a job description for comparison!")
            
            # Update progress
            progress_bar.progress(60)
            status_text.text("🧠 AI is processing your resume... Identifying strengths and areas for improvement...")
            
            # Perform analysis
            analysis_results, status_message = perform_resume_analysis(
                st.session_state.extracted_text, 
                job_context
            )
            
            # Update progress
            progress_bar.progress(80)
            status_text.text("📊 Formatting analysis results and generating insights...")
            
            if analysis_results:
                # Store in session state
                st.session_state.analysis_results = analysis_results
                
                # Save to database
                try:
                    metadata = {
                        'filename': uploaded_file.name if uploaded_file else 'analysis.txt',
                        'file_type': uploaded_file.name.split('.')[-1] if uploaded_file else 'txt',
                        'file_size': len(st.session_state.extracted_text),
                        'language': 'en'  # Could be enhanced with language detection
                    }
                    
                    cv_id = db.store_cv_analysis(
                        st.session_state.extracted_text,
                        analysis_results,
                        metadata
                    )
                    logger.info(f"Analysis saved to database with ID: {cv_id}")
                except Exception as db_error:
                    logger.warning(f"Failed to save analysis to database: {db_error}")
                
                # Update progress
                progress_bar.progress(100)
                status_text.text("✅ Analysis completed successfully!")
                
                # Show success message with context
                if job_context:
                    st.success(f"{status_message} 🎯 Job comparison included!")
                else:
                    st.success(f"{status_message} 💡 Add a job description for even better insights!")
                
                # Show helpful stats
                strengths_count = len(analysis_results.get('strengths', []))
                suggestions_count = len(analysis_results.get('suggestions', []))
                st.info(f"📈 Found {strengths_count} strengths and {suggestions_count} improvement suggestions")
                
            else:
                progress_bar.progress(100)
                status_text.text("❌ Analysis failed")
                st.error(f"{status_message}")
                
                # Provide helpful suggestions
                st.markdown("""
                **💡 Troubleshooting Tips:**
                - Check your OpenAI API key configuration
                - Ensure you have sufficient API credits
                - Try again in a few moments (temporary API issues)
                - The extracted text might be too short or unclear
                """)
                
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Analysis failed")
            st.error(f"An unexpected error occurred during analysis: {str(e)}")
            
            # Provide helpful error context
            st.markdown("""
            **🔧 What you can try:**
            - Check your OpenAI API key in the .env file
            - Verify your internet connection
            - Try again in a few minutes
            - Contact support if the problem persists
            """)
            
            logger.error(f"Analysis process failed: {e}")
    
    # Display analysis results if available
    if st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results, job_description)
    else:
        if not st.session_state.extracted_text:
            st.info("Please extract text from your resume first.")
        else:
            st.info("Click 'Analyze Resume' to get AI-powered insights and suggestions.")


def format_analysis_for_download(analysis_results: Dict[str, Any]) -> str:
    """
    Format analysis results for download as text file.
    
    Args:
        analysis_results: Dictionary containing analysis data
        
    Returns:
        Formatted text string
    """
    from datetime import datetime
    
    output = []
    output.append("AI RESUME ANALYSIS REPORT")
    output.append("=" * 50)
    output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Elevator pitch
    if 'one_sentence_pitch' in analysis_results:
        output.append("ELEVATOR PITCH")
        output.append("-" * 20)
        output.append(analysis_results['one_sentence_pitch'])
        output.append("")
    
    # Strengths
    if 'strengths' in analysis_results and analysis_results['strengths']:
        output.append("STRENGTHS")
        output.append("-" * 20)
        for i, strength in enumerate(analysis_results['strengths'], 1):
            if isinstance(strength, dict):
                output.append(f"{i}. {strength.get('text', strength)}")
                if 'evidence' in strength:
                    output.append(f"   Evidence: {strength['evidence']}")
            else:
                output.append(f"{i}. {strength}")
        output.append("")
    
    # Areas for improvement
    if 'weak_points' in analysis_results and analysis_results['weak_points']:
        output.append("AREAS FOR IMPROVEMENT")
        output.append("-" * 30)
        for i, weakness in enumerate(analysis_results['weak_points'], 1):
            if isinstance(weakness, dict):
                output.append(f"{i}. {weakness.get('text', weakness)}")
                if 'reason' in weakness:
                    output.append(f"   Reason: {weakness['reason']}")
            else:
                output.append(f"{i}. {weakness}")
        output.append("")
    
    # Suggestions
    if 'suggestions' in analysis_results and analysis_results['suggestions']:
        output.append("IMPROVEMENT SUGGESTIONS")
        output.append("-" * 30)
        for i, suggestion in enumerate(analysis_results['suggestions'], 1):
            if isinstance(suggestion, dict):
                output.append(f"{i}. {suggestion.get('suggestion', suggestion)}")
                if 'for' in suggestion:
                    output.append(f"   For: {suggestion['for']}")
            else:
                output.append(f"{i}. {suggestion}")
        output.append("")
    
    # Top skills
    if 'top_skills' in analysis_results and analysis_results['top_skills']:
        output.append("TOP SKILLS IDENTIFIED")
        output.append("-" * 25)
        for skill in analysis_results['top_skills']:
            output.append(f"• {skill}")
        output.append("")
    
    # Job match analysis (if available)
    if 'compatibility_score' in analysis_results:
        output.append("JOB MATCH ANALYSIS")
        output.append("-" * 25)
        output.append(f"Compatibility Score: {analysis_results.get('compatibility_score', 0)}%")
        output.append("")
        
        if 'matching_skills' in analysis_results and analysis_results['matching_skills']:
            output.append("Matching Skills:")
            for skill in analysis_results['matching_skills']:
                output.append(f"• {skill}")
            output.append("")
        
        if 'missing_skills' in analysis_results and analysis_results['missing_skills']:
            output.append("Missing Skills:")
            for skill in analysis_results['missing_skills']:
                output.append(f"• {skill}")
            output.append("")
    
    output.append("=" * 50)
    output.append("Generated by AI Resume Analyzer")
    
    return "\n".join(output)


def generate_pitch_video(analysis_results: Dict[str, Any], video_type: str = "General Pitch", 
                        industry_style: str = "Professional", job_analysis: Dict = None) -> tuple[str, str]:
    """
    Generate personalized video pitch from analysis results with job-specific options.
    
    Args:
        analysis_results: Dictionary containing analysis data
        video_type: Type of video to generate
        industry_style: Industry-specific styling
        job_analysis: Optional job analysis for job-specific videos
        
    Returns:
        Tuple of (video_path, status_message)
    """
    try:
        # Generate script based on video type
        if video_type == "Job-Specific Pitch" and job_analysis:
            # Try using Gemini for advanced job-specific video
            try:
                import gemini_video
                
                # Create job-specific video with Gemini
                video_path = gemini_video.create_job_specific_video(
                    analysis_results, job_analysis, industry_style
                )
                
                if video_path and os.path.exists(video_path):
                    return video_path, "Job-specific video generated successfully with Gemini"
                    
            except Exception as gemini_error:
                logger.warning(f"Gemini video generation failed, falling back to basic: {gemini_error}")
        
        elif video_type == "Interview Preparation" and job_analysis:
            # Try using Gemini for interview preparation video
            try:
                import gemini_video
                
                video_path = gemini_video.create_interview_prep_video(
                    analysis_results, job_analysis, industry_style
                )
                
                if video_path and os.path.exists(video_path):
                    return video_path, "Interview preparation video generated successfully with Gemini"
                    
            except Exception as gemini_error:
                logger.warning(f"Gemini interview video generation failed, falling back to basic: {gemini_error}")
        
        # Fallback to basic video generation
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
            language="en",  # TODO: detect language from analysis
            target_duration=10.0
        )
        
        if os.path.exists(video_path):
            return video_path, f"{video_type} generated successfully"
        else:
            return "", "Video file was not created"
            
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        return "", f"Video generation failed: {str(e)}"


def display_video_generation_tab(generate_video_button):
    """Display video generation tab content with progress tracking."""
    st.header("🎥 Video Generation")
    
    # Video generation options
    col1, col2 = st.columns(2)
    
    with col1:
        video_type = st.radio(
            "Video Type",
            options=["General Pitch", "Job-Specific Pitch", "Interview Preparation"],
            help="Choose the type of video to generate",
            disabled=not st.session_state.analysis_results,
            key="video_type_selection"
        )
    
    with col2:
        # Industry style selection for job-specific videos
        if video_type in ["Job-Specific Pitch", "Interview Preparation"] and st.session_state.job_analysis_results:
            industry_style = st.selectbox(
                "Industry Style",
                options=["Professional", "Creative", "Technical", "Corporate", "Startup", "Academic"],
                help="Select video style based on job industry",
                disabled=not st.session_state.analysis_results,
                key="industry_style_selection"
            )
        else:
            industry_style = "Professional"
    
    # Job-specific interview tips display
    if video_type == "Interview Preparation" and st.session_state.job_analysis_results:
        with st.expander("💡 Interview Tips Preview", expanded=False):
            job_analysis = st.session_state.job_analysis_results
            
            if 'interview_focus_areas' in job_analysis:
                st.markdown("**🎯 Focus Areas for Interview:**")
                for area in job_analysis['interview_focus_areas']:
                    st.markdown(f"• {area}")
            
            if 'key_talking_points' in job_analysis:
                st.markdown("**💬 Key Talking Points:**")
                for point in job_analysis['key_talking_points']:
                    st.markdown(f"• {point}")
            
            if 'company_culture_fit' in job_analysis:
                st.markdown("**🏢 Company Culture Alignment:**")
                st.markdown(job_analysis['company_culture_fit'])
    
    # Generate video button with dynamic text
    generate_video_button_local = st.button(
        f"🎥 Generate {video_type}",
        disabled=not st.session_state.analysis_results,
        help="Generate personalized video pitch (requires analysis first)",
        key="generate_video_local"
    )
    
    if (generate_video_button or generate_video_button_local) and st.session_state.analysis_results:
        # Show progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress with detailed messages
            progress_bar.progress(20)
            status_text.text("📝 Generating personalized pitch script... Crafting your story...")
            
            # Update progress
            progress_bar.progress(40)
            status_text.text("🎤 Synthesizing professional audio... This may take 30-60 seconds...")
            
            # Update progress
            progress_bar.progress(60)
            status_text.text("🎬 Creating animated video elements... Adding visual appeal...")
            
            # Generate video with job-specific options
            job_analysis = st.session_state.job_analysis_results if hasattr(st.session_state, 'job_analysis_results') else None
            video_path, status_message = generate_pitch_video(
                st.session_state.analysis_results, 
                video_type, 
                industry_style,
                job_analysis
            )
            
            # Update progress
            progress_bar.progress(80)
            status_text.text("🔧 Finalizing video composition and encoding...")
            
            if video_path and os.path.exists(video_path):
                # Store in session state
                st.session_state.video_path = video_path
                
                # Update progress
                progress_bar.progress(100)
                status_text.text("✅ Your personalized video pitch is ready!")
                
                # Show success message with excitement
                st.success(f"{status_message} 🎉 Your 10-second pitch is ready to impress!")
                
                # Show helpful info
                file_size = os.path.getsize(video_path)
                file_size_mb = round(file_size / (1024 * 1024), 2)
                st.info(f"🎬 Video created: {file_size_mb} MB | Perfect for sharing on social media or with recruiters!")
                
            else:
                progress_bar.progress(100)
                status_text.text("❌ Video generation failed")
                st.error(f"{status_message}")
                
                # Provide helpful suggestions
                st.markdown("""
                **💡 Troubleshooting Tips:**
                - Ensure you have sufficient disk space
                - Check if required video libraries are installed
                - Try generating the video again
                - The analysis data might be incomplete
                """)
                
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Video generation failed")
            st.error(f"An unexpected error occurred during video generation: {str(e)}")
            
            # Provide helpful error context
            st.markdown("""
            **🔧 What you can try:**
            - Ensure all dependencies are installed (moviepy, edge-tts)
            - Check available disk space
            - Try restarting the application
            - Contact support if the problem persists
            """)
            
            logger.error(f"Video generation process failed: {e}")
    
    # Display video if available
    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
        st.markdown("### 🎬 Your Personalized Pitch Video")
        
        try:
            # Display video using Streamlit's native video player
            with open(st.session_state.video_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
            
            # Show video information
            file_size = os.path.getsize(st.session_state.video_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            st.info(f"📊 Video size: {file_size_mb} MB | Duration: ~10 seconds")
            
            # Video description
            st.markdown("""
            **🎯 About Your Video:**
            - Personalized 10-second elevator pitch
            - AI-generated script based on your resume analysis
            - Professional text-to-speech narration
            - Animated visual elements for engagement
            """)
            
        except Exception as e:
            st.error(f"Error displaying video: {str(e)}")
            logger.error(f"Video display failed: {e}")
    
    else:
        if not st.session_state.analysis_results:
            st.info("Please complete resume analysis first.")
        else:
            st.info("Click 'Generate Pitch Video' to create your personalized 10-second video pitch.")
            
            # Show preview of what will be included
            if st.session_state.analysis_results:
                st.markdown("### 🎬 Video Preview")
                st.markdown("Your video will include:")
                
                # Show pitch content
                pitch = st.session_state.analysis_results.get('one_sentence_pitch', '')
                if pitch:
                    st.markdown(f"**Pitch:** {pitch}")
                
                # Show top skills
                skills = st.session_state.analysis_results.get('top_skills', [])
                if skills:
                    st.markdown(f"**Key Skills:** {', '.join(skills[:3])}")
                
                st.markdown("**Duration:** ~10 seconds with professional narration and animations")


def display_history_tab():
    """Display analysis history panel with job matching tracking and search functionality."""
    st.header("📚 Analysis & Job Matching History")
    
    # History type selection
    history_type = st.radio(
        "History Type",
        options=["All Analyses", "Job Matches", "CV Improvements"],
        horizontal=True,
        help="Filter history by type"
    )
    
    try:
        # Initialize database
        database = db.init_database()
        
        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input(
                "🔍 Search history",
                placeholder="Search by filename or content...",
                help="Search through your previous analyses"
            )
        
        with col2:
            language_filter = st.selectbox(
                "Language",
                options=["All", "en", "ro"],
                help="Filter by resume language"
            )
        
        with col3:
            limit = st.selectbox(
                "Show",
                options=[10, 25, 50, 100],
                index=1,
                help="Number of records to display"
            )
        
        # Get history data
        if search_query:
            # Build filters
            filters = {}
            if language_filter != "All":
                filters['language'] = language_filter
            
            history_data = db.search_analysis_history(search_query, filters)
        else:
            history_data = db.get_analysis_history(limit)
        
        # Display statistics
        if history_data:
            total_analyses = len(history_data)
            st.info(f"📊 Found {total_analyses} analysis record{'s' if total_analyses != 1 else ''}")
            
            # Display history based on selected type
            if history_type == "Job Matches":
                display_job_matching_history(history_data)
            elif history_type == "CV Improvements":
                display_cv_improvement_tracking(history_data)
            else:
                display_all_analyses_history(history_data)
        
        else:
            if search_query:
                st.info(f"No results found for '{search_query}'. Try different search terms.")
            else:
                st.info("No analysis history found. Upload and analyze a resume to get started!")
        
        # Database statistics
        with st.expander("📊 Database Statistics", expanded=False):
            stats = db.get_database_stats()
            if stats:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total CVs", stats.get('cv_records', 0))
                    st.metric("Total Analyses", stats.get('analysis_results', 0))
                
                with col2:
                    st.metric("Videos Generated", stats.get('video_records', 0))
                    db_size_mb = round(stats.get('database_size_bytes', 0) / (1024 * 1024), 2)
                    st.metric("Database Size", f"{db_size_mb} MB")
                
                with col3:
                    if stats.get('oldest_record'):
                        st.metric("Oldest Record", stats['oldest_record'][:10])
                    if stats.get('newest_record'):
                        st.metric("Newest Record", stats['newest_record'][:10])
                
                # Cleanup option
                st.markdown("**🧹 Maintenance**")
                if st.button("🗑️ Clean Old Records (30+ days)"):
                    deleted_count = db.cleanup_old_records(30)
                    if deleted_count > 0:
                        st.success(f"Cleaned up {deleted_count} old records")
                    else:
                        st.info("No old records to clean up")
    
    except Exception as e:
        st.error(f"Failed to load history: {str(e)}")
        st.markdown("""
        **💡 Troubleshooting:**
        - The database might not be initialized yet
        - Try analyzing a resume first to create the database
        - Check file permissions in the application directory
        """)
        logger.error(f"History display failed: {e}")


def load_historical_analysis(record: Dict):
    """
    Load a historical analysis into the current session.
    
    Args:
        record: Historical record dictionary
    """
    try:
        # Load extracted text
        st.session_state.extracted_text = record['original_text']
        
        # Load analysis results if available
        if 'analysis' in record and record['analysis']:
            st.session_state.analysis_results = record['analysis']
        
        st.success(f"✅ Loaded analysis for {record['filename']}")
        st.info("💡 Switch to other tabs to view the loaded data")
        
    except Exception as e:
        st.error(f"Failed to load historical analysis: {str(e)}")
        logger.error(f"Failed to load historical analysis: {e}")


def display_historical_analysis_details(analysis: Dict):
    """
    Display detailed view of historical analysis results.
    
    Args:
        analysis: Analysis results dictionary
    """
    st.markdown("### 📊 Detailed Analysis Results")
    
    # One-sentence pitch
    if analysis.get('one_sentence_pitch'):
        st.markdown("#### 🎯 Elevator Pitch")
        st.info(analysis['one_sentence_pitch'])
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Strengths")
        strengths = analysis.get('strengths', [])
        if strengths:
            for i, strength in enumerate(strengths, 1):
                if isinstance(strength, dict):
                    st.markdown(f"**{i}.** {strength.get('text', strength)}")
                    if 'evidence' in strength:
                        st.caption(f"Evidence: {strength['evidence']}")
                else:
                    st.markdown(f"**{i}.** {strength}")
        else:
            st.info("No strengths recorded")
    
    with col2:
        st.markdown("#### ⚠️ Areas for Improvement")
        weak_points = analysis.get('weak_points', [])
        if weak_points:
            for i, weakness in enumerate(weak_points, 1):
                if isinstance(weakness, dict):
                    st.markdown(f"**{i}.** {weakness.get('text', weakness)}")
                    if 'reason' in weakness:
                        st.caption(f"Reason: {weakness['reason']}")
                else:
                    st.markdown(f"**{i}.** {weakness}")
        else:
            st.info("No major weaknesses identified")
    
    # Suggestions
    st.markdown("#### 💡 Improvement Suggestions")
    suggestions = analysis.get('suggestions', [])
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            if isinstance(suggestion, dict):
                st.markdown(f"**{i}.** {suggestion.get('suggestion', suggestion)}")
                if 'for' in suggestion:
                    st.caption(f"For: {suggestion['for']}")
            else:
                st.markdown(f"**{i}.** {suggestion}")
    else:
        st.info("No specific suggestions available")
    
    # Skills
    st.markdown("#### 🛠️ Top Skills")
    top_skills = analysis.get('top_skills', [])
    if top_skills:
        skills_html = ""
        for skill in top_skills:
            skills_html += f'<span style="background-color: #e1f5fe; color: #000000; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px;">{skill}</span> '
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.info("No skills identified")
    
    # Job matching results if available
    if analysis.get('compatibility_score'):
        st.markdown("#### 🎯 Job Match Results")
        
        score = analysis.get('compatibility_score', 0)
        st.metric("Compatibility Score", f"{score}%")
        st.progress(score / 100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Matching Skills**")
            matching_skills = analysis.get('matching_skills', [])
            if matching_skills:
                for skill in matching_skills:
                    st.markdown(f"• {skill}")
            else:
                st.info("No matching skills recorded")
        
        with col2:
            st.markdown("**❌ Missing Skills**")
            missing_skills = analysis.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f"• {skill}")
            else:
                st.success("No critical skills missing!")


def delete_historical_record(record_id: int) -> bool:
    """
    Delete a historical record from the database.
    
    Args:
        record_id: ID of the record to delete
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        return db.delete_cv_record(record_id)
    except Exception as e:
        logger.error(f"Failed to delete record {record_id}: {e}")
        return False


def save_current_analysis():
    """Save current analysis to database if both text and results are available."""
    if st.session_state.extracted_text and st.session_state.analysis_results:
        try:
            # Prepare metadata
            metadata = {
                'filename': 'current_analysis.txt',  # Default filename
                'file_type': 'txt',
                'file_size': len(st.session_state.extracted_text),
                'language': 'en'  # Default language
            }
            
            # Store in database
            cv_id = db.store_cv_analysis(
                st.session_state.extracted_text,
                st.session_state.analysis_results,
                metadata
            )
            
            # Store video record if available
            if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                script_data = ai_integration.generate_pitch_script(st.session_state.analysis_results)
                db.store_video_record(cv_id, script_data, st.session_state.video_path)
            
            logger.info(f"Saved current analysis to database with ID: {cv_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save current analysis: {e}")
            return False
    
    return False


def display_footer():
    """Display application footer with helpful information."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🚀 Quick Start**
        1. Upload resume
        2. Extract text
        3. Analyze with AI
        4. Generate video
        """)
    
    with col2:
        st.markdown("""
        **💡 Tips**
        - Use high-quality PDF/DOCX files
        - Add job descriptions for better insights
        - Review extracted text for accuracy
        - Share your video pitch professionally
        """)
    
    with col3:
        st.markdown("""
        **🔧 Support**
        - Check API key configuration
        - Ensure stable internet connection
        - Contact support for technical issues
        - Star us on GitHub if you like the tool!
        """)
    
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>Made with ❤️ using Streamlit, OpenAI, and Python | 
        <a href='https://github.com/your-repo/ai-resume-analyzer' target='_blank'>View on GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


def display_all_analyses_history(history_data):
    """Display all analyses history with enhanced job matching information."""
    for i, record in enumerate(history_data):
        # Enhanced title with job matching indicator
        title = f"📄 {record['filename']} - {record['created_at'][:19]}"
        if 'analysis' in record and record['analysis'] and record['analysis'].get('compatibility_score'):
            title += f" (Job Match: {record['analysis']['compatibility_score']}%)"
        
        with st.expander(title, expanded=False):
            # Record metadata
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("File Type", record['file_type'].upper())
            
            with col2:
                file_size_mb = round(record['file_size'] / (1024 * 1024), 2) if record['file_size'] else 0
                st.metric("Size", f"{file_size_mb} MB")
            
            with col3:
                st.metric("Language", record['language'].upper())
            
            with col4:
                # Load this analysis button
                if st.button(f"📂 Load Analysis", key=f"load_{record['id']}"):
                    load_historical_analysis(record)
            
            # Show analysis results if available
            if 'analysis' in record and record['analysis']:
                analysis = record['analysis']
                
                # One-sentence pitch
                if analysis.get('one_sentence_pitch'):
                    st.markdown("**🎯 Pitch:**")
                    st.info(analysis['one_sentence_pitch'])
                
                # Skills and scores with job matching
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if analysis.get('top_skills'):
                        st.markdown("**🛠️ Top Skills:**")
                        skills_text = ", ".join(analysis['top_skills'][:5])
                        st.write(skills_text)
                
                with col2:
                    if analysis.get('compatibility_score'):
                        score = analysis['compatibility_score']
                        st.markdown("**🎯 Job Match:**")
                        st.write(f"{score}%")
                        if score >= 80:
                            st.success("Excellent match!")
                        elif score >= 60:
                            st.info("Good match")
                        else:
                            st.warning("Needs improvement")
                
                with col3:
                    if analysis.get('missing_skills'):
                        missing_count = len(analysis['missing_skills'])
                        st.markdown("**❌ Missing Skills:**")
                        st.write(f"{missing_count} skills")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"👁️ View Details", key=f"view_{record['id']}"):
                        display_historical_analysis_details(analysis)
                
                with col2:
                    # Download analysis
                    analysis_text = format_analysis_for_download(analysis)
                    st.download_button(
                        label="💾 Download",
                        data=analysis_text,
                        file_name=f"analysis_{record['filename']}.txt",
                        mime="text/plain",
                        key=f"download_{record['id']}"
                    )
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{record['id']}"):
                        if delete_historical_record(record['id']):
                            st.success("Record deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete record")
            
            else:
                st.info("No analysis data available for this record")


def display_job_matching_history(history_data):
    """Display job matching history with compatibility tracking."""
    st.markdown("### 🎯 Job Matching Performance")
    
    # Filter records with job matching data
    job_matches = [record for record in history_data 
                   if 'analysis' in record and record['analysis'] 
                   and record['analysis'].get('compatibility_score')]
    
    if not job_matches:
        st.info("No job matching history found. Analyze resumes with job descriptions to see matching data.")
        return
    
    # Job matching statistics
    scores = [record['analysis']['compatibility_score'] for record in job_matches]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average Match", f"{avg_score:.1f}%")
    with col2:
        st.metric("Best Match", f"{max_score}%")
    with col3:
        st.metric("Lowest Match", f"{min_score}%")
    with col4:
        st.metric("Total Matches", len(job_matches))
    
    # Job matching timeline
    st.markdown("### 📈 Matching Score Timeline")
    
    # Create simple timeline visualization
    for i, record in enumerate(job_matches):
        analysis = record['analysis']
        score = analysis['compatibility_score']
        date = record['created_at'][:10]
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.write(f"**{date}** - {record['filename']}")
        
        with col2:
            st.metric("Score", f"{score}%")
        
        with col3:
            # Progress bar for score
            st.progress(score / 100)
            
            # Show improvement suggestions count
            if analysis.get('optimization_advice'):
                advice_count = len(analysis['optimization_advice'].get('actionable_items', []))
                st.caption(f"{advice_count} improvement suggestions")


def display_cv_improvement_tracking(history_data):
    """Display CV improvement tracking over time."""
    st.markdown("### 📊 CV Improvement Progress")
    
    # Filter records with analysis data
    analyses = [record for record in history_data 
                if 'analysis' in record and record['analysis']]
    
    if len(analyses) < 2:
        st.info("Need at least 2 analyses to track improvement. Keep analyzing your CV to see progress!")
        return
    
    # Sort by date
    analyses.sort(key=lambda x: x['created_at'])
    
    # Track improvements over time
    st.markdown("### 📈 Progress Over Time")
    
    # Skills development tracking
    all_skills = set()
    for record in analyses:
        skills = record['analysis'].get('top_skills', [])
        all_skills.update(skills)
    
    st.markdown("#### 🛠️ Skills Development")
    st.write(f"Total unique skills identified: **{len(all_skills)}**")
    
    # Show skills progression
    for i, record in enumerate(analyses):
        skills = record['analysis'].get('top_skills', [])
        date = record['created_at'][:10]
        
        with st.expander(f"📅 {date} - {len(skills)} skills", expanded=False):
            skills_html = ""
            for skill in skills:
                skills_html += f'<span style="background-color: #e1f5fe; color: #000000; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px;">{skill}</span> '
            st.markdown(skills_html, unsafe_allow_html=True)
    
    # Job matching improvement
    job_scores = [(record['created_at'][:10], record['analysis']['compatibility_score']) 
                  for record in analyses 
                  if record['analysis'].get('compatibility_score')]
    
    if len(job_scores) >= 2:
        st.markdown("#### 🎯 Job Matching Improvement")
        
        first_score = job_scores[0][1]
        latest_score = job_scores[-1][1]
        improvement = latest_score - first_score
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("First Score", f"{first_score}%")
        
        with col2:
            st.metric("Latest Score", f"{latest_score}%")
        
        with col3:
            st.metric("Improvement", f"{improvement:+.1f}%", 
                     delta=f"{improvement:+.1f}%" if improvement != 0 else None)
        
        # Show score progression
        for date, score in job_scores:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{date}**")
            with col2:
                st.progress(score / 100)
                st.caption(f"{score}%")
    
    # Application success rate monitoring
    st.markdown("#### 📈 Application Success Rate")
    
    # This would be enhanced with actual application tracking
    # For now, show placeholder for future implementation
    st.info("""
    **Coming Soon:** Track your job application success rate
    - Applications sent
    - Interview invitations received
    - Job offers received
    - Success rate by job type
    """)
    
    # Improvement recommendations
    st.markdown("#### 💡 Improvement Recommendations")
    
    latest_analysis = analyses[-1]['analysis']
    if latest_analysis.get('optimization_advice'):
        advice = latest_analysis['optimization_advice']
        
        if advice.get('actionable_items'):
            st.markdown("**Priority Actions:**")
            for i, item in enumerate(advice['actionable_items'][:3], 1):
                st.markdown(f"{i}. {item}")
        
        if advice.get('keyword_optimization'):
            st.markdown("**Keywords to Add:**")
            keywords = advice['keyword_optimization'][:5]
            keywords_html = ""
            for keyword in keywords:
                keywords_html += f'<span style="background-color: #fff3cd; padding: 4px 8px; margin: 2px; border-radius: 12px; display: inline-block; font-size: 14px; border: 1px solid #ffeaa7;">{keyword}</span> '
            st.markdown(keywords_html, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        main()
        display_footer()
    except Exception as e:
        st.error(f"Application failed to start: {str(e)}")
        st.markdown("""
        **🔧 Troubleshooting:**
        - Check your Python environment and dependencies
        - Ensure all required packages are installed
        - Verify your .env file configuration
        - Try restarting the application
        """)
        logger.error(f"Application startup failed: {e}")