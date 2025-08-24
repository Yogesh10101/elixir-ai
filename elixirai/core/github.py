"""GitHub integration functionality for Elixir AI"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
import requests
from urllib.parse import urlparse, urljoin


def clone_or_download_github(url: str, dest: str) -> str:
    """Clone or download a GitHub repository"""
    try:
        # Parse GitHub URL
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc:
            raise ValueError("Not a GitHub URL")
        
        # Extract owner and repo from path
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        # Handle branch specification
        branch = 'main'
        if len(path_parts) > 2 and path_parts[2] == 'tree':
            if len(path_parts) > 3:
                branch = path_parts[3]
        
        # Try main first, then master
        branches_to_try = [branch]
        if branch == 'main':
            branches_to_try.append('master')
        elif branch == 'master':
            branches_to_try.append('main')
        
        # Download repository
        for try_branch in branches_to_try:
            try:
                return _download_github_zip(owner, repo, try_branch, dest)
            except Exception as e:
                if try_branch == branches_to_try[-1]:  # Last attempt
                    raise e
                continue
                
    except Exception as e:
        raise RuntimeError(f"Failed to download GitHub repository: {e}")


def _download_github_zip(owner: str, repo: str, branch: str, dest: str) -> str:
    """Download GitHub repository as ZIP file"""
    # Create destination directory
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # GitHub API URL for zipball
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    
    # Download ZIP file
    print(f"Downloading {owner}/{repo} ({branch})...")
    response = requests.get(zip_url, stream=True)
    response.raise_for_status()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file_path = temp_file.name
    
    try:
        # Extract ZIP file
        print("Extracting files...")
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(dest_path)
        
        # Find the extracted directory (GitHub adds branch name suffix)
        extracted_dirs = [d for d in dest_path.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise RuntimeError("No directories found in extracted ZIP")
        
        extracted_dir = extracted_dirs[0]
        
        # Move contents up one level if needed
        if extracted_dir.name != repo:
            repo_path = dest_path / repo
            if repo_path.exists():
                import shutil
                shutil.rmtree(repo_path)
            
            extracted_dir.rename(repo_path)
            final_path = repo_path
        else:
            final_path = extracted_dir
        
        print(f"[OK] Repository downloaded to {final_path}")
        return str(final_path)
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


def get_github_info(url: str) -> dict:
    """Get information about a GitHub repository"""
    try:
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc:
            raise ValueError("Not a GitHub URL")
        
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        # GitHub API URL
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        # Get repository information
        response = requests.get(api_url)
        response.raise_for_status()
        
        repo_info = response.json()
        
        return {
            'owner': owner,
            'repo': repo,
            'name': repo_info.get('name', repo),
            'description': repo_info.get('description', ''),
            'language': repo_info.get('language', ''),
            'stars': repo_info.get('stargazers_count', 0),
            'forks': repo_info.get('forks_count', 0),
            'default_branch': repo_info.get('default_branch', 'main'),
            'url': repo_info.get('html_url', url)
        }
        
    except Exception as e:
        return {'error': str(e)}


def is_github_url(url: str) -> bool:
    """Check if a URL is a GitHub repository URL"""
    try:
        parsed = urlparse(url)
        return 'github.com' in parsed.netloc and len(parsed.path.strip('/').split('/')) >= 2
    except Exception:
        return False
