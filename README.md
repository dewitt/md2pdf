# md2pdf

**Publication-Quality Markdown to PDF Converter with Native Mermaid Diagram Rendering & Executive Styling**

`md2pdf` is a lightweight, zero-browser Markdown-to-PDF compiler designed specifically for technical specifications, RFCs, and executive reports. It reliably produces beautifully styled documents on headless Linux environments (e.g. Cloudtop, remote servers, CI/CD) and macOS without requiring Chromium, Puppeteer, or desktop graphical display sessions.

---

## ✨ Key Features

* **Rendered Mermaid Diagrams**: Automatically detects and compiles Mermaid flowcharts, class diagrams, state machines, sequence diagrams, and architecture maps via `mermaid.ink` and embeds them as crisp, high-resolution figures.
* **Rich Executive Tables**: Dynamic column width balancing (e.g. key-value tables automatically allocate compact title columns and generous value space), Google Blue headers, alternating row shading (`#ffffff` / `#f8f9fa`), and clean cell padding.
* **Clean Engineering Typography**: Standardized Helvetica-Bold hierarchy (H1–H4), Courier code blocks with background shading, and styled blockquotes/alerts.
* **Two-Pass Page Numbering**: Renders running headers (from page 2 onwards) and official footers with *"Google Confidential & Proprietary"* disclaimers and exact *"Page X of Y"* counts.
* **Headless & Sandbox Safe**: Operates purely in Python using `ReportLab` and `Pillow`, completely avoiding the Chrome headless crashpad/remoting/sandbox hangs common on enterprise Linux development machines.

---

## 🚀 Quick Start & Installation

### Option 1: One-Line Installer (Recommended)

Clone the repository and run the automated installer:

```bash
git clone git@github.com:dewitt/md2pdf.git ~/git/md2pdf
cd ~/git/md2pdf
./install.sh
```

This will create an isolated virtual environment in `~/.local/share/md2pdf_venv/`, install all dependencies in editable mode, and link `md2pdf` into `~/.local/bin/`.

Ensure `~/.local/bin` is in your `$PATH` (in `~/.zshrc` or `~/.bashrc`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Option 2: Manual Setup via `pip`

```bash
# 1. Create a virtual environment
python3 -m venv ~/.local/share/md2pdf_venv

# 2. Install the package
~/.local/share/md2pdf_venv/bin/pip install -e ~/git/md2pdf

# 3. Create a symlink in your PATH
ln -sf ~/.local/share/md2pdf_venv/bin/md2pdf ~/.local/bin/md2pdf
```

---

## 📖 Usage

### Basic Conversion

```bash
# Converts report.md to report.pdf in the same directory
md2pdf report.md
```

### Specify Custom Output Path

```bash
md2pdf input.md /path/to/custom_output.pdf
```

### Custom Running Header & Footer

```bash
md2pdf spec.md --header "Project Sobi — Architecture Specification" --footer "Internal Confidential"
```

### Help & Options

```bash
md2pdf --help
```

```text
usage: md2pdf [-h] [--header HEADER] [--footer FOOTER] [-v] input [output]

Convert Markdown files to publication-quality PDFs with rendered Mermaid diagrams.

positional arguments:
  input            Path to input Markdown (.md) file
  output           Optional path to output PDF file (defaults to input filename with .pdf)

options:
  -h, --help       show this help message and exit
  --header HEADER  Custom running header title
  --footer FOOTER  Custom running footer text
  -v, --version    show program's version number and exit
```

---

## 🎨 Mermaid Diagram Authoring Guidelines

To ensure 100% diagram compilation without HTTP 400 bad requests from diagram backends:

1. **Subgraphs**: Use plain square brackets without quotes:
   ```mermaid
   subgraph ClientTier [1. Client and Ingestion Tier]
       UI[Web UI]
   end
   ```
   *(Avoid `subgraph ClientTier ["1. Client Tier"]`)*.

2. **Edge Labels**: Avoid raw parentheses inside edge text delimiters:
   ```mermaid
   A -->|Stage: ACTIVE / ON-HOLD| B
   ```
   *(Avoid `A -->|Stage (ACTIVE / ON-HOLD)| B`)*.

3. **Comparison Symbols**: Avoid raw `<` characters inside node labels (they get parsed as unclosed HTML tags). Use `under 500ms` or `&lt;500ms` instead of `<500ms`.

4. **Node Shapes**: For paths and directories, avoid unclosed single slashes like `Node[/workspace]`. Use standard quoted nodes `Node["workspace Directory"]` or double-slashed parallelograms `Node[/workspace/]`.

---

## 💻 Remote Development Workflow (SSH + MacBook Pro)

When paired with Cloudtop and Google Drive for Desktop:

1. SSH into the remote machine:
   ```bash
   ssh dewitt-cloudtop
   ```
2. Generate reports and compile to PDF:
   ```bash
   md2pdf report.md
   ```
3. Copy to Google Drive:
   ```bash
   cp report.md report.pdf "$HOME/DriveFileStream/My Drive/ProjectFolder/"
   ```
4. Open the PDF immediately on your MacBook Pro in Preview via `/Volumes/GoogleDrive/My Drive/ProjectFolder/report.pdf`.

---

## 🛠️ Architecture

```
md2pdf/
├── bin/
│   └── md2pdf                   # Standalone bash wrapper
├── examples/
│   └── sample.md                # Example markdown test document
├── src/
│   └── md2pdf/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Argument parsing & entry point
│       ├── engine.py            # Flowable parser & ReportLab PDF generator
│       └── styles.py            # Color palettes, typography & paragraph styles
├── install.sh                   # Self-contained installer
├── pyproject.toml               # PEP 517/518 build definition
├── LICENSE                      # MIT License
└── README.md                    # Documentation
```

---

## 📄 License

MIT License. Copyright (c) 2026 DeWitt Clinton.
