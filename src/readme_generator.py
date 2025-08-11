"""
README Generator Module
Uses OpenRouter AI to generate comprehensive README.md content
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp

from src.config import Config
from src.models import RepositoryData

logger = logging.getLogger(__name__)


class ReadmeGenerator:
    """Generates README.md content using AI analysis."""

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

    def _create_analysis_prompt(self, repo_data: RepositoryData) -> str:
        """Create a comprehensive prompt for AI analysis."""

        # Prepare file structure summary
        file_structure = self._create_file_structure_summary(repo_data.files)

        # Prepare code samples
        code_samples = self._create_code_samples(repo_data)

        # Prepare language statistics
        lang_stats = ""
        if repo_data.languages.languages:
            lang_stats = "\n".join(
                [
                    f"- {lang}: {percent:.1f}%"
                    for lang, percent in sorted(
                        repo_data.languages.languages.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                ]
            )

        prompt = f"""
You are an expert technical writer tasked with creating a comprehensive README.md file for a GitHub repository.

## Repository Information:
- Name: {repo_data.name}
- Description: {repo_data.description}
- Project Type: {repo_data.project_type}
- Main Language: {repo_data.get_main_language()}
- Stars: {repo_data.stars}
- Forks: {repo_data.forks}
- Open Issues: {repo_data.open_issues}

## Language Statistics:
{lang_stats}

## File Structure:
{file_structure}

## Key Code Samples:
{code_samples}

## Existing README (if any):
{repo_data.readme_content[:2000] if repo_data.readme_content else "No existing README found"}

## License Information:
{repo_data.license_content[:500] if repo_data.license_content else "No license file found"}

## Requirements:
Please generate a comprehensive README.md that includes:

1. **Project Title and Description**: Clear, engaging description
2. **Badges**: Relevant badges for language, license, issues, etc.
3. **Table of Contents**: Well-organized navigation
4. **Features**: Key features and capabilities
5. **Installation**: Step-by-step installation instructions
6. **Usage**: Code examples and usage instructions
7. **API Documentation**: If applicable, document key functions/classes
8. **Configuration**: Environment variables and config options
9. **Contributing**: Guidelines for contributors
10. **Testing**: How to run tests
11. **Deployment**: Deployment instructions if applicable
12. **License**: License information
13. **Acknowledgments**: Credits and thanks

## Guidelines:
- Write in clear, professional English
- Use proper Markdown formatting
- Include realistic code examples based on the actual code
- Make installation instructions specific to the project type
- Focus on practical information that helps users and contributors
- Ensure the content is accurate based on the repository analysis
- Use appropriate technical terminology for the project domain
- Include relevant links and references

