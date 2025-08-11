# README Generator

README Generator is a Flask application designed to create comprehensive README.md files by analyzing GitHub repositories. This tool leverages AI to generate detailed documentation that helps users understand, install, and utilize software projects effectively.

## Badges

![Python](https://img.shields.io/badge/Python-100%25-blue)
![Flask](https://img.shields.io/badge/Flask-Application-green)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **AI-Powered Analysis**: Utilizes OpenRouter AI to analyze GitHub repositories and generate README.md content.
- **Customizable Templates**: Supports comprehensive templates with options to include badges, table of contents, installation instructions, and more.
- **Asynchronous Operations**: Efficiently handles API requests using asynchronous programming.

## Installation

### Prerequisites

- Python 3.8 or later
- OpenRouter API key (free tier available)

### Quick Setup

1. Clone or download the project files
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### Manual Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

## Usage

### Basic Usage

Generate a README for any GitHub repository:

```bash
python main.py https://github.com/user/repository-name
```

### Advanced Usage

```bash
# Specify output file
python main.py https://github.com/user/repo --output my-readme.md

# Use custom configuration
python main.py https://github.com/user/repo --config custom-config.json

# Enable verbose logging
python main.py https://github.com/user/repo --verbose

# Combination of options
python main.py https://github.com/user/repo \
  --output generated-readme.md \
  --config config.json \
  --verbose
```

### Help

```bash
python main.py --help
```

## Project Structure

```
readme-generator/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── github_analyzer.py # GitHub repository analysis
│   ├── readme_generator.py # AI-powered README generation
│   ├── models.py          # Data models and structures
│   └── utils.py           # Utility functions
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── .env.example          # Environment variables example
├── config.example.json   # Configuration file example
└── README.md             # This file
```

## Configuration

### Environment Variables

Create a `.env` file with your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_api_key_here
MODEL_NAME=openai/gpt-4o  # Optional: override default model
```

### Configuration File

Create a custom configuration file (JSON format):

```json
{
  "model_name": "openai/gpt-4o",
  "max_file_size": 100000,
  "max_files": 50,
  "include_badges": true,
  "include_toc": true,
  "request_timeout": 30
}
```

## How It Works

1. **Repository Analysis**: The tool fetches repository information from GitHub's API, including:
   - Repository metadata (name, description, stars, etc.)
   - File structure and content
   - Language statistics
   - Configuration files
   - Existing documentation

2. **Content Analysis**: It analyzes the code to understand:
   - Project type and framework
   - Dependencies and requirements
   - Main entry points
   - Configuration patterns

3. **AI Generation**: Using OpenRouter's GPT-4, it generates:
   - Project description and features
   - Installation instructions
   - Usage examples
   - API documentation
   - Contributing guidelines

4. **Post-processing**: The generated content is refined with:
   - Proper Markdown formatting
   - Relevant badges
   - Table of contents
   - Link validation

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.

## Testing

To run tests, execute the following command:

```bash
pytest tests/
```

## Deployment

For deployment instructions, please refer to the `setup.sh` script, which automates the deployment process.

## Acknowledgments

Special thanks to the contributors and the open-source community for their support and collaboration.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Fun Fact

This Readme file was created with this repository.

---

This README.md file provides a comprehensive overview of the README Generator project, guiding users through installation, usage, and contribution processes. For further details, please refer to the source code and configuration files.
