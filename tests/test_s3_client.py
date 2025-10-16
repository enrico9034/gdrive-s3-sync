"""
Unit tests for S3 Client
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from botocore.exceptions import ClientError

from src.s3_client import S3Client


class TestS3Client:
    """Test suite for S3Client"""
    
    @patch('src.s3_client.boto3')
    def test_init(self, mock_boto3):
        """Test S3Client initialization"""
        client = S3Client(
            access_key="test-key",
            secret_key="test-secret",
            region="us-east-1",
            bucket_name="test-bucket"
        )
        
        assert client.bucket_name == "test-bucket"
        assert client.endpoint_url is None
        mock_boto3.client.assert_called_once()
    
    @patch('src.s3_client.boto3')
    def test_init_with_custom_endpoint(self, mock_boto3):
        """Test S3Client initialization with custom endpoint"""
        custom_endpoint = "http://localhost:9000"
        client = S3Client(
            access_key="test-key",
            secret_key="test-secret",
            region="us-east-1",
            bucket_name="test-bucket",
            endpoint_url=custom_endpoint
        )
        
        assert client.bucket_name == "test-bucket"
        assert client.endpoint_url == custom_endpoint
        
        # Verify boto3.client was called with endpoint_url
        call_kwargs = mock_boto3.client.call_args[1]
        assert call_kwargs['endpoint_url'] == custom_endpoint
    
    @patch('src.s3_client.boto3')
    def test_list_files_success(self, mock_boto3):
        """Test listing files successfully"""
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'file1.txt',
                    'Size': 100,
                    'LastModified': '2024-01-01',
                    'ETag': '"abc123"'
                },
                {
                    'Key': 'file2.txt',
                    'Size': 200,
                    'LastModified': '2024-01-02',
                    'ETag': '"def456"'
                }
            ]
        }
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        files = client.list_files()
        
        assert len(files) == 2
        assert files[0]['key'] == 'file1.txt'
        assert files[0]['size'] == 100
        assert files[1]['key'] == 'file2.txt'
    
    @patch('src.s3_client.boto3')
    def test_list_files_empty(self, mock_boto3):
        """Test listing files when bucket is empty"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {}
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        files = client.list_files()
        
        assert files == []
    
    @patch('src.s3_client.boto3')
    def test_download_file_success(self, mock_boto3, tmp_path):
        """Test downloading file successfully"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        local_path = str(tmp_path / "downloaded.txt")
        
        result = client.download_file("file.txt", local_path)
        
        assert result is True
        mock_s3.download_file.assert_called_once_with("bucket", "file.txt", local_path)
    
    @patch('src.s3_client.boto3')
    def test_download_file_error(self, mock_boto3, tmp_path):
        """Test download file with error"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.download_file.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'download_file'
        )
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.download_file("file.txt", "/tmp/file.txt")
        
        assert result is False
    
    @patch('src.s3_client.boto3')
    def test_file_exists_true(self, mock_boto3):
        """Test file_exists returns True"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.head_object.return_value = {'ContentLength': 100}
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.file_exists("file.txt")
        
        assert result is True
    
    @patch('src.s3_client.boto3')
    def test_file_exists_false(self, mock_boto3):
        """Test file_exists returns False"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.head_object.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'head_object'
        )
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.file_exists("file.txt")
        
        assert result is False
    
    @patch('src.s3_client.boto3')
    def test_upload_file_success(self, mock_boto3, tmp_path):
        """Test upload file successfully"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        # Create a test file
        test_file = tmp_path / "upload.txt"
        test_file.write_text("test content")
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.upload_file(str(test_file), "uploaded.txt")
        
        assert result is True
        mock_s3.upload_file.assert_called_once_with(str(test_file), "bucket", "uploaded.txt")
    
    @patch('src.s3_client.boto3')
    def test_upload_file_error(self, mock_boto3, tmp_path):
        """Test upload file with error"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.upload_file.side_effect = ClientError(
            {'Error': {'Code': '500', 'Message': 'Internal Error'}},
            'upload_file'
        )
        
        # Create a test file
        test_file = tmp_path / "upload.txt"
        test_file.write_text("test content")
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.upload_file(str(test_file), "uploaded.txt")
        
        assert result is False
    
    @patch('src.s3_client.boto3')
    def test_delete_file_success(self, mock_boto3):
        """Test delete file successfully"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.delete_file("file.txt")
        
        assert result is True
        mock_s3.delete_object.assert_called_once_with(Bucket="bucket", Key="file.txt")
    
    @patch('src.s3_client.boto3')
    def test_delete_file_error(self, mock_boto3):
        """Test delete file with error"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.delete_object.side_effect = ClientError(
            {'Error': {'Code': '500', 'Message': 'Internal Error'}},
            'delete_object'
        )
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        result = client.delete_file("file.txt")
        
        assert result is False
    
    @patch('src.s3_client.boto3')
    def test_list_files_filters_directories(self, mock_boto3):
        """Test that list_files filters out directory markers"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'dir1/', 'Size': 0, 'LastModified': '2024-01-01', 'ETag': 'abc'},
                {'Key': 'dir1/file.txt', 'Size': 100, 'LastModified': '2024-01-01', 'ETag': 'def'},
                {'Key': 'dir2/', 'Size': 0, 'LastModified': '2024-01-01', 'ETag': 'ghi'},
                {'Key': 'file.txt', 'Size': 50, 'LastModified': '2024-01-01', 'ETag': 'jkl'},
            ]
        }
        
        client = S3Client("key", "secret", "us-east-1", "bucket")
        files = client.list_files()
        
        # Should only return actual files, not directory markers
        assert len(files) == 2
        assert files[0]['key'] == 'dir1/file.txt'
        assert files[1]['key'] == 'file.txt'
