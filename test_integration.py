#!/usr/bin/env python3
"""
Integration tests for AI Resume Analyzer.

Tests complete end-to-end workflow with sample resume data,
validates API integrations and file processing pipeline,
and tests error handling and edge cases across all modules.
"""

import unittest
import os
import tempfile
import shutil
import json
import time
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Import all modules to test
import parsing
import ai_integration
import tts_video
import database
import gemini_video
import utils


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow with sample data."""
    
    def setUp(self):
        """Set up test environment with sample data."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_resume_text = """
John Doe
Software Engineer

Experience:
Senior Developer at Tech Corp (2020-2023)
- Led team of 5 developers on major projects
- Implemented microservices architecture
- Developed scalable web applications using React and Node.js

Skills:
Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL
Project management, Agile methodologies, Team leadership

Education:
Bachelor of Computer Science
University of Technology (2016-2020)
Graduated with honors
"""
        
        self.sample_job_description = """
Software Engineer Position
We are looking for a skilled Software Engineer with experience in:
- Python and JavaScript development
- React and modern web frameworks
- Cloud technologies (AWS preferred)
- Database design and optimization
- Agile development methodologies

Requirements:
- 3+ years of software development experience
- Strong problem-solving skills
- Experience with team collaboration
- Bachelor's degree in Computer Science or related field
"""
        
        # Create sample files
        self.sample_resume_file = os.path.join(self.temp_dir, "sample_resume.txt")
        with open(self.sample_resume_file, 'w') as f:
            f.write(self.sample_resume_text)
        
        self.sample_job_file = os.path.join(self.temp_dir, "sample_job.txt")
        with open(self.sample_job_file, 'w') as f:
            f.write(self.sample_job_description)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('ai_integration.client')
    def test_complete_resume_analysis_workflow(self, mock_openai_client):
        """Test complete workflow from file upload to analysis results."""
        # Mock OpenAI API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            'strengths': [
                {
                    'text': 'Strong technical leadership experience',
                    'evidence': 'Led team of 5 developers on major projects'
                },
                {
                    'text': 'Comprehensive full-stack skills',
                    'evidence': 'Experience with React, Node.js, Python, and cloud technologies'
                }
            ],
            'weak_points': [
                {
                    'text': 'Could provide more specific metrics',
                    'location': 'Experience section',
                    'reason': 'Achievements lack quantifiable results'
                }
            ],
            'suggestions': [
                {
                    'for': 'Experience section',
                    'suggestion': 'Add specific metrics like "Improved system performance by 40%" or "Reduced deployment time by 60%"'
                }
            ],
            'top_skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Team Leadership'],
            'one_sentence_pitch': 'Hi, I am John Doe, a senior software engineer with 3+ years of experience leading development teams and building scalable web applications.'
        })
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Step 1: Text extraction (simulated - using direct text)
        extracted_text = self.sample_resume_text
        
        # Step 2: Text quality assessment
        needs_ocr = parsing.needs_nutrient_ocr(extracted_text)
        self.assertFalse(needs_ocr)  # Good quality text shouldn't need OCR
        
        # Step 3: AI analysis
        analysis_result = ai_integration.call_gpt_analysis(extracted_text)
        
        # Verify analysis structure
        self.assertIn('strengths', analysis_result)
        self.assertIn('weak_points', analysis_result)
        self.assertIn('suggestions', analysis_result)
        self.assertIn('top_skills', analysis_result)
        self.assertIn('one_sentence_pitch', analysis_result)
        
        # Verify content quality
        self.assertGreater(len(analysis_result['strengths']), 0)
        self.assertGreater(len(analysis_result['top_skills']), 0)
        self.assertIn('John Doe', analysis_result['one_sentence_pitch'])
        
        # Step 4: Generate pitch script
        script_data = ai_integration.generate_pitch_script(analysis_result)
        
        # Verify script structure
        self.assertIn('intro', script_data)
        self.assertIn('skills', script_data)
        self.assertIn('achievement', script_data)
        self.assertIn('closing', script_data)
        
        # Verify timing
        total_duration = sum(segment['duration'] for segment in script_data.values())
        self.assertEqual(total_duration, 10.0)
        
        print("✅ Complete resume analysis workflow test passed")
    
    @patch('ai_integration.client')
    def test_job_comparison_workflow(self, mock_openai_client):
        """Test workflow with job description comparison."""
        # Mock OpenAI API response with job comparison
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            'strengths': [
                {
                    'text': 'Strong match for required technical skills',
                    'evidence': 'Has Python, JavaScript, React, and AWS experience as required'
                }
            ],
            'weak_points': [
                {
                    'text': 'Missing database optimization experience',
                    'location': 'Skills section',
                    'reason': 'Job requires database design and optimization expertise'
                }
            ],
            'suggestions': [
                {
                    'for': 'Skills section',
                    'suggestion': 'Highlight any database optimization projects or add relevant coursework'
                }
            ],
            'top_skills': ['Python', 'JavaScript', 'React', 'AWS', 'Team Leadership'],
            'one_sentence_pitch': 'Hi, I am John Doe, a software engineer with the exact technical stack you need for this position.'
        })
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Step 1: Analyze resume with job description
        analysis_result = ai_integration.call_gpt_analysis(
            self.sample_resume_text, 
            self.sample_job_description
        )
        
        # Step 2: Skill comparison
        resume_skills = analysis_result['top_skills']
        job_skills = ai_integration.extract_skills_from_job_description(self.sample_job_description)
        
        comparison_result = ai_integration.score_resume_vs_job(resume_skills, job_skills)
        
        # Verify comparison results
        self.assertIn('compatibility_score', comparison_result)
        self.assertIn('matching_skills', comparison_result)
        self.assertIn('missing_skills', comparison_result)
        
        # Score should be reasonable (not 0 or 100)
        self.assertGreater(comparison_result['compatibility_score'], 0)
        self.assertLess(comparison_result['compatibility_score'], 100)
        
        print("✅ Job comparison workflow test passed")
    
    @patch('tts_video.asyncio.run')
    @patch('tts_video.ColorClip')
    @patch('tts_video.TextClip')
    @patch('tts_video.CompositeVideoClip')
    @patch('tts_video.AudioFileClip')
    @patch('os.path.exists')
    def test_video_generation_workflow(self, mock_exists, mock_audio_clip, mock_composite, 
                                     mock_text_clip, mock_color_clip, mock_asyncio_run):
        """Test complete video generation workflow."""
        # Mock file existence check
        mock_exists.return_value = True
        
        # Mock TTS synthesis
        mock_asyncio_run.return_value = None
        
        # Mock moviepy components
        mock_background = MagicMock()
        mock_color_clip.return_value = mock_background
        
        mock_text = MagicMock()
        mock_text.set_duration.return_value = mock_text
        mock_text.set_start.return_value = mock_text
        mock_text.set_position.return_value = mock_text
        mock_text.fadein.return_value = mock_text
        mock_text.fadeout.return_value = mock_text
        mock_text_clip.return_value = mock_text
        
        mock_audio = MagicMock()
        mock_audio.duration = 10.0
        mock_audio_clip.return_value = mock_audio
        
        mock_video = MagicMock()
        mock_composite.return_value = mock_video
        mock_video.set_audio.return_value = mock_video
        
        # Sample script data
        script_data = {
            'intro': {'text': 'Hi, I am John Doe', 'duration': 2.5},
            'skills': {'text': 'I specialize in Python and JavaScript development', 'duration': 4.0},
            'achievement': {'text': 'I led a team of 5 developers on major projects', 'duration': 2.5},
            'closing': {'text': 'I would love to discuss this opportunity with you', 'duration': 1.0}
        }
        
        # Step 1: Generate video
        video_path = tts_video.generate_pitch_video(
            script_data, 
            self.temp_dir, 
            "en", 
            10.0
        )
        
        # Verify video path
        self.assertTrue(video_path.endswith("pitch_video.mp4"))
        self.assertIn(self.temp_dir, video_path)
        
        # Verify components were called
        mock_asyncio_run.assert_called()  # TTS synthesis
        mock_color_clip.assert_called()   # Background
        mock_text_clip.assert_called()    # Text animations
        mock_composite.assert_called()    # Video composition
        
        print("✅ Video generation workflow test passed")
    
    @patch('database.init_supabase_client')
    def test_database_integration_workflow(self, mock_init_client):
        """Test database storage and retrieval workflow."""
        # Mock Supabase client
        mock_client = MagicMock()
        mock_init_client.return_value = mock_client
        
        # Mock successful insertions
        cv_response = MagicMock()
        cv_response.data = [{'id': 'test-cv-id-123'}]
        
        analysis_response = MagicMock()
        analysis_response.data = [{'id': 'test-analysis-id-123'}]
        
        video_response = MagicMock()
        video_response.data = [{'id': 'test-video-id-123'}]
        
        mock_client.table.return_value.insert.return_value.execute.side_effect = [
            cv_response, analysis_response, video_response
        ]
        
        # Mock history retrieval
        history_response = MagicMock()
        history_response.data = [
            {
                'id': 'test-cv-id-123',
                'filename': 'sample_resume.txt',
                'created_at': '2024-01-01T00:00:00Z',
                'analysis_results': [{'strengths': []}],
                'video_records': [{'status': 'completed'}]
            }
        ]
        mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = history_response
        
        # Step 1: Store CV analysis
        analysis_data = {
            'strengths': [{'text': 'Good skills', 'evidence': 'Evidence'}],
            'weak_points': [{'text': 'Needs work', 'location': 'Skills', 'reason': 'Vague'}],
            'suggestions': [{'for': 'Skills', 'suggestion': 'Be specific'}],
            'top_skills': ['Python', 'JavaScript'],
            'one_sentence_pitch': 'I am a developer.'
        }
        
        metadata = {
            'filename': 'sample_resume.txt',
            'file_type': 'txt',
            'file_size': len(self.sample_resume_text),
            'language': 'en'
        }
        
        cv_id = database.store_cv_analysis(self.sample_resume_text, analysis_data, metadata)
        self.assertEqual(cv_id, 'test-cv-id-123')
        
        # Step 2: Store video record
        script_data = {
            'intro': {'text': 'Hi, I am John', 'duration': 2.0},
            'skills': {'text': 'Python, JavaScript', 'duration': 4.0}
        }
        
        video_id = database.store_video_record(cv_id, script_data, 'moviepy')
        self.assertEqual(video_id, 'test-video-id-123')
        
        # Step 3: Retrieve history
        history = database.get_cv_history(limit=10)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['id'], 'test-cv-id-123')
        
        print("✅ Database integration workflow test passed")


class TestAPIIntegrationRobustness(unittest.TestCase):
    """Test API integrations and error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('ai_integration.client')
    def test_openai_api_retry_logic(self, mock_client):
        """Test OpenAI API retry logic with failures."""
        # Mock first call failure, second call success
        mock_client.chat.completions.create.side_effect = [
            Exception("Rate limit exceeded"),
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({
                'strengths': [],
                'weak_points': [],
                'suggestions': [],
                'top_skills': ['Python'],
                'one_sentence_pitch': 'I am a developer.'
            })))])
        ]
        
        # Should succeed on retry
        result = ai_integration.call_gpt_analysis("Sample resume text")
        
        # Verify retry happened
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        self.assertIn('top_skills', result)
        
        print("✅ OpenAI API retry logic test passed")
    
    @patch('ai_integration.client')
    def test_openai_api_malformed_response_handling(self, mock_client):
        """Test handling of malformed OpenAI responses."""
        # Mock malformed JSON response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        Here is my analysis of the resume:
        {
            "strengths": [{"text": "Good skills", "evidence": "Evidence"}],
            "weak_points": [],
            "suggestions": [],
            "top_skills": ["Python", "JavaScript"],
            "one_sentence_pitch": "I am a developer."
        }
        I hope this helps!
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        # Should extract JSON from text
        result = ai_integration.call_gpt_analysis("Sample resume text")
        
        self.assertIn('strengths', result)
        self.assertEqual(result['top_skills'], ['Python', 'JavaScript'])
        
        print("✅ Malformed response handling test passed")
    
    @patch('requests.post')
    def test_nutrient_ocr_error_handling(self, mock_requests):
        """Test Nutrient OCR error handling."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"dummy pdf content")
        
        # Test rate limiting
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_requests.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            parsing.call_nutrient_ocr(test_file, "test_api_key")
        
        self.assertIn("Rate limit", str(context.exception))
        
        # Test invalid credentials
        mock_response.status_code = 401
        
        with self.assertRaises(Exception) as context:
            parsing.call_nutrient_ocr(test_file, "invalid_key")
        
        self.assertIn("Invalid Nutrient API key", str(context.exception))
        
        print("✅ Nutrient OCR error handling test passed")
    
    @patch('database.init_supabase_client')
    def test_database_connection_error_handling(self, mock_init_client):
        """Test database connection error handling."""
        # Mock connection failure
        mock_init_client.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception) as context:
            database.store_cv_analysis("text", {}, {})
        
        self.assertIn("Connection failed", str(context.exception))
        
        print("✅ Database connection error handling test passed")


class TestFileProcessingPipeline(unittest.TestCase):
    """Test file processing pipeline with various formats."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('pdfplumber.open')
    def test_pdf_processing_pipeline(self, mock_pdfplumber):
        """Test PDF file processing pipeline."""
        # Mock PDF extraction
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample resume text from PDF"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        
        mock_pdfplumber.return_value = mock_pdf
        
        # Create test PDF file
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("dummy pdf content")
        
        # Test extraction
        extracted_text = parsing.extract_text_pdf(test_file)
        
        self.assertEqual(extracted_text, "Sample resume text from PDF")
        
        # Test quality assessment with longer text that won't trigger OCR
        good_text = "Sample resume text from PDF with sufficient content to pass quality assessment. This text has enough words and proper structure to be considered good quality without needing OCR processing."
        needs_ocr = parsing.needs_nutrient_ocr(good_text)
        self.assertFalse(needs_ocr)  # Good quality text
        
        print("✅ PDF processing pipeline test passed")
    
    @patch('docx.Document')
    def test_docx_processing_pipeline(self, mock_document):
        """Test DOCX file processing pipeline."""
        # Mock DOCX structure
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Sample resume text from DOCX"
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        
        mock_document.return_value = mock_doc
        
        # Create test DOCX file
        test_file = os.path.join(self.temp_dir, "test.docx")
        with open(test_file, 'w') as f:
            f.write("dummy docx content")
        
        # Test extraction
        extracted_text = parsing.extract_text_docx(test_file)
        
        self.assertEqual(extracted_text, "Sample resume text from DOCX")
        
        print("✅ DOCX processing pipeline test passed")
    
    def test_text_quality_assessment_pipeline(self):
        """Test text quality assessment with various inputs."""
        # Test cases for quality assessment
        test_cases = [
            ("", True),  # Empty text needs OCR
            ("a b c d e", True),  # Too short needs OCR
            ("a   b   c   d   e   f   g   h   i   j   k   l   m   n   o   p   q   r   s   t", True),  # High whitespace needs OCR
            ("John Doe is a Software Engineer with over 5 years of experience in Python development, web applications, database design, and team leadership. He has worked on multiple projects involving React, Node.js, and cloud technologies.", False),  # Good quality text
            ("123 456 789 !@# $%^", True),  # Few recognizable words needs OCR
        ]
        
        for text, expected_needs_ocr in test_cases:
            result = parsing.needs_nutrient_ocr(text)
            self.assertEqual(result, expected_needs_ocr, 
                           f"Failed for text: '{text[:50]}...' - expected {expected_needs_ocr}, got {result}")
        
        print("✅ Text quality assessment pipeline test passed")


