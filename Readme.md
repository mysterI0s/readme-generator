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

To install and run the README Generator, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/readme-generator.git
   cd readme-generator
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Application**:
   - Copy `config.example.json` to `config.json`.
   - Modify `config.json` with your specific settings.

5. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage

To generate a README.md file for a GitHub repository, use the following command:

```bash
python main.py --repo-url <GitHub Repository URL>
```

## Configuration

The application can be configured using the `config.json` file. Key configuration options include:

- `model_name`: The AI model to use for analysis.
- `api_base_url`: The base URL for the API.
- `max_file_size`: Maximum file size for analysis.
- `include_*`: Boolean flags to include various sections in the README.

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

## Fun Fact

This Readme file was created with this repository.

---

This README.md file provides a comprehensive overview of the README Generator project, guiding users through installation, usage, and contribution processes. For further details, please refer to the source code and configuration files.