Generate a complete, professional README.md file:
"""
        return prompt

    def _create_file_structure_summary(self, files: List) -> str:
        """Create a summary of the file structure."""
        structure = {}

        for file_data in files[:30]:  # Limit to first 30 files
            parts = file_data.path.split("/")
            current = structure

            for part in parts[:-1]:  # Directories
                if part not in current:
                    current[part] = {}
                current = current[part]

            # File
            current[parts[-1]] = f"({file_data.size} bytes)"

        return self._format_structure(structure)

    def _format_structure(self, structure: Dict, indent: int = 0) -> str:
        """Format the file structure as text."""
        lines = []
        prefix = "  " * indent

        for key, value in sorted(structure.items()):
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}/")
                lines.append(self._format_structure(value, indent + 1))
            else:
                lines.append(f"{prefix}{key} {value}")

        return "\n".join(lines)

    def _create_code_samples(self, repo_data: RepositoryData) -> str:
        """Create relevant code samples from the repository."""
        samples = []

        # Look for main entry points
        main_files = [
            "main.py",
            "app.py",
            "index.js",
            "main.js",
            "server.js",
            "main.java",
            "Main.java",
            "main.go",
            "lib.rs",
            "main.rs",
        ]

        for filename in main_files:
            file_data = repo_data.get_file_by_name(filename)
            if file_data and file_data.content:
                samples.append(
                    f"### {filename}\n```{self._get_language_for_extension(file_data.extension)}\n{file_data.content[:500]}...\n```"
                )
                break

        # Look for configuration files
        config_files = repo_data.get_config_files()
        for config_file in config_files[:2]:  # Max 2 config files
            if config_file.content and len(config_file.content) < 1000:
                lang = self._get_language_for_extension(config_file.extension)
                samples.append(
                    f"### {config_file.name}\n```{lang}\n{config_file.content}\n```"
                )

        return "\n\n".join(samples) if samples else "No significant code samples found."

    def _get_language_for_extension(self, extension: str) -> str:
        """Get the appropriate language identifier for syntax highlighting."""
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".sh": "bash",
            ".bat": "batch",
            ".md": "markdown",
        }
        return lang_map.get(extension.lower(), "")

    async def _call_openrouter_api(self, prompt: str) -> Optional[str]:
        """Call the OpenRouter API to generate README content."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
            )

        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/readme-generator",
            "X-Title": "README Generator",
        }

        payload = {
            "model": self.config.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert technical writer specializing in creating comprehensive, professional README.md files for software projects. You analyze code repositories and generate clear, well-structured documentation that helps users understand, install, and use the software effectively.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 4000,
            "temperature": 0.3,
            "top_p": 0.9,
        }

        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(
                    f"{self.config.api_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:

                    if response.status == 200:
                        result = await response.json()

                        if "choices" in result and result["choices"]:
                            content = result["choices"][0]["message"]["content"]
                            return content.strip()
                        else:
                            logger.error("Invalid response format from OpenRouter API")
                            return None

                    elif response.status == 401:
                        logger.error("Invalid API key for OpenRouter")
                        return None

                    elif response.status == 429:
                        logger.warning("Rate limit exceeded, retrying...")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay * (2**attempt))
                            continue

                    else:
                        error_text = await response.text()
                        logger.error(
                            f"OpenRouter API error {response.status}: {error_text}"
                        )

            except aiohttp.ClientError as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")

            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(self.config.retry_delay * (2**attempt))

        return None

    def _post_process_readme(self, content: str, repo_data: RepositoryData) -> str:
        """Post-process the generated README content."""
        # Ensure proper markdown formatting
        if not content.startswith("# "):
            content = f"# {repo_data.name}\n\n{content}"

        # Add badges if enabled and not present
        if self.config.include_badges and not "![" in content[:500]:
            badges = self._generate_badges(repo_data)
            if badges:
                # Insert badges after the title
                lines = content.split("\n")
                title_line = 0
                for i, line in enumerate(lines):
                    if line.startswith("# "):
                        title_line = i
                        break

                lines.insert(title_line + 1, "")
                lines.insert(title_line + 2, badges)
                lines.insert(title_line + 3, "")
                content = "\n".join(lines)

        # Ensure proper spacing
        content = content.replace("\n\n\n", "\n\n")

        return content

    def _generate_badges(self, repo_data: RepositoryData) -> str:
        """Generate relevant badges for the project."""
        badges = []

        # Language badge
        if repo_data.language:
            badges.append(
                f"![Language](https://img.shields.io/badge/Language-{repo_data.language}-blue)"
            )

        # Stars badge
        if repo_data.stars > 0:
            badges.append(
                f"![Stars](https://img.shields.io/github/stars/{repo_data.full_name})"
            )

        # Forks badge
        if repo_data.forks > 0:
            badges.append(
                f"![Forks](https://img.shields.io/github/forks/{repo_data.full_name})"
            )

        # Issues badge
        if repo_data.has_issues:
            badges.append(
                f"![Issues](https://img.shields.io/github/issues/{repo_data.full_name})"
            )

        # License badge
        if repo_data.license_content:
            badges.append(
                f"![License](https://img.shields.io/github/license/{repo_data.full_name})"
            )

        # Last commit badge
        badges.append(
            f"![Last Commit](https://img.shields.io/github/last-commit/{repo_data.full_name})"
        )

        return " ".join(badges) if badges else ""

    async def generate_readme(self, repo_data: RepositoryData) -> Optional[str]:
        """Generate a comprehensive README.md file."""
        try:
            logger.info("Creating analysis prompt...")
            prompt = self._create_analysis_prompt(repo_data)

            logger.info("Calling OpenRouter API...")
            readme_content = await self._call_openrouter_api(prompt)

            if not readme_content:
                logger.error("Failed to generate README content")
                return None

            logger.info("Post-processing README content...")
            final_content = self._post_process_readme(readme_content, repo_data)

            return final_content

        except Exception as e:
            logger.error(f"Failed to generate README: {e}")
            return None
        finally:
            if self.session:
                await self.session.close()
                self.session = None
