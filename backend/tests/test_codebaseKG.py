import pytest
import os
from codinit.codebaseKG import clone_repo, check_if_repo_has_been_cloned, check_if_repo_has_been_embedded
from unittest.mock import Mock

# Test the clone_repo function

def test_clone_repo_success(tmp_path):
    """
    Test successful cloning of a repository.
    """
    repo_url = "https://github.com/gordonwilliamsburg/test-repo.git"  # Replace with a real repo URL for testing
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

def test_clone_repo_with_readme(tmp_path):
    """
    Test that the repository with only a README file is cloned successfully.
    """
    repo_url = "https://github.com/gordonwilliamsburg/test-repo.git"  # Replace with your repository URL
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
