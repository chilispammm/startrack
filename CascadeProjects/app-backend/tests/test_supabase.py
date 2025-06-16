import pytest
from app.services.supabase_service import SupabaseService
from app.core.config import settings
import uuid
from datetime import datetime
from app.models.schemas import ApplicationStatus

@pytest.fixture
async def supabase_service():
    service = SupabaseService()
    # Clear test data before each test
    await service.delete_submission("test_submission_id")
    return service

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

@pytest.fixture
async def test_cv_file():
    # Create a minimal valid PDF file
    return b"%PDF-1.4\n%\u00c3\u00b7\u00c2\u00b0\u00c3\u00b7\u00e2\u009c\u0093\n\n"\
           b"1 0 obj\n"\
           b"<< /Type /Catalog /Pages 2 0 R >>\n"\
           b"endobj\n"\
           b"2 0 obj\n"\
           b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"\
           b"endobj\n"\
           b"3 0 obj\n"\
           b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\n"\
           b"endobj\n"\
           b"trailer\n"\
           b"<< /Root 1 0 R /Size 4 >>\n"\
           b"startxref\n"\
           b"0\n"\
           b"%%EOF"

@pytest.mark.asyncio
async def test_create_submission(supabase_service, test_submission_data):
    # Test successful creation
    result = await supabase_service.create_submission(test_submission_data)
    assert isinstance(result, dict)
    assert 'id' in result
    assert 'timestamp' in result
    assert result['status'] == 'pending'
    
    # Test validation failure
    invalid_data = test_submission_data.copy()
    invalid_data['full_name'] = ''
    with pytest.raises(ValueError):
        await supabase_service.create_submission(invalid_data)

@pytest.mark.asyncio
async def test_upload_cv(supabase_service, test_cv_file):
    # Test valid PDF upload
    filename = "test_cv.pdf"
    result = await supabase_service.upload_cv(test_cv_file, filename)
    assert isinstance(result, str)
    assert result.startswith("cvs/")
    
    # Test invalid file type
    invalid_filename = "test_cv.docx"
    with pytest.raises(ValueError):
        await supabase_service.upload_cv(test_cv_file, invalid_filename)
    
    # Test empty file
    empty_file = b""
    with pytest.raises(ValueError):
        await supabase_service.upload_cv(empty_file, filename)

@pytest.mark.asyncio
async def test_get_submission(supabase_service, test_submission_data):
    # Create a submission first
    submission = await supabase_service.create_submission(test_submission_data)
    
    # Get it back
    result = await supabase_service.get_submission(submission['id'])
    assert result is not None
    assert result['full_name'] == test_submission_data['full_name']
    
    # Test non-existent submission
    invalid_id = "invalid_id"
    with pytest.raises(ValueError):
        await supabase_service.get_submission(invalid_id)

@pytest.mark.asyncio
async def test_get_cv_url(supabase_service, test_cv_file):
    # Upload a test file first
    filename = "test_cv.pdf"
    file_path = await supabase_service.upload_cv(test_cv_file, filename)
    
    # Get the URL
    url = await supabase_service.get_cv_url(file_path)
    assert isinstance(url, str)
    assert url.startswith("http://") or url.startswith("https://")
    
    # Test invalid file path
    invalid_path = "invalid/path"
    with pytest.raises(ValueError):
        await supabase_service.get_cv_url(invalid_path)

@pytest.mark.asyncio
async def test_update_submission_status(supabase_service, test_submission_data):
    # Create a submission first
    submission = await supabase_service.create_submission(test_submission_data)
    
    # Test valid status update
    result = await supabase_service.update_submission_status(
        submission['id'], ApplicationStatus.SENT.value
    )
    assert result['status'] == ApplicationStatus.SENT.value
    
    # Test invalid status
    with pytest.raises(ValueError):
        await supabase_service.update_submission_status(
            submission['id'], "invalid_status"
        )
    
    # Test non-existent submission
    invalid_id = "invalid_id"
    with pytest.raises(ValueError):
        await supabase_service.update_submission_status(
            invalid_id, ApplicationStatus.SENT.value
        )

@pytest.mark.asyncio
async def test_delete_submission(supabase_service, test_submission_data, test_cv_file):
    # Create a submission with CV
    submission = await supabase_service.create_submission(test_submission_data)
    filename = "test_cv.pdf"
    cv_path = await supabase_service.upload_cv(test_cv_file, filename)
    
    # Update submission with CV path
    await supabase_service.update_submission_status(
        submission['id'], ApplicationStatus.COMPLETED.value
    )
    
    # Delete submission
    result = await supabase_service.delete_submission(submission['id'])
    assert result is True
    
    # Verify submission is deleted
    with pytest.raises(ValueError):
        await supabase_service.get_submission(submission['id'])

@pytest.mark.asyncio
async def test_list_submissions(supabase_service, test_submission_data):
    # Create multiple submissions
    submissions = []
    for i in range(3):
        data = test_submission_data.copy()
        data['full_name'] = f"Test User {i}"
        submission = await supabase_service.create_submission(data)
        submissions.append(submission)
    
    # Test listing with filters
    results = await supabase_service.get_submissions(
        limit=10,
        status=ApplicationStatus.PENDING.value,
        user_email=test_submission_data['user_email']
    )
    assert len(results) == 3
    
    # Test pagination
    page_1 = await supabase_service.get_submissions(limit=2, offset=0)
    page_2 = await supabase_service.get_submissions(limit=2, offset=2)
    assert len(page_1) == 2
    assert len(page_2) == 1
    assert page_1[0]['id'] != page_2[0]['id']
