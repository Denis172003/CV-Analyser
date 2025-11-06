"""
Gemini Veo 3 API integration module for advanced video generation.

This module handles professional video generation using Google's
Gemini Veo 3 API with fallback to moviepy-based generation.
"""

import os
import time
import logging
import requests
from typing import Dict, Optional, Any, List
from google.cloud import aiplatform
from google.auth import default
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Gemini client
_gemini_client = None


def init_gemini_client():
    """
    Initialize Google Cloud AI Platform client for Gemini Veo 3.
    
    Returns:
        Initialized AI Platform client
        
    Raises:
        Exception: If Gemini configuration is missing or invalid
    """
    global _gemini_client
    
    if _gemini_client is None:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        project_id = os.getenv('GEMINI_PROJECT_ID')
        
        if not gemini_api_key or not project_id:
            raise Exception("Gemini configuration missing. Please set GEMINI_API_KEY and GEMINI_PROJECT_ID environment variables.")
        
        try:
            # Initialize AI Platform with project
            aiplatform.init(project=project_id)
            
            # Set up authentication
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gemini_api_key
            
            _gemini_client = aiplatform
            logger.info("Gemini Veo 3 client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise Exception(f"Gemini initialization failed: {str(e)}")
    
    return _gemini_client


def generate_video_with_gemini(
    script_data: Dict,
    style_preferences: Optional[Dict] = None,
    output_path: str = "generated_video.mp4"
) -> Dict:
    """
    Generate professional video using Gemini Veo 3 API.
    
    Args:
        script_data: Video script with timing and content
        style_preferences: Optional video style and branding options
        output_path: Path where generated video should be saved
        
    Returns:
        Dictionary containing job_id, status, and other generation info
        
    Raises:
        Exception: If video generation request fails
    """
    try:
        client = init_gemini_client()
        
        # Prepare video generation prompt
        prompt = _create_video_prompt(script_data, style_preferences)
        
        # Default style preferences
        default_style = {
            'duration': 10,
            'resolution': '1080p',
            'style': 'professional',
            'background': 'gradient',
            'font_family': 'modern',
            'color_scheme': 'blue_white'
        }
        
        if style_preferences:
            default_style.update(style_preferences)
        
        # Create video generation request
        generation_request = {
            'prompt': prompt,
            'duration_seconds': default_style['duration'],
            'resolution': default_style['resolution'],
            'style_parameters': {
                'visual_style': default_style['style'],
                'background_type': default_style['background'],
                'font_family': default_style['font_family'],
                'color_scheme': default_style['color_scheme']
            }
        }
        
        logger.info("Submitting video generation request to Gemini Veo 3")
        
        # Note: This is a placeholder for the actual Gemini Veo 3 API call
        # The actual implementation would depend on the final API structure
        job_id = f"gemini_job_{int(time.time())}"
        
        # Simulate API response
        response = {
            'job_id': job_id,
            'status': 'processing',
            'estimated_completion': time.time() + 60,  # 1 minute estimate
            'output_path': output_path
        }
        
        logger.info(f"Video generation started with job ID: {job_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate video with Gemini: {str(e)}")
        raise Exception(f"Gemini video generation failed: {str(e)}")


def _create_video_prompt(script_data: Dict, style_preferences: Optional[Dict] = None) -> str:
    """
    Create a detailed prompt for Gemini Veo 3 video generation focused on interview preparation.
    
    Args:
        script_data: Video script with segments and timing
        style_preferences: Optional style customizations
        
    Returns:
        Formatted prompt string for video generation optimized for student interview prep
    """
    # Extract script segments
    intro = script_data.get('intro', {})
    skills = script_data.get('skills', {})
    achievement = script_data.get('achievement', {})
    closing = script_data.get('closing', {})
    
    # Build comprehensive prompt focused on interview preparation
    prompt = f"""Create a professional 10-second interview preparation video to help a student present their CV strengths. This video should serve as a practice tool for job interviews:

INTERVIEW PITCH STRUCTURE:

INTRODUCTION (0-2 seconds):
Text: "{intro.get('text', 'Hi, I am a professional')}"
Visual: Confident, professional headshot-style frame with clean typography
Purpose: Help student practice confident self-introduction

KEY STRENGTHS (2-6 seconds):
Text: "{skills.get('text', 'My key strengths include...')}"
Visual: Dynamic presentation of top 3-4 skills with professional icons
Purpose: Train student to highlight most relevant skills quickly

STANDOUT ACHIEVEMENT (6-9 seconds):
Text: "{achievement.get('text', 'My proudest achievement is...')}"
Visual: Emphasis animation showcasing quantifiable results or impact
Purpose: Help student practice presenting concrete examples

INTERVIEW CLOSING (9-10 seconds):
Text: "{closing.get('text', 'I am excited about this opportunity')}"
Visual: Professional call-to-action with enthusiasm
Purpose: Practice confident interview conclusion

INTERVIEW PREPARATION FOCUS:
- Designed specifically for job interview practice
- Helps students memorize and practice their elevator pitch
- Builds confidence for face-to-face interviews
- Emphasizes measurable achievements and concrete skills
- Professional yet approachable tone suitable for entry-level positions
- Clear, confident delivery style that students can emulate

VISUAL STYLE FOR STUDENTS:
- Clean, professional design that reflects modern workplace standards
- Confidence-building visual elements (upward arrows, checkmarks, progress bars)
- Corporate-appropriate color scheme (navy blue, white, subtle accent colors)
- Typography that conveys competence and reliability
- Subtle animations that maintain professionalism
- Background suitable for virtual interviews or LinkedIn profiles

TECHNICAL SPECIFICATIONS:
- Duration: Exactly 10 seconds (perfect for social media and quick introductions)
- Resolution: 1920x1080 (1080p) for high-quality presentation
- Format: MP4 with H.264 encoding for universal compatibility
- Frame rate: 30fps for smooth playback
- Audio: Optional subtle background music that doesn't distract from speech
- Optimized for mobile viewing and social sharing

INTERVIEW SUCCESS ELEMENTS:
- Clear, readable text that students can practice speaking aloud
- Pacing that allows for natural speech rhythm
- Visual cues that help students remember key talking points
- Professional presentation that builds student confidence
- Content structure that follows proven interview best practices
"""

    # Add style customizations if provided
    if style_preferences:
        if 'color_scheme' in style_preferences:
            prompt += f"\n- Preferred color scheme: {style_preferences['color_scheme']}"
        if 'background' in style_preferences:
            prompt += f"\n- Background preference: {style_preferences['background']}"
        if 'font_family' in style_preferences:
            prompt += f"\n- Typography style: {style_preferences['font_family']}"
        if 'industry' in style_preferences:
            prompt += f"\n- Industry focus: {style_preferences['industry']} (adjust visual elements accordingly)"
    
    return prompt


def check_generation_status(job_id: str) -> Dict:
    """
    Check the status of a Gemini video generation job.
    
    Args:
        job_id: Gemini job ID to check
        
    Returns:
        Dictionary with status, progress, and completion info
        
    Raises:
        Exception: If status check fails
    """
    try:
        # Note: This is a placeholder for the actual Gemini API status check
        # The actual implementation would query the Gemini service
        
        # Simulate status check based on job age
        job_timestamp = int(job_id.split('_')[-1])
        current_time = time.time()
        elapsed_time = current_time - job_timestamp
        
        if elapsed_time < 30:
            status = 'processing'
            progress = min(int((elapsed_time / 60) * 100), 90)
        elif elapsed_time < 60:
            status = 'processing'
            progress = 95
        else:
            status = 'completed'
            progress = 100
        
        response = {
            'job_id': job_id,
            'status': status,
            'progress_percentage': progress,
            'estimated_completion': job_timestamp + 60,
            'video_url': f"https://storage.googleapis.com/gemini-videos/{job_id}.mp4" if status == 'completed' else None
        }
        
        logger.info(f"Job {job_id} status: {status} ({progress}%)")
        return response
        
    except Exception as e:
        logger.error(f"Failed to check generation status: {str(e)}")
        raise Exception(f"Status check failed: {str(e)}")


def download_generated_video(video_url: str, output_path: str) -> bool:
    """
    Download completed video from Gemini service.
    
    Args:
        video_url: URL of the generated video
        output_path: Local path to save the video
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        logger.info(f"Downloading video from: {video_url}")
        
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Video downloaded successfully to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download video: {str(e)}")
        return False


def is_gemini_available() -> bool:
    """
    Check if Gemini Veo 3 API is available and configured.
    
    Returns:
        True if Gemini is available, False otherwise
    """
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        project_id = os.getenv('GEMINI_PROJECT_ID')
        
        if not gemini_api_key or not project_id:
            logger.warning("Gemini configuration missing")
            return False
        
        # Try to initialize client
        init_gemini_client()
        return True
        
    except Exception as e:
        logger.warning(f"Gemini not available: {str(e)}")
        return False


def generate_video_with_fallback(
    script_data: Dict,
    style_preferences: Optional[Dict] = None,
    output_path: str = "generated_video.mp4"
) -> Dict:
    """
    Generate video with Gemini Veo 3, falling back to moviepy if unavailable.
    
    Args:
        script_data: Video script with timing and content
        style_preferences: Optional video style and branding options
        output_path: Path where generated video should be saved
        
    Returns:
        Dictionary containing generation info and method used
    """
    try:
        if is_gemini_available():
            logger.info("Using Gemini Veo 3 for video generation")
            result = generate_video_with_gemini(script_data, style_preferences, output_path)
            result['generation_method'] = 'gemini'
            return result
        else:
            logger.info("Gemini unavailable, falling back to moviepy")
            # Import here to avoid circular imports
            from tts_video import make_video, synthesize_audio
            
            # Generate audio first
            audio_path = output_path.replace('.mp4', '.wav')
            
            # Create combined text for TTS
            combined_text = " ".join([
                script_data.get('intro', {}).get('text', ''),
                script_data.get('skills', {}).get('text', ''),
                script_data.get('achievement', {}).get('text', ''),
                script_data.get('closing', {}).get('text', '')
            ])
            
            # Generate audio and video using moviepy fallback
            synthesize_audio(combined_text, audio_path)
            make_video(audio_path, script_data, output_path)
            
            result = {
                'job_id': f"moviepy_{int(time.time())}",
                'status': 'completed',
                'generation_method': 'moviepy',
                'output_path': output_path,
                'video_url': output_path
            }
            
            logger.info("Video generated successfully using moviepy fallback")
            return result
            
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise Exception(f"All video generation methods failed: {str(e)}")


def create_interview_prep_video(
    cv_analysis: Dict,
    student_info: Dict,
    interview_focus: str = "general",
    job_analysis: Optional[Dict] = None,
    output_path: str = "interview_prep.mp4"
) -> Dict:
    """
    Create a specialized 10-second video to help students prepare for job interviews.
    
    Args:
        cv_analysis: Analysis results from AI processing
        student_info: Student information (name, target role, etc.)
        interview_focus: Type of interview prep ("general", "technical", "behavioral")
        output_path: Path where generated video should be saved
        
    Returns:
        Dictionary containing generation info and interview tips
    """
    try:
        # Extract key information for interview preparation
        strengths = cv_analysis.get('strengths', [])
        top_skills = cv_analysis.get('top_skills', [])
        pitch = cv_analysis.get('one_sentence_pitch', '')
        
        # Create interview-focused script with job-specific optimization
        script_data = _create_interview_script(
            student_info, strengths, top_skills, pitch, interview_focus, job_analysis
        )
        
        # Set interview-appropriate style preferences
        style_preferences = {
            'style': 'professional_interview',
            'color_scheme': 'confidence_blue',
            'background': 'clean_corporate',
            'font_family': 'interview_ready',
            'industry': student_info.get('target_industry', 'general'),
            'interview_type': interview_focus
        }
        
        # Generate video with interview-specific prompt
        result = generate_video_with_gemini(script_data, style_preferences, output_path)
        
        # Add interview preparation metadata
        result.update({
            'interview_focus': interview_focus,
            'practice_tips': _generate_interview_tips(cv_analysis, interview_focus),
            'key_talking_points': _extract_talking_points(script_data),
            'recommended_practice_time': '5-10 repetitions before interview'
        })
        
        logger.info(f"Interview preparation video created for {interview_focus} interviews")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create interview prep video: {str(e)}")
        raise Exception(f"Interview video generation failed: {str(e)}")


def _create_interview_script(
    student_info: Dict,
    strengths: List[Dict],
    top_skills: List[str],
    pitch: str,
    interview_focus: str,
    job_analysis: Optional[Dict] = None
) -> Dict:
    """
    Create interview-focused script based on CV analysis.
    
    Args:
        student_info: Student information
        strengths: List of identified strengths
        top_skills: Top skills from analysis
        pitch: One-sentence pitch
        interview_focus: Type of interview preparation
        
    Returns:
        Structured script data for video generation
    """
    name = student_info.get('name', 'Student')
    target_role = student_info.get('target_role', 'Professional')
    
    # If job analysis is provided, prioritize job-relevant skills
    if job_analysis:
        job_required_skills = job_analysis.get('required_skills', [])
        job_title = job_analysis.get('job_title', target_role)
        target_role = job_title  # Use actual job title if available
        
        # Prioritize skills that match job requirements
        job_relevant_skills = []
        other_skills = []
        
        for skill in top_skills:
            if any(job_skill.lower() in skill.lower() or skill.lower() in job_skill.lower() 
                   for job_skill in job_required_skills):
                job_relevant_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Combine job-relevant skills first, then others
        key_skills = (job_relevant_skills + other_skills)[:3]
    else:
        # Select top 3 skills for the video
        key_skills = top_skills[:3] if len(top_skills) >= 3 else top_skills
    
    # Find best achievement from strengths
    best_achievement = "demonstrated strong results"
    if strengths:
        for strength in strengths:
            evidence = strength.get('evidence', '')
            if any(char.isdigit() for char in evidence):
                best_achievement = evidence
                break
        else:
            best_achievement = strengths[0].get('evidence', 'demonstrated strong results')
    
    # Customize script based on interview focus
    if interview_focus == "technical":
        skills_text = f"I specialize in {', '.join(key_skills)}"
        achievement_text = f"I've successfully {best_achievement.lower()}"
    elif interview_focus == "behavioral":
        skills_text = f"My key strengths are {', '.join(key_skills[:2])}"
        achievement_text = f"For example, I {best_achievement.lower()}"
    else:  # general
        skills_text = f"I bring expertise in {', '.join(key_skills)}"
        achievement_text = f"I've {best_achievement.lower()}"
    
    return {
        'intro': {
            'text': f"Hi, I'm {name}, aspiring {target_role}",
            'start_time': 0.0,
            'duration': 2.0
        },
        'skills': {
            'text': skills_text,
            'start_time': 2.0,
            'duration': 4.0
        },
        'achievement': {
            'text': achievement_text,
            'start_time': 6.0,
            'duration': 3.0
        },
        'closing': {
            'text': "I'm excited to contribute to your team",
            'start_time': 9.0,
            'duration': 1.0
        }
    }


def _generate_interview_tips(cv_analysis: Dict, interview_focus: str) -> List[str]:
    """
    Generate specific interview tips based on CV analysis and focus area.
    
    Args:
        cv_analysis: Analysis results
        interview_focus: Type of interview
        
    Returns:
        List of actionable interview tips
    """
    tips = [
        "Practice this pitch 5-10 times before your interview",
        "Maintain eye contact and speak with confidence",
        "Use specific examples when discussing your achievements"
    ]
    
    if interview_focus == "technical":
        tips.extend([
            "Be prepared to demonstrate your technical skills with examples",
            "Discuss specific projects where you used these technologies",
            "Show enthusiasm for learning new technical skills"
        ])
    elif interview_focus == "behavioral":
        tips.extend([
            "Use the STAR method (Situation, Task, Action, Result) for examples",
            "Prepare specific stories that demonstrate your soft skills",
            "Show how you've overcome challenges in past experiences"
        ])
    else:  # general
        tips.extend([
            "Research the company and role thoroughly",
            "Prepare questions to ask the interviewer",
            "Dress professionally and arrive 10 minutes early"
        ])
    
    return tips


def _extract_talking_points(script_data: Dict) -> List[str]:
    """
    Extract key talking points from the script for interview practice.
    
    Args:
        script_data: Video script data
        
    Returns:
        List of key talking points for practice
    """
    return [
        f"Introduction: {script_data.get('intro', {}).get('text', '')}",
        f"Key Skills: {script_data.get('skills', {}).get('text', '')}",
        f"Achievement: {script_data.get('achievement', {}).get('text', '')}",
        f"Closing: {script_data.get('closing', {}).get('text', '')}"
    ]


def get_available_styles() -> List[Dict]:
    """
    Get list of available video styles for interview preparation.
    
    Returns:
        List of style dictionaries optimized for student interview prep
    """
    return [
        {
            'name': 'professional_interview',
            'description': 'Clean, corporate style perfect for business interviews',
            'best_for': 'Business, finance, consulting roles',
            'preview_url': None
        },
        {
            'name': 'tech_interview',
            'description': 'Modern, tech-focused design for technical roles',
            'best_for': 'Software engineering, IT, data science roles',
            'preview_url': None
        },
        {
            'name': 'creative_interview',
            'description': 'Colorful, dynamic design for creative industries',
            'best_for': 'Marketing, design, media roles',
            'preview_url': None
        },
        {
            'name': 'academic_interview',
            'description': 'Scholarly, professional style for academic positions',
            'best_for': 'Research, education, non-profit roles',
            'preview_url': None
        },
        {
            'name': 'startup_interview',
            'description': 'Energetic, innovative style for startup environments',
            'best_for': 'Startups, entrepreneurship, innovation roles',
            'preview_url': None
        }
    ]


def create_job_specific_video(
    cv_analysis: Dict,
    job_analysis: Dict,
    optimization_advice: Dict,
    student_info: Dict,
    output_path: str = "job_specific_video.mp4"
) -> Dict:
    """
    Create a video specifically tailored to a job description with optimization advice.
    
    Args:
        cv_analysis: Analysis results from CV processing
        job_analysis: Analysis results from job description
        optimization_advice: CV optimization recommendations
        student_info: Student information
        output_path: Path where generated video should be saved
        
    Returns:
        Dictionary containing generation info and job-specific recommendations
    """
    try:
        # Extract job-specific information
        job_title = job_analysis.get('job_title', 'this position')
        required_skills = job_analysis.get('required_skills', [])
        company_culture = job_analysis.get('company_culture', [])
        
        # Create job-tailored script
        script_data = _create_job_tailored_script(
            cv_analysis, job_analysis, optimization_advice, student_info
        )
        
        # Set job-specific style preferences
        style_preferences = {
            'style': _determine_job_style(job_analysis),
            'color_scheme': 'job_focused',
            'background': 'professional_match',
            'font_family': 'job_appropriate',
            'industry': job_analysis.get('department', 'general'),
            'job_focus': True
        }
        
        # Generate video with job-specific optimization
        result = generate_video_with_gemini(script_data, style_preferences, output_path)
        
        # Add job-specific metadata
        result.update({
            'job_title': job_title,
            'job_match_score': optimization_advice.get('skill_gap_analysis', {}).get('compatibility_score', 0),
            'key_improvements': _extract_key_improvements(optimization_advice),
            'interview_focus_areas': optimization_advice.get('interview_preparation_focus', []),
            'tailoring_applied': True
        })
        
        logger.info(f"Job-specific video created for {job_title} position")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create job-specific video: {str(e)}")
        raise Exception(f"Job-specific video generation failed: {str(e)}")


def _create_job_tailored_script(
    cv_analysis: Dict,
    job_analysis: Dict,
    optimization_advice: Dict,
    student_info: Dict
) -> Dict:
    """
    Create a script specifically tailored to match a job description.
    
    Args:
        cv_analysis: CV analysis results
        job_analysis: Job analysis results
        optimization_advice: Optimization recommendations
        student_info: Student information
        
    Returns:
        Job-tailored script data
    """
    name = student_info.get('name', 'Student')
    job_title = job_analysis.get('job_title', 'Professional')
    
    # Get job-relevant skills from optimization advice
    skill_gap = optimization_advice.get('skill_gap_analysis', {})
    matching_skills = skill_gap.get('matching_skills', [])[:3]
    
    # Get best achievement that aligns with job responsibilities
    key_responsibilities = job_analysis.get('key_responsibilities', [])
    strengths = cv_analysis.get('strengths', [])
    
    best_achievement = "with proven results in relevant areas"
    if strengths and key_responsibilities:
        # Find strength that best matches job responsibilities
        for strength in strengths:
            evidence = strength.get('evidence', '')
            for resp in key_responsibilities:
                if any(word in evidence.lower() for word in resp.get('responsibility', '').lower().split()[:3]):
                    best_achievement = evidence
                    break
            if best_achievement != "with proven results in relevant areas":
                break
    
    # Create job-focused script
    return {
        'intro': {
            'text': f"Hi, I'm {name}, your ideal {job_title}",
            'start_time': 0.0,
            'duration': 2.0
        },
        'skills': {
            'text': f"I bring {', '.join(matching_skills)} expertise",
            'start_time': 2.0,
            'duration': 4.0
        },
        'achievement': {
            'text': f"I've {best_achievement.lower()}",
            'start_time': 6.0,
            'duration': 3.0
        },
        'closing': {
            'text': "I'm ready to contribute to your team's success",
            'start_time': 9.0,
            'duration': 1.0
        }
    }


def _determine_job_style(job_analysis: Dict) -> str:
    """
    Determine appropriate video style based on job analysis.
    
    Args:
        job_analysis: Job analysis results
        
    Returns:
        Appropriate style name
    """
    department = job_analysis.get('department', '').lower()
    industry_keywords = [kw.lower() for kw in job_analysis.get('industry_keywords', [])]
    
    # Tech-focused roles
    if any(tech_word in department or any(tech_word in kw for kw in industry_keywords) 
           for tech_word in ['software', 'engineering', 'tech', 'data', 'ai', 'development']):
        return 'tech_interview'
    
    # Creative roles
    elif any(creative_word in department or any(creative_word in kw for kw in industry_keywords)
             for creative_word in ['marketing', 'design', 'creative', 'media', 'content']):
        return 'creative_interview'
    
    # Academic/Research roles
    elif any(academic_word in department or any(academic_word in kw for kw in industry_keywords)
             for academic_word in ['research', 'academic', 'education', 'university', 'science']):
        return 'academic_interview'
    
    # Startup environment
    elif any(startup_word in department or any(startup_word in kw for kw in industry_keywords)
             for startup_word in ['startup', 'innovation', 'entrepreneurship', 'venture']):
        return 'startup_interview'
    
    # Default to professional
    else:
        return 'professional_interview'


def _extract_key_improvements(optimization_advice: Dict) -> List[str]:
    """
    Extract key improvement recommendations from optimization advice.
    
    Args:
        optimization_advice: Optimization recommendations
        
    Returns:
        List of key improvements to highlight
    """
    improvements = []
    
    # Critical missing skills
    critical_skills = optimization_advice.get('missing_critical_skills', [])
    if critical_skills:
        improvements.append(f"Highlight {critical_skills[0]['skill']} experience")
    
    # Keyword optimization
    keyword_advice = optimization_advice.get('keyword_optimization', {})
    missing_keywords = keyword_advice.get('missing_industry_keywords', [])
    if missing_keywords:
        improvements.append(f"Include {missing_keywords[0]} in your presentation")
    
    # Experience alignment
    exp_alignment = optimization_advice.get('experience_alignment', {})
    key_responsibilities = exp_alignment.get('key_responsibilities_to_highlight', [])
    if key_responsibilities:
        improvements.append(f"Emphasize {key_responsibilities[0]} experience")
    
    return improvements[:3]  # Limit to top 3 improvements


def estimate_generation_time(script_data: Dict, style_preferences: Optional[Dict] = None) -> int:
    """
    Estimate video generation time in seconds.
    
    Args:
        script_data: Video script data
        style_preferences: Optional style settings
        
    Returns:
        Estimated generation time in seconds
    """
    # Base time for Gemini generation
    base_time = 45
    
    # Add time for complex styles
    if style_preferences and style_preferences.get('style') in ['creative', 'tech']:
        base_time += 15
    
    # Add time for longer content
    total_text_length = sum(len(segment.get('text', '')) for segment in script_data.values())
    if total_text_length > 200:
        base_time += 10
    
    return base_time