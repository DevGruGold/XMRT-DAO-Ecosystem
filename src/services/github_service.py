"""
GitHub Integration Service

This module provides GitHub integration capabilities for the XMRT DAO Ecosystem,
enabling autonomous repository management, code deployment, and self-improvement
through GitHub operations.
"""

import logging
from typing import Dict, List, Any, Optional
from github import Github
from github.Repository import Repository
from github.ContentFile import ContentFile
import base64
import json

class GitHubService:
    """
    GitHub integration service for autonomous operations.
    
    Capabilities:
    - Repository management
    - Code deployment
    - Autonomous commits and pushes
    - Repository analysis
    - Self-improvement through code updates
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # GitHub configuration
        self.token = config.get('github_token')
        self.username = config.get('github_username')
        self.email = config.get('github_email')
        
        # Initialize GitHub client
        self.github = Github(self.token) if self.token else None
        self.user = self.github.get_user() if self.github else None
        
        self.logger.info("GitHub Service initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('github_service')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def create_repository(self, name: str, description: str = "", private: bool = True) -> Optional[Repository]:
        """Create a new GitHub repository."""
        try:
            if not self.user:
                self.logger.error("GitHub user not initialized")
                return None
            
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=True
            )
            
            self.logger.info(f"Created repository: {name}")
            return repo
            
        except Exception as e:
            self.logger.error(f"Error creating repository {name}: {e}")
            return None
    
    async def get_repository(self, repo_name: str) -> Optional[Repository]:
        """Get a repository by name."""
        try:
            if not self.user:
                self.logger.error("GitHub user not initialized")
                return None
            
            repo = self.user.get_repo(repo_name)
            return repo
            
        except Exception as e:
            self.logger.error(f"Error getting repository {repo_name}: {e}")
            return None
    
    async def create_file(self, repo: Repository, path: str, content: str, message: str) -> bool:
        """Create a new file in the repository."""
        try:
            repo.create_file(path, message, content)
            self.logger.info(f"Created file: {path} in {repo.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating file {path}: {e}")
            return False
    
    async def update_file(self, repo: Repository, path: str, content: str, message: str) -> bool:
        """Update an existing file in the repository."""
        try:
            # Get the current file to get its SHA
            file = repo.get_contents(path)
            repo.update_file(path, message, content, file.sha)
            self.logger.info(f"Updated file: {path} in {repo.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating file {path}: {e}")
            return False
    
    async def create_or_update_file(self, repo: Repository, path: str, content: str, message: str) -> bool:
        """Create a new file or update existing file."""
        try:
            # Try to get the file first
            try:
                file = repo.get_contents(path)
                # File exists, update it
                repo.update_file(path, message, content, file.sha)
                self.logger.info(f"Updated existing file: {path} in {repo.name}")
            except:
                # File doesn't exist, create it
                repo.create_file(path, message, content)
                self.logger.info(f"Created new file: {path} in {repo.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating/updating file {path}: {e}")
            return False
    
    async def get_file_content(self, repo: Repository, path: str) -> Optional[str]:
        """Get the content of a file from the repository."""
        try:
            file = repo.get_contents(path)
            if isinstance(file, list):
                return None  # Path is a directory
            
            content = base64.b64decode(file.content).decode('utf-8')
            return content
            
        except Exception as e:
            self.logger.error(f"Error getting file content {path}: {e}")
            return None
    
    async def list_repositories(self) -> List[str]:
        """List all repositories for the user."""
        try:
            if not self.user:
                self.logger.error("GitHub user not initialized")
                return []
            
            repos = self.user.get_repos()
            repo_names = [repo.name for repo in repos]
            return repo_names
            
        except Exception as e:
            self.logger.error(f"Error listing repositories: {e}")
            return []
    
    async def analyze_repository(self, repo_name: str) -> Dict[str, Any]:
        """Analyze a repository for improvement opportunities."""
        try:
            repo = await self.get_repository(repo_name)
            if not repo:
                return {}
            
            analysis = {
                'name': repo.name,
                'description': repo.description,
                'language': repo.language,
                'size': repo.size,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'issues': repo.open_issues_count,
                'last_updated': repo.updated_at.isoformat(),
                'has_readme': False,
                'has_license': False,
                'has_ci': False,
                'improvement_opportunities': []
            }
            
            # Check for README
            try:
                repo.get_contents("README.md")
                analysis['has_readme'] = True
            except:
                analysis['improvement_opportunities'].append("Add README.md")
            
            # Check for LICENSE
            try:
                repo.get_contents("LICENSE")
                analysis['has_license'] = True
            except:
                analysis['improvement_opportunities'].append("Add LICENSE file")
            
            # Check for CI/CD
            try:
                repo.get_contents(".github/workflows")
                analysis['has_ci'] = True
            except:
                analysis['improvement_opportunities'].append("Add CI/CD workflows")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing repository {repo_name}: {e}")
            return {}
    
    async def deploy_application(self, repo_name: str, app_config: Dict[str, Any]) -> bool:
        """Deploy an application to a GitHub repository."""
        try:
            repo = await self.get_repository(repo_name)
            if not repo:
                # Create repository if it doesn't exist
                repo = await self.create_repository(repo_name, app_config.get('description', ''))
                if not repo:
                    return False
            
            # Deploy application files
            app_type = app_config.get('type', 'generic')
            
            if app_type == 'flask':
                await self._deploy_flask_app(repo, app_config)
            elif app_type == 'react':
                await self._deploy_react_app(repo, app_config)
            elif app_type == 'dapp':
                await self._deploy_dapp(repo, app_config)
            else:
                await self._deploy_generic_app(repo, app_config)
            
            self.logger.info(f"Deployed application to repository: {repo_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying application to {repo_name}: {e}")
            return False
    
    async def _deploy_flask_app(self, repo: Repository, config: Dict[str, Any]):
        """Deploy a Flask application."""
        # Create basic Flask app structure
        app_py = '''from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "XMRT DAO Application", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
        
        requirements = '''flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
'''
        
        await self.create_or_update_file(repo, "app.py", app_py, "Deploy Flask application")
        await self.create_or_update_file(repo, "requirements.txt", requirements, "Add requirements")
    
    async def _deploy_react_app(self, repo: Repository, config: Dict[str, Any]):
        """Deploy a React application."""
        # Create basic React app files
        package_json = '''{
  "name": "xmrt-dao-app",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}'''
        
        await self.create_or_update_file(repo, "package.json", package_json, "Deploy React application")
    
    async def _deploy_dapp(self, repo: Repository, config: Dict[str, Any]):
        """Deploy a decentralized application."""
        # Create basic dApp structure
        await self._deploy_react_app(repo, config)  # dApp frontend
        
        # Add Web3 dependencies
        package_json_content = await self.get_file_content(repo, "package.json")
        if package_json_content:
            package_data = json.loads(package_json_content)
            package_data["dependencies"]["web3"] = "^4.0.0"
            package_data["dependencies"]["ethers"] = "^6.0.0"
            
            await self.create_or_update_file(
                repo, 
                "package.json", 
                json.dumps(package_data, indent=2), 
                "Add Web3 dependencies"
            )
    
    async def _deploy_generic_app(self, repo: Repository, config: Dict[str, Any]):
        """Deploy a generic application."""
        readme = f'''# {config.get('name', 'XMRT DAO Application')}

{config.get('description', 'An autonomous application created by Eliza for the XMRT DAO Ecosystem.')}

## Features

- Autonomous operation
- XMRT DAO integration
- Self-improvement capabilities

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```
'''
        
        await self.create_or_update_file(repo, "README.md", readme, "Add README")
    
    def get_status(self) -> Dict[str, Any]:
        """Get GitHub service status."""
        return {
            'initialized': self.github is not None,
            'username': self.username,
            'user_authenticated': self.user is not None
        }

