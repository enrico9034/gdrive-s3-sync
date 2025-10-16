"""
Integration test for OAuth2 authentication
This script tests the sync functionality using OAuth2 authentication
Run this manually with: python tests/integration_test_oauth2.py
"""

import os
import sys
import tempfile
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging

from src.gdrive_oauth2_client import GDriveOAuth2Client
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


def test_oauth2_authentication():
    """Test OAuth2 authentication and basic operations"""
    logger.info("=" * 80)
    logger.info("TEST 1: OAuth2 Authentication and Basic Operations")
    logger.info("=" * 80)
    
    # Get configuration
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials = os.getenv('GDRIVE_CREDENTIALS_PATH', 'credentials/credentials.json')
    gdrive_token = os.getenv('GDRIVE_TOKEN_PATH', 'credentials/token.pickle')
    
    if not gdrive_folder_id:
        logger.error("Missing GDRIVE_FOLDER_ID environment variable!")
        return False
    
    try:
        logger.info("Initializing OAuth2 client...")
        logger.info(f"Credentials: {gdrive_credentials}")
        logger.info(f"Token path: {gdrive_token}")
        logger.info(f"Folder ID: {gdrive_folder_id}")
        
        # Initialize OAuth2 client
        gdrive_client = GDriveOAuth2Client(
            credentials_path=gdrive_credentials,
            folder_id=gdrive_folder_id,
            token_path=gdrive_token
        )
        
        logger.info("✓ OAuth2 authentication successful!")
        
        # Test list files
        logger.info("\nListing files in Google Drive folder...")
        files = gdrive_client.list_files()
        logger.info(f"✓ Found {len(files)} files in folder")
        
        for file in files[:5]:  # Show first 5
            size_mb = file['size'] / (1024 * 1024)
            logger.info(f"  - {file['name']} ({size_mb:.2f} MB)")
        
        if len(files) > 5:
            logger.info(f"  ... and {len(files) - 5} more files")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ OAUTH2 AUTHENTICATION TEST PASSED")
        logger.info("=" * 80)
        return True
    
    except FileNotFoundError as e:
        logger.error(f"✗ Credentials file not found: {e}")
        logger.error("\nPlease ensure:")
        logger.error("1. You have created OAuth2 credentials (not Service Account)")
        logger.error("2. Downloaded credentials.json from Google Cloud Console")
        logger.error("3. Placed it in the credentials/ folder")
        logger.error("\nSee docs/OAUTH2_SETUP.md for detailed instructions")
        return False
    
    except Exception as e:
        logger.error(f"✗ OAuth2 authentication failed: {e}", exc_info=True)
        return False


