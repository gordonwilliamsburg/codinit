import pytest
import os
from codinit.codebaseKG import clone_repo

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
