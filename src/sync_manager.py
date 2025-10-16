"""
Sync Manager Module
Handles the one-way synchronization from S3 to Google Drive
"""

import logging
import os
import tempfile
from typing import Dict, Set

from .gdrive_client import GDriveClient
from .s3_client import S3Client

logger = logging.getLogger(__name__)


class SyncManager:
    """Manages one-way synchronization from S3 to Google Drive"""
    
    def __init__(self, s3_client: S3Client, gdrive_client: GDriveClient, preserve_structure: bool = True):
        """
        Initialize Sync Manager
        
        Args:
            s3_client: Initialized S3 client
            gdrive_client: Initialized Google Drive client
            preserve_structure: If True, recreates S3 directory structure in Google Drive (dir/file.txt -> dir/file.txt)
                               If False, flattens structure using _ (dir/file.txt -> dir_file.txt)
        """
        self.s3_client = s3_client
        self.gdrive_client = gdrive_client
        self.preserve_structure = preserve_structure
        self.folder_cache = {}  # Cache for folder IDs {path: folder_id}
        logger.info(f"Sync Manager initialized (preserve_structure={preserve_structure})")
    
    def _parse_s3_key(self, s3_key: str) -> tuple[str, str]:
        """
        Parse S3 key into directory path and filename
        
        Args:
            s3_key: S3 object key (e.g., 'dir1/dir2/file.txt' or 'file.txt')
            
        Returns:
            Tuple of (directory_path, filename)
            - directory_path: 'dir1/dir2' or '' for root
            - filename: 'file.txt'
        """
        if '/' in s3_key:
            parts = s3_key.rsplit('/', 1)
            return parts[0], parts[1]
        else:
            return '', s3_key
    
    def _get_gdrive_folder_for_path(self, path: str) -> str:
        """
        Get or create Google Drive folder for the given path
        
        Args:
            path: Directory path (e.g., 'dir1/dir2' or '' for root)
            
        Returns:
            Folder ID
        """
        if not path:
            return self.gdrive_client.folder_id
        
        # Check cache
        if path in self.folder_cache:
            return self.folder_cache[path]
        
        # Create path and cache it
        folder_id = self.gdrive_client.get_or_create_path(path)
        self.folder_cache[path] = folder_id
        
        return folder_id
    
    def _get_file_identifier(self, s3_key: str) -> str:
        """
        Get unique identifier for file in Google Drive
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Identifier used to match files (either full path or flattened name)
        """
        if self.preserve_structure:
            # Use full S3 key as identifier
            return s3_key
        else:
            # Use flattened name (replace / with _)
            return s3_key.replace('/', '_')
    
    def sync(self) -> Dict[str, int]:
        """
        Perform one-way sync from S3 to Google Drive
        
        This will:
        - Upload new files from S3 to GDrive (preserving directory structure if enabled)
        - Update modified files
        - Delete files from GDrive that no longer exist in S3
        
        Returns:
            Dictionary with sync statistics (uploaded, updated, deleted, errors)
        """
        stats = {
            'uploaded': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
            'unchanged': 0
        }
        
        logger.info("=" * 60)
        logger.info("Starting synchronization from S3 to Google Drive")
        if self.preserve_structure:
            logger.info("Mode: Preserve directory structure")
        else:
            logger.info("Mode: Flatten structure (replace / with _)")
        logger.info("=" * 60)
        
        try:
            # Get files from both sources
            s3_files = self.s3_client.list_files()
            gdrive_files = self.gdrive_client.list_files()
            
            # Create maps with identifiers
            # Map: file_identifier -> s3_file_info
            s3_map = {}
            for f in s3_files:
                identifier = self._get_file_identifier(f['key'])
                s3_map[identifier] = f
            
            # Map: gdrive_name -> gdrive_file_info  
            # Note: With preserve_structure, this only works for root level files
            # TODO: Implement recursive listing for folder structure
            gdrive_map = {f['name']: f for f in gdrive_files}
            
            s3_identifiers: Set[str] = set(s3_map.keys())
            gdrive_names: Set[str] = set(gdrive_map.keys())
            
            logger.info(f"S3 files count: {len(s3_identifiers)}")
            logger.info(f"Google Drive files count: {len(gdrive_names)}")
            
            # Files to upload (in S3 but not in GDrive)
            files_to_upload = s3_identifiers - gdrive_names
            
            # Files to potentially update (in both)
            files_to_check = s3_identifiers & gdrive_names
            
            # Files to delete (in GDrive but not in S3)
            files_to_delete = gdrive_names - s3_identifiers
            
            logger.info(f"Files to upload: {len(files_to_upload)}")
            logger.info(f"Files to check for updates: {len(files_to_check)}")
            logger.info(f"Files to delete: {len(files_to_delete)}")
            
            # Upload new files
            for identifier in files_to_upload:
                logger.info(f"Processing new file: {identifier}")
                s3_file = s3_map[identifier]
                if self._upload_file(identifier, s3_file['key']):
                    stats['uploaded'] += 1
                else:
                    stats['errors'] += 1
            
            # Check and update existing files if needed
            for identifier in files_to_check:
                s3_file = s3_map[identifier]
                gdrive_file = gdrive_map[identifier]
                
                # Check if file sizes differ (simple check for modifications)
                s3_size = s3_file['size']
                gdrive_size = int(gdrive_file.get('size', 0))
                
                if s3_size != gdrive_size:
                    logger.info(f"File size mismatch for {identifier}: S3={s3_size}, GDrive={gdrive_size}")
                    if self._update_file(identifier, gdrive_file['id'], s3_file['key']):
                        stats['updated'] += 1
                    else:
                        stats['errors'] += 1
                else:
                    logger.debug(f"File unchanged: {identifier}")
                    stats['unchanged'] += 1
            
            # Delete files that are no longer in S3
            for identifier in files_to_delete:
                gdrive_file = gdrive_map[identifier]
                logger.info(f"Deleting file from Google Drive: {identifier}")
                if self.gdrive_client.delete_file(gdrive_file['id'], identifier):
                    stats['deleted'] += 1
                else:
                    stats['errors'] += 1
            
            logger.info("=" * 60)
            logger.info("Synchronization completed")
            logger.info(f"Statistics: {stats}")
            logger.info("=" * 60)
            
            return stats
        
        except Exception as e:
            logger.error(f"Error during synchronization: {e}", exc_info=True)
            raise
    
    def _upload_file(self, identifier: str, s3_key: str) -> bool:
        """
        Download file from S3 and upload to Google Drive
        
        Args:
            identifier: File identifier (depends on preserve_structure mode)
            s3_key: S3 object key (may include path like 'dir1/file.txt')
            
        Returns:
            True if successful, False otherwise
        """
        temp_file = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_file = tmp.name
            
            logger.info(f"Downloading from S3: {s3_key}")
            
            # Download from S3 using the original S3 key
            if not self.s3_client.download_file(s3_key, temp_file):
                logger.error(f"Failed to download file from S3: {s3_key}")
                return False
            
            # Determine target folder and filename
            if self.preserve_structure:
                # Parse path and filename
                dir_path, filename = self._parse_s3_key(s3_key)
                
                # Get or create the target folder
                target_folder_id = self._get_gdrive_folder_for_path(dir_path)
                
                logger.info(f"Uploading to Google Drive: {filename} (in folder: {dir_path or 'root'})")
                
                # Upload to the correct folder
                file_id = self.gdrive_client.upload_file(temp_file, filename, target_folder_id)
            else:
                # Flatten mode: replace / with _
                filename = identifier
                logger.info(f"Uploading to Google Drive as: {filename}")
                
                # Upload to root folder
                file_id = self.gdrive_client.upload_file(temp_file, filename)
            
            if file_id:
                logger.info(f"Successfully synced new file: {identifier}")
                return True
            else:
                logger.error(f"Failed to upload file to Google Drive: {identifier}")
                return False
        
        except Exception as e:
            logger.error(f"Error uploading file {identifier}: {e}", exc_info=True)
            return False
        
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {e}")
    
    def _update_file(self, filename: str, gdrive_file_id: str, s3_key: str) -> bool:
        """
        Download file from S3 and update in Google Drive
        
        Args:
            filename: Google Drive filename (identifier)
            gdrive_file_id: Google Drive file ID
            s3_key: S3 object key (may include path)
            
        Returns:
            True if successful, False otherwise
        """
        temp_file = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_file = tmp.name
            
            logger.info(f"Downloading from S3 for update: {s3_key}")
            
            # Download from S3 using the original S3 key
            if not self.s3_client.download_file(s3_key, temp_file):
                logger.error(f"Failed to download file from S3: {s3_key}")
                return False
            
            # Get identifier for logging
            identifier = self._get_file_identifier(s3_key)
            logger.info(f"Updating in Google Drive: {identifier}")
            
            # Update in Google Drive (filename stays the same, just update content)
            if self.gdrive_client.update_file(gdrive_file_id, temp_file, filename):
                logger.info(f"Successfully updated file: {identifier}")
                return True
            else:
                logger.error(f"Failed to update file in Google Drive: {identifier}")
                return False
        
        except Exception as e:
            logger.error(f"Error updating file {filename}: {e}", exc_info=True)
            return False
        
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {e}")