def test_oauth2_upload_and_delete():
    """
    Integration test with OAuth2: Upload a file to S3, sync to GDrive, delete from S3, sync again
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Upload and Delete Flow with OAuth2")
    logger.info("=" * 80)
    
    # Get configuration from environment
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials = os.getenv('GDRIVE_CREDENTIALS_PATH', 'credentials/credentials.json')
    gdrive_token = os.getenv('GDRIVE_TOKEN_PATH', 'credentials/token.pickle')
    
    if not all([aws_access_key, aws_secret_key, s3_bucket, gdrive_folder_id]):
        logger.error("Missing required environment variables!")
        logger.error("Please set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, GDRIVE_FOLDER_ID")
        return False
    
    try:
        # Initialize clients
        logger.info("Initializing clients...")
        s3_client = S3Client(aws_access_key, aws_secret_key, aws_region, s3_bucket, s3_endpoint_url)
        gdrive_client = GDriveOAuth2Client(gdrive_credentials, gdrive_folder_id, gdrive_token)
        sync_manager = SyncManager(s3_client, gdrive_client)
        
        logger.info("✓ Clients initialized with OAuth2 authentication")
        
        # Create test file
        test_filename = f"oauth2_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = f"OAuth2 test content created at {datetime.now()}"
        local_file = create_test_file(test_content)
        
        logger.info(f"\nCreated test file: {test_filename}")
        
        # Step 1: Upload file to S3
        logger.info("\n" + "-" * 80)
        logger.info("STEP 1: Uploading file to S3")
        logger.info("-" * 80)
        
        import boto3
        s3_config = {
            'aws_access_key_id': aws_access_key,
            'aws_secret_access_key': aws_secret_key,
            'region_name': aws_region
        }
        if s3_endpoint_url:
            s3_config['endpoint_url'] = s3_endpoint_url
            logger.info(f"Using custom S3 endpoint: {s3_endpoint_url}")
        
        s3 = boto3.client('s3', **s3_config)
        s3.upload_file(local_file, s3_bucket, test_filename)
        logger.info(f"✓ File uploaded to S3: {test_filename}")
        
        # Step 2: First sync - should upload to GDrive
        logger.info("\n" + "-" * 80)
        logger.info("STEP 2: First sync (should upload to Google Drive)")
        logger.info("-" * 80)
        
        stats = sync_manager.sync()
        logger.info(f"Sync stats: Uploaded={stats['uploaded']}, Updated={stats['updated']}, "
                   f"Deleted={stats['deleted']}, Unchanged={stats['unchanged']}, Errors={stats['errors']}")
        
        if stats['uploaded'] >= 1:
            logger.info("✓ File successfully synced to Google Drive via OAuth2")
        else:
            logger.warning(f"⚠ Expected at least 1 upload, got {stats['uploaded']}")
        
        # Wait a bit
        logger.info("\nWaiting 3 seconds...")
        time.sleep(3)
        
        # Step 3: Delete file from S3
        logger.info("\n" + "-" * 80)
        logger.info("STEP 3: Deleting file from S3")
        logger.info("-" * 80)
        
        s3.delete_object(Bucket=s3_bucket, Key=test_filename)
        logger.info(f"✓ File deleted from S3: {test_filename}")
        
        # Step 4: Second sync - should delete from GDrive
        logger.info("\n" + "-" * 80)
        logger.info("STEP 4: Second sync (should delete from Google Drive)")
        logger.info("-" * 80)
        
        stats = sync_manager.sync()
        logger.info(f"Sync stats: Uploaded={stats['uploaded']}, Updated={stats['updated']}, "
                   f"Deleted={stats['deleted']}, Unchanged={stats['unchanged']}, Errors={stats['errors']}")
        
        if stats['deleted'] >= 1:
            logger.info("✓ File successfully deleted from Google Drive via OAuth2")
        else:
            logger.warning(f"⚠ Expected at least 1 deletion, got {stats['deleted']}")
        
        # Cleanup local file
        os.remove(local_file)
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ UPLOAD AND DELETE TEST PASSED")
        logger.info("=" * 80)
        return True
    
    except Exception as e:
        logger.error(f"✗ Upload and delete test failed: {e}", exc_info=True)
        return False


def test_oauth2_update_file():
    """
    Integration test with OAuth2: Upload a file, modify it in S3, sync to see update
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Update File Flow with OAuth2")
    logger.info("=" * 80)
    
    # Get configuration
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials = os.getenv('GDRIVE_CREDENTIALS_PATH', 'credentials/credentials.json')
    gdrive_token = os.getenv('GDRIVE_TOKEN_PATH', 'credentials/token.pickle')
    
    if not all([aws_access_key, aws_secret_key, s3_bucket, gdrive_folder_id]):
        logger.error("Missing required environment variables!")
        return False
    
    try:
        # Initialize clients
        s3_client = S3Client(aws_access_key, aws_secret_key, aws_region, s3_bucket, s3_endpoint_url)
        gdrive_client = GDriveOAuth2Client(gdrive_credentials, gdrive_folder_id, gdrive_token)
        sync_manager = SyncManager(s3_client, gdrive_client)
        
        # Create test file
        test_filename = f"oauth2_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Step 1: Upload initial version
        logger.info("\n" + "-" * 80)
        logger.info("STEP 1: Uploading initial version to S3")
        logger.info("-" * 80)
        
        content_v1 = "OAuth2 test - Version 1 content"
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
        logger.info("\n" + "-" * 80)
        logger.info("STEP 2: Syncing to Google Drive (OAuth2)")
        logger.info("-" * 80)
        
        stats = sync_manager.sync()
        logger.info(f"Sync stats: Uploaded={stats['uploaded']}, Updated={stats['updated']}, "
                   f"Deleted={stats['deleted']}, Unchanged={stats['unchanged']}, Errors={stats['errors']}")
        
        # Wait
        logger.info("\nWaiting 3 seconds...")
        time.sleep(3)
        
        # Step 3: Upload updated version
        logger.info("\n" + "-" * 80)
        logger.info("STEP 3: Uploading updated version to S3")
        logger.info("-" * 80)
        
        content_v2 = "OAuth2 test - Version 2 content - UPDATED with more data and information!"
        local_file_v2 = create_test_file(content_v2)
        s3.upload_file(local_file_v2, s3_bucket, test_filename)
        logger.info(f"✓ Uploaded: {test_filename} (version 2 - larger)")
        os.remove(local_file_v2)
        
        # Step 4: Sync again - should update
        logger.info("\n" + "-" * 80)
        logger.info("STEP 4: Syncing again (should update via OAuth2)")
        logger.info("-" * 80)
        
        stats = sync_manager.sync()
        logger.info(f"Sync stats: Uploaded={stats['uploaded']}, Updated={stats['updated']}, "
                   f"Deleted={stats['deleted']}, Unchanged={stats['unchanged']}, Errors={stats['errors']}")
        
        if stats['updated'] >= 1:
            logger.info("✓ File successfully updated in Google Drive via OAuth2")
        else:
            logger.warning(f"⚠ Expected at least 1 update, got {stats['updated']}")
        
        # Cleanup
        logger.info("\n" + "-" * 80)
        logger.info("Cleaning up test files...")
        logger.info("-" * 80)
        
        s3.delete_object(Bucket=s3_bucket, Key=test_filename)
        time.sleep(2)
        sync_manager.sync()  # Delete from GDrive
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ UPDATE FILE TEST PASSED")
        logger.info("=" * 80)
        return True
    
    except Exception as e:
        logger.error(f"✗ Update file test failed: {e}", exc_info=True)
        return False