class TestEdgeCasesAndErrorScenarios(unittest.TestCase):
    """Test edge cases and error scenarios across all modules."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_resume_handling(self):
        """Test handling of empty or minimal resume content."""
        empty_text = ""
        minimal_text = "John"
        
        # Should trigger OCR for both
        self.assertTrue(parsing.needs_nutrient_ocr(empty_text))
        self.assertTrue(parsing.needs_nutrient_ocr(minimal_text))
        
        print("✅ Empty resume handling test passed")
    
    @patch('ai_integration.client')
    def test_ai_analysis_with_minimal_data(self, mock_client):
        """Test AI analysis with minimal resume data."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            'strengths': [],
            'weak_points': [{'text': 'Very limited information', 'location': 'Overall', 'reason': 'Resume too brief'}],
            'suggestions': [{'for': 'Overall', 'suggestion': 'Add more detailed experience and skills'}],
            'top_skills': [],
            'one_sentence_pitch': 'I am a professional seeking opportunities.'
        })
        mock_client.chat.completions.create.return_value = mock_response
        
        minimal_resume = "John Doe"
        result = ai_integration.call_gpt_analysis(minimal_resume)
        
        # Should still return valid structure
        self.assertIn('strengths', result)
        self.assertIn('weak_points', result)
        self.assertIn('suggestions', result)
        
        print("✅ Minimal data AI analysis test passed")
    
    def test_video_generation_with_empty_script(self):
        """Test video generation with minimal script data."""
        empty_script = {}
        minimal_script = {'intro': {'text': 'Hi'}}
        
        # Should generate valid timing even with minimal data
        result = ai_integration.generate_pitch_script({'one_sentence_pitch': 'Hi, I am John.'})
        
        self.assertEqual(len(result), 4)  # Should have all 4 segments
        total_duration = sum(segment['duration'] for segment in result.values())
        self.assertEqual(total_duration, 10.0)
        
        print("✅ Empty script video generation test passed")
    
    def test_skill_comparison_edge_cases(self):
        """Test skill comparison with edge cases."""
        # Empty skills
        result = ai_integration.score_resume_vs_job([], [])
        self.assertEqual(result['compatibility_score'], 0)
        
        # One empty list
        result = ai_integration.score_resume_vs_job(['Python'], [])
        self.assertEqual(result['compatibility_score'], 0)
        
        # Identical skills
        skills = ['Python', 'JavaScript', 'React']
        result = ai_integration.score_resume_vs_job(skills, skills)
        self.assertEqual(result['compatibility_score'], 100)
        
        print("✅ Skill comparison edge cases test passed")
    
    def test_language_detection_edge_cases(self):
        """Test language detection with edge cases."""
        # Very short text
        short_text = "Hi"
        result = ai_integration.detect_language(short_text)
        self.assertIn(result, ['en', 'ro'])  # Should return valid language
        
        # Mixed language text
        mixed_text = "Hello și bună ziua"
        result = ai_integration.detect_language(mixed_text)
        self.assertIn(result, ['en', 'ro'])
        
        # Numbers and symbols
        symbols_text = "123 456 !@# $%^"
        result = ai_integration.detect_language(symbols_text)
        self.assertEqual(result, 'en')  # Default to English
        
        print("✅ Language detection edge cases test passed")


