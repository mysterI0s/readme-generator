import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import aiohttp
import base64
import json

from src.config import Config
from src.models import RepositoryData, FileData, LanguageStats

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyzes GitHub repositories to extract comprehensive information."""

    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repository name."""
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")

        return path_parts[0], path_parts[1]

    async def _get_github_api_data(self, endpoint: str) -> Optional[Dict]:
        """Fetch data from GitHub API."""
        url = f"https://api.github.com/{endpoint}"

        for attempt in range(self.config.max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.error(f"Repository not found or not accessible")
                        return None
                    elif response.status == 403:
                        logger.warning("GitHub API rate limit exceeded")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay * (2**attempt))
                            continue
                        return None
                    else:
                        logger.warning(f"GitHub API returned status {response.status}")

            except aiohttp.ClientError as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")

            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(self.config.retry_delay * (2**attempt))

        return None

    async def _get_repository_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Get basic repository information."""
        return await self._get_github_api_data(f"repos/{owner}/{repo}")

    async def _get_repository_contents(
        self, owner: str, repo: str, path: str = ""
    ) -> Optional[List[Dict]]:
        """Get repository contents."""
        endpoint = (
            f"repos/{owner}/{repo}/contents/{path}"
            if path
            else f"repos/{owner}/{repo}/contents"
        )
        return await self._get_github_api_data(endpoint)

    async def _get_file_content(
        self, owner: str, repo: str, path: str
    ) -> Optional[str]:
        """Get individual file content."""
        data = await self._get_github_api_data(f"repos/{owner}/{repo}/contents/{path}")

        if data and data.get("type") == "file" and data.get("content"):
            try:
                # Decode base64 content
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
            except (UnicodeDecodeError, ValueError) as e:
                logger.warning(f"Failed to decode file {path}: {e}")
                return None

        return None

    async def _analyze_directory_structure(
        self, owner: str, repo: str, path: str = "", level: int = 0, max_level: int = 3
    ) -> List[FileData]:
        """Recursively analyze directory structure."""
        if level > max_level:
            return []

        files = []
        contents = await self._get_repository_contents(owner, repo, path)

        if not contents:
            return files

        for item in contents:
            if len(files) >= self.config.max_files:
                break

            file_path = item["path"]
            file_name = item["name"]

            if item["type"] == "dir":
                # Recursively analyze subdirectories
                subfiles = await self._analyze_directory_structure(
                    owner, repo, file_path, level + 1, max_level
                )
                files.extend(subfiles)
            else:
                # Analyze file
                file_extension = Path(file_name).suffix.lower()

                if file_extension in self.config.supported_extensions or file_name in [
                    "README.md",
                    "LICENSE",
                    "Dockerfile",
                    "Makefile",
                ]:

                    file_size = item.get("size", 0)
                    if file_size <= self.config.max_file_size:
                        content = await self._get_file_content(owner, repo, file_path)

                        files.append(
                            FileData(
                                path=file_path,
                                name=file_name,
                                extension=file_extension,
                                size=file_size,
                                content=content or "",
                            )
                        )

        return files

    def _analyze_languages(self, files: List[FileData]) -> LanguageStats:
        """Analyze programming languages used in the repository."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React",
            ".tsx": "React TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".rb": "Ruby",
            ".go": "Go",
            ".rs": "Rust",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
        }

        language_counts = {}
        total_lines = 0

        for file_data in files:
            if file_data.extension in language_map:
                language = language_map[file_data.extension]
                lines = len(file_data.content.splitlines()) if file_data.content else 0
                language_counts[language] = language_counts.get(language, 0) + lines
                total_lines += lines

        # Calculate percentages
        language_percentages = {}
        if total_lines > 0:
            for language, lines in language_counts.items():
                language_percentages[language] = (lines / total_lines) * 100

        return LanguageStats(languages=language_percentages, total_lines=total_lines)

    def _detect_project_type(self, files: List[FileData]) -> str:
        """Detect the type of project based on files."""
        file_names = {f.name.lower() for f in files}
        file_extensions = {f.extension for f in files}

        # Web frameworks
        if "package.json" in file_names:
            if any(".jsx" in ext or ".tsx" in ext for ext in file_extensions):
                return "React Application"
            elif any(".vue" in ext for ext in file_extensions):
                return "Vue.js Application"
            return "Node.js Application"

        # Python frameworks
        if "requirements.txt" in file_names or "pyproject.toml" in file_names:
            if "manage.py" in file_names:
                return "Django Application"
            elif any("flask" in f.content.lower() for f in files if f.content):
                return "Flask Application"
            elif any("fastapi" in f.content.lower() for f in files if f.content):
                return "FastAPI Application"
            return "Python Project"

        # Other frameworks
        if "pom.xml" in file_names or "build.gradle" in file_names:
            return "Java Project"

        if "cargo.toml" in file_names:
            return "Rust Project"

        if "go.mod" in file_names:
            return "Go Project"

        if "gemfile" in file_names:
            return "Ruby Project"

        return "General Project"

    async def analyze_repository(self, repo_url: str) -> Optional[RepositoryData]:
        """Analyze a GitHub repository and return comprehensive data."""
        try:
            # Parse GitHub URL
            owner, repo_name = self._parse_github_url(repo_url)
            logger.info(f"Analyzing repository: {owner}/{repo_name}")

            # Create session if not exists
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
                )

            # Get repository information
            repo_info = await self._get_repository_info(owner, repo_name)
            if not repo_info:
                return None

            # Analyze repository structure
            files = await self._analyze_directory_structure(owner, repo_name)

            # Analyze languages
            language_stats = self._analyze_languages(files)

            # Detect project type
            project_type = self._detect_project_type(files)

            # Find important files
            readme_file = next(
                (f for f in files if f.name.lower().startswith("readme")), None
            )
            license_file = next(
                (f for f in files if f.name.lower().startswith("license")), None
            )

            return RepositoryData(
                name=repo_info["name"],
                full_name=repo_info["full_name"],
                description=repo_info.get("description", ""),
                url=repo_info["html_url"],
                clone_url=repo_info["clone_url"],
                language=repo_info.get("language", ""),
                languages=language_stats,
                stars=repo_info.get("stargazers_count", 0),
                forks=repo_info.get("forks_count", 0),
                open_issues=repo_info.get("open_issues_count", 0),
                created_at=repo_info.get("created_at", ""),
                updated_at=repo_info.get("updated_at", ""),
                project_type=project_type,
                files=files,
                readme_content=readme_file.content if readme_file else "",
                license_content=license_file.content if license_file else "",
                has_wiki=repo_info.get("has_wiki", False),
                has_issues=repo_info.get("has_issues", False),
                has_projects=repo_info.get("has_projects", False),
            )

        except Exception as e:
            logger.error(f"Failed to analyze repository: {e}")
            return None
        finally:
            if self.session:
                await self.session.close()
                self.session = None
