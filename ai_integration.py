"""
AI integration module for resume analysis using OpenAI GPT.

This module handles GPT API calls, structured analysis,
and job description comparison functionality.
"""

import os
import json
import logging
import re
import time
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def call_gpt_analysis(resume_text: str, job_text: str = "") -> Dict:
    """
    Call OpenAI GPT API for structured resume analysis.
    
    Args:
        resume_text: Extracted resume text
        job_text: Optional job description for comparison
        
    Returns:
        Dictionary containing analysis results with keys:
        - strengths: List of strength items
        - weak_points: List of weakness items  
        - suggestions: List of improvement suggestions
        - top_skills: List of top skills
        - one_sentence_pitch: Brief pitch text
        
    Raises:
        Exception: If GPT API call fails
    """
    # Detect language for appropriate response
    language = detect_language(resume_text)
    
    # Create system prompt for structured JSON analysis with consistent language
    language_instruction = "Romanian" if language == "ro" else "English"
    
    system_prompt = f"""You are an expert resume analyzer. Analyze the provided resume and respond ONLY with valid JSON in the following format:

{{
    "strengths": [
        {{
            "text": "Brief strength description",
            "evidence": "Specific evidence from resume"
        }}
    ],
    "weak_points": [
        {{
            "text": "Brief weakness description", 
            "location": "Section where found",
            "reason": "Why this is a weakness"
        }}
    ],
    "suggestions": [
        {{
            "for": "What to improve",
            "suggestion": "Specific actionable suggestion"
        }}
    ],
    "top_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "one_sentence_pitch": "Professional pitch starting with 'Hi, I'm [Name]' using the person's actual name from the resume"
}}

CRITICAL LANGUAGE REQUIREMENT:
- ALL text content MUST be written in {language_instruction} ONLY
- Do NOT mix languages - use {language_instruction} consistently throughout
- If the resume is in {language_instruction}, respond entirely in {language_instruction}

IMPORTANT for one_sentence_pitch:
- MUST start with "Hi, I'm [ActualName]" using the person's real name from the resume
- If no name is found, use "Hi, I'm a professional"
- Should be a complete, confident introduction suitable for video
- Example: "Hi, I'm John Smith, a software engineer with 5 years of experience in Python and machine learning"

Respond in {language_instruction}. Provide 3-5 items for each category. Be specific and actionable."""

    # Create user message with resume and optional job description
    user_message = f"Resume text:\n{resume_text}"
    if job_text.strip():
        user_message += f"\n\nJob Description:\n{job_text}"
        user_message += "\n\nPlease analyze the resume and compare it against the job requirements."
    
    try:
        # Call OpenAI API with retry logic
        response = _call_gpt_with_retry(system_prompt, user_message)
        
        # Parse and validate JSON response
        analysis_data = _parse_and_validate_response(response)
        
        logger.info("Successfully analyzed resume with GPT")
        return analysis_data
        
    except Exception as e:
        logger.error(f"GPT analysis failed: {str(e)}")
        raise Exception(f"Failed to analyze resume: {str(e)}")


def generate_pitch_script(analysis_data: Dict) -> Dict:
    """
    Generate structured pitch script for video generation.
    
    Args:
        analysis_data: Analysis results from call_gpt_analysis
        
    Returns:
        Dictionary with script segments:
        - intro: Introduction text and timing
        - skills: Skills text and timing
        - achievement: Achievement text and timing
        - closing: Closing text and timing
    """
    # Extract name from one_sentence_pitch with improved pattern matching
    pitch = analysis_data.get('one_sentence_pitch', '')
    name = _extract_name_from_pitch(pitch)
    
    # Get top skills (limit to 3 for video timing)
    top_skills = analysis_data.get('top_skills', [])[:3]
    skills_text = ", ".join(top_skills) if top_skills else "multiple technical skills"
    
    # Find best achievement from strengths
    strengths = analysis_data.get('strengths', [])
    achievement_text = _extract_best_achievement(strengths)
    
    # Clean and validate text content
    name_clean = _clean_text_for_video(name)
    skills_text_clean = _clean_text_for_video(skills_text)
    achievement_text_clean = _clean_text_for_video(achievement_text)
    
    # Create professional script with 10-second timing distribution
    script = {
        "intro": {
            "text": f"Hi, I'm {name_clean}",
            "start_time": 0.0,
            "duration": 2.0
        },
        "skills": {
            "text": f"Expert in {skills_text_clean}",
            "start_time": 2.0,
            "duration": 4.0
        },
        "achievement": {
            "text": achievement_text_clean,
            "start_time": 6.0,
            "duration": 3.0
        },
        "closing": {
            "text": "Let's connect!",
            "start_time": 9.0,
            "duration": 1.0
        }
    }
    
    # Debug logging to help troubleshoot script generation
    logger.info(f"Generated pitch script for '{name}' with 10-second timing")
    logger.info(f"Script content: intro='{script['intro']['text']}', skills='{script['skills']['text']}', achievement='{script['achievement']['text']}', closing='{script['closing']['text']}'")
    
    return script


