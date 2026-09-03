# CodeDocAI

AI-powered documentation generator for Python projects.

**Developed and maintained by Khushi Saxena**

CodeDocAI is a command-line tool that analyzes a Python codebase and uses an LLM to generate structured, professional project documentation. It scans project files, creates concise summaries, builds reusable context, and generates a README automatically.

## Features

- Scans and analyzes Python project files
- Generates AI-powered file summaries
- Uses a multi-stage documentation pipeline
- Stores processed context for efficient updates
- Automatically generates and updates `README.md`
- Supports selective documentation updates
- Provides a simple command-line interface

## How It Works

```text
Python Project
      |
      v
File Scanner
      |
      v
File Summarization
      |
      v
Context Cache
      |
      v
AI Documentation Generation
      |
      v
README.md
