"""
GitHub Integration Module for Eliza Agent

This module provides GitHub integration capabilities for the Eliza agent,
enabling autonomous code generation, repository management, and deployment
of new utilities to enhance the XMRT-DAO-Ecosystem.

Features:
- Code generation based on natural language specifications
- GitHub repository management via GitHub API
- Branch creation and pull request management
- Automated code deployment and integration
- Secure credential management
"""

import os
import json
import logging
import requests
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai

class GitHubIntegrationService:
    """
    GitHub Integration Service for autonomous development capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME', 'DevGruGold')
        self.repository_name = 'XMRT-DAO-Ecosystem'
        self.base_url = 'https://api.github.com'
        
        # OpenAI configuration for code generation
        self.openai_client = openai.OpenAI()
        
        # Validate credentials
        if not self.github_token:
            self.logger.warning("GitHub token not found in environment variables")
        
        self.logger.info("GitHub Integration Service initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the service"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _make_github_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to GitHub API"""
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise
    
    def generate_code_from_specification(self, specification: str, file_type: str = "python") -> str:
        """
        Generate code based on natural language specification using OpenAI
        
        Args:
            specification: Natural language description of the desired functionality
            file_type: Type of file to generate (python, javascript, etc.)
        
        Returns:
            Generated code as string
        """
        try:
            prompt = f"""
            Generate {file_type} code based on the following specification:
            
            {specification}
            
            Requirements:
            - Follow best practices for {file_type} development
            - Include proper error handling
            - Add comprehensive docstrings/comments
            - Ensure compatibility with the XMRT-DAO-Ecosystem
            - Include necessary imports
            - Make the code production-ready
            
            Return only the code without any explanations or markdown formatting.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert software developer specializing in autonomous systems and blockchain applications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            generated_code = response.choices[0].message.content.strip()
            self.logger.info(f"Successfully generated {file_type} code from specification")
            return generated_code
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            raise
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> Dict:
        """
        Create a new branch in the repository
        
        Args:
            branch_name: Name of the new branch
            base_branch: Base branch to create from
        
        Returns:
            Branch creation response
        """
        try:
            # Get the SHA of the base branch
            base_ref = self._make_github_request(
                'GET', 
                f'repos/{self.github_username}/{self.repository_name}/git/ref/heads/{base_branch}'
            )
            base_sha = base_ref['object']['sha']
            
            # Create new branch
            branch_data = {
                'ref': f'refs/heads/{branch_name}',
                'sha': base_sha
            }
            
            response = self._make_github_request(
                'POST',
                f'repos/{self.github_username}/{self.repository_name}/git/refs',
                branch_data
            )
            
            self.logger.info(f"Successfully created branch: {branch_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create branch {branch_name}: {e}")
            raise
    
    def commit_file(self, file_path: str, content: str, commit_message: str, branch: str) -> Dict:
        """
        Commit a file to the repository
        
        Args:
            file_path: Path of the file in the repository
            content: Content of the file
            commit_message: Commit message
            branch: Branch to commit to
        
        Returns:
            Commit response
        """
        try:
            # Encode content to base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            # Check if file exists to get SHA for update
            file_sha = None
            try:
                existing_file = self._make_github_request(
                    'GET',
                    f'repos/{self.github_username}/{self.repository_name}/contents/{file_path}?ref={branch}'
                )
                file_sha = existing_file['sha']
            except requests.exceptions.HTTPError as e:
                if e.response.status_code != 404:
                    raise
            
            # Prepare commit data
            commit_data = {
                'message': commit_message,
                'content': encoded_content,
                'branch': branch
            }
            
            if file_sha:
                commit_data['sha'] = file_sha
            
            response = self._make_github_request(
                'PUT',
                f'repos/{self.github_username}/{self.repository_name}/contents/{file_path}',
                commit_data
            )
            
            self.logger.info(f"Successfully committed file: {file_path} to branch: {branch}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to commit file {file_path}: {e}")
            raise
    
    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> Dict:
        """
        Create a pull request
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch
        
        Returns:
            Pull request response
        """
        try:
            pr_data = {
                'title': title,
                'body': body,
                'head': head_branch,
                'base': base_branch
            }
            
            response = self._make_github_request(
                'POST',
                f'repos/{self.github_username}/{self.repository_name}/pulls',
                pr_data
            )
            
            self.logger.info(f"Successfully created pull request: {title}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create pull request: {e}")
            raise
    
    def autonomous_utility_development(self, utility_specification: str) -> Dict:
        """
        Autonomous development of a new utility based on specification
        
        Args:
            utility_specification: Natural language description of the utility
        
        Returns:
            Development result with branch and PR information
        """
        try:
            # Generate a unique branch name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"feature/autonomous_utility_{timestamp}"
            
            # Generate code based on specification
            self.logger.info("Generating code from specification...")
            generated_code = self.generate_code_from_specification(utility_specification)
            
            # Create new branch
            self.logger.info(f"Creating branch: {branch_name}")
            self.create_branch(branch_name)
            
            # Determine file path and name
            utility_name = f"autonomous_utility_{timestamp}.py"
            file_path = f"src/utilities/{utility_name}"
            
            # Commit the generated code
            commit_message = f"Add autonomous utility: {utility_name}\n\nGenerated from specification:\n{utility_specification[:200]}..."
            self.logger.info(f"Committing code to: {file_path}")
            commit_response = self.commit_file(file_path, generated_code, commit_message, branch_name)
            
            # Create pull request
            pr_title = f"Autonomous Utility: {utility_name}"
            pr_body = f"""
## Autonomous Utility Development

**Specification:**
{utility_specification}

**Generated File:** `{file_path}`

**Branch:** `{branch_name}`

This utility was autonomously generated by Eliza agent based on the provided specification.

### Review Checklist:
- [ ] Code follows project standards
- [ ] Functionality matches specification
- [ ] No security vulnerabilities
- [ ] Integration with existing system is clean
- [ ] Tests are included (if applicable)

**Auto-generated by Eliza Agent on {datetime.now().isoformat()}**
            """
            
            self.logger.info("Creating pull request...")
            pr_response = self.create_pull_request(pr_title, pr_body, branch_name)
            
            result = {
                'success': True,
                'branch_name': branch_name,
                'file_path': file_path,
                'commit_sha': commit_response['commit']['sha'],
                'pull_request_url': pr_response['html_url'],
                'pull_request_number': pr_response['number'],
                'generated_code_length': len(generated_code)
            }
            
            self.logger.info(f"Autonomous utility development completed successfully: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Autonomous utility development failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_repository_info(self) -> Dict:
        """Get repository information"""
        try:
            return self._make_github_request(
                'GET',
                f'repos/{self.github_username}/{self.repository_name}'
            )
        except Exception as e:
            self.logger.error(f"Failed to get repository info: {e}")
            raise
    
    def list_branches(self) -> List[Dict]:
        """List all branches in the repository"""
        try:
            return self._make_github_request(
                'GET',
                f'repos/{self.github_username}/{self.repository_name}/branches'
            )
        except Exception as e:
            self.logger.error(f"Failed to list branches: {e}")
            raise
    
    def get_pull_requests(self, state: str = "open") -> List[Dict]:
        """Get pull requests"""
        try:
            return self._make_github_request(
                'GET',
                f'repos/{self.github_username}/{self.repository_name}/pulls?state={state}'
            )
        except Exception as e:
            self.logger.error(f"Failed to get pull requests: {e}")
            raise