def _extract_name_from_pitch(pitch: str) -> str:
    """
    Extract name from one-sentence pitch with multiple pattern matching.
    
    Args:
        pitch: One-sentence pitch text
        
    Returns:
        Extracted name or professional fallback
    """
    if not pitch:
        return "a professional"
    
    # Clean the pitch text
    pitch_clean = pitch.strip()
    
    # Try multiple patterns to extract name
    patterns = [
        r"I'm ([A-Z][a-z]+ [A-Z][a-z]+)",  # "I'm John Smith"
        r"I am ([A-Z][a-z]+ [A-Z][a-z]+)",  # "I am John Smith"
        r"My name is ([A-Z][a-z]+ [A-Z][a-z]+)",  # "My name is John Smith"
        r"I'm ([A-Z][a-z]+)",  # "I'm John"
        r"I am ([A-Z][a-z]+)",  # "I am John"
        r"Hi, I'm ([^,\.!]+)",  # "Hi, I'm John" or "Hi, I'm John Smith"
        r"Hello, I'm ([^,\.!]+)",  # "Hello, I'm John"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, pitch_clean)
        if match:
            name = match.group(1).strip()
            # Validate the extracted name (avoid generic terms)
            if name.lower() not in ['a student', 'student', 'a professional', 'professional', 'someone']:
                return name
    
    # If no name found, return professional fallback
    return "a professional"


def _extract_best_achievement(strengths: List[Dict]) -> str:
    """
    Extract the best achievement from strengths list.
    
    Args:
        strengths: List of strength dictionaries
        
    Returns:
        Best achievement text for video script
    """
    if not strengths:
        return "with proven results and strong performance"
    
    # Look for quantifiable achievements first
    for strength in strengths:
        evidence = strength.get('evidence', '')
        if evidence and any(char.isdigit() for char in evidence):
            # Clean up the evidence text for video
            clean_evidence = evidence.strip()
            if not clean_evidence.lower().startswith('i '):
                clean_evidence = f"I {clean_evidence.lower()}"
            return clean_evidence
    
    # Look for achievements with impact words
    impact_words = ['increased', 'improved', 'developed', 'created', 'led', 'managed', 'achieved', 'delivered']
    for strength in strengths:
        evidence = strength.get('evidence', '')
        if evidence and any(word in evidence.lower() for word in impact_words):
            clean_evidence = evidence.strip()
            if not clean_evidence.lower().startswith('i '):
                clean_evidence = f"I {clean_evidence.lower()}"
            return clean_evidence
    
    # Fallback to first strength evidence
    first_evidence = strengths[0].get('evidence', 'with proven results')
    if first_evidence:
        clean_evidence = first_evidence.strip()
        if not clean_evidence.lower().startswith('i '):
            clean_evidence = f"I {clean_evidence.lower()}"
        return clean_evidence
    
    return "with proven results and strong performance"


def _clean_text_for_video(text: str) -> str:
    """
    Clean text content for video generation to avoid encoding issues.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text safe for video generation
    """
    if not text:
        return ""
    
    # Remove any non-printable characters and strange encodings
    import string
    
    # Keep only printable ASCII characters, spaces, and common punctuation
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' '
    cleaned = ''.join(char for char in text if char in allowed_chars)
    
    # Remove multiple spaces and clean up
    cleaned = ' '.join(cleaned.split())
    
    # Remove any remaining problematic characters that might cause TTS issues
    problematic_chars = ['=', '/', '\\', '<', '>', '{', '}', '[', ']', '|', '~', '`']
    for char in problematic_chars:
        cleaned = cleaned.replace(char, '')
    
    # Ensure the text is not empty after cleaning
    if not cleaned.strip():
        return "professional content"
    
    return cleaned.strip()

def detect_language(text: str) -> str:
    """
    Detect if text is primarily English or Romanian with improved accuracy.
    
    Args:
        text: Text to analyze
        
    Returns:
        'en' for English, 'ro' for Romanian
    """
    if not text or len(text.strip()) < 10:
        return 'en'  # Default to English for very short texts
    
    # Romanian-specific words and patterns (expanded list)
    romanian_indicators = [
        # Common words
        'și', 'cu', 'în', 'de', 'la', 'pe', 'pentru', 'din', 'sau', 'dar', 'care', 'este', 'sunt', 'avea', 'face',
        # Professional terms
        'experiență', 'lucru', 'proiect', 'echipă', 'dezvoltare', 'management', 'companie', 'responsabilități', 
        'abilități', 'educație', 'universitate', 'facultate', 'liceu', 'școală', 'cursuri', 'certificat',
        # Romanian-specific characters and patterns
        'ă', 'â', 'î', 'ș', 'ț', 'română', 'român', 'bucurești', 'cluj', 'timișoara', 'iași',
        # Months in Romanian
        'ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 'iunie', 'iulie', 'august', 
        'septembrie', 'octombrie', 'noiembrie', 'decembrie'
    ]
    
    # English-specific indicators
    english_indicators = [
        'the', 'and', 'with', 'for', 'from', 'that', 'this', 'have', 'been', 'will', 'would', 'could',
        'experience', 'work', 'project', 'team', 'development', 'management', 'company', 'responsibilities',
        'skills', 'education', 'university', 'college', 'school', 'courses', 'certificate'
    ]
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Count indicators
    romanian_count = sum(1 for word in romanian_indicators if word in text_lower)
    english_count = sum(1 for word in english_indicators if word in text_lower)
    
    # Enhanced heuristic with ratio consideration
    total_indicators = romanian_count + english_count
    if total_indicators == 0:
        return 'en'  # Default to English if no indicators found
    
    romanian_ratio = romanian_count / total_indicators
    
    # If Romanian indicators are more than 40% of total, consider it Romanian
    return 'ro' if romanian_ratio > 0.4 else 'en'


def _call_gpt_with_retry(system_prompt: str, user_message: str, max_attempts: int = 2) -> str:
    """
    Call GPT API with exponential backoff retry logic.
    
    Args:
        system_prompt: System message for GPT
        user_message: User message with resume text
        max_attempts: Maximum retry attempts
        
    Returns:
        Raw response text from GPT
        
    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"GPT API attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_attempts - 1:
                # Exponential backoff: wait 2^attempt seconds
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e


def _parse_and_validate_response(response_text: str) -> Dict:
    """
    Parse GPT response and validate JSON structure.
    
    Args:
        response_text: Raw response from GPT
        
    Returns:
        Parsed and validated analysis data
        
    Raises:
        Exception: If JSON parsing or validation fails
    """
    try:
        # Try direct JSON parsing first
        data = json.loads(response_text)
        
    except json.JSONDecodeError:
        # Fallback: extract JSON from text using regex
        logger.warning("Direct JSON parsing failed, trying regex extraction")
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if not json_match:
            raise Exception("No valid JSON found in response")
            
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            raise Exception("Failed to parse extracted JSON")
    
    # Validate required fields
    required_fields = ['strengths', 'weak_points', 'suggestions', 'top_skills', 'one_sentence_pitch']
    for field in required_fields:
        if field not in data:
            raise Exception(f"Missing required field: {field}")
    
    # Ensure lists are actually lists
    list_fields = ['strengths', 'weak_points', 'suggestions', 'top_skills']
    for field in list_fields:
        if not isinstance(data[field], list):
            raise Exception(f"Field {field} must be a list")
    
    # Ensure one_sentence_pitch is a string
    if not isinstance(data['one_sentence_pitch'], str):
        raise Exception("one_sentence_pitch must be a string")
    
    return data


def score_resume_vs_job(resume_skills: List[str], job_skills: List[str]) -> Dict:
    """
    Calculate skill gap analysis between resume and job description.
    
    Args:
        resume_skills: List of skills from resume
        job_skills: List of required skills from job description
        
    Returns:
        Dictionary containing:
        - compatibility_score: Percentage match score
        - missing_skills: List of skills not found in resume
        - matching_skills: List of overlapping skills
    """
    if not resume_skills or not job_skills:
        return {
            "compatibility_score": 0,
            "missing_skills": job_skills if job_skills else [],
            "matching_skills": []
        }
    
    # Normalize skills for comparison (lowercase, strip whitespace)
    resume_skills_norm = [skill.lower().strip() for skill in resume_skills]
    job_skills_norm = [skill.lower().strip() for skill in job_skills]
    
    # Find exact matches
    exact_matches = []
    for job_skill in job_skills_norm:
        for resume_skill in resume_skills_norm:
            if job_skill == resume_skill:
                exact_matches.append(job_skill)
                break
    
    # Find partial matches (weighted lower)
    partial_matches = []
    for job_skill in job_skills_norm:
        if job_skill not in exact_matches:
            for resume_skill in resume_skills_norm:
                # Check if one skill is contained in another (e.g., "python" in "python programming")
                # Require minimum length and avoid short false matches
                if job_skill != resume_skill and len(job_skill) > 3:
                    if job_skill in resume_skill or resume_skill in job_skill:
                        # Additional check: avoid false matches like "java" in "javascript"
                        if not (job_skill == "java" and "javascript" in resume_skill):
                            partial_matches.append(job_skill)
                            break
    
    # Calculate weighted compatibility score
    exact_weight = 1.0
    partial_weight = 0.5
    
    total_score = (len(exact_matches) * exact_weight + len(partial_matches) * partial_weight)
    max_possible_score = len(job_skills_norm) * exact_weight
    
    compatibility_score = int((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
    
    # Find missing skills
    all_matches_norm = exact_matches + partial_matches
    missing_skills = []
    for skill in job_skills:
        if skill.lower().strip() not in all_matches_norm:
            missing_skills.append(skill)
    
    # Get original case matching skills
    matching_skills = []
    all_matches_norm = exact_matches + partial_matches
    for original_skill in job_skills:
        if original_skill.lower().strip() in all_matches_norm:
            matching_skills.append(original_skill)
    
    result = {
        "compatibility_score": compatibility_score,
        "missing_skills": missing_skills,
        "matching_skills": matching_skills
    }
    
    logger.info(f"Skill comparison complete: {compatibility_score}% compatibility")
    return result


def extract_skills_from_job_description(job_text: str) -> List[str]:
    """
    Extract skills from job description text using keyword patterns.
    
    Args:
        job_text: Job description text
        
    Returns:
        List of extracted skills
    """
    # Common skill keywords and patterns
    skill_patterns = [
        r'\b(?:python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift)\b',
        r'\b(?:react|angular|vue|node\.js|express|django|flask|spring|laravel)\b',
        r'\b(?:sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
        r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|github)\b',
        r'\b(?:machine learning|ai|data science|analytics|statistics)\b',
        r'\b(?:project management|agile|scrum|leadership|communication)\b'
    ]
    
    skills = []
    job_text_lower = job_text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, job_text_lower, re.IGNORECASE)
        skills.extend(matches)
    
    # Remove duplicates and return
    return list(set(skills))


def analyze_job_description(job_text: str) -> Dict:
    """
    Analyze job description to extract key requirements and preferences.
    
    Args:
        job_text: Job description text
        
    Returns:
        Dictionary containing job analysis with requirements, skills, and keywords
    """
    try:
        # Detect language for appropriate response
        language = detect_language(job_text)
        
        # Create system prompt for job analysis with consistent language
        language_instruction = "Romanian" if language == "ro" else "English"
        
        system_prompt = f"""You are an expert job market analyst. Analyze the provided job description and respond ONLY with valid JSON in the following format:

{{
    "required_skills": ["skill1", "skill2", "skill3"],
    "preferred_skills": ["skill1", "skill2"],
    "experience_level": "entry|mid|senior",
    "key_responsibilities": [
        {{
            "responsibility": "Main task description",
            "importance": "high|medium|low"
        }}
    ],
    "company_culture": [
        "culture_aspect1",
        "culture_aspect2"
    ],
    "education_requirements": "degree requirement or 'not specified'",
    "industry_keywords": ["keyword1", "keyword2", "keyword3"],
    "job_title": "extracted job title",
    "department": "department or team name",
    "employment_type": "full-time|part-time|contract|internship"
}}

CRITICAL LANGUAGE REQUIREMENT:
- ALL text content MUST be written in {language_instruction} ONLY
- Do NOT mix languages - use {language_instruction} consistently throughout
- Extract information and present it in {language_instruction}

Respond in {language_instruction}. Be specific and extract actual requirements from the text."""

        user_message = f"Job Description:\n{job_text}"
        
        # Call GPT API with retry logic
        response = _call_gpt_with_retry(system_prompt, user_message)
        
        # Parse and validate JSON response
        job_analysis = _parse_and_validate_job_response(response)
        
        logger.info("Successfully analyzed job description")
        return job_analysis
        
    except Exception as e:
        logger.error(f"Job description analysis failed: {str(e)}")
        raise Exception(f"Failed to analyze job description: {str(e)}")


def generate_cv_optimization_advice(resume_analysis: Dict, job_analysis: Dict) -> Dict:
    """
    Generate specific advice on how to optimize CV for a particular job.
    
    Args:
        resume_analysis: Analysis results from call_gpt_analysis
        job_analysis: Analysis results from analyze_job_description
        
    Returns:
        Dictionary containing optimization advice and recommendations
    """
    try:
        # Extract key information
        resume_skills = resume_analysis.get('top_skills', [])
        job_required_skills = job_analysis.get('required_skills', [])
        job_preferred_skills = job_analysis.get('preferred_skills', [])
        job_responsibilities = job_analysis.get('key_responsibilities', [])
        
        # Perform skill gap analysis
        skill_gap = score_resume_vs_job(resume_skills, job_required_skills + job_preferred_skills)
        
        # Generate optimization recommendations
        optimization_advice = {
            'skill_gap_analysis': skill_gap,
            'missing_critical_skills': _identify_critical_missing_skills(job_analysis, resume_analysis),
            'keyword_optimization': _generate_keyword_recommendations(job_analysis, resume_analysis),
            'experience_alignment': _analyze_experience_alignment(job_analysis, resume_analysis),
            'cv_sections_to_improve': _identify_sections_to_improve(job_analysis, resume_analysis),
            'tailoring_suggestions': _generate_tailoring_suggestions(job_analysis, resume_analysis),
            'interview_preparation_focus': _generate_interview_focus_areas(job_analysis, resume_analysis)
        }
        
        logger.info("Generated CV optimization advice")
        return optimization_advice
        
    except Exception as e:
        logger.error(f"CV optimization advice generation failed: {str(e)}")
        raise Exception(f"Failed to generate optimization advice: {str(e)}")


def _parse_and_validate_job_response(response_text: str) -> Dict:
    """
    Parse and validate job description analysis response.
    
    Args:
        response_text: Raw response from GPT
        
    Returns:
        Parsed and validated job analysis data
    """
    try:
        # Try direct JSON parsing first
        data = json.loads(response_text)
        
    except json.JSONDecodeError:
        # Fallback: extract JSON from text using regex
        logger.warning("Direct JSON parsing failed, trying regex extraction")
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if not json_match:
            raise Exception("No valid JSON found in job analysis response")
            
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            raise Exception("Failed to parse extracted JSON from job analysis")
    
    # Validate required fields for job analysis
    required_fields = ['required_skills', 'job_title', 'experience_level']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing field {field} in job analysis, using default")
            if field == 'required_skills':
                data[field] = []
            elif field == 'job_title':
                data[field] = 'Position'
            elif field == 'experience_level':
                data[field] = 'mid'
    
    return data


def _identify_critical_missing_skills(job_analysis: Dict, resume_analysis: Dict) -> List[Dict]:
    """
    Identify critical skills missing from resume that are required for the job.
    
    Args:
        job_analysis: Job requirements analysis
        resume_analysis: Resume analysis results
        
    Returns:
        List of critical missing skills with recommendations
    """
    resume_skills = [skill.lower() for skill in resume_analysis.get('top_skills', [])]
    required_skills = job_analysis.get('required_skills', [])
    
    critical_missing = []
    
    for skill in required_skills:
        if skill.lower() not in resume_skills:
            # Check if it's a partial match
            is_partial_match = any(skill.lower() in resume_skill or resume_skill in skill.lower() 
                                 for resume_skill in resume_skills)
            
            if not is_partial_match:
                critical_missing.append({
                    'skill': skill,
                    'priority': 'high',
                    'recommendation': f"Consider adding {skill} to your skills section or highlighting relevant experience",
                    'learning_suggestion': f"If you don't have {skill} experience, consider taking an online course or mentioning willingness to learn"
                })
    
    return critical_missing


def _generate_keyword_recommendations(job_analysis: Dict, resume_analysis: Dict) -> Dict:
    """
    Generate keyword optimization recommendations for ATS systems.
    
    Args:
        job_analysis: Job requirements analysis
        resume_analysis: Resume analysis results
        
    Returns:
        Dictionary with keyword recommendations
    """
    job_keywords = job_analysis.get('industry_keywords', [])
    job_title = job_analysis.get('job_title', '')
    department = job_analysis.get('department', '')
    
    return {
        'missing_industry_keywords': [kw for kw in job_keywords if kw not in str(resume_analysis)],
        'title_optimization': f"Consider including variations of '{job_title}' in your professional summary",
        'department_keywords': f"Include {department}-related terminology if applicable",
        'ats_optimization_tips': [
            "Use exact keyword matches from the job description",
            "Include keywords in multiple sections (summary, experience, skills)",
            "Use both acronyms and full forms (e.g., 'AI' and 'Artificial Intelligence')",
            "Match the job description's language and terminology"
        ]
    }


def _analyze_experience_alignment(job_analysis: Dict, resume_analysis: Dict) -> Dict:
    """
    Analyze how well the candidate's experience aligns with job requirements.
    
    Args:
        job_analysis: Job requirements analysis
        resume_analysis: Resume analysis results
        
    Returns:
        Dictionary with experience alignment analysis
    """
    required_level = job_analysis.get('experience_level', 'mid')
    key_responsibilities = job_analysis.get('key_responsibilities', [])
    
    # Extract high-priority responsibilities
    high_priority_responsibilities = [
        resp['responsibility'] for resp in key_responsibilities 
        if resp.get('importance') == 'high'
    ]
    
    return {
        'experience_level_match': required_level,
        'key_responsibilities_to_highlight': high_priority_responsibilities[:3],
        'experience_gaps': f"Focus on demonstrating experience with {', '.join(high_priority_responsibilities[:2])}",
        'recommendations': [
            f"Emphasize experience that aligns with {required_level}-level expectations",
            "Quantify achievements that demonstrate relevant experience",
            "Use action verbs that match the job's responsibility descriptions"
        ]
    }


def _identify_sections_to_improve(job_analysis: Dict, resume_analysis: Dict) -> List[Dict]:
    """
    Identify specific CV sections that need improvement for this job.
    
    Args:
        job_analysis: Job requirements analysis
        resume_analysis: Resume analysis results
        
    Returns:
        List of sections with improvement recommendations
    """
    sections_to_improve = []
    
    # Check if education requirements are met
    education_req = job_analysis.get('education_requirements', 'not specified')
    if education_req != 'not specified':
        sections_to_improve.append({
            'section': 'Education',
            'priority': 'medium',
            'recommendation': f"Ensure your education section clearly shows {education_req}",
            'action': 'highlight_relevant_coursework'
        })
    
    # Check skills section
    missing_skills = len(job_analysis.get('required_skills', [])) - len(resume_analysis.get('top_skills', []))
    if missing_skills > 0:
        sections_to_improve.append({
            'section': 'Skills',
            'priority': 'high',
            'recommendation': 'Add missing technical and soft skills from job requirements',
            'action': 'expand_skills_section'
        })
    
    # Check professional summary
    sections_to_improve.append({
        'section': 'Professional Summary',
        'priority': 'high',
        'recommendation': f"Tailor summary to match {job_analysis.get('job_title', 'this position')}",
        'action': 'customize_summary'
    })
    
    return sections_to_improve


def _generate_tailoring_suggestions(job_analysis: Dict, resume_analysis: Dict) -> List[str]:
    """
    Generate specific suggestions for tailoring the CV to this job.
    
    Args:
        job_analysis: Job requirements analysis
        resume_analysis: Resume analysis results
        
    Returns:
        List of actionable tailoring suggestions
    """
    suggestions = []
    
    job_title = job_analysis.get('job_title', 'this position')
    company_culture = job_analysis.get('company_culture', [])
    
    # Title-specific suggestions
    suggestions.append(f"Customize your professional summary to emphasize fit for {job_title} role")
    
    # Culture fit suggestions
    if company_culture:
        culture_aspects = ', '.join(company_culture[:2])
        suggestions.append(f"Highlight experiences that demonstrate {culture_aspects}")
    
    # Responsibility alignment
    key_responsibilities = job_analysis.get('key_responsibilities', [])
    if key_responsibilities:
        top_responsibility = key_responsibilities[0].get('responsibility', '')
        suggestions.append(f"Lead with experience related to: {top_responsibility}")
    
    # Industry-specific suggestions
    industry_keywords = job_analysis.get('industry_keywords', [])
    if industry_keywords:
        suggestions.append(f"Incorporate industry terms: {', '.join(industry_keywords[:3])}")
    
    # General tailoring advice
    suggestions.extend([
        "Reorder bullet points to prioritize most relevant experience",
        "Use similar language and terminology as the job description",
        "Quantify achievements that align with job requirements",
        "Remove or de-emphasize irrelevant experience to focus on relevant skills"
    ])
    
    return suggestions


def _generate_interview_focus_areas(job_analysis: Dict, resume_analysis: Dict) -> List[str]:
    """
    Generate interview preparation focus areas based on job-CV alignment.
    
    Args:
        job_analysis: Job requirements analysis
        resume_analysis: Resume analysis results
        
    Returns:
        List of interview preparation focus areas
    """
    focus_areas = []
    
    # Skills-based focus
    required_skills = job_analysis.get('required_skills', [])
    if required_skills:
        focus_areas.append(f"Prepare examples demonstrating {', '.join(required_skills[:2])}")
    
    # Responsibility-based focus
    key_responsibilities = job_analysis.get('key_responsibilities', [])
    high_priority_resp = [r for r in key_responsibilities if r.get('importance') == 'high']
    if high_priority_resp:
        resp_text = high_priority_resp[0].get('responsibility', '')
        focus_areas.append(f"Practice discussing experience with: {resp_text}")
    
    # Experience level focus
    exp_level = job_analysis.get('experience_level', 'mid')
    if exp_level == 'senior':
        focus_areas.append("Prepare leadership and mentoring examples")
    elif exp_level == 'entry':
        focus_areas.append("Emphasize learning agility and growth potential")
    
    # Company culture focus
    company_culture = job_analysis.get('company_culture', [])
    if company_culture:
        focus_areas.append(f"Prepare examples showing {company_culture[0]} mindset")
    
    return focus_areas


def generate_interview_questions(resume_analysis: Dict, job_analysis: Dict = None) -> Dict:
    """
    Generate potential interview questions based on CV and job requirements.
    
    Args:
        resume_analysis: Analysis results from CV processing
        job_analysis: Optional job analysis results
        
    Returns:
        Dictionary with categorized interview questions by difficulty
    """
    try:
        # Extract key information
        top_skills = resume_analysis.get('top_skills', [])
        strengths = resume_analysis.get('strengths', [])
        weak_points = resume_analysis.get('weak_points', [])
        
        # Job-specific information if available
        job_title = job_analysis.get('job_title', 'this position') if job_analysis else 'this position'
        required_skills = job_analysis.get('required_skills', []) if job_analysis else []
        key_responsibilities = job_analysis.get('key_responsibilities', []) if job_analysis else []
        
        # Detect language from resume analysis for consistent responses
        resume_text = resume_analysis.get('original_text', '')
        if not resume_text:
            # Try to get language from top skills or other text fields
            resume_text = ' '.join(resume_analysis.get('top_skills', []))
        language = detect_language(resume_text)
        language_instruction = "Romanian" if language == "ro" else "English"
        
        # Create system prompt for generating interview questions
        system_prompt = f"""You are an expert HR interviewer. Generate realistic interview questions based on the candidate's CV and job requirements. 

Respond ONLY with valid JSON in this format:
{{
    "easy_questions": [
        {{
            "question": "Question text",
            "category": "General/Technical/Behavioral",
            "focus": "What this question tests",
            "tip": "Brief tip for answering"
        }}
    ],
    "medium_questions": [
        {{
            "question": "Question text",
            "category": "General/Technical/Behavioral", 
            "focus": "What this question tests",
            "tip": "Brief tip for answering"
        }}
    ],
    "hard_questions": [
        {{
            "question": "Question text",
            "category": "General/Technical/Behavioral",
            "focus": "What this question tests", 
            "tip": "Brief tip for answering"
        }}
    ]
}}

CRITICAL LANGUAGE REQUIREMENT:
- ALL text content MUST be written in {language_instruction} ONLY
- Do NOT mix languages - use {language_instruction} consistently throughout
- Questions, categories, focus areas, and tips must all be in {language_instruction}

Generate 4-5 questions per difficulty level. Make questions specific to the candidate's background and job requirements."""

        # Create user message with CV and job context
        user_message = f"""
        CANDIDATE PROFILE:
        - Top Skills: {', '.join(top_skills[:5])}
        - Key Strengths: {', '.join([s.get('text', '') for s in strengths[:3]])}
        - Areas for Improvement: {', '.join([w.get('text', '') for w in weak_points[:2]])}
        
        JOB CONTEXT:
        - Position: {job_title}
        - Required Skills: {', '.join(required_skills[:5])}
        - Key Responsibilities: {', '.join([r.get('responsibility', '') for r in key_responsibilities[:3]])}
        
        Generate interview questions that:
        1. EASY: Basic questions about background, motivation, and general skills
        2. MEDIUM: Specific questions about experience, technical skills, and job-related scenarios
        3. HARD: Complex behavioral questions, problem-solving, and challenging technical/strategic questions
        
        Make questions realistic and relevant to both the candidate's profile and job requirements.
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            questions_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: extract JSON from text using regex
            logger.warning("Direct JSON parsing failed, trying regex extraction")
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
            else:
                raise Exception("Failed to extract JSON from response")
        
        # Validate and structure the response
        structured_questions = {
            'easy_questions': questions_data.get('easy_questions', []),
            'medium_questions': questions_data.get('medium_questions', []),
            'hard_questions': questions_data.get('hard_questions', [])
        }
        
        logger.info("Successfully generated interview questions")
        return structured_questions
        
    except Exception as e:
        logger.error(f"Failed to generate interview questions: {str(e)}")
        
        # Fallback questions based on available data
        return _generate_fallback_interview_questions(resume_analysis, job_analysis)


def _generate_fallback_interview_questions(resume_analysis: Dict, job_analysis: Dict = None) -> Dict:
    """
    Generate fallback interview questions when AI generation fails.
    
    Args:
        resume_analysis: Analysis results from CV processing
        job_analysis: Optional job analysis results
        
    Returns:
        Dictionary with basic interview questions
    """
    top_skills = resume_analysis.get('top_skills', [])
    job_title = job_analysis.get('job_title', 'this position') if job_analysis else 'this position'
    
    return {
        'easy_questions': [
            {
                'question': 'Tell me about yourself and your background.',
                'category': 'General',
                'focus': 'Self-presentation and communication skills',
                'tip': 'Keep it concise, focus on relevant experience and skills'
            },
            {
                'question': f'Why are you interested in {job_title}?',
                'category': 'General', 
                'focus': 'Motivation and job fit',
                'tip': 'Show genuine interest and connect your skills to the role'
            },
            {
                'question': 'What are your greatest strengths?',
                'category': 'Behavioral',
                'focus': 'Self-awareness and relevant skills',
                'tip': 'Choose strengths relevant to the job and provide examples'
            },
            {
                'question': 'Where do you see yourself in 5 years?',
                'category': 'General',
                'focus': 'Career goals and ambition',
                'tip': 'Align your goals with the company and role growth path'
            }
        ],
        'medium_questions': [
            {
                'question': f'How would you apply your {top_skills[0] if top_skills else "technical skills"} in this role?',
                'category': 'Technical',
                'focus': 'Practical application of skills',
                'tip': 'Give specific examples and relate to job requirements'
            },
            {
                'question': 'Describe a challenging project you worked on and how you overcame obstacles.',
                'category': 'Behavioral',
                'focus': 'Problem-solving and resilience',
                'tip': 'Use the STAR method: Situation, Task, Action, Result'
            },
            {
                'question': 'How do you handle working under pressure and tight deadlines?',
                'category': 'Behavioral',
                'focus': 'Stress management and time management',
                'tip': 'Provide concrete examples and mention specific strategies'
            },
            {
                'question': 'What interests you most about our company?',
                'category': 'General',
                'focus': 'Company research and genuine interest',
                'tip': 'Research the company beforehand and mention specific aspects'
            }
        ],
        'hard_questions': [
            {
                'question': 'Describe a time when you had to learn a new technology or skill quickly. How did you approach it?',
                'category': 'Behavioral',
                'focus': 'Learning agility and adaptability',
                'tip': 'Emphasize your learning process and how you applied the new skill'
            },
            {
                'question': 'How would you handle a situation where you disagree with your manager\'s approach?',
                'category': 'Behavioral',
                'focus': 'Conflict resolution and professional communication',
                'tip': 'Show respect for hierarchy while demonstrating your ability to contribute ideas'
            },
            {
                'question': 'What would you do if you realized you made a significant mistake in your work?',
                'category': 'Behavioral',
                'focus': 'Accountability and problem-solving',
                'tip': 'Emphasize taking responsibility, learning from mistakes, and preventing future issues'
            },
            {
                'question': f'How would you prioritize multiple competing deadlines in {job_title}?',
                'category': 'Technical',
                'focus': 'Project management and decision-making',
                'tip': 'Discuss your prioritization framework and communication strategies'
            }
        ]
    }


def conduct_mock_interview(resume_analysis: Dict, job_analysis: Dict = None, interview_type: str = "general") -> Dict:
    """
    Generate 3 interview questions for a mock interview session.
    
    Args:
        resume_analysis: Analysis results from CV processing
        job_analysis: Optional job analysis results
        interview_type: Type of interview (general, technical, behavioral)
        
    Returns:
        Dictionary with 3 interview questions for the mock session
    """
    try:
        # Extract key information
        top_skills = resume_analysis.get('top_skills', [])
        strengths = resume_analysis.get('strengths', [])
        
        # Job-specific information if available
        job_title = job_analysis.get('job_title', 'this position') if job_analysis else 'this position'
        required_skills = job_analysis.get('required_skills', []) if job_analysis else []
        company_name = job_analysis.get('company_name', 'our company') if job_analysis else 'our company'
        
        # Detect language from resume analysis for consistent responses
        resume_text = resume_analysis.get('original_text', '')
        if not resume_text:
            # Try to get language from top skills or other text fields
            resume_text = ' '.join(resume_analysis.get('top_skills', []))
        language = detect_language(resume_text)
        language_instruction = "Romanian" if language == "ro" else "English"
        
        # Create system prompt for mock interview
        system_prompt = f"""You are an experienced HR interviewer conducting a mock interview. Generate exactly 3 realistic interview questions based on the candidate's profile and job requirements.

Respond ONLY with valid JSON in this format:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Question text",
            "category": "General/Technical/Behavioral",
            "difficulty": "Easy/Medium/Hard",
            "expected_elements": ["element1", "element2", "element3"],
            "evaluation_criteria": "What to look for in a good answer"
        }}
    ],
    "interview_context": {{
        "position": "Job title",
        "company": "Company name",
        "focus_areas": ["area1", "area2", "area3"]
    }}
}}

