"""
Unit tests for parsing.py module.

Tests text extraction functionality for PDF and DOCX files,
text quality assessment, and Nutrient OCR integration.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
import json

from parsing import extract_text_pdf, extract_text_docx, needs_nutrient_ocr, call_nutrient_ocr


class TestTextExtraction(unittest.TestCase):
    """Test cases for text extraction functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_text = "John Doe\nSoftware Engineer\nExperience: 5 years\nSkills: Python, JavaScript"
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pdfplumber.open')
    def test_extract_text_pdf_success(self, mock_pdfplumber_open):
        """Test successful PDF text extraction."""
        # Mock PDF structure
        mock_page = MagicMock()
        mock_page.extract_text.return_value = self.sample_text
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        
        mock_pdfplumber_open.return_value = mock_pdf
        
        # Test extraction
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("dummy pdf content")
            
        result = extract_text_pdf(test_file)
        
        self.assertEqual(result, self.sample_text)
        mock_pdfplumber_open.assert_called_once_with(test_file)

    def test_extract_text_pdf_file_not_found(self):
        """Test PDF extraction with non-existent file."""
        with self.assertRaises(Exception) as context:
            extract_text_pdf("nonexistent.pdf")
        self.assertIn("PDF file not found", str(context.exception))

    @patch('pdfplumber.open')
    def test_extract_text_pdf_empty_pages(self, mock_pdfplumber_open):
        """Test PDF extraction with no pages."""
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        
        mock_pdfplumber_open.return_value = mock_pdf
        
        test_file = os.path.join(self.temp_dir, "empty.pdf")
        with open(test_file, 'w') as f:
            f.write("dummy")
            
        with self.assertRaises(Exception) as context:
            extract_text_pdf(test_file)
        self.assertIn("PDF file contains no pages", str(context.exception))

    @patch('docx.Document')
    def test_extract_text_docx_success(self, mock_document_class):
        """Test successful DOCX text extraction."""
        # Mock document structure
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "John Doe"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Software Engineer"
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_doc.tables = []
        
        mock_document_class.return_value = mock_doc
        
        # Test extraction
        test_file = os.path.join(self.temp_dir, "test.docx")
        with open(test_file, 'w') as f:
            f.write("dummy docx content")
            
        result = extract_text_docx(test_file)
        
        self.assertEqual(result, "John Doe\nSoftware Engineer")
        mock_document_class.assert_called_once_with(test_file)

    def test_extract_text_docx_file_not_found(self):
        """Test DOCX extraction with non-existent file."""
        with self.assertRaises(Exception) as context:
            extract_text_docx("nonexistent.docx")
        self.assertIn("DOCX file not found", str(context.exception))

    @patch('docx.Document')
    def test_extract_text_docx_with_table(self, mock_document_class):
        """Test DOCX extraction with table content."""
        # Mock table structure
        mock_cell1 = MagicMock()
        mock_cell1.text = "Skill"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Level"
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc.tables = [mock_table]
        
        mock_document_class.return_value = mock_doc
        
        test_file = os.path.join(self.temp_dir, "test_table.docx")
        with open(test_file, 'w') as f:
            f.write("dummy")
            
        result = extract_text_docx(test_file)
        
        self.assertEqual(result, "Skill | Level")


class TestTextQualityAssessment(unittest.TestCase):
    """Test cases for text quality assessment."""
    
    def test_needs_nutrient_ocr_short_text(self):
        """Test quality assessment with very short text."""
        short_text = "Hi"
        self.assertTrue(needs_nutrient_ocr(short_text))
    
    def test_needs_nutrient_ocr_empty_text(self):
        """Test quality assessment with empty text."""
        self.assertTrue(needs_nutrient_ocr(""))
        self.assertTrue(needs_nutrient_ocr("   "))
    
    def test_needs_nutrient_ocr_high_whitespace(self):
        """Test quality assessment with excessive whitespace."""
        whitespace_text = "a   b   c   d   e   f   g   h   i   j   k   l   m   n   o   p   q   r   s   t"
        self.assertTrue(needs_nutrient_ocr(whitespace_text))
    
    def test_needs_nutrient_ocr_many_short_lines(self):
        """Test quality assessment with many short lines (multi-column indicator)."""
        short_lines = "\n".join(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"] * 3)
        self.assertTrue(needs_nutrient_ocr(short_lines))
    
    def test_needs_nutrient_ocr_formatting_artifacts(self):
        """Test quality assessment with formatting artifacts."""
        artifact_text = "Resume... John Doe___ Software Engineer   Experience\n\n\nSkills..." * 5
        self.assertTrue(needs_nutrient_ocr(artifact_text))
    
    def test_needs_nutrient_ocr_good_quality_text(self):
        """Test quality assessment with good quality text."""
        good_text = """John Doe
Software Engineer with 5 years of experience in full-stack development.

Experience:
Senior Developer at Tech Corp (2020-2023)
Led team of 5 developers on major projects and implemented microservices architecture.
Developed scalable web applications using modern frameworks and cloud technologies.

Skills:
Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes
Database design and optimization, API development, Agile methodologies

Education:
Bachelor of Computer Science
University of Technology (2016-2020)
Graduated with honors, relevant coursework in software engineering and algorithms."""
        self.assertFalse(needs_nutrient_ocr(good_text))
    
    def test_needs_nutrient_ocr_few_words(self):
        """Test quality assessment with too few recognizable words."""
        few_words_text = "123 456 789 !@# $%^ &*( )_+ {}[]"
        self.assertTrue(needs_nutrient_ocr(few_words_text))


class TestNutrientOCR(unittest.TestCase):
    """Test cases for Nutrient OCR integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = "test_nutrient_api_key"
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('requests.post')
    def test_call_nutrient_ocr_success(self, mock_requests_post):
        """Test successful Nutrient OCR call."""
        # Mock file operations
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"dummy pdf content")
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Extracted text from Nutrient OCR"
        mock_requests_post.return_value = mock_response
        
        result = call_nutrient_ocr(test_file, self.api_key)
        
        self.assertEqual(result, "Extracted text from Nutrient OCR")
        mock_requests_post.assert_called_once()

    def test_call_nutrient_ocr_file_not_found(self):
        """Test Nutrient OCR with non-existent file."""
        with self.assertRaises(Exception) as context:
            call_nutrient_ocr("nonexistent.pdf", self.api_key)
        self.assertIn("File not found", str(context.exception))

    def test_call_nutrient_ocr_missing_credentials(self):
        """Test Nutrient OCR with missing credentials."""
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("dummy")
            
        with self.assertRaises(Exception) as context:
            call_nutrient_ocr(test_file, "")
        self.assertIn("API key is required", str(context.exception))

    @patch('requests.post')
    def test_call_nutrient_ocr_rate_limit(self, mock_requests_post):
        """Test Nutrient OCR with rate limiting."""
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"dummy")
        
        # Mock rate limit response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_requests_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            call_nutrient_ocr(test_file, self.api_key)
        
        self.assertIn("Rate limit", str(context.exception))

    @patch('requests.post')
    def test_call_nutrient_ocr_invalid_credentials(self, mock_requests_post):
        """Test Nutrient OCR with invalid credentials."""
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"dummy")
        
        # Mock unauthorized response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_requests_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            call_nutrient_ocr(test_file, self.api_key)
        
        self.assertIn("Invalid Nutrient API key", str(context.exception))


if __name__ == '__main__':
    unittest.main()