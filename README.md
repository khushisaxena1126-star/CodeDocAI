# CodeDocAI

AI-powered documentation generator for multi-language software projects.

[🚀 Live Demo](https://codedocai-cknl.onrender.com

CodeDocAI is a command-line tool developed by Khushi Saxena that analyzes Python codebases to generate structured, professional project documentation using a large language model. It accepts a Python project as input and produces a generated or updated `README.md` file as output.

## Features

- **Automated Documentation Generation**: Scans Python codebases and generates professional `README.md` files using AI.
- **Multi-Stage Pipeline**: Includes file scanning, summarization, context caching, and AI documentation generation.
- **Selective Updates**: Supports updating documentation for specific files or directories without regenerating the entire project documentation.
- **Context Caching**: Stores processed context to ensure efficient handling of project changes and avoid redundant processing.
- **Model Management**: Lists available AI models from the Groq API and allows configuration of specific models and providers.
- **Git Integration**: Respects `.gitignore` patterns during file scanning and automatically updates `.gitignore` to exclude generated artifacts.

## How It Works

1. **Initialization**: The tool scans the repository structure, respects `.gitignore` rules, and generates a `doclify.yaml` configuration file.
2. **File Extraction**: It reads specified source files (`.py`, `.md`, `.txt`, `.ipynb`), partitions content into chunks suitable for LLM consumption, and handles Jupyter Notebook code cells.
3. **Summarization**: File contents are sent to a Large Language Model (via Groq API) to generate summaries.
4. **Caching**: Summaries are cached in `.doclify/cache.json` to optimize performance for subsequent runs.
5. **README Generation**: Cached summaries are aggregated to produce a final `README.md`, with previous versions backed up.

## Technologies Used

- **Python**: Core implementation language.
- **Groq API**: Used for AI model inference and documentation generation.
- **Click**: Command-line interface framework.
- **Rich**: Console output and formatting.
- **Pydantic**: Data validation for configuration and schema definitions.
- **YAML**: Configuration file management (`doclify.yaml`).
- **Pathspec**: Parsing gitignore-style patterns.
- **LiteLLM**: Configuration for language learning models.

## Project Structure

```
doclify/
├── __init__.py
├── components/
│   ├── config.py      # Manages doclify.yaml configuration
│   ├── init.py        # Initializes project and generates config
│   ├── models.py      # Lists available Groq API models
│   ├── run.py         # Executes documentation generation pipeline
│   └── update.py      # Updates documentation for specific files
├── config/
│   └── constants.py   # Defines default LLM configuration
├── pipelines/
│   └── supervisor
