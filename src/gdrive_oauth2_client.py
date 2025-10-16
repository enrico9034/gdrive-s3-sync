"""
Google Drive Client Module with OAuth2 Support
Handles all Google Drive operations using OAuth2 user authentication
"""

import logging
import os
import pickle
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)


class GDriveOAuth2Client:
    """Client for interacting with Google Drive API using OAuth2"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_path: str, folder_id: str, token_path: str = 'token.pickle'):
        """
        Initialize Google Drive client with OAuth2
        
        Args:
            credentials_path: Path to OAuth2 credentials.json file (from Google Cloud Console)
            folder_id: Google Drive folder ID where files will be synced
            token_path: Path to store the OAuth2 token (for reuse)
        """
        self.folder_id = folder_id
        self.credentials_path = credentials_path
        self.token_path = token_path
        
        if not os.path.exists(credentials_path):
            logger.error(f"OAuth2 credentials file not found: {credentials_path}")
            raise FileNotFoundError(f"OAuth2 credentials file not found: {credentials_path}")
        
        # Authenticate using OAuth2
        self.creds = self._get_credentials()
        self.service = build('drive', 'v3', credentials=self.creds)
        logger.info(f"Google Drive OAuth2 client initialized for folder: {folder_id}")
    
    def _get_credentials(self) -> Credentials:
        """
        Get or refresh OAuth2 credentials
        
        Returns:
            Valid OAuth2 credentials
        """
        creds = None
        
        # Check if token.pickle exists (saved credentials)
        if os.path.exists(self.token_path):
            logger.info(f"Loading saved OAuth2 token from {self.token_path}")
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired OAuth2 token")
                creds.refresh(Request())
            else:
                logger.info("Starting OAuth2 authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("OAuth2 authentication successful")
            
            # Save credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
                logger.info(f"OAuth2 token saved to {self.token_path}")
        
        return creds
    
    def list_files(self) -> List[Dict[str, any]]:
        """
        List all files in the Google Drive folder
        
        Returns:
            List of dictionaries containing file information
        """
        try:
            logger.info(f"Listing files in Google Drive folder: {self.folder_id}")
            
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime)",
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in Google Drive folder")
            
            # Convert to standardized format
            formatted_files = []
            for file in files:
                formatted_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'size': int(file.get('size', 0)),
                    'modified_time': file.get('modifiedTime')
                })
            
            return formatted_files
            
        except HttpError as error:
            logger.error(f"Error listing Google Drive files: {error}")
            raise
    
    def upload_file(self, file_path: str, file_name: str, parent_folder_id: str = None) -> str:
        """
        Upload a file to Google Drive folder
        
        Args:
            file_path: Path to the local file to upload
            file_name: Name to give the file in Google Drive
            parent_folder_id: Parent folder ID (if None, uses root folder_id)
            
        Returns:
            File ID of the uploaded file
        """
        try:
            parent_id = parent_folder_id if parent_folder_id else self.folder_id
            
            logger.info(f"Uploading file to Google Drive: {file_name} (parent: {parent_id})")
            
            file_metadata = {
                'name': file_name,
                'parents': [parent_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"File uploaded successfully: {file_name} (ID: {file_id})")
            return file_id
            
        except HttpError as error:
            logger.error(f"Error uploading file {file_name}: {error}")
            raise
    
    def delete_file(self, file_id: str, filename: str = None) -> bool:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: ID of the file to delete
            filename: (Optional) Filename for logging purposes - kept for compatibility
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            log_name = filename if filename else file_id
            logger.info(f"Deleting file from Google Drive: {log_name} (ID: {file_id})")
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"File deleted successfully: {log_name}")
            return True
            
        except HttpError as error:
            logger.error(f"Error deleting file {file_id}: {error}")
            raise
    
    def find_file_by_name(self, file_name: str) -> Optional[Dict[str, any]]:
        """
        Find a file by name in the Google Drive folder
        
        Args:
            file_name: Name of the file to find
            
        Returns:
            File information dict if found, None otherwise
        """
        try:
            query = f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size, modifiedTime)",
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                file = files[0]
                return {
                    'id': file['id'],
                    'name': file['name'],
                    'size': int(file.get('size', 0)),
                    'modified_time': file.get('modifiedTime')
                }
            
            return None
            
        except HttpError as error:
            logger.error(f"Error finding file {file_name}: {error}")
            raise
    
    def update_file(self, file_id: str, file_path: str, filename: str = None) -> bool:
        """
        Update an existing file in Google Drive
        
        Args:
            file_id: ID of the file to update
            file_path: Path to the new file content
            filename: (Optional) Filename for logging purposes - kept for compatibility
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            log_name = filename if filename else file_id
            logger.info(f"Updating file in Google Drive: {log_name} (ID: {file_id})")
            
            media = MediaFileUpload(file_path, resumable=True)
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            logger.info(f"File updated successfully: {log_name}")
            return True
            
        except HttpError as error:
            logger.error(f"Error updating file {file_id}: {error}")
            raise
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Parent folder ID (if None, uses root folder_id)
            
        Returns:
            Folder ID of the created folder
        """
        try:
            parent_id = parent_folder_id if parent_folder_id else self.folder_id
            
            logger.info(f"Creating folder in Google Drive: {folder_name} (parent: {parent_id})")
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Folder created successfully: {folder_name} (ID: {folder_id})")
            return folder_id
            
        except HttpError as error:
            logger.error(f"Error creating folder {folder_name}: {error}")
            raise
    
    def find_folder_by_name(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """
        Find a folder by name in a parent folder
        
        Args:
            folder_name: Name of the folder to find
            parent_folder_id: Parent folder ID (if None, uses root folder_id)
            
        Returns:
            Folder ID if found, None otherwise
        """
        try:
            parent_id = parent_folder_id if parent_folder_id else self.folder_id
            
            query = (f"name='{folder_name}' and "
                    f"'{parent_id}' in parents and "
                    f"mimeType='application/vnd.google-apps.folder' and "
                    f"trashed=false")
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)",
                pageSize=1
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                folder_id = folders[0]['id']
                logger.debug(f"Found folder '{folder_name}': {folder_id}")
                return folder_id
            
            logger.debug(f"Folder not found: {folder_name}")
            return None
            
        except HttpError as error:
            logger.error(f"Error finding folder {folder_name}: {error}")
            raise
    
    def get_or_create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Get existing folder or create it if it doesn't exist
        
        Args:
            folder_name: Name of the folder
            parent_folder_id: Parent folder ID (if None, uses root folder_id)
            
        Returns:
            Folder ID
        """
        folder_id = self.find_folder_by_name(folder_name, parent_folder_id)
        
        if folder_id:
            return folder_id
        
        return self.create_folder(folder_name, parent_folder_id)
    
    def get_or_create_path(self, path: str) -> str:
        """
        Create nested folder structure from path (e.g., 'dir1/dir2/dir3')
        
        Args:
            path: Path string with folders separated by '/'
            
        Returns:
            ID of the deepest folder in the path
        """
        if not path or path == '/':
            return self.folder_id
        
        # Remove leading/trailing slashes and split
        path_parts = path.strip('/').split('/')
        
        current_parent = self.folder_id
        
        for folder_name in path_parts:
            if folder_name:  # Skip empty parts
                current_parent = self.get_or_create_folder(folder_name, current_parent)
        
        return current_parent
