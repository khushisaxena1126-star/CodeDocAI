import os
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, request, render_template

from doclify.utils.llm import generate_doc

app = Flask(__name__)

ALLOWED_EXTENSIONS = { # Python
    ".py", ".pyw", ".ipynb",

    # JavaScript / TypeScript
    ".js", ".jsx", ".ts", ".tsx",

    # Java / JVM
    ".java", ".kt", ".kts", ".scala",

    # C / C++
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",

    # C#
    ".cs",

    # Go
    ".go",

    # Rust
    ".rs",

    # PHP
    ".php",

    # Ruby
    ".rb",

    # Swift
    ".swift",

    # Dart
    ".dart",

    # R
    ".r", ".R",

    # Web
    ".html", ".htm", ".css", ".scss", ".sass",
    ".less", ".vue", ".svelte",

    # SQL
    ".sql",

    # Shell
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",

    # Data / configuration
    ".json", ".yaml", ".yml", ".xml", ".toml", ".ini", ".cfg",

    # Documentation
    ".md", ".txt",

    # Other common project files
    ".gradle", ".properties"}

MAX_ZIP_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILES = 100
MAX_TOTAL_CONTENT = 250_000

MAX_SINGLE_FILE = 200_000


def extract_project(zip_path, output_dir):
    """Safely extract a ZIP file."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        members = zip_ref.infolist()

        if len(members) > MAX_FILES:
            raise ValueError(
                f"Project contains too many files. Maximum allowed is {MAX_FILES}."
            )

        output_root = Path(output_dir).resolve()

        for member in members:
            target = (output_root / member.filename).resolve()

            if not str(target).startswith(str(output_root)):
                raise ValueError("Invalid ZIP file.")

            zip_ref.extract(member, output_root)


def collect_project_files(project_dir):
    """Collect supported source/documentation files."""
    files = []

    for path in Path(project_dir).rglob("*"):
        if not path.is_file():
            continue

        if any(part.startswith(".") for part in path.parts):
            continue

        if path.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append(path)

    return files


def read_project_files(files, project_dir):
    """Read supported project files for AI analysis."""
    contents = []
    total_chars = 0

    for path in files:
        try:
            if path.stat().st_size > MAX_SINGLE_FILE:
                continue

            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if not content.strip():
                continue

            remaining = MAX_TOTAL_CONTENT - total_chars

            if remaining <= 0:
                break

            if len(content) > remaining:
                content = content[:remaining]

            relative_path = path.relative_to(project_dir)

            extension = path.suffix.lower().lstrip(".")

            if not extension:
                extension = "text"

            contents.append(
                f"FILE: {relative_path}\n"
                f"```{extension}\n"
                f"{content}\n"
                f"```\n"
            )

            total_chars += len(content)

        except Exception:
            continue

    return "\n".join(contents)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "GET":
        return render_template("index.html")

    uploaded_file = request.files.get("project")

    if not uploaded_file or not uploaded_file.filename:
        return render_template(
            "index.html",
            error="Please select a ZIP file."
        )

    if not uploaded_file.filename.lower().endswith(".zip"):
        return render_template(
            "index.html",
            error="Please upload a ZIP file."
        )

    try:
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)

        if file_size > MAX_ZIP_SIZE:
            return render_template(
                "index.html",
                error="ZIP file is too large. Maximum size is 10 MB."
            )

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_dir = Path(temp_dir)

            zip_path = temp_dir / "project.zip"
            project_dir = temp_dir / "project"

            project_dir.mkdir()

            uploaded_file.save(zip_path)

            extract_project(zip_path, project_dir)

            project_files = collect_project_files(project_dir)

            if not project_files:
                return render_template(
                    "index.html",
                    error="No supported project files were found."
                )

            project_content = read_project_files(
                project_files,
                project_dir
            )

            if not project_content.strip():
                return render_template(
                    "index.html",
                    error="The uploaded project does not contain readable source files."
                )

            prompt = f"""
You are a senior technical documentation engineer.

Generate a concise README.md for the uploaded Python project.

Use ONLY the source files provided below.

IMPORTANT RULES:
- Do not invent features.
- Do not invent dependencies.
- Do not invent APIs or services.
- Do not invent installation commands.
- Do not invent deployment information.
- Do not invent database usage.
- Do not invent a license.
- Do not create fake URLs.
- Base every statement on information explicitly present in the files.
- If information is unavailable, omit that section.

Include relevant sections such as:
- Project title
- Project description
- Features
- How it works
- Technologies used
- Usage
- Project structure
- Installation, only when supported by the files

Keep the README concise and professional.

Return ONLY the README in Markdown.

PROJECT SOURCE FILES:

[FILE CONTENT START]

{project_content}

[FILE CONTENT END]
"""

            readme = generate_doc(
                prompt,
                prompt_type="web_summary"
            )

            if not readme:
                raise ValueError(
                    "The AI did not return documentation."
                )

            return render_template(
                "index.html",
                readme=readme
            )

    except zipfile.BadZipFile:
        return render_template(
            "index.html",
            error="The uploaded file is not a valid ZIP archive."
        )

    except Exception as e:
        return render_template(
            "index.html",
            error=f"Documentation generation failed: {e}"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )