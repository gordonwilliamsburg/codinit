import shutil
import pytest
import os
from codinit.codebaseKG import clone_repo, check_if_repo_has_been_cloned, check_if_repo_has_been_embedded, clone_repo_if_not_exists, embed_repository_if_not_exists
from unittest.mock import Mock, patch
@pytest.fixture
def repo_url():
    return "https://github.com/gordonwilliamsburg/test-repo.git"

# Test the clone_repo function

def test_clone_repo_success(tmp_path, repo_url):
    """
    Test successful cloning of a repository.
    """
    local_dir = tmp_path / "test_repo"

    clone_repo(repo_url, str(local_dir))

    # Check if the directory exists and is not empty
    assert os.path.isdir(local_dir) and os.listdir(local_dir)

def test_clone_repo_invalid_url(tmp_path):
    """
    Test cloning with an invalid URL.
    """
    repo_url = "https://github.com/invalid/repo.git"  # An invalid repo URL
    local_dir = tmp_path / "test_repo"

    with pytest.raises(Exception):
        clone_repo(repo_url, str(local_dir))

def test_clone_repo_with_readme(tmp_path, repo_url):
    """
    Test that the repository with only a README file is cloned successfully.
    """
    local_dir = tmp_path / "test_repo"

    clone_repo(repo_url, str(local_dir))

    # Check if README file exists in the cloned directory
    assert os.path.isfile(local_dir / "README.md")

# Test for check_if_repo_has_been_cloned
def test_check_if_repo_has_been_cloned_returns_true_if_directory_exists(tmp_path):
    # Create a temporary directory
    repo_dir = tmp_path / "test_repo"
    os.makedirs(repo_dir)
    dir = str(repo_dir)

    # Test with a directory that exists
    result = check_if_repo_has_been_cloned(repo_dir=dir)
    # Check if the function correctly identifies the directory
    assert result is True

def test_check_if_repo_has_been_cloned_returns_false_if_directory_does_not_exist(tmp_path):
    # Test with a non-existent directory
    assert check_if_repo_has_been_cloned(str(tmp_path / "non_existent_repo")) is False


# Test for check_if_repo_has_been_embedded
def test_check_if_repo_has_been_embedded_returns_true_if_repo_exists_in_weaviate():
    repo_dir = "test_repo"

    # Mocking Weaviate client and its method chain
    mock_client = Mock()
    mock_client.query.get().with_where().do.return_value = {
        "data": {
            "Get": {
                "Repository": [{"name": repo_dir}]  # Mocked response for existing repo
            }
        }
    }

    # Test with existing repo
    assert check_if_repo_has_been_embedded(repo_dir, mock_client) is True

def test_check_if_repo_has_been_embedded_returns_false_if_repo_does_not_exist_in_weaviate():
    repo_dir = "test_repo"

    # Mocking Weaviate client and its method chain
    mock_client = Mock()

    # set mock return value to simulate non-existing repo
    mock_client.query.get().with_where().do.return_value = {
        "data": {
            "Get": {
                "Repository": []  # Empty list to simulate non-existing repo
            }
        }
    }

    # Test with non-existing repo
    assert check_if_repo_has_been_embedded(repo_dir, mock_client) is False

# Test for clone_repo_if_not_exists
def setup_function(function):
    # Setup that runs before each test function
    # Create a clean directory for cloning
    os.makedirs("/tmp/test_clone_repo", exist_ok=True)

def teardown_function(function):
    # Teardown that runs after each test function
    # Clean up the directory
    shutil.rmtree("/tmp/test_clone_repo")

def test_clone_repo_if_not_exists_not_cloned(repo_url):
    local_dir = "/tmp/test_clone_repo"

    # Test cloning when the repo hasn't been cloned yet
    clone_repo_if_not_exists(repo_url, local_dir)

    # Check if the repo is cloned
    assert os.path.isdir(local_dir)
    # Further checks can be added to verify the contents of the cloned repo

def test_clone_repo_if_not_exists_already_cloned(repo_url):
    local_dir = "/tmp/test_clone_repo"

    # First clone to ensure the repo is already there
    clone_repo_if_not_exists(repo_url, local_dir)

    # Test cloning again when the repo has already been cloned
    clone_repo_if_not_exists(repo_url, local_dir)

    # The test here can be to check that it didn't re-clone unnecessarily
    # Use patch to capture logging output
    with patch('logging.info') as mock_logging_info:
        # Test cloning again when the repo has already been cloned
        clone_repo_if_not_exists(repo_url, local_dir)

        # Check that the specific log message was emitted
        mock_logging_info.assert_called_with(f"Repository has already been cloned to {local_dir}")

def setup_test_repo(tmp_path):
    # Create a temporary directory to mimic a repository
    test_repo_dir = tmp_path / "test_repo"
    test_repo_dir.mkdir()
    # Add test files or directories as needed
    return test_repo_dir

@pytest.fixture
def test_repo_dir(tmp_path):
    return setup_test_repo(tmp_path)

def test_embed_repository_if_not_exists(test_embedded_weaviate_client, test_repo_dir, repo_url):

    # Test embedding when the repo has not been embedded yet
    embed_repository_if_not_exists(str(test_repo_dir), repo_url, test_embedded_weaviate_client)

    # Verify the repository is now embedded
    assert check_if_repo_has_been_embedded(str(test_repo_dir), test_embedded_weaviate_client)


def test_embed_repository_if_not_exists_already_embedded_does_not_reembed(test_embedded_weaviate_client, test_repo_dir, repo_url):
    # Test embedding when the repo has not been embedded yet
    embed_repository_if_not_exists(str(test_repo_dir), repo_url, test_embedded_weaviate_client)

    # Use patch to capture logging output
    with patch('logging.info') as mock_logging_info:
        # Test embedding again when the repo has already been embedded
        embed_repository_if_not_exists(str(test_repo_dir), repo_url, test_embedded_weaviate_client)

        # Check that the specific log message was emitted
        mock_logging_info.assert_any_call(f"Repository {str(test_repo_dir)}= has already been embedded to Weaviate")
