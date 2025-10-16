"""
Main application entry point
Runs the S3 to Google Drive synchronization
"""

import logging
import os
import sys
import time

from dotenv import load_dotenv

from src.gdrive_client import GDriveClient
from src.gdrive_oauth2_client import GDriveOAuth2Client
from src.s3_client import S3Client
from src.sync_manager import SyncManager


def setup_logging(log_level: str = "INFO"):
    """
    Configure logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("sync.log")
        ]
    )


def validate_env_vars():
    """Validate that all required environment variables are set"""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'S3_BUCKET_NAME',
        'GDRIVE_FOLDER_ID',
        'GDRIVE_CREDENTIALS_PATH'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


def main():
    """Main application function"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting S3 to Google Drive Sync Application")
    
    try:
        # Validate environment variables
        validate_env_vars()
        
        # Get configuration from environment
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION')
        s3_bucket = os.getenv('S3_BUCKET_NAME')
        s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')  # Endpoint personalizzato (opzionale)
        gdrive_folder_id = os.getenv('GDRIVE_FOLDER_ID')
        gdrive_credentials_path = os.getenv('GDRIVE_CREDENTIALS_PATH')
        sync_interval = int(os.getenv('SYNC_INTERVAL_SECONDS', '300'))
        
        # Initialize clients
        logger.info("Initializing S3 client...")
        s3_client = S3Client(
            access_key=aws_access_key,
            secret_key=aws_secret_key,
            region=aws_region,
            bucket_name=s3_bucket,
            endpoint_url=s3_endpoint_url  # Passa endpoint personalizzato
        )
        
        logger.info("Initializing Google Drive client...")
        
        # Check if using OAuth2 or Service Account
        use_oauth2 = os.getenv('GDRIVE_USE_OAUTH2', 'true').lower() == 'true'
        
        if use_oauth2:
            logger.info("Using OAuth2 authentication")
            token_path = os.getenv('GDRIVE_TOKEN_PATH', 'token.pickle')
            gdrive_client = GDriveOAuth2Client(
                credentials_path=gdrive_credentials_path,
                folder_id=gdrive_folder_id,
                token_path=token_path
            )
        else:
            logger.info("Using Service Account authentication (deprecated - use OAuth2)")
            gdrive_client = GDriveClient(
                credentials_path=gdrive_credentials_path,
                folder_id=gdrive_folder_id
            )
        
        # Get preserve structure option (default: True to maintain S3 folder structure)
        preserve_structure = os.getenv('PRESERVE_STRUCTURE', 'true').lower() == 'true'
        
        # Initialize sync manager
        sync_manager = SyncManager(s3_client, gdrive_client, preserve_structure=preserve_structure)
        
        logger.info(f"Path handling: {'Preserve S3 folder structure' if preserve_structure else 'Flatten to root (replace / with _)'}")
        
        # Run sync loop
        logger.info(f"Starting sync loop (interval: {sync_interval} seconds)")
        
        while True:
            try:
                stats = sync_manager.sync()
                
                logger.info(
                    f"Sync completed - "
                    f"Uploaded: {stats['uploaded']}, "
                    f"Updated: {stats['updated']}, "
                    f"Deleted: {stats['deleted']}, "
                    f"Unchanged: {stats['unchanged']}, "
                    f"Errors: {stats['errors']}"
                )
                
                logger.info(f"Waiting {sync_interval} seconds before next sync...")
                time.sleep(sync_interval)
            
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            
            except Exception as e:
                logger.error(f"Error during sync: {e}", exc_info=True)
                logger.info(f"Waiting {sync_interval} seconds before retry...")
                time.sleep(sync_interval)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
