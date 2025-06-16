import pytest
from app.services.supabase_service import SupabaseService
from app.core.config import settings
import uuid
from datetime import datetime

@pytest.fixture
async def supabase_service():
    return SupabaseService()

@pytest.fixture
async def test_submission_data():
    return {
        'full_name': 'Test User',
        'user_email': 'test@example.com',
        'company_email': 'company@example.com',
        'job_title': 'Test Job',
        'email_subject': 'Test Subject',
        'email_body': 'Test Body'
    }

@pytest.mark.asyncio
async def test_create_submission(supabase_service, test_submission_data):
    result = await supabase_service.create_submission(test_submission_data)
    assert isinstance(result, dict)
    assert 'id' in result
    assert 'timestamp' in result

@pytest.mark.asyncio
async def test_upload_cv(supabase_service):
    test_file = b"%PDF-1.4\n%\u00c3\u00b7\u00c2\u00b0\u00c3\u00b7\u00e2\u009c\u0093\n"  # Minimal PDF header
    filename = "test_cv.pdf"
    result = await supabase_service.upload_cv(test_file, filename)
    assert isinstance(result, str)
    assert result.startswith("cvs/")

@pytest.mark.asyncio
async def test_get_submission(supabase_service, test_submission_data):
    # Create a submission first
    submission = await supabase_service.create_submission(test_submission_data)
    
    # Get it back
    result = await supabase_service.get_submission(submission['id'])
    assert result is not None
    assert result['full_name'] == test_submission_data['full_name']

@pytest.mark.asyncio
async def test_get_cv_url(supabase_service):
    # Upload a test file first
    test_file = b"%PDF-1.4\n%\u00c3\u00b7\u00c2\u00b0\u00c3\u00b7\u00e2\u009c\u0093\n"
    filename = "test_cv.pdf"
    file_path = await supabase_service.upload_cv(test_file, filename)
    
    # Get the URL
    url = await supabase_service.get_cv_url(file_path)
    assert isinstance(url, str)
    assert url.startswith("http://") or url.startswith("https://")