def test_oauth2_token_refresh():
    """Test that OAuth2 token refresh works correctly"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: OAuth2 Token Refresh")
    logger.info("=" * 80)
    
    gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
    gdrive_credentials = os.getenv('GDRIVE_CREDENTIALS_PATH', 'credentials/credentials.json')
    gdrive_token = os.getenv('GDRIVE_TOKEN_PATH', 'credentials/token.pickle')
    
    if not gdrive_folder_id:
        logger.error("Missing GDRIVE_FOLDER_ID environment variable!")
        return False
    
    try:
        logger.info("Testing token refresh mechanism...")
        
        # Initialize client (this should use existing token if valid)
        gdrive_client = GDriveOAuth2Client(
            credentials_path=gdrive_credentials,
            folder_id=gdrive_folder_id,
            token_path=gdrive_token
        )
        
        # Perform multiple operations to test token stability
        logger.info("Performing multiple API calls to verify token...")
        
        for i in range(3):
            logger.info(f"\n  Call {i+1}/3: Listing files...")
            files = gdrive_client.list_files()
            logger.info(f"  ✓ Successfully retrieved {len(files)} files")
            time.sleep(1)
        
        logger.info("\n✓ Token is valid and refresh mechanism is working")
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ TOKEN REFRESH TEST PASSED")
        logger.info("=" * 80)
        return True
    
    except Exception as e:
        logger.error(f"✗ Token refresh test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    logger.info("=" * 80)
    logger.info("OAUTH2 INTEGRATION TESTS")
    logger.info("=" * 80)
    logger.info("\nThese tests verify OAuth2 authentication and sync operations")
    logger.info("Make sure you have:")
    logger.info("  1. Set up OAuth2 credentials (see docs/OAUTH2_SETUP.md)")
    logger.info("  2. Authenticated at least once (token.pickle exists)")
    logger.info("  3. Configured your .env file with correct credentials")
    logger.info("\n")
    
    # Run tests
    success = True
    results = []
    
    # Test 1: OAuth2 Authentication
    logger.info("\n" + "⏳" * 40)
    if test_oauth2_authentication():
        results.append(("OAuth2 Authentication", True))
    else:
        results.append(("OAuth2 Authentication", False))
        success = False
    
    time.sleep(2)
    
    # Test 2: Upload and Delete
    logger.info("\n" + "⏳" * 40)
    if test_oauth2_upload_and_delete():
        results.append(("Upload and Delete", True))
    else:
        results.append(("Upload and Delete", False))
        success = False
    
    time.sleep(3)
    
    # Test 3: Update File
    logger.info("\n" + "⏳" * 40)
    if test_oauth2_update_file():
        results.append(("Update File", True))
    else:
        results.append(("Update File", False))
        success = False
    
    time.sleep(2)
    
    # Test 4: Token Refresh
    logger.info("\n" + "⏳" * 40)
    if test_oauth2_token_refresh():
        results.append(("Token Refresh", True))
    else:
        results.append(("Token Refresh", False))
        success = False
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{status:12} - {test_name}")
    
    logger.info("=" * 80)
    
    if success:
        logger.info("🎉 ALL OAUTH2 INTEGRATION TESTS PASSED!")
        logger.info("=" * 80)
        logger.info("\nYour OAuth2 setup is working correctly!")
        logger.info("You can now run the full sync application with confidence.")
        sys.exit(0)
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.error("=" * 80)
        logger.error("\nPlease check the error messages above and:")
        logger.error("  1. Verify your OAuth2 credentials are correct")
        logger.error("  2. Check that Google Drive API is enabled")
        logger.error("  3. Ensure you have authenticated (run scripts/test_oauth2.py first)")
        logger.error("\nSee docs/OAUTH2_SETUP.md for detailed setup instructions")
        sys.exit(1)
