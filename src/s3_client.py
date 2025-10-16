"""
S3 Client Module
Handles all S3 operations for listing and downloading files
"""

import logging
from typing import Dict, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Client:
    """Client for interacting with AWS S3 or S3-compatible storage"""
    
    def __init__(
        self, 
        access_key: str, 
        secret_key: str, 
        region: str, 
        bucket_name: str,
        endpoint_url: str = None
    ):
        """
        Initialize S3 client
        
        Args:
            access_key: AWS access key ID or S3-compatible access key
            secret_key: AWS secret access key or S3-compatible secret key
            region: AWS region (or any value for S3-compatible storage)
            bucket_name: S3 bucket name
            endpoint_url: Custom S3 endpoint URL (e.g., for MinIO, Wasabi, etc.)
                         If None, uses standard AWS S3
        """
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        
        # Configurazione client S3
        client_config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'region_name': region
        }
        
        # Aggiungi endpoint personalizzato se specificato
        if endpoint_url:
            client_config['endpoint_url'] = endpoint_url
            logger.info(f"Using custom S3 endpoint: {endpoint_url}")
        
        self.s3_client = boto3.client('s3', **client_config)
        
        if endpoint_url:
            logger.info(f"S3 client initialized for bucket '{bucket_name}' at custom endpoint: {endpoint_url}")
        else:
            logger.info(f"S3 client initialized for bucket '{bucket_name}' (AWS S3)")
    
    def list_files(self) -> List[Dict[str, any]]:
        """
        List all files in the S3 bucket
        
        Filters out directory markers (keys ending with '/') and returns only actual files.
        
        Returns:
            List of dictionaries containing file information (key, size, last_modified)
        """
        try:
            logger.info(f"Listing files in S3 bucket: {self.bucket_name}")
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                logger.info("No files found in S3 bucket")
                return []
            
            files = []
            directories_skipped = 0
            
            for obj in response['Contents']:
                key = obj['Key']
                
                # Skip directory markers (keys ending with '/')
                if key.endswith('/'):
                    directories_skipped += 1
                    logger.debug(f"Skipping directory marker: {key}")
                    continue
                
                # Skip zero-byte files that might be directory placeholders
                if obj['Size'] == 0 and '/' in key:
                    logger.debug(f"Skipping potential directory placeholder: {key}")
                    directories_skipped += 1
                    continue
                
                files.append({
                    'key': key,
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
            
            if directories_skipped > 0:
                logger.info(f"Skipped {directories_skipped} directory markers/placeholders")
            
            logger.info(f"Found {len(files)} actual files in S3 bucket")
            return files
        
        except ClientError as e:
            logger.error(f"Error listing S3 files: {e}")
            raise
    
    def upload_file(self, local_path: str, key: str) -> bool:
        """
        Upload a file to S3
        
        Args:
            local_path: Local file path to upload
            key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Uploading file to S3: {local_path} as {key}")
            self.s3_client.upload_file(local_path, self.bucket_name, key)
            logger.info(f"Successfully uploaded: {key}")
            return True
        
        except ClientError as e:
            logger.error(f"Error uploading file {key}: {e}")
            return False
    
    def download_file(self, key: str, local_path: str) -> bool:
        """
        Download a file from S3 to local path
        
        Args:
            key: S3 object key
            local_path: Local file path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading S3 file: {key} to {local_path}")
            self.s3_client.download_file(self.bucket_name, key, local_path)
            logger.info(f"Successfully downloaded: {key}")
            return True
        
        except ClientError as e:
            logger.error(f"Error downloading file {key}: {e}")
            return False
    
    def file_exists(self, key: str) -> bool:
        """
        Check if a file exists in S3
        
        Args:
            key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting S3 file: {key}")
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Successfully deleted: {key}")
            return True
        
        except ClientError as e:
            logger.error(f"Error deleting file {key}: {e}")
            return False