CRITICAL LANGUAGE REQUIREMENT:
- ALL text content MUST be written in {language_instruction} ONLY
- Do NOT mix languages - use {language_instruction} consistently throughout
- Questions, categories, expected elements, and evaluation criteria must all be in {language_instruction}

Generate questions that:
1. Are realistic and commonly asked in interviews
2. Are relevant to the candidate's background and job requirements
3. Progress from easier to more challenging
4. Test different aspects (motivation, skills, problem-solving)"""

        # Create user message with context
        user_message = f"""
        CANDIDATE PROFILE:
        - Top Skills: {', '.join(top_skills[:5])}
        - Key Strengths: {', '.join([s.get('text', '') for s in strengths[:3]])}
        
        JOB CONTEXT:
        - Position: {job_title}
        - Company: {company_name}
        - Required Skills: {', '.join(required_skills[:5])}
        - Interview Type: {interview_type}
        
        Generate 3 interview questions:
        1. First question: Easier, about background/motivation
        2. Second question: Medium difficulty, about skills/experience
        3. Third question: More challenging, behavioral/problem-solving
        
        Make questions specific to this role and candidate profile.
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            interview_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: extract JSON from text using regex
            logger.warning("Direct JSON parsing failed, trying regex extraction")
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                interview_data = json.loads(json_match.group())
            else:
                raise Exception("Failed to extract JSON from response")
        
        logger.info("Successfully generated mock interview questions")
        return interview_data
        
    except Exception as e:
        logger.error(f"Failed to generate mock interview: {str(e)}")
        
        # Fallback questions
        return _generate_fallback_mock_interview(resume_analysis, job_analysis)


