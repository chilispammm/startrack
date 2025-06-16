from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
from app.core.logger import logger
from app.core.config import settings
from app.models.schemas import ApplicationBase
from pydantic import ValidationError
from app.models.schemas import ApplicationStatus

class SupabaseService:
    def __init__(self):
        """
        Initialize Supabase client with error handling
        """
        try:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Successfully initialized Supabase client")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise

    async def check_connection(self) -> str:
        """
        Check Supabase connection status
        
        Returns:
            str: Connection status ('healthy' or error message)
        """
        try:
            # Try a simple query to check connection
            await self.client.table('applications').select('id').limit(1).execute()
            return "healthy"
        except Exception as e:
            logger.error(f"Supabase connection check failed: {str(e)}")
            return f"unhealthy: {str(e)}"

    def create_submission(self, data: Dict) -> Dict:
        """
        Create a new submission record in Supabase
        
        Args:
            data: Dictionary containing submission data
            
        Returns:
            Dict: Created submission record
            
        Raises:
            ValueError: If data validation fails
            Exception: If database operation fails
        """
        try:
            # Validate input data
            ApplicationBase(**data)
            
            submission_data = {
                'id': str(UUID(int=0)),  # Will be replaced by Supabase
                'full_name': data['full_name'],
                'user_email': data['user_email'],
                'company_email': data['company_email'],
                'job_title': data['job_title'],
                'email_subject': data.get('email_subject', ''),
                'email_body': data.get('email_body', ''),
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            response = self.client.table('submissions').insert(submission_data).execute()
            
            if not response.data:
                raise ValueError("No data returned from database")
                
            logger.info(f"Successfully created submission: {submission_data}")
            return response.data[0]
            
        except ValidationError as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise ValueError(f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise

    def get_submissions(
        self, 
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> List[Dict]:
        """
        Get list of submissions with filtering options
        
        Args:
            limit: Maximum number of submissions to return
            offset: Offset for pagination
            status: Filter by submission status
            user_email: Filter by user email
            
        Returns:
            List[Dict]: List of filtered submission records
        """
        try:
            query = self.client.table('submissions').select('*')
            
            if status:
                query = query.eq('status', status)
            if user_email:
                query = query.eq('user_email', user_email)
            
            response = query.limit(limit).offset(offset).execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching submissions: {str(e)}")
            raise

    def get_submission_by_id(self, submission_id: str) -> Optional[Dict]:
        """
        Get a specific submission by ID with validation
        
        Args:
            submission_id: ID of the submission to fetch
            
        Returns:
            Optional[Dict]: Submission record if found, None otherwise
            
        Raises:
            ValueError: If submission_id is invalid
        """
        try:
            UUID(submission_id)  # Validate UUID format
            response = self.client.table('submissions').select('*').eq('id', submission_id).execute()
            return response.data[0] if response.data else None
            
        except ValueError:
            logger.error(f"Invalid submission ID: {submission_id}")
            raise ValueError("Invalid submission ID format")
        except Exception as e:
            logger.error(f"Error fetching submission {submission_id}: {str(e)}")
            raise

    def update_submission_status(self, submission_id: str, status: str) -> Optional[Dict]:
        """
        Update submission status
        
        Args:
            submission_id: ID of the submission to update
            status: New status to set
            
        Returns:
            Optional[Dict]: Updated submission record
            
        Raises:
            ValueError: If submission_id or status is invalid
        """
        try:
            UUID(submission_id)  # Validate UUID format
            
            valid_statuses = ['pending', 'sent', 'error', 'completed']
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
                
            response = self.client.table('applications').update({'status': status}).eq('id', submission_id).execute()
            
            if not response.data:
                raise ValueError("No submission found with this ID")
                
            logger.info(f"Updated submission {submission_id} status to {status}")
            return response.data[0]
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating submission status: {str(e)}")
            raise

    def upload_cv(self, file: bytes, filename: str) -> str:
        """
        Upload CV file to Supabase Storage with validation
        
        Args:
            file: File contents as bytes
            filename: Original filename
            
        Returns:
            str: Storage path of uploaded file
            
        Raises:
            ValueError: If file is empty or invalid
        """
        try:
            if not file or len(file) == 0:
                raise ValueError("File cannot be empty")
                
            file_id = str(UUID(int=0))  # Will be replaced by Supabase
            file_path = f"cvs/{file_id}_{filename}"
            
            # Validate file type
            if not filename.lower().endswith('.pdf'):
                raise ValueError("Only PDF files are allowed")
                
            self.client.storage.from_('cvs').upload(
                file_path,
                file,
                {'content-type': 'application/pdf'}
            )
            
            logger.info(f"Successfully uploaded CV: {filename}")
            return file_path
            
        except ValueError as e:
            logger.error(f"File validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error uploading CV: {str(e)}")
            raise

    def get_cv_url(self, file_path: str) -> str:
        """
        Get public URL for a CV file with validation
        
        Args:
            file_path: Storage path of the file
            
        Returns:
            str: Public URL of the file
            
        Raises:
            ValueError: If file_path is invalid
        """
        try:
            if not file_path or not file_path.startswith('cvs/'):  # Validate path format
                raise ValueError("Invalid file path format")
                
            url = self.client.storage.from_('cvs').get_public_url(file_path)
            
            # Validate URL
            if not url or not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL returned from storage")
                
            return url
            
        except ValueError as e:
            logger.error(f"URL validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting CV URL: {str(e)}")
            raise

    def delete_submission(self, submission_id: str) -> bool:
        """
        Delete a submission and its associated CV file
        
        Args:
            submission_id: ID of the submission to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValueError: If submission_id is invalid
        """
        try:
            UUID(submission_id)  # Validate UUID format
            
            # Get submission to find CV path
            submission = self.get_submission_by_id(submission_id)
            if not submission:
                raise ValueError("Submission not found")
                
            # Delete CV file if exists
            if submission.get('cv_url'):
                try:
                    self.client.storage.from_('cvs').remove([submission['cv_url']])
                except Exception as e:
                    logger.warning(f"Error deleting CV file: {str(e)}")
                    
            # Delete submission
            response = self.client.table('applications').delete().eq('id', submission_id).execute()
            
            return bool(response.data)
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting submission: {str(e)}")
            raise
            return False

    def get_all_submissions(self) -> List[Dict]:
        """
        Get all submissions from Supabase
        
        Returns:
            List of dictionaries containing all submissions
        """
        try:
            response = self.client.table('applications').select('*').execute()
            submissions = response.data
            logger.info(f"Retrieved {len(submissions)} submissions from Supabase")
            return submissions
            
        except Exception as e:
            logger.error(f"Error retrieving submissions: {str(e)}")
            return []
