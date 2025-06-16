from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Dict, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/forms.body']
        )
        self.service = build('forms', 'v1', credentials=self.credentials)

    def create_feedback_form(self, application_data: Dict[str, str]) -> str:
        """
        Create a Google Form for application feedback.
        """
        try:
            # Form configuration
            form = {
                "info": {
                    "title": f"Feedback for {application_data['full_name']}'s Application",
                    "documentTitle": "Application Feedback",
                    "description": "Please provide feedback about the job application.",
                },
                "questions": [
                    {
                        "questionId": "00000000000000000000",
                        "title": "Overall Experience",
                        "question": {
                            "scale": {
                                "low": 1,
                                "high": 5,
                                "lowLabel": "Very Poor",
                                "highLabel": "Excellent",
                            },
                        },
                    },
                    {
                        "questionId": "00000000000000000001",
                        "title": "Would you recommend this service?",
                        "question": {
                            "scale": {
                                "low": 1,
                                "high": 5,
                                "lowLabel": "No",
                                "highLabel": "Yes",
                            },
                        },
                    },
                    {
                        "questionId": "00000000000000000002",
                        "title": "Additional Feedback",
                        "question": {
                            "paragraph": {},
                        },
                    },
                ],
            }

            # Create form
            result = self.service.forms().create(body=form).execute()
            return result.get('formId')

        except Exception as e:
            logger.error(f"Error creating feedback form: {str(e)}")
            return None

    def get_form_url(self, form_id: str) -> Optional[str]:
        """
        Get the URL for a Google Form.
        """
        try:
            form = self.service.forms().get(formId=form_id).execute()
            return form.get('responderUri')
        except Exception as e:
            logger.error(f"Error getting form URL: {str(e)}")
            return None

# Initialize feedback service
feedback_service = FeedbackService()