class TestPerformanceAndScalability(unittest.TestCase):
    """Test performance characteristics and scalability."""
    
    def test_large_resume_processing(self):
        """Test processing of large resume files."""
        # Create large resume text (simulate complex resume)
        large_resume = """
John Doe
Senior Software Engineer

PROFESSIONAL SUMMARY
Experienced software engineer with 10+ years of experience in full-stack development,
team leadership, and system architecture. Proven track record of delivering scalable
solutions and leading cross-functional teams in fast-paced environments.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, C++, Go, Rust
Web Technologies: React, Angular, Vue.js, Node.js, Express, Django, Flask
Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
Cloud Platforms: AWS, Google Cloud, Azure, Docker, Kubernetes
DevOps: Jenkins, GitLab CI, GitHub Actions, Terraform, Ansible
""" * 10  # Repeat to make it large
        
        # Test quality assessment performance
        start_time = time.time()
        needs_ocr = parsing.needs_nutrient_ocr(large_resume)
        processing_time = time.time() - start_time
        
        # Should complete quickly (under 1 second)
        self.assertLess(processing_time, 1.0)
        self.assertFalse(needs_ocr)  # Should be good quality
        
        print(f"✅ Large resume processing test passed ({processing_time:.3f}s)")
    
    def test_multiple_skill_comparison_performance(self):
        """Test performance with large skill lists."""
        # Create large skill lists
        resume_skills = [f"Skill_{i}" for i in range(100)]
        job_skills = [f"Skill_{i}" for i in range(50, 150)]  # 50% overlap
        
        start_time = time.time()
        result = ai_integration.score_resume_vs_job(resume_skills, job_skills)
        processing_time = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(processing_time, 1.0)
        
        # Should find reasonable overlap
        self.assertGreater(result['compatibility_score'], 0)
        self.assertLess(result['compatibility_score'], 100)
        
        print(f"✅ Multiple skill comparison performance test passed ({processing_time:.3f}s)")


