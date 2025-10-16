"""
Test configuration and fixtures
"""

import pytest
import os
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing"""
    mock = Mock()
    mock.bucket_name = "test-bucket"
    mock.list_files = Mock(return_value=[])
    mock.download_file = Mock(return_value=True)
    mock.file_exists = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_gdrive_client():
    """Mock Google Drive client for testing"""
    mock = Mock()
    mock.folder_id = "test-folder-id"
    mock.list_files = Mock(return_value=[])
    mock.upload_file = Mock(return_value="file-id-123")
    mock.delete_file = Mock(return_value=True)
    mock.find_file_by_name = Mock(return_value=None)
    mock.update_file = Mock(return_value=True)
    return mock


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing"""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("This is a test file")
    return str(test_file)
