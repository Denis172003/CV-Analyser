"""
Utility functions for AI Resume Analyzer.

This module contains helper functions for text processing,
file management, language detection, and cross-platform compatibility.
"""

import os
import re
import logging
import unicodedata
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text for resume processing.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text with normalized whitespace and formatting
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
    
    # Clean up common PDF extraction artifacts
    text = re.sub(r'[^\w\s\-.,;:()\[\]{}@#$%&*+=<>?/\\|`~"\'!\n]', '', text)
    
    # Remove page numbers and headers/footers patterns
    text = re.sub(r'\b(Page \d+|\d+ of \d+)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(Resume|CV|Curriculum Vitae)\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Clean up email and phone formatting
    text = re.sub(r'(\w+@\w+\.\w+)', r' \1 ', text)  # Add spaces around emails
    text = re.sub(r'(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})', r' \1 ', text)  # Phone numbers
    
    return text.strip()


def clean_text_for_analysis(text: str) -> str:
    """
    Advanced text cleaning specifically for AI analysis.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Text optimized for AI processing
    """
    if not text:
        return ""
    
    # Start with basic cleaning
    text = clean_text(text)
    
    # Remove redundant section headers
    text = re.sub(r'^(EXPERIENCE|EDUCATION|SKILLS|SUMMARY|OBJECTIVE|PROJECTS|CERTIFICATIONS|ACHIEVEMENTS)\s*:?\s*$', 
                  r'\1:', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Normalize bullet points
    text = re.sub(r'^[\s]*[•·▪▫◦‣⁃]\s*', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*[-*]\s*', '• ', text, flags=re.MULTILINE)
    
    # Clean up date formats
    text = re.sub(r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})\b', r'\1/\2/\3', text)
    text = re.sub(r'\b(\w+)\s+(\d{4})\s*[-–—]\s*(\w+)?\s*(\d{4}|Present|Current)\b', 
                  r'\1 \2 - \3 \4', text, flags=re.IGNORECASE)
    
    # Normalize common abbreviations
    abbreviations = {
        r'\bPhD\b': 'Ph.D.',
        r'\bMBA\b': 'M.B.A.',
        r'\bBS\b': 'B.S.',
        r'\bBA\b': 'B.A.',
        r'\bMS\b': 'M.S.',
        r'\bMA\b': 'M.A.',
        r'\bCEO\b': 'Chief Executive Officer',
        r'\bCTO\b': 'Chief Technology Officer',
        r'\bVP\b': 'Vice President'
    }
    
    for abbrev, full_form in abbreviations.items():
        text = re.sub(abbrev, full_form, text, flags=re.IGNORECASE)
    
    return text.strip()


def detect_language(text: str) -> str:
    """
    Detect if text is primarily English or Romanian using multiple heuristics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code: "en" for English, "ro" for Romanian
    """
    if not text:
        return "en"
    
    text_lower = text.lower()
    
    # Romanian diacritical marks (strong indicators)
    romanian_diacritics = ['ă', 'â', 'î', 'ș', 'ț']
    diacritic_count = sum(text_lower.count(char) for char in romanian_diacritics)
    
    # Common Romanian words
    romanian_words = [
        'și', 'cu', 'de', 'la', 'în', 'pe', 'pentru', 'sau', 'dar', 'că',
        'este', 'sunt', 'avea', 'face', 'lucru', 'timp', 'ani', 'experiență',
        'competențe', 'educație', 'proiecte', 'certificări', 'realizări'
    ]
    
    # Common English words that are rare in Romanian
    english_words = [
        'the', 'and', 'with', 'for', 'from', 'have', 'work', 'experience',
        'skills', 'education', 'projects', 'certifications', 'achievements',
        'management', 'development', 'analysis', 'implementation'
    ]
    
    romanian_word_count = sum(1 for word in romanian_words if f' {word} ' in f' {text_lower} ')
    english_word_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ')
    
    # Scoring system
    romanian_score = diacritic_count * 3 + romanian_word_count * 2
    english_score = english_word_count * 2
    
    # Additional check for Romanian-specific patterns
    if re.search(r'\b(universitatea|facultatea|licența|masterul|doctoratul)\b', text_lower):
        romanian_score += 5
    
    if re.search(r'\b(university|college|bachelor|master|phd|degree)\b', text_lower):
        english_score += 3
    
    return "ro" if romanian_score > english_score else "en"


def detect_language_advanced(text: str) -> Dict[str, float]:
    """
    Advanced language detection with confidence scores.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with language codes and confidence scores
    """
    if not text:
        return {"en": 1.0, "ro": 0.0}
    
    text_lower = text.lower()
    total_chars = len(text_lower.replace(' ', ''))
    
    if total_chars == 0:
        return {"en": 1.0, "ro": 0.0}
    
    # Character frequency analysis
    romanian_chars = 'ăâîșț'
    romanian_char_freq = sum(text_lower.count(char) for char in romanian_chars) / total_chars
    
    # Word pattern analysis
    romanian_patterns = [
        r'\b(și|cu|de|la|în|pe|pentru|sau|dar|că)\b',
        r'\b(experiență|competențe|educație|proiecte)\b',
        r'\b(universitatea|facultatea|licența)\b'
    ]
    
    english_patterns = [
        r'\b(the|and|with|for|from|have|work)\b',
        r'\b(experience|skills|education|projects)\b',
        r'\b(university|college|bachelor|master)\b'
    ]
    
    romanian_pattern_count = sum(len(re.findall(pattern, text_lower)) for pattern in romanian_patterns)
    english_pattern_count = sum(len(re.findall(pattern, text_lower)) for pattern in english_patterns)
    
    total_patterns = romanian_pattern_count + english_pattern_count
    
    if total_patterns == 0:
        # Fallback to character analysis
        ro_confidence = min(romanian_char_freq * 10, 1.0)
        en_confidence = 1.0 - ro_confidence
    else:
        ro_confidence = (romanian_pattern_count + romanian_char_freq * 5) / (total_patterns + 5)
        en_confidence = 1.0 - ro_confidence
    
    return {
        "en": max(0.1, min(0.9, en_confidence)),
        "ro": max(0.1, min(0.9, ro_confidence))
    }


def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path to ensure exists
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {path}")
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise


def get_safe_filename(filename: str) -> str:
    """
    Generate safe filename for cross-platform compatibility.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename with invalid characters removed
    """
    if not filename:
        return f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Remove or replace invalid characters for Windows/Unix compatibility
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe_name)  # Remove control characters
    
    # Handle reserved names on Windows
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    name_without_ext = os.path.splitext(safe_name)[0].upper()
    if name_without_ext in reserved_names:
        safe_name = f"file_{safe_name}"
    
    # Limit length (255 is typical filesystem limit)
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        max_name_length = 255 - len(ext)
        safe_name = name[:max_name_length] + ext
    
    # Ensure it doesn't start or end with spaces or dots
    safe_name = safe_name.strip(' .')
    
    return safe_name or f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def get_temp_file_path(suffix: str = "", prefix: str = "resume_analyzer_") -> str:
    """
    Generate a temporary file path with proper cleanup handling.
    
    Args:
        suffix: File extension or suffix
        prefix: File prefix
        
    Returns:
        Path to temporary file
    """
    temp_dir = tempfile.gettempdir()
    ensure_directory(temp_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f"{prefix}{timestamp}{suffix}"
    
    return os.path.join(temp_dir, get_safe_filename(filename))


def cleanup_temp_files(pattern: str = "resume_analyzer_*") -> int:
    """
    Clean up temporary files matching the pattern.
    
    Args:
        pattern: Glob pattern for files to clean up
        
    Returns:
        Number of files cleaned up
    """
    temp_dir = Path(tempfile.gettempdir())
    cleaned_count = 0
    
    try:
        for temp_file in temp_dir.glob(pattern):
            if temp_file.is_file():
                try:
                    temp_file.unlink()
                    cleaned_count += 1
                    logger.debug(f"Cleaned up temp file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_file}: {e}")
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {e}")
    
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} temporary files")
    
    return cleaned_count


def get_project_root() -> Path:
    """
    Get the project root directory path.
    
    Returns:
        Path object pointing to project root
    """
    current_file = Path(__file__).resolve()
    return current_file.parent


def get_samples_dir() -> Path:
    """
    Get the samples directory path.
    
    Returns:
        Path object pointing to samples directory
    """
    return get_project_root() / "samples"


def get_output_dir() -> Path:
    """
    Get or create the output directory for generated files.
    
    Returns:
        Path object pointing to output directory
    """
    output_dir = get_project_root() / "output"
    ensure_directory(str(output_dir))
    return output_dir


def normalize_file_path(file_path: str) -> str:
    """
    Normalize file path for cross-platform compatibility.
    
    Args:
        file_path: Original file path
        
    Returns:
        Normalized file path
    """
    if not file_path:
        return ""
    
    # Convert to Path object and resolve
    path = Path(file_path).resolve()
    
    # Return as string with forward slashes (works on all platforms)
    return str(path).replace('\\', '/')


def validate_file_type(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Validate if file has an allowed extension.
    
    Args:
        file_path: Path to file
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])
        
    Returns:
        True if file type is allowed
    """
    if not file_path:
        return False
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB, or 0 if file doesn't exist
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract potential skills from resume text using pattern matching.
    
    Args:
        text: Resume text to analyze
        
    Returns:
        List of identified skills
    """
    if not text:
        return []
    
    # Common technical skills patterns
    skill_patterns = [
        # Programming languages
        r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|Scala|R|MATLAB)\b',
        # Web technologies
        r'\b(React|Angular|Vue\.js|Node\.js|Django|Flask|Laravel|Spring|Express|jQuery|Bootstrap)\b',
        # Databases
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB)\b',
        # Cloud platforms
        r'\b(AWS|Azure|Google Cloud|GCP|Heroku|DigitalOcean|Kubernetes|Docker)\b',
        # Tools and frameworks
        r'\b(Git|Jenkins|Jira|Confluence|Slack|Trello|Figma|Photoshop|Illustrator)\b',
        # Methodologies
        r'\b(Agile|Scrum|Kanban|DevOps|CI/CD|TDD|BDD|Microservices|REST|GraphQL)\b'
    ]
    
    skills = set()
    text_upper = text.upper()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update(match.strip() for match in matches if match.strip())
    
    # Additional manual skill extraction for common abbreviations
    manual_skills = {
        'ML': 'Machine Learning',
        'AI': 'Artificial Intelligence',
        'NLP': 'Natural Language Processing',
        'API': 'API Development',
        'UI/UX': 'UI/UX Design',
        'SEO': 'Search Engine Optimization',
        'CRM': 'Customer Relationship Management'
    }
    
    for abbrev, full_name in manual_skills.items():
        if abbrev in text_upper:
            skills.add(full_name)
    
    return sorted(list(skills))


def format_text_for_display(text: str, max_length: int = 1000) -> str:
    """
    Format text for display in UI with length limiting.
    
    Args:
        text: Text to format
        max_length: Maximum length before truncation
        
    Returns:
        Formatted text suitable for display
    """
    if not text:
        return "No text available"
    
    # Clean the text
    formatted_text = clean_text(text)
    
    # Truncate if too long
    if len(formatted_text) > max_length:
        formatted_text = formatted_text[:max_length] + "..."
    
    return formatted_text


def create_backup_file(file_path: str) -> Optional[str]:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to file to backup
        
    Returns:
        Path to backup file, or None if backup failed
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return None


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse various date string formats commonly found in resumes.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Parsed datetime object or None if parsing failed
    """
    if not date_str:
        return None
    
    # Common date formats in resumes
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %Y',
        '%b %Y',
        '%Y',
        '%m-%Y',
        '%Y-%m'
    ]
    
    # Clean the date string
    date_str = date_str.strip().replace('Present', '').replace('Current', '')
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None