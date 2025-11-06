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
    
    # Create system prompt for structured JSON analysis
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

IMPORTANT for one_sentence_pitch:
- MUST start with "Hi, I'm [ActualName]" using the person's real name from the resume
- If no name is found, use "Hi, I'm a professional"
- Should be a complete, confident introduction suitable for video
- Example: "Hi, I'm John Smith, a software engineer with 5 years of experience in Python and machine learning"

Respond in {"Romanian" if language == "ro" else "English"}. Provide 3-5 items for each category. Be specific and actionable."""

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
    Detect if text is primarily English or Romanian.
    
    Args:
        text: Text to analyze
        
    Returns:
        'en' for English, 'ro' for Romanian
    """
    # Romanian-specific words and patterns
    romanian_indicators = [
        'și', 'cu', 'în', 'de', 'la', 'pe', 'pentru', 'din', 'sau', 'dar',
        'experiență', 'lucru', 'proiect', 'echipă', 'dezvoltare', 'management',
        'companie', 'responsabilități', 'abilități', 'educație', 'universitate'
    ]
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Count Romanian indicators
    romanian_count = sum(1 for word in romanian_indicators if word in text_lower)
    
    # Simple heuristic: if we find 3+ Romanian indicators, assume Romanian
    return 'ro' if romanian_count >= 3 else 'en'


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
        
        # Create system prompt for job analysis
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

Respond in {"Romanian" if language == "ro" else "English"}. Be specific and extract actual requirements from the text."""

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