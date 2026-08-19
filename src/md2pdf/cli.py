"""
Command line interface for md2pdf.
"""

import sys
import argparse
import os

from .engine import convert_md_to_pdf
from . import __version__

def main():
    parser = argparse.ArgumentParser(
        prog="md2pdf",
        description="Convert Markdown files to publication-quality PDFs with rendered Mermaid diagrams."
    )
    parser.add_argument("input", help="Path to input Markdown (.md) file")
    parser.add_argument("output", nargs="?", help="Optional path to output PDF file (defaults to input filename with .pdf)")
    parser.add_argument("--header", help="Custom running header title")
    parser.add_argument("--footer", help="Custom running footer text")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        convert_md_to_pdf(
            input_md_path=args.input,
            output_pdf_path=args.output,
            header_title=args.header,
            footer_text=args.footer
        )
    except Exception as e:
        print(f"Error converting document: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
