"""
Unit tests for Google Drive Client
"""

from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from googleapiclient.errors import HttpError

from src.gdrive_client import GDriveClient


class TestGDriveClient:
    """Test suite for GDriveClient"""
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_init_success(self, mock_build, mock_service_account, mock_exists):
        """Test GDriveClient initialization"""
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_service_account.Credentials.from_service_account_file.return_value = mock_creds
        
        client = GDriveClient(
            credentials_path="/path/to/creds.json",
            folder_id="folder-123"
        )
        
        assert client.folder_id == "folder-123"
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
    
    @patch('src.gdrive_client.os.path.exists')
    def test_init_missing_credentials(self, mock_exists):
        """Test initialization with missing credentials file"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            GDriveClient(
                credentials_path="/path/to/missing.json",
                folder_id="folder-123"
            )
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_list_files_success(self, mock_build, mock_service_account, mock_exists):
        """Test listing files successfully"""
        mock_exists.return_value = True
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.files().list().execute.return_value = {
            'files': [
                {'id': '1', 'name': 'file1.txt', 'size': '100'},
                {'id': '2', 'name': 'file2.txt', 'size': '200'}
            ]
        }
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        files = client.list_files()
        
        assert len(files) == 2
        assert files[0]['name'] == 'file1.txt'
        assert files[1]['name'] == 'file2.txt'
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_upload_file_success(self, mock_build, mock_service_account, mock_exists, temp_file):
        """Test uploading file successfully"""
        mock_exists.return_value = True
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.files().create().execute.return_value = {'id': 'new-file-id'}
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        file_id = client.upload_file(temp_file, "uploaded.txt")
        
        assert file_id == "new-file-id"
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_delete_file_success(self, mock_build, mock_service_account, mock_exists):
        """Test deleting file successfully"""
        mock_exists.return_value = True
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        result = client.delete_file("file-id-123", "file.txt")
        
        assert result is True
        mock_service.files().delete.assert_called_once()
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_find_file_by_name_found(self, mock_build, mock_service_account, mock_exists):
        """Test finding file by name when it exists"""
        mock_exists.return_value = True
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.files().list().execute.return_value = {
            'files': [{'id': 'found-id', 'name': 'test.txt', 'size': '100'}]
        }
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        file_info = client.find_file_by_name("test.txt")
        
        assert file_info is not None
        assert file_info['id'] == 'found-id'
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_find_file_by_name_not_found(self, mock_build, mock_service_account, mock_exists):
        """Test finding file by name when it doesn't exist"""
        mock_exists.return_value = True
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.files().list().execute.return_value = {'files': []}
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        file_info = client.find_file_by_name("nonexistent.txt")
        
        assert file_info is None
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_update_file_success(self, mock_build, mock_service_account, mock_exists, temp_file):
        """Test updating file successfully"""
        mock_exists.return_value = True
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        result = client.update_file("file-id-123", temp_file, "updated.txt")
        
        assert result is True
        mock_service.files().update.assert_called_once()


class TestGDriveFolderOperations:
    """Test suite for folder operations"""
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_create_folder_success(self, mock_build, mock_service_account, mock_exists):
        """Test creating folder successfully"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.files().create().execute.return_value = {'id': 'new-folder-id'}
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        folder_id = client.create_folder("New Folder", "parent-id")
        
        assert folder_id == "new-folder-id"
        # Verify it was created with correct MIME type
        call_args = mock_service.files().create.call_args
        assert call_args[1]['body']['mimeType'] == 'application/vnd.google-apps.folder'
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_find_folder_by_name_found(self, mock_build, mock_service_account, mock_exists):
        """Test finding folder by name when it exists"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.files().list().execute.return_value = {
            'files': [{'id': 'folder-id-123'}]
        }
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        folder_id = client.find_folder_by_name("My Folder", "parent-id")
        
        assert folder_id == "folder-id-123"
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_find_folder_by_name_not_found(self, mock_build, mock_service_account, mock_exists):
        """Test finding folder by name when it doesn't exist"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.files().list().execute.return_value = {'files': []}
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        folder_id = client.find_folder_by_name("Nonexistent", "parent-id")
        
        assert folder_id is None
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_get_or_create_folder_exists(self, mock_build, mock_service_account, mock_exists):
        """Test get_or_create_folder when folder exists"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        
        # Mock find to return existing folder
        with patch.object(client, 'find_folder_by_name', return_value='existing-folder-id'):
            folder_id = client.get_or_create_folder("Existing", "parent-id")
            
            assert folder_id == "existing-folder-id"
            # Should not have called create
            mock_service.files().create.assert_not_called()
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_get_or_create_folder_creates(self, mock_build, mock_service_account, mock_exists):
        """Test get_or_create_folder when folder doesn't exist"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        client = GDriveClient("/path/to/creds.json", "folder-123")
        
        # Mock find to return None, create to return new ID
        with patch.object(client, 'find_folder_by_name', return_value=None), \
             patch.object(client, 'create_folder', return_value='new-folder-id'):
            
            folder_id = client.get_or_create_folder("New Folder", "parent-id")
            
            assert folder_id == "new-folder-id"
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_get_or_create_path_single_level(self, mock_build, mock_service_account, mock_exists):
        """Test get_or_create_path with single directory"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        client = GDriveClient("/path/to/creds.json", "root-folder-123")
        
        with patch.object(client, 'get_or_create_folder', return_value='folder-id-1'):
            folder_id = client.get_or_create_path("docs")
            
            assert folder_id == "folder-id-1"
            client.get_or_create_folder.assert_called_once_with("docs", "root-folder-123")
    
    @patch('src.gdrive_client.os.path.exists')
    @patch('src.gdrive_client.service_account')
    @patch('src.gdrive_client.build')
    def test_get_or_create_path_nested(self, mock_build, mock_service_account, mock_exists):
        """Test get_or_create_path with nested directories"""
        mock_exists.return_value = True
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        client = GDriveClient("/path/to/creds.json", "root-folder-123")
        
        # Mock sequential folder creation
        def mock_get_or_create(name, parent):
            if name == "dir1":
                return "folder-id-1"
            elif name == "dir2":
                return "folder-id-2"
            elif name == "dir3":
                return "folder-id-3"
        
        with patch.object(client, 'get_or_create_folder', side_effect=mock_get_or_create):
            folder_id = client.get_or_create_path("dir1/dir2/dir3")
            
            assert folder_id == "folder-id-3"
            # Should have called 3 times with correct parent chain
            assert client.get_or_create_folder.call_count == 3
