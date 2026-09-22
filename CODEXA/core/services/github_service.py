import os
import re
import shutil
import tempfile
import logging
from typing import Dict, Any, Optional, Tuple
from django.utils import timezone
import requests
import git

logger = logging.getLogger(__name__)


class GitHubServiceError(Exception):
    """Custom exception for GitHub operations."""
    pass


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Extracts owner and repository name from various GitHub URL formats.
    
    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - http://github.com/owner/repo
    - git@github.com:owner/repo.git
    """
    cleaned_url = url.strip()
    
    # HTTPS / HTTP format
    https_pattern = r'^(?:https?:\/\/)?(?:www\.)?github\.com\/([^\/]+)\/([^\/\.]+)(?:\.git)?(?:\/)?$'
    match = re.match(https_pattern, cleaned_url, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
        
    # SSH format
    ssh_pattern = r'^git@github\.com:([^\/]+)\/([^\/\.]+)(?:\.git)?$'
    match = re.match(ssh_pattern, cleaned_url, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
        
    raise GitHubServiceError(f"Invalid GitHub URL format: {url}")


def fetch_github_metadata(owner: str, repo: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches repository metadata from GitHub REST API v3.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CODEXA-Code-Analysis-Engine"
    }
    if token:
        headers["Authorization"] = f"token {token}"
        
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "owner": data.get("owner", {}).get("login"),
                "description": data.get("description", ""),
                "default_branch": data.get("default_branch", "main"),
                "size_kb": data.get("size", 0),
                "stargazers_count": data.get("stargazers_count", 0),
                "forks_count": data.get("forks_count", 0),
                "open_issues_count": data.get("open_issues_count", 0),
                "language": data.get("language", ""),
                "is_private": data.get("private", False),
                "html_url": data.get("html_url"),
                "clone_url": data.get("clone_url"),
            }
        elif response.status_code == 404:
            raise GitHubServiceError(f"Repository '{owner}/{repo}' not found on GitHub or is private without token.")
        elif response.status_code == 403:
            raise GitHubServiceError("GitHub API rate limit exceeded or access forbidden.")
        else:
            raise GitHubServiceError(f"GitHub API returned error {response.status_code}: {response.text}")
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch GitHub metadata: {e}")
        return {
            "name": repo,
            "owner": owner,
            "default_branch": "main",
            "error": str(e)
        }


def clone_github_repo(
    github_url: str,
    target_dir: Optional[str] = None,
    depth: int = 1,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches GitHub metadata and clones the repository into a designated or temporary folder.

    Returns a dictionary with:
    - success: bool
    - owner: str
    - name: str
    - clone_path: str
    - metadata: dict
    - cloned_at: datetime
    """
    owner, repo_name = parse_github_url(github_url)
    metadata = fetch_github_metadata(owner, repo_name, token=token)

    # Determine clone target directory
    if not target_dir:
        target_dir = tempfile.mkdtemp(prefix=f"codexa_{repo_name}_")

    # If auth token provided for private repo cloning
    clone_url = github_url
    if token and "https://" in github_url:
        clone_url = github_url.replace("https://", f"https://x-access-token:{token}@")

    try:
        logger.info(f"Cloning {owner}/{repo_name} to {target_dir} (depth={depth})...")
        git.Repo.clone_from(
            url=clone_url,
            to_path=target_dir,
            depth=depth,
            single_branch=True
        )
        
        return {
            "success": True,
            "owner": owner,
            "name": repo_name,
            "github_url": github_url,
            "clone_path": os.path.abspath(target_dir),
            "cloned_at": timezone.now(),
            "metadata": metadata
        }
    except git.GitCommandError as e:
        # Clean up failed directory
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
        raise GitHubServiceError(f"Git clone failed: {e.stderr if hasattr(e, 'stderr') else str(e)}")
    except Exception as e:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
        raise GitHubServiceError(f"Unexpected clone error: {str(e)}")


def cleanup_cloned_repo(path: str) -> bool:
    """
    Safely deletes temporary cloned repository folder from disk.
    Handles read-only files (common on Windows .git directory).
    """
    def _onerror(func, path, exc_info):
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if os.path.exists(path):
        shutil.rmtree(path, onerror=_onerror)
        return True
    return False
