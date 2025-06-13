import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService
from app.core.config import settings

@patch("smtplib.SMTP")
def test_send_email_success(mock_smtp):
    # Arrange
    email_service = EmailService()
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    
    # Act
    success, msg = email_service.send_email(
        recipient_email="test@example.com",
        subject="Test Subject",
        body="Test Body"
    )
    
    # Assert
    assert success is True
    assert msg == "Email sent successfully"
    mock_smtp_instance.login.assert_called_once_with(
        settings.SENDER_EMAIL, settings.SENDER_PASSWORD
    )
    mock_smtp_instance.send_message.assert_called_once()

@patch("smtplib.SMTP")
def test_send_email_failure(mock_smtp):
    # Arrange
    email_service = EmailService()
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.login.side_effect = Exception("SMTP Error")
    
    # Act
    success, msg = email_service.send_email(
        recipient_email="test@example.com",
        subject="Test Subject",
        body="Test Body"
    )
    
    # Assert
    assert success is False
    assert "Failed to send email" in msg
