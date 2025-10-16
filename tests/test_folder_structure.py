"""
Test script to verify folder structure preservation in Google Drive
This creates test files with nested paths to verify the folder creation logic
"""

import logging
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.gdrive_oauth2_client import GDriveOAuth2Client
from src.s3_client import S3Client
from src.sync_manager import SyncManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_files_in_s3(s3_client: S3Client) -> list:
    """Create test files with nested directory structure in S3"""
    test_files = [
        "test_root.txt",
        "level1/test_level1.txt",
        "level1/level2/test_level2.txt",
        "level1/level2/level3/test_level3.txt",
        "docs/readme.md",
        "docs/images/logo.png",
        "src/main.py",
        "src/utils/helper.py",
    ]
    
    logger.info("Creating test files in S3...")
    created_keys = []
    
    for key in test_files:
        # Create temporary file with content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write(f"Test content for {key}\n")
            tmp.write(f"Path: {key}\n")
            tmp_path = tmp.name
        
        try:
            if s3_client.upload_file(tmp_path, key):
                logger.info(f"✓ Created: {key}")
                created_keys.append(key)
            else:
                logger.error(f"✗ Failed: {key}")
        finally:
            os.remove(tmp_path)
    
    return created_keys


def cleanup_test_files(s3_client: S3Client, keys: list):
    """Remove test files from S3"""
    logger.info("Cleaning up test files from S3...")
    for key in keys:
        if s3_client.delete_file(key):
            logger.info(f"✓ Deleted: {key}")
        else:
            logger.error(f"✗ Failed to delete: {key}")


def main():
    """Main test function"""
    # Load environment variables
    load_dotenv()
    
    logger.info("=== Folder Structure Preservation Test ===\n")
    
    # Get configuration
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials_path = os.getenv('GDRIVE_CREDENTIALS_PATH')
    token_path = os.getenv('GDRIVE_TOKEN_PATH', 'token.pickle')
    
    # Validate
    if not all([aws_access_key, aws_secret_key, aws_region, s3_bucket, 
                gdrive_folder_id, gdrive_credentials_path]):
        logger.error("Missing required environment variables!")
        return
    
    # Initialize clients
    logger.info("Initializing clients...\n")
    
    s3_client = S3Client(
        access_key=aws_access_key,
        secret_key=aws_secret_key,
        region=aws_region,
        bucket_name=s3_bucket,
        endpoint_url=s3_endpoint_url
    )
    
    gdrive_client = GDriveOAuth2Client(
        credentials_path=gdrive_credentials_path,
        folder_id=gdrive_folder_id,
        token_path=token_path
    )
    
    # Create test files
    created_keys = create_test_files_in_s3(s3_client)
    
    if not created_keys:
        logger.error("No test files were created. Aborting test.")
        return
    
    logger.info(f"\nCreated {len(created_keys)} test files in S3\n")
    
    try:
        # Test 1: Sync with preserve_structure=True
        logger.info("=== Test 1: Sync with PRESERVE_STRUCTURE=True ===")
        sync_manager = SyncManager(s3_client, gdrive_client, preserve_structure=True)
        stats = sync_manager.sync()
        
        logger.info(f"""
Results:
  - Uploaded: {stats['uploaded']}
  - Updated: {stats['updated']}
  - Deleted: {stats['deleted']}
  - Unchanged: {stats['unchanged']}
  - Errors: {stats['errors']}
""")
        
        logger.info("Check your Google Drive folder to verify the folder structure!")
        logger.info("Expected structure:")
        for key in created_keys:
            logger.info(f"  - {key}")
        
        input("\nPress Enter to continue to cleanup (or Ctrl+C to abort)...")
        
        # Test 2: Sync with preserve_structure=False
        logger.info("\n=== Test 2: Sync with PRESERVE_STRUCTURE=False ===")
        sync_manager_flat = SyncManager(s3_client, gdrive_client, preserve_structure=False)
        stats_flat = sync_manager_flat.sync()
        
        logger.info(f"""
Results:
  - Uploaded: {stats_flat['uploaded']}
  - Updated: {stats_flat['updated']}
  - Deleted: {stats_flat['deleted']}
  - Unchanged: {stats_flat['unchanged']}
  - Errors: {stats_flat['errors']}
""")
        
        logger.info("Check your Google Drive folder to see flattened filenames!")
        logger.info("Expected filenames:")
        for key in created_keys:
            flattened = key.replace('/', '_')
            logger.info(f"  - {flattened}")
        
        input("\nPress Enter to cleanup...")
        
    finally:
        # Cleanup
        cleanup_test_files(s3_client, created_keys)
        logger.info("\n=== Test completed ===")


if __name__ == '__main__':
    main()
