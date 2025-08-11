import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from a .env file in the project root if present.
# This allows users to keep their API keys in .env without having to export them manually.
load_dotenv()


@dataclass
class Config:
    """Configuration class for the README generator."""

    # API Configuration
    openrouter_api_key: str = ""
    model_name: str = "openai/gpt-4o"
    api_base_url: str = "https://openrouter.ai/api/v1"

    # Analysis Configuration
    max_file_size: int = 100_000  # Maximum file size to analyze in bytes
    max_files: int = 50  # Maximum number of files to analyze
    supported_extensions: List[str] = field(
        default_factory=lambda: [
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".cs",
            ".rb",
            ".go",
            ".rust",
            ".rs",
            ".php",
            ".swift",
            ".kt",
            ".scala",
            ".md",
            ".txt",
            ".yaml",
            ".yml",
            ".json",
            ".toml",
            ".cfg",
            ".ini",
            ".dockerfile",
            "Dockerfile",
            "Makefile",
            ".sh",
            ".bat",
        ]
    )

    # Generation Configuration
    readme_template: str = "comprehensive"  # Options: simple, comprehensive, detailed
    include_badges: bool = True
    include_toc: bool = True
    include_installation: bool = True
    include_usage: bool = True
    include_api_docs: bool = True
    include_contributing: bool = True
    include_license: bool = True

    # Request Configuration
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    max_tokens: int = 2000  # Max completion tokens for OpenRouter responses

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from environment variables and optional config file."""
        config = cls()

        # Load from environment variables
        config.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        config.model_name = os.getenv("MODEL_NAME", config.model_name)
        config.api_base_url = os.getenv("API_BASE_URL", config.api_base_url)

        # Load from config file if provided
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        file_config = json.load(f)

                    # Update configuration with file values
                    for key, value in file_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
                        else:
                            logger.warning(f"Unknown configuration key: {key}")

                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Failed to load config file {config_path}: {e}")
            else:
                logger.warning(f"Config file not found: {config_path}")

        # Load select overrides from environment variables
        max_tokens_env = os.getenv("MAX_TOKENS")
        if max_tokens_env:
            try:
                config.max_tokens = int(max_tokens_env)
            except ValueError:
                logger.warning("Invalid MAX_TOKENS value; using default")

        # Validation
        if not config.openrouter_api_key:
            logger.warning("OpenRouter API key not set")

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "openrouter_api_key": "***" if self.openrouter_api_key else "",
            "model_name": self.model_name,
            "api_base_url": self.api_base_url,
            "max_file_size": self.max_file_size,
            "max_files": self.max_files,
            "supported_extensions": self.supported_extensions,
            "readme_template": self.readme_template,
            "include_badges": self.include_badges,
            "include_toc": self.include_toc,
            "include_installation": self.include_installation,
            "include_usage": self.include_usage,
            "include_api_docs": self.include_api_docs,
            "include_contributing": self.include_contributing,
            "include_license": self.include_license,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "max_tokens": self.max_tokens,
        }

    def save(self, config_path: str) -> None:
        """Save configuration to file."""
        config_dict = self.to_dict()
        # Don't save the API key for security
        config_dict.pop("openrouter_api_key")

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2)
