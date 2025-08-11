#!/usr/bin/env python3
"""
README Generator - Main Application
Generates comprehensive README.md files by analyzing GitHub repositories
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from src.config import Config
from src.github_analyzer import GitHubAnalyzer
from src.readme_generator import ReadmeGenerator
from src.utils import (
    setup_logging,
    validate_github_url,
    extract_repo_info,
    sanitize_filename,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive README.md files from GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://github.com/user/repo
  python main.py https://github.com/user/repo --output custom_readme.md
  python main.py https://github.com/user/repo --verbose
        """,
    )

    parser.add_argument(
        "repo_url", help="GitHub repository URL (e.g., https://github.com/user/repo)"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="README.md",
        help="Output file path (default: README.md)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument("--config", help="Path to custom configuration file")

    return parser.parse_args()


async def main() -> int:
    """Main application entry point."""
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    try:
        # Validate GitHub URL
        if not validate_github_url(args.repo_url):
            logger.error("Invalid GitHub URL format")
            return 1

        # Load configuration
        config = Config.load(args.config)

        # Validate OpenRouter API key
        if not config.openrouter_api_key:
            logger.error(
                "OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable"
            )
            return 1

        logger.info(f"Starting README generation for: {args.repo_url}")

        # Initialize components
        analyzer = GitHubAnalyzer(config)
        generator = ReadmeGenerator(config)

        # Analyze repository
        logger.info("Analyzing repository structure and content...")
        repo_data = await analyzer.analyze_repository(args.repo_url)

        if not repo_data:
            logger.error("Failed to analyze repository")
            return 1

        # Generate README
        logger.info("Generating README content...")
        readme_content = await generator.generate_readme(repo_data)

        if not readme_content:
            logger.error("Failed to generate README content")
            return 1

        # Determine output path. If default is used, place under 'readmes/readme-<repo>.md'
        if args.output == "README.md":
            owner_repo = extract_repo_info(args.repo_url)
            if owner_repo:
                _, repo_name = owner_repo
                safe_repo_name = sanitize_filename(repo_name)
                output_dir = Path("readmes")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"readme-{safe_repo_name}.md"
            else:
                output_dir = Path("readmes")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "readme-output.md"
        else:
            output_path = Path(args.output)

        output_path.write_text(readme_content, encoding="utf-8")

        logger.info(f"README successfully generated: {output_path.absolute()}")
        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
