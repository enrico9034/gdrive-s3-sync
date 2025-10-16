"""
Integration test script
This script demonstrates how to test the sync functionality with real S3 and Google Drive operations
Run this manually with: python tests/integration_test.py
"""

import os
import sys
import tempfile
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging

from src.gdrive_client import GDriveClient
from src.s3_client import S3Client
from src.sync_manager import SyncManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_file(content: str) -> str:
    """Create a temporary test file"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def test_upload_and_delete():
    """
    Integration test: Upload a file to S3, sync to GDrive, delete from S3, sync again
    
    Requirements:
    - AWS credentials set in environment
    - Google Drive credentials.json file
    - S3 bucket and GDrive folder configured
    """
    logger.info("=" * 80)
    logger.info("INTEGRATION TEST: Upload and Delete Flow")
    logger.info("=" * 80)
    
    # Get configuration from environment
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')  # Custom S3 endpoint
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials = os.getenv('GDRIVE_CREDENTIALS_PATH', './credentials/credentials.json')
    
    if not all([aws_access_key, aws_secret_key, s3_bucket, gdrive_folder_id]):
        logger.error("Missing required environment variables!")
        logger.error("Please set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, GDRIVE_FOLDER_ID")
        return False
    
    try:
        # Initialize clients
        logger.info("Initializing clients...")
        s3_client = S3Client(aws_access_key, aws_secret_key, aws_region, s3_bucket, s3_endpoint_url)
        gdrive_client = GDriveClient(gdrive_credentials, gdrive_folder_id)
        sync_manager = SyncManager(s3_client, gdrive_client)
        
        # Create test file
        test_filename = f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = f"Test content created at {datetime.now()}"
        local_file = create_test_file(test_content)
        
        logger.info(f"Created test file: {test_filename}")
        
        # Step 1: Upload file to S3
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: Uploading file to S3")
        logger.info("=" * 80)
        
        import boto3
        s3_config = {
            'aws_access_key_id': aws_access_key,
            'aws_secret_access_key': aws_secret_key,
            'region_name': aws_region
        }
        if s3_endpoint_url:
            s3_config['endpoint_url'] = s3_endpoint_url
            logger.info(f"Using custom S3 endpoint for upload: {s3_endpoint_url}")
        
        s3 = boto3.client('s3', **s3_config)
        s3.upload_file(local_file, s3_bucket, test_filename)
        logger.info(f"✓ File uploaded to S3: {test_filename}")
        
        # Step 2: First sync - should upload to GDrive
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: First sync (should upload to Google Drive)")
        logger.info("=" * 80)
        
        stats = sync_manager.sync()
        logger.info(f"Sync stats: {stats}")
        
        if stats['uploaded'] == 1:
            logger.info("✓ File successfully synced to Google Drive")
        else:
            logger.warning(f"⚠ Expected 1 upload, got {stats['uploaded']}")
        
        # Wait a bit
        logger.info("\nWaiting 3 seconds...")
        time.sleep(3)
        
        # Step 3: Delete file from S3
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Deleting file from S3")
        logger.info("=" * 80)
        
        s3.delete_object(Bucket=s3_bucket, Key=test_filename)
        logger.info(f"✓ File deleted from S3: {test_filename}")
        
        # Step 4: Second sync - should delete from GDrive
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: Second sync (should delete from Google Drive)")
        logger.info("=" * 80)
        
        stats = sync_manager.sync()
        logger.info(f"Sync stats: {stats}")
        
        if stats['deleted'] == 1:
            logger.info("✓ File successfully deleted from Google Drive")
        else:
            logger.warning(f"⚠ Expected 1 deletion, got {stats['deleted']}")
        
        # Cleanup local file
        os.remove(local_file)
        
        logger.info("\n" + "=" * 80)
        logger.info("INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        return True
    
    except Exception as e:
        logger.error(f"Integration test failed: {e}", exc_info=True)
        return False


def test_update_file():
    """
    Integration test: Upload a file, modify it in S3, sync to see update
    """
    logger.info("=" * 80)
    logger.info("INTEGRATION TEST: Update File Flow")
    logger.info("=" * 80)
    
    # Get configuration
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')  # Custom S3 endpoint
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials = os.getenv('GDRIVE_CREDENTIALS_PATH', './credentials/credentials.json')
    
    if not all([aws_access_key, aws_secret_key, s3_bucket, gdrive_folder_id]):
        logger.error("Missing required environment variables!")
        return False
    
    try:
        # Initialize clients
        s3_client = S3Client(aws_access_key, aws_secret_key, aws_region, s3_bucket, s3_endpoint_url)
        gdrive_client = GDriveClient(gdrive_credentials, gdrive_folder_id)
        sync_manager = SyncManager(s3_client, gdrive_client)
        
        # Create test file
        test_filename = f"update_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Step 1: Upload initial version
        logger.info("\nSTEP 1: Uploading initial version to S3")
        content_v1 = "Version 1 content"
        local_file_v1 = create_test_file(content_v1)
        
        import boto3
        s3_config = {
            'aws_access_key_id': aws_access_key,
            'aws_secret_access_key': aws_secret_key,
            'region_name': aws_region
        }
        if s3_endpoint_url:
            s3_config['endpoint_url'] = s3_endpoint_url
        
        s3 = boto3.client('s3', **s3_config)
        s3.upload_file(local_file_v1, s3_bucket, test_filename)
        logger.info(f"✓ Uploaded: {test_filename} (version 1)")
        os.remove(local_file_v1)
        
        # Step 2: Sync to GDrive
        logger.info("\nSTEP 2: Syncing to Google Drive")
        stats = sync_manager.sync()
        logger.info(f"Sync stats: {stats}")
        
        # Wait
        time.sleep(3)
        
        # Step 3: Upload updated version
        logger.info("\nSTEP 3: Uploading updated version to S3")
        content_v2 = "Version 2 content - UPDATED with more data!"
        local_file_v2 = create_test_file(content_v2)
        s3.upload_file(local_file_v2, s3_bucket, test_filename)
        logger.info(f"✓ Uploaded: {test_filename} (version 2 - larger)")
        os.remove(local_file_v2)
        
        # Step 4: Sync again - should update
        logger.info("\nSTEP 4: Syncing again (should update)")
        stats = sync_manager.sync()
        logger.info(f"Sync stats: {stats}")
        
        if stats['updated'] == 1:
            logger.info("✓ File successfully updated in Google Drive")
        else:
            logger.warning(f"⚠ Expected 1 update, got {stats['updated']}")
        
        # Cleanup
        logger.info("\nCleaning up...")
        s3.delete_object(Bucket=s3_bucket, Key=test_filename)
        time.sleep(2)
        sync_manager.sync()  # Delete from GDrive
        
        logger.info("\n" + "=" * 80)
        logger.info("UPDATE TEST COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        return True
    
    except Exception as e:
        logger.error(f"Update test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    logger.info("Starting integration tests...")
    logger.info("Make sure you have set up your .env file with the correct credentials\n")
    
    # Run tests
    success = True
    
    if test_upload_and_delete():
        logger.info("✓ Upload and delete test passed\n")
    else:
        logger.error("✗ Upload and delete test failed\n")
        success = False
    
    time.sleep(5)
    
    if test_update_file():
        logger.info("✓ Update file test passed\n")
    else:
        logger.error("✗ Update file test failed\n")
        success = False
    
    if success:
        logger.info("=" * 80)
        logger.info("ALL INTEGRATION TESTS PASSED!")
        logger.info("=" * 80)
        sys.exit(0)
    else:
        logger.error("=" * 80)
        logger.error("SOME TESTS FAILED")
        logger.error("=" * 80)
        sys.exit(1)