def evaluate_interview_responses(questions: List[Dict], responses: List[str], resume_analysis: Dict, job_analysis: Dict = None) -> Dict:
    """
    Evaluate user responses to mock interview questions and provide feedback.
    
    Args:
        questions: List of interview questions asked
        responses: List of user responses
        resume_analysis: Analysis results from CV processing
        job_analysis: Optional job analysis results
        
    Returns:
        Dictionary with evaluation results and feedback
    """
    try:
        # Detect language from resume analysis for consistent responses
        resume_text = resume_analysis.get('original_text', '')
        if not resume_text:
            # Try to get language from top skills or other text fields
            resume_text = ' '.join(resume_analysis.get('top_skills', []))
        language = detect_language(resume_text)
        language_instruction = "Romanian" if language == "ro" else "English"
        
        # Create system prompt for evaluation
        system_prompt = f"""You are an expert HR interviewer evaluating interview responses. Provide constructive feedback and scoring.

Respond ONLY with valid JSON in this format:
{{
    "overall_score": 85,
    "individual_scores": [
        {{
            "question_id": 1,
            "score": 80,
            "feedback": "Detailed feedback on this response",
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }}
    ],
    "overall_feedback": {{
        "strengths": ["overall strength1", "overall strength2"],
        "areas_for_improvement": ["improvement1", "improvement2"],
        "recommendations": ["recommendation1", "recommendation2"]
    }},
    "interview_performance": {{
        "communication": 85,
        "relevance": 80,
        "confidence": 75,
        "specificity": 70
    }}
}}

CRITICAL LANGUAGE REQUIREMENT:
- ALL text content MUST be written in {language_instruction} ONLY
- Do NOT mix languages - use {language_instruction} consistently throughout
- Feedback, strengths, improvements, and recommendations must all be in {language_instruction}

Scoring criteria (0-100):
- 90-100: Excellent, comprehensive answers with specific examples
- 80-89: Good answers with some examples and clear communication
- 70-79: Adequate answers but lacking detail or examples
- 60-69: Basic answers that address the question but need improvement
- Below 60: Insufficient or unclear answers

Be constructive and specific in feedback."""

        # Prepare evaluation context
        evaluation_context = f"""
        INTERVIEW EVALUATION:
        
        Questions and Responses:
        """
        
        for i, (question, response) in enumerate(zip(questions, responses), 1):
            evaluation_context += f"""
        Question {i}: {question.get('question', '')}
        Category: {question.get('category', 'General')}
        Expected Elements: {', '.join(question.get('expected_elements', []))}
        
        Candidate Response: {response}
        
        ---
        """
        
        evaluation_context += f"""
        
        CANDIDATE CONTEXT:
        - Top Skills: {', '.join(resume_analysis.get('top_skills', [])[:5])}
        - Key Strengths: {', '.join([s.get('text', '') for s in resume_analysis.get('strengths', [])[:3]])}
        """
        
        if job_analysis:
            evaluation_context += f"""
        - Target Position: {job_analysis.get('job_title', 'Unknown')}
        - Required Skills: {', '.join(job_analysis.get('required_skills', [])[:5])}
        """

        # Call OpenAI API for evaluation
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": evaluation_context}
            ],
            temperature=0.3,  # Lower temperature for more consistent evaluation
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            evaluation_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: extract JSON from text using regex
            logger.warning("Direct JSON parsing failed, trying regex extraction")
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                evaluation_data = json.loads(json_match.group())
            else:
                raise Exception("Failed to extract JSON from response")
        
        logger.info("Successfully evaluated interview responses")
        return evaluation_data
        
    except Exception as e:
        logger.error(f"Failed to evaluate interview responses: {str(e)}")
        
        # Fallback evaluation
        return _generate_fallback_evaluation(questions, responses)


