"""
Data models for the README generator
Defines the structure for repository data and related objects
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class FileData:
    """Represents a file in the repository."""

    path: str
    name: str
    extension: str
    size: int
    content: str


@dataclass
class LanguageStats:
    """Statistics about programming languages used."""

    languages: Dict[str, float]  # Language name -> percentage
    total_lines: int


@dataclass
class RepositoryData:
    """Complete repository analysis data."""

    # Basic info
    name: str
    full_name: str
    description: str
    url: str
    clone_url: str

    # Language info
    language: str
    languages: LanguageStats

    # Statistics
    stars: int
    forks: int
    open_issues: int

    # Timestamps
    created_at: str
    updated_at: str

    # Analysis results
    project_type: str
    files: List[FileData]

    # Special files
    readme_content: str
    license_content: str

    # Features
    has_wiki: bool
    has_issues: bool
    has_projects: bool

    def get_files_by_extension(self, extension: str) -> List[FileData]:
        """Get all files with a specific extension."""
        return [f for f in self.files if f.extension == extension]

    def get_file_by_name(self, name: str) -> Optional[FileData]:
        """Get a file by its name."""
        return next((f for f in self.files if f.name.lower() == name.lower()), None)

    def get_main_language(self) -> str:
        """Get the primary programming language."""
        if self.languages.languages:
            return max(self.languages.languages.items(), key=lambda x: x[1])[0]
        return self.language or "Unknown"

    def has_file(self, filename: str) -> bool:
        """Check if repository contains a specific file."""
        return any(f.name.lower() == filename.lower() for f in self.files)

    def get_config_files(self) -> List[FileData]:
        """Get configuration files."""
        config_patterns = [
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            "dockerfile",
            "makefile",
            ".env",
        ]
        config_files = []

        for file_data in self.files:
            if (
                file_data.extension.lower() in config_patterns
                or file_data.name.lower() in ["dockerfile", "makefile"]
                or file_data.name.lower().startswith(".env")
            ):
                config_files.append(file_data)

        return config_files

    def get_documentation_files(self) -> List[FileData]:
        """Get documentation files."""
        doc_extensions = [".md", ".txt", ".rst"]
        return [f for f in self.files if f.extension.lower() in doc_extensions]
