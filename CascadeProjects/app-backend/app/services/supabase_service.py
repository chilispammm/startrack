from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.core.config import settings
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def create_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new submission record in Supabase
        """
        try:
            response = self.client.table('submissions').insert({
                'id': str(uuid.uuid4()),
                'full_name': data['full_name'],
                'user_email': data['user_email'],
                'company_email': data['company_email'],
                'job_title': data['job_title'],
                'email_subject': data['email_subject'],
                'email_body': data['email_body'],
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise

    async def upload_cv(self, file: bytes, filename: str) -> str:
        """
        Upload CV file to Supabase Storage
        """
        try:
            file_id = str(uuid.uuid4())
            file_path = f"cvs/{file_id}_{filename}"
            
            self.client.storage.from_('cvs').upload(
                file_path,
                file,
                {'content-type': 'application/pdf'}
            )
            
            return file_path
        except Exception as e:
            logger.error(f"Error uploading CV: {str(e)}")
            raise

    async def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a submission by ID
        """
        try:
            response = self.client.table('submissions').select('*').eq('id', submission_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting submission: {str(e)}")
            raise

    async def get_cv_url(self, file_path: str) -> str:
        """
        Get public URL for a CV file
        """
        try:
            return self.client.storage.from_('cvs').get_public_url(file_path)
        except Exception as e:
            logger.error(f"Error getting CV URL: {str(e)}")
            raise
