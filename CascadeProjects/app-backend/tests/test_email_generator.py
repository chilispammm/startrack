import pytest
from app.services.email_generator import EmailGenerator
from unittest.mock import patch, MagicMock
import tempfile
import os

def test_extract_cv_text():
    generator = EmailGenerator()
    
    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b"%PDF-1.4\n%\u00c3\u00b7\u00c2\u00b0\u00c3\u00b7\u00e2\u009c\u0093\n")
        tmp_file_path = tmp_file.name
    
    try:
        # Mock pdfplumber
        with patch('app.services.email_generator.pdfplumber.open') as mock_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Test content"
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            result = generator.extract_cv_text(tmp_file_path)
            assert isinstance(result, str)
            assert result == "Test content"
    finally:
        os.unlink(tmp_file_path)

def test_generate_email_content():
    generator = EmailGenerator()
    
    # Mock OpenAI response
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Subject\n\nBody content"
        mock_create.return_value = mock_response
        
        result = generator.generate_email_content(
            "Test CV content",
            "Test User",
            "Test Job",
            "test@example.com"
        )
        
        assert isinstance(result, dict)
        assert 'subject' in result
        assert 'body' in result
        assert result['subject'] == "Subject"
        assert result['body'] == "Body content"

def test_generate_email_content_fallback():
    generator = EmailGenerator()
    
    # Simulate API error
    with patch('openai.ChatCompletion.create', side_effect=Exception("API error")):
        result = generator.generate_email_content(
            "Test CV content",
            "Test User",
            "Test Job",
            "test@example.com"
        )
        
        assert isinstance(result, dict)
        assert 'subject' in result
        assert 'body' in result
        assert result['subject'] == "Application for Test Job Position"
        assert "Test User" in result['body']
