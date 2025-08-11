import logging
import re
import sys
from typing import Optional
from urllib.parse import urlparse


def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from aiohttp
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)


def validate_github_url(url: str) -> bool:
    """Validate if the URL is a valid GitHub repository URL."""
    if not url:
        return False

    # Regular expression for GitHub repository URLs
    github_pattern = re.compile(r"^https?://github\.com/[\w\-\.]+/[\w\-\.]+/?$")

    return bool(github_pattern.match(url.strip().rstrip("/")))


def extract_repo_info(url: str) -> Optional[tuple[str, str]]:
    """Extract owner and repository name from GitHub URL."""
    try:
        parsed = urlparse(url.strip().rstrip("/"))
        if parsed.netloc != "github.com":
            return None

        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]

    except Exception:
        pass

    return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    filename = filename.strip(" .")

    # Ensure it's not empty
    if not filename:
        filename = "README"

    return filename


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def clean_markdown(content: str) -> str:
    """Clean and format markdown content."""
    if not content:
        return ""

    lines = content.split("\n")
    cleaned_lines = []

    for line in lines:
        # Remove excessive whitespace
        line = line.rstrip()
        cleaned_lines.append(line)

    # Join lines and normalize multiple newlines
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def is_binary_file(filepath: str) -> bool:
    """Check if file is likely a binary file based on extension."""
    binary_extensions = {
        ".exe",
        ".bin",
        ".dll",
        ".so",
        ".dylib",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
        ".mp3",
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wav",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".class",
        ".jar",
        ".pyc",
        ".pyo",
    }

    return any(filepath.lower().endswith(ext) for ext in binary_extensions)


def extract_imports(code_content: str, file_extension: str) -> list[str]:
    """Extract import statements from code."""
    imports = []

    if file_extension == ".py":
        # Python imports
        import_patterns = [
            r"^import\s+(\w+(?:\.\w+)*)",
            r"^from\s+(\w+(?:\.\w+)*)\s+import",
        ]

        for line in code_content.split("\n"):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))

    elif file_extension in [".js", ".ts", ".jsx", ".tsx"]:
        # JavaScript/TypeScript imports
        import_patterns = [
            r'import.*from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
        ]

        for line in code_content.split("\n"):
            line = line.strip()
            for pattern in import_patterns:
                matches = re.findall(pattern, line)
                imports.extend(matches)

    return list(set(imports))  # Remove duplicates


def detect_framework(files: list, file_contents: dict) -> Optional[str]:
    """Detect the framework used based on files and content."""
    filenames = {f.lower() for f in files}

    # Check for specific files
    if "package.json" in filenames:
        # Check package.json content for React/Vue/Angular
        package_content = file_contents.get("package.json", "")
        if "react" in package_content.lower():
            return "React"
        elif "vue" in package_content.lower():
            return "Vue.js"
        elif "angular" in package_content.lower():
            return "Angular"
        elif "@nestjs" in package_content.lower():
            return "NestJS"
        return "Node.js"

    if "requirements.txt" in filenames or "pyproject.toml" in filenames:
        # Check Python dependencies
        reqs_content = file_contents.get("requirements.txt", "") + file_contents.get(
            "pyproject.toml", ""
        )

        if "django" in reqs_content.lower():
            return "Django"
        elif "flask" in reqs_content.lower():
            return "Flask"
        elif "fastapi" in reqs_content.lower():
            return "FastAPI"
        elif "streamlit" in reqs_content.lower():
            return "Streamlit"
        return "Python"

    if "cargo.toml" in filenames:
        return "Rust"

    if "go.mod" in filenames:
        return "Go"

    if "pom.xml" in filenames or "build.gradle" in filenames:
        return "Java"

    return None


def generate_table_of_contents(content: str) -> str:
    """Generate a table of contents from markdown headers."""
    toc_lines = []
    headers = re.findall(r"^(#{2,6})\s+(.+)$", content, re.MULTILINE)

    for level_hash, title in headers:
        level = len(level_hash) - 1  # Convert ## to level 1, ### to level 2, etc.
        indent = "  " * (level - 1)

        # Create anchor link
        anchor = title.lower()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[\s_]+", "-", anchor)

        toc_lines.append(f"{indent}- [{title}](#{anchor})")

    if toc_lines:
        return "## Table of Contents\n\n" + "\n".join(toc_lines) + "\n\n"

    return ""