def _generate_fallback_mock_interview(resume_analysis: Dict, job_analysis: Dict = None) -> Dict:
    """Generate fallback mock interview questions when AI generation fails."""
    top_skills = resume_analysis.get('top_skills', [])
    job_title = job_analysis.get('job_title', 'this position') if job_analysis else 'this position'
    company_name = job_analysis.get('company_name', 'our company') if job_analysis else 'our company'
    
    return {
        "questions": [
            {
                "id": 1,
                "question": f"Tell me about yourself and why you're interested in {job_title}.",
                "category": "General",
                "difficulty": "Easy",
                "expected_elements": ["Background summary", "Relevant experience", "Motivation for role"],
                "evaluation_criteria": "Clear communication, relevant background, genuine interest"
            },
            {
                "id": 2,
                "question": f"How would you apply your {top_skills[0] if top_skills else 'technical skills'} in this role?",
                "category": "Technical",
                "difficulty": "Medium",
                "expected_elements": ["Specific examples", "Technical knowledge", "Practical application"],
                "evaluation_criteria": "Technical understanding, specific examples, job relevance"
            },
            {
                "id": 3,
                "question": "Describe a challenging situation you faced and how you overcame it.",
                "category": "Behavioral",
                "difficulty": "Hard",
                "expected_elements": ["STAR method", "Problem-solving approach", "Learning outcome"],
                "evaluation_criteria": "Structured response, problem-solving skills, self-reflection"
            }
        ],
        "interview_context": {
            "position": job_title,
            "company": company_name,
            "focus_areas": ["Communication", "Technical skills", "Problem-solving"]
        }
    }


