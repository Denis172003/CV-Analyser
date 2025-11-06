"""
Unit tests for AI integration module.

Tests cover GPT API integration, language detection,
skill comparison, and pitch script generation.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from ai_integration import (
    detect_language,
    generate_pitch_script,
    score_resume_vs_job,
    extract_skills_from_job_description,
    _parse_and_validate_response,
    call_gpt_analysis
)


class TestLanguageDetection(unittest.TestCase):
    """Test language detection functionality."""
    
    def test_detect_english(self):
        """Test detection of English text."""
        english_text = "I am a software developer with experience in Python and JavaScript."
        result = detect_language(english_text)
        self.assertEqual(result, 'en')
    
    def test_detect_romanian(self):
        """Test detection of Romanian text."""
        romanian_text = "Sunt dezvoltator software cu experiență în Python și JavaScript pentru echipă."
        result = detect_language(romanian_text)
        self.assertEqual(result, 'ro')
    
    def test_detect_mixed_content(self):
        """Test detection with mixed content."""
        mixed_text = "I work cu echipă și am experiență în development."
        result = detect_language(mixed_text)
        self.assertEqual(result, 'ro')  # Should detect Romanian due to multiple indicators


class TestPitchScriptGeneration(unittest.TestCase):
    """Test pitch script generation functionality."""
    
    def test_generate_basic_script(self):
        """Test basic pitch script generation."""
        analysis_data = {
            'one_sentence_pitch': "Hi, I'm John Smith, a Python developer.",
            'top_skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'],
            'strengths': [
                {
                    'text': 'Strong technical skills',
                    'evidence': 'Led team of 5 developers on major project'
                }
            ]
        }
        
        result = generate_pitch_script(analysis_data)
        
        # Check structure
        self.assertIn('intro', result)
        self.assertIn('skills', result)
        self.assertIn('achievement', result)
        self.assertIn('closing', result)
        
        # Check timing adds up to 10 seconds
        total_duration = sum(segment['duration'] for segment in result.values())
        self.assertEqual(total_duration, 10.0)
        
        # Check content
        self.assertIn('John Smith', result['intro']['text'])
        self.assertIn('Python', result['skills']['text'])
    
    def test_generate_script_no_name(self):
        """Test script generation when no name is found."""
        analysis_data = {
            'one_sentence_pitch': "I am a developer with great skills.",
            'top_skills': ['Python', 'JavaScript'],
            'strengths': []
        }
        
        result = generate_pitch_script(analysis_data)
        self.assertIn('professional', result['intro']['text'])
    
    def test_generate_script_empty_data(self):
        """Test script generation with minimal data."""
        analysis_data = {}
        
        result = generate_pitch_script(analysis_data)
        
        # Should still generate valid structure
        self.assertEqual(len(result), 4)
        total_duration = sum(segment['duration'] for segment in result.values())
        self.assertEqual(total_duration, 10.0)


class TestSkillComparison(unittest.TestCase):
    """Test skill comparison and scoring functionality."""
    
    def test_exact_skill_matches(self):
        """Test exact skill matching."""
        resume_skills = ['Python', 'JavaScript', 'React', 'SQL']
        job_skills = ['Python', 'JavaScript', 'Node.js']
        
        result = score_resume_vs_job(resume_skills, job_skills)
        
        self.assertEqual(result['compatibility_score'], 66)  # 2/3 = 66%
        self.assertEqual(len(result['matching_skills']), 2)
        self.assertEqual(len(result['missing_skills']), 1)
        self.assertIn('Node.js', result['missing_skills'])
    
    def test_partial_skill_matches(self):
        """Test partial skill matching."""
        resume_skills = ['Python Programming', 'JavaScript Development']
        job_skills = ['Python', 'JavaScript', 'Java']
        
        result = score_resume_vs_job(resume_skills, job_skills)
        
        # Should find partial matches for Python and JavaScript
        self.assertGreater(result['compatibility_score'], 0)
        self.assertEqual(len(result['missing_skills']), 1)
        self.assertIn('Java', result['missing_skills'])
    
    def test_no_skill_matches(self):
        """Test when no skills match."""
        resume_skills = ['Python', 'JavaScript']
        job_skills = ['Java', 'C++']
        
        result = score_resume_vs_job(resume_skills, job_skills)
        
        self.assertEqual(result['compatibility_score'], 0)
        self.assertEqual(len(result['matching_skills']), 0)
        self.assertEqual(len(result['missing_skills']), 2)
    
    def test_empty_skills(self):
        """Test with empty skill lists."""
        result = score_resume_vs_job([], ['Python', 'JavaScript'])
        
        self.assertEqual(result['compatibility_score'], 0)
        self.assertEqual(len(result['matching_skills']), 0)
        self.assertEqual(len(result['missing_skills']), 2)


class TestSkillExtraction(unittest.TestCase):
    """Test skill extraction from job descriptions."""
    
    def test_extract_technical_skills(self):
        """Test extraction of technical skills."""
        job_text = """
        We are looking for a Python developer with experience in React and Node.js.
        Knowledge of SQL and MongoDB is required. AWS experience is a plus.
        """
        
        result = extract_skills_from_job_description(job_text)
        
        expected_skills = ['python', 'react', 'node.js', 'sql', 'mongodb', 'aws']
        for skill in expected_skills:
            self.assertIn(skill, result)
    
    def test_extract_soft_skills(self):
        """Test extraction of soft skills."""
        job_text = """
        Looking for someone with project management experience and leadership skills.
        Must have excellent communication abilities and agile methodology knowledge.
        """
        
        result = extract_skills_from_job_description(job_text)
        
        expected_skills = ['project management', 'agile']
        for skill in expected_skills:
            self.assertIn(skill, result)


class TestResponseParsing(unittest.TestCase):
    """Test GPT response parsing and validation."""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        valid_response = json.dumps({
            'strengths': [{'text': 'Good skills', 'evidence': 'Evidence here'}],
            'weak_points': [{'text': 'Needs improvement', 'location': 'Skills', 'reason': 'Vague'}],
            'suggestions': [{'for': 'Skills', 'suggestion': 'Be more specific'}],
            'top_skills': ['Python', 'JavaScript'],
            'one_sentence_pitch': 'I am a developer.'
        })
        
        result = _parse_and_validate_response(valid_response)
        
        self.assertIn('strengths', result)
        self.assertIn('weak_points', result)
        self.assertIn('suggestions', result)
        self.assertIn('top_skills', result)
        self.assertIn('one_sentence_pitch', result)
    
    def test_parse_json_with_extra_text(self):
        """Test parsing JSON embedded in text."""
        response_with_text = '''Here is the analysis:
        {
            "strengths": [],
            "weak_points": [],
            "suggestions": [],
            "top_skills": ["Python"],
            "one_sentence_pitch": "I am a developer."
        }
        Hope this helps!'''
        
        result = _parse_and_validate_response(response_with_text)
        self.assertEqual(result['top_skills'], ['Python'])
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        invalid_response = "This is not JSON at all"
        
        with self.assertRaises(Exception):
            _parse_and_validate_response(invalid_response)
    
    def test_parse_missing_fields(self):
        """Test handling of missing required fields."""
        incomplete_response = json.dumps({
            'strengths': [],
            'weak_points': []
            # Missing other required fields
        })
        
        with self.assertRaises(Exception):
            _parse_and_validate_response(incomplete_response)


class TestGPTIntegration(unittest.TestCase):
    """Test GPT API integration with mocking."""
    
    @patch('ai_integration.client')
    def test_successful_gpt_call(self, mock_client):
        """Test successful GPT API call."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            'strengths': [{'text': 'Good skills', 'evidence': 'Evidence'}],
            'weak_points': [{'text': 'Needs work', 'location': 'Skills', 'reason': 'Vague'}],
            'suggestions': [{'for': 'Skills', 'suggestion': 'Be specific'}],
            'top_skills': ['Python', 'JavaScript'],
            'one_sentence_pitch': 'I am a Python developer.'
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        result = call_gpt_analysis("Sample resume text")
        
        self.assertIn('strengths', result)
        self.assertIn('top_skills', result)
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('ai_integration.client')
    def test_gpt_call_with_job_description(self, mock_client):
        """Test GPT call with job description."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            'strengths': [],
            'weak_points': [],
            'suggestions': [],
            'top_skills': ['Python'],
            'one_sentence_pitch': 'I am a developer.'
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        call_gpt_analysis("Resume text", "Job description text")
        
        # Check that job description was included in the call
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]['messages'][1]['content']
        self.assertIn('Job Description:', user_message)


if __name__ == '__main__':
    unittest.main()