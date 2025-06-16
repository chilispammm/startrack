from supabase import create_client, Client
from typing import Dict, List, Optional
from datetime import datetime
from app.core.logger import logger
from app.core.config import settings

class SupabaseService:
    def __init__(self):
        """
        Initialize Supabase client
        """
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def create_submission(self, data: Dict) -> Dict:
        """
        Create a new submission record in Supabase
        
        Args:
            data: Dictionary containing submission data
            
        Returns:
            Dict: Created submission record
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
            
            logger.info(f"Successfully created submission: {data}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise

    def get_submissions(self, limit: int = 100) -> List[Dict]:
        """
        Get list of submissions
        
        Args:
            limit: Maximum number of submissions to return
            
        Returns:
            List[Dict]: List of submission records
        """
        try:
            response = self.client.table('submissions').select('*').limit(limit).execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching submissions: {str(e)}")
            raise

    def get_submission_by_id(self, submission_id: str) -> Optional[Dict]:
        """
        Get a specific submission by ID
        
        Args:
            submission_id: ID of the submission to fetch
            
        Returns:
            Optional[Dict]: Submission record if found, None otherwise
        """
        try:
            response = self.client.table('submissions').select('*').eq('id', submission_id).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error fetching submission {submission_id}: {str(e)}")
            raise

    def upload_cv(self, file: bytes, filename: str) -> str:
        """
        Upload CV file to Supabase Storage
        
        Args:
            file: File contents as bytes
            filename: Original filename
            
        Returns:
            str: Storage path of uploaded file
        """
        try:
            file_id = str(uuid.uuid4())
            file_path = f"cvs/{file_id}_{filename}"
            
            self.client.storage.from_('cvs').upload(
                file_path,
                file,
                {'content-type': 'application/pdf'}
            )
            
            logger.info(f"Successfully uploaded CV: {filename}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error uploading CV: {str(e)}")
            raise

    def get_cv_url(self, file_path: str) -> str:
        """
        Get public URL for a CV file
        
        Args:
            file_path: Storage path of the file
            
        Returns:
            str: Public URL of the file
        """
        try:
            return self.client.storage.from_('cvs').get_public_url(file_path)
            
        except Exception as e:
            logger.error(f"Error getting CV URL: {str(e)}")
            raise
            return False

    def get_all_submissions(self) -> List[Dict]:
        """
        Get all submissions from the local JSON file
        
        Returns:
            List of dictionaries containing all submissions
        """
        try:
            with open(self.data_file, 'r') as f:
                submissions = json.load(f)
            logger.info(f"Retrieved {len(submissions)} submissions from mock sheets")
            return submissions
            
        except Exception as e:
            logger.error(f"Error retrieving submissions: {str(e)}")
            return []