def _generate_fallback_evaluation(questions: List[Dict], responses: List[str]) -> Dict:
    """Generate fallback evaluation when AI evaluation fails."""
    # Simple scoring based on response length and basic criteria
    individual_scores = []
    total_score = 0
    
    for i, (question, response) in enumerate(zip(questions, responses)):
        # Basic scoring based on response length and content
        response_length = len(response.split())
        
        if response_length < 10:
            score = 40
        elif response_length < 30:
            score = 60
        elif response_length < 60:
            score = 75
        else:
            score = 85
        
        individual_scores.append({
            "question_id": i + 1,
            "score": score,
            "feedback": f"Your response was {'brief' if response_length < 30 else 'detailed'}. Consider providing more specific examples.",
            "strengths": ["Clear communication"],
            "improvements": ["Add more specific examples", "Provide more detail"]
        })
        
        total_score += score
    
    overall_score = total_score // len(questions)
    
    return {
        "overall_score": overall_score,
        "individual_scores": individual_scores,
        "overall_feedback": {
            "strengths": ["Completed the interview", "Provided responses to all questions"],
            "areas_for_improvement": ["Provide more specific examples", "Use the STAR method for behavioral questions"],
            "recommendations": ["Practice with more detailed responses", "Prepare specific examples from your experience"]
        },
        "interview_performance": {
            "communication": overall_score,
            "relevance": overall_score - 5,
            "confidence": overall_score - 10,
            "specificity": overall_score - 15
        }
    }