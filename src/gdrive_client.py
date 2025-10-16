"""
Google Drive Client Module
Handles all Google Drive operations for uploading and deleting files
"""

import logging
import os
from typing import Dict, List, Optional

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)


class GDriveClient:
    """Client for interacting with Google Drive API"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_path: str, folder_id: str):
        """
        Initialize Google Drive client
        
        Args:
            credentials_path: Path to credentials.json file
            folder_id: Google Drive folder ID where files will be synced
        """
        self.folder_id = folder_id
        self.credentials_path = credentials_path
        
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found: {credentials_path}")
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
        
        # Authenticate using service account
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=self.SCOPES
        )
        
        self.service = build('drive', 'v3', credentials=self.creds)
        logger.info(f"Google Drive client initialized for folder: {folder_id}")
    
    def list_files(self) -> List[Dict[str, any]]:
        """
        List all files in the Google Drive folder
        
        Returns:
            List of dictionaries containing file information (id, name, size)
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
            return files
        
        except HttpError as e:
            logger.error(f"Error listing Google Drive files: {e}")
            raise
    
    def upload_file(self, local_path: str, filename: str, parent_folder_id: str = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            local_path: Local file path
            filename: Name for the file in Google Drive
            parent_folder_id: Parent folder ID (if None, uses root folder_id)
            
        Returns:
            File ID if successful, None otherwise
        """
        try:
            parent_id = parent_folder_id if parent_folder_id else self.folder_id
            
            logger.info(f"Uploading file to Google Drive: {filename} (parent: {parent_id})")
            
            file_metadata = {
                'name': filename,
                'parents': [parent_id]
            }
            
            media = MediaFileUpload(local_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Successfully uploaded file: {filename} (ID: {file_id})")
            return file_id
        
        except HttpError as e:
            logger.error(f"Error uploading file {filename}: {e}")
            return None
    
    def delete_file(self, file_id: str, filename: str) -> bool:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            filename: Filename (for logging purposes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting file from Google Drive: {filename} (ID: {file_id})")
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Successfully deleted file: {filename}")
            return True
        
        except HttpError as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def find_file_by_name(self, filename: str) -> Optional[Dict[str, any]]:
        """
        Find a file in the folder by name
        
        Args:
            filename: Name of the file to find
            
        Returns:
            File information dict if found, None otherwise
        """
        try:
            query = f"name='{filename}' and '{self.folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, size)",
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            return files[0] if files else None
        
        except HttpError as e:
            logger.error(f"Error finding file {filename}: {e}")
            return None
    
    def update_file(self, file_id: str, local_path: str, filename: str) -> bool:
        """
        Update an existing file in Google Drive
        
        Args:
            file_id: Google Drive file ID
            local_path: Local file path
            filename: Filename (for logging purposes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Updating file in Google Drive: {filename} (ID: {file_id})")
            
            media = MediaFileUpload(local_path, resumable=True)
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            logger.info(f"Successfully updated file: {filename}")
            return True
        
        except HttpError as e:
            logger.error(f"Error updating file {filename}: {e}")
            return False
    
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