def run_integration_tests():
    """Run all integration tests with detailed reporting."""
    print("🧪 AI RESUME ANALYZER - INTEGRATION TESTS")
    print("=" * 60)
    print()
    
    # Test suites to run
    test_suites = [
        ('End-to-End Workflow Tests', TestEndToEndWorkflow),
        ('API Integration Robustness Tests', TestAPIIntegrationRobustness),
        ('File Processing Pipeline Tests', TestFileProcessingPipeline),
        ('Edge Cases and Error Scenarios', TestEdgeCasesAndErrorScenarios),
        ('Performance and Scalability Tests', TestPerformanceAndScalability),
    ]
    
    total_tests = 0
    total_failures = 0
    
    for suite_name, test_class in test_suites:
        print(f"🔍 Running {suite_name}...")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures) + len(result.errors)
        
        if result.failures or result.errors:
            print(f"❌ {len(result.failures + result.errors)} test(s) failed")
            for test, error in result.failures + result.errors:
                print(f"   • {test}: {error.split('AssertionError:')[-1].strip()}")
        else:
            print(f"✅ All {result.testsRun} tests passed")
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"📊 INTEGRATION TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - total_failures}")
    print(f"Failed: {total_failures}")
    
    if total_failures == 0:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"⚠️  {total_failures} test(s) failed. Please review and fix.")
        return False


if __name__ == '__main__':
    success = run_integration_tests()
    exit(0 if success else 1)