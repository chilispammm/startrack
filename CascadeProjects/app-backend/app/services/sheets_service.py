import json
import os
from typing import Dict, List
from datetime import datetime
from app.core.logger import logger
from app.core.config import settings

class SheetsService:
    def __init__(self):
        """
        Initialize the mock sheets service that uses a local JSON file
        """
        self.data_file = "submissions.json"
        
        # Create the file if it doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)

    def log_submission(self, data: Dict) -> bool:
        """
        Log a form submission to a local JSON file (mocking Google Sheets)
        
        Args:
            data: Dictionary containing form data
            
        Returns:
            bool: True if logging was successful
        """
        try:
            # Read existing data
            with open(self.data_file, 'r') as f:
                submissions = json.load(f)
            
            # Add new submission
            submission = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **data
            }
            submissions.append(submission)
            
            # Write back to file
            with open(self.data_file, 'w') as f:
                json.dump(submissions, f, indent=2)
            
            logger.info(f"Successfully logged submission: {data}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging to mock sheets: {str(e)}")
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
