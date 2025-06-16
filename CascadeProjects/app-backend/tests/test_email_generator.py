import pytest
from app.services.email_generator import EmailGenerator
from app.services.cache_service import CacheService
from unittest.mock import patch, MagicMock
import tempfile
import os
from datetime import datetime
import json

@pytest.fixture
def email_generator():
    return EmailGenerator()

@pytest.fixture
def mock_cache():
    with patch('app.services.cache_service.Redis') as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis_instance.get.return_value = None
        mock_redis_instance.set.return_value = True
        mock_redis.from_url.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture
def mock_openai():
    with patch('openai.ChatCompletion.create') as mock_create:
        yield mock_create

@pytest.fixture
def mock_pdf():
    with patch('app.services.email_generator.pdfplumber.open') as mock_open:
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        yield mock_open

def test_extract_cv_text_valid_pdf(email_generator, mock_pdf):
    """Test extracting text from valid PDF"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b"%PDF-1.4\n%\u00c3\u00b7\u00c2\u00b0\u00c3\u00b7\u00e2\u009c\u0093\n")
        tmp_file_path = tmp_file.name
    
    try:
        result = email_generator.extract_cv_text(tmp_file_path)
        assert isinstance(result, str)
        assert result == "Test content"
    finally:
        os.unlink(tmp_file_path)

def test_extract_cv_text_invalid_file(email_generator):
    """Test handling of invalid file types"""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(b"Test content")
        tmp_file_path = tmp_file.name
    
    try:
        with pytest.raises(ValueError):
            email_generator.extract_cv_text(tmp_file_path)
    finally:
        os.unlink(tmp_file_path)

def test_extract_cv_text_empty_pdf(email_generator, mock_pdf):
    """Test handling of empty PDF"""
    mock_pdf.return_value.__enter__.return_value.pages = []
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b"%PDF-1.4\n%\u00c3\u00b7\u00c2\u00b0\u00c3\u00b7\u00e2\u009c\u0093\n")
        tmp_file_path = tmp_file.name
    
    try:
        with pytest.raises(ValueError):
            email_generator.extract_cv_text(tmp_file_path)
    finally:
        os.unlink(tmp_file_path)

def test_generate_email_content_with_cache(email_generator, mock_cache, mock_openai):
    """Test email generation with cache hit"""
    # Set up mock cache
    mock_cache.get.return_value = json.dumps({
        "subject": "Cached Subject",
        "body": "Cached Body"
    })
    
    result = email_generator.generate_email_content(
        "Test CV content",
        "Test User",
        "Test Job",
        "test@example.com"
    )
    
    assert result == {"subject": "Cached Subject", "body": "Cached Body"}
    mock_openai.assert_not_called()

def test_generate_email_content_without_cache(email_generator, mock_cache, mock_openai):
    """Test email generation with cache miss"""
    # Set up mock AI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Subject\n\nBody content"
    mock_openai.return_value = mock_response
    
    result = email_generator.generate_email_content(
        "Test CV content",
        "Test User",
        "Test Job",
        "test@example.com"
    )
    
    assert result == {"subject": "Subject", "body": "Body content"}
    assert mock_cache.set.called

def test_generate_email_content_fallback(email_generator, mock_cache, mock_openai):
    """Test fallback behavior when AI fails"""
    # Simulate API error
    mock_openai.side_effect = Exception("API error")
    
    result = email_generator.generate_email_content(
        "Test CV content",
        "Test User",
        "Test Job",
        "test@example.com"
    )
    
    assert result == {
        "subject": "Application for Test Job Position",
        "body": "Dear Hiring Manager,\n\nI am writing to express my interest in the Test Job position.\n\nBest regards,\nTest User"
    }

def test_generate_email_content_formatting(email_generator, mock_cache, mock_openai):
    """Test formatting of AI-generated content"""
    # Set up mock AI response with long content
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
    This is a very long subject line that should be truncated to fit within 100 characters
    \n\nThis is a very long email body that should be truncated to fit within 500 words. It contains many words and
    should be properly formatted. The content should be properly split into paragraphs and
    formatted in a way that makes it easy to read. It should also include proper punctuation
    and capitalization. The email should be professional and concise, but still convey all
    the necessary information in a clear and organized manner.
    """
    mock_openai.return_value = mock_response
    
    result = email_generator.generate_email_content(
        "Test CV content",
        "Test User",
        "Test Job",
        "test@example.com"
    )
    
    assert len(result['subject']) <= 100
    assert len(result['body'].split()) <= 500

def test_generate_email_content_timeout(email_generator, mock_cache, mock_openai):
    """Test timeout handling"""
    # Simulate timeout
    mock_openai.side_effect = Exception("Timeout")
    
    result = email_generator.generate_email_content(
        "Test CV content",
        "Test User",
        "Test Job",
        "test@example.com"
    )
    
    assert result == {
        "subject": "Application for Test Job Position",
        "body": "Dear Hiring Manager,\n\nI am writing to express my interest in the Test Job position.\n\nBest regards,\nTest User"
    }
