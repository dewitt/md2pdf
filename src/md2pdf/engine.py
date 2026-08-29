"""
Core conversion engine for md2pdf.
"""

import sys
import os
import re
import base64
import json
import urllib.request
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable, PageBreak
)
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from .styles import get_custom_styles, get_font_names, register_system_fonts

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        sans_font, sans_bold, mono_font, mono_bold = get_font_names()
        self.setFont(sans_font, 8)
        self.setFillColor(colors.HexColor("#5f6368"))
        
        # Header (pages after first)
        if self._pageNumber > 1:
            header_title = getattr(self, '_doc_header', 'Technical & Engineering Report')
            self.drawString(36, 760, header_title)
            self.setStrokeColor(colors.HexColor("#dadce0"))
            self.setLineWidth(0.5)
            self.line(36, 752, 576, 752)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#dadce0"))
        self.setLineWidth(0.5)
        self.line(36, 42, 576, 42)
        
        footer_text = getattr(self, '_doc_footer', 'Confidential & Proprietary — Engineering Document')
        self.drawString(36, 30, footer_text)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_text)
        self.restoreState()

def fetch_mermaid_png(mermaid_code):
    try:
        obj = {"code": mermaid_code.strip(), "mermaid": {"theme": "default"}}
        b64 = base64.urlsafe_b64encode(json.dumps(obj).encode('utf-8')).decode('ascii')
        url = f"https://mermaid.ink/img/{b64}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (md2pdf)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            tmp_f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp_f.write(data)
            tmp_f.close()
            return tmp_f.name
    except Exception as e:
        print(f"Warning: Failed to render Mermaid diagram ({e})", file=sys.stderr)
        return None

def clean_inline_md(text):
    sans_font, sans_bold, mono_font, mono_bold = get_font_names()
    text = text.replace("<br/>", "___BR___").replace("<br>", "___BR___")
    
    # Replace LaTeX/math arrows and tokens
    text = (text.replace(r'$\rightarrow$', '→')
                .replace(r'$\leftarrow$', '←')
                .replace(r'$\leftrightarrow$', '↔')
                .replace(r'$\Rightarrow$', '⇒')
                .replace(r'$\Leftarrow$', '⇐')
                .replace(r'$\Leftrightarrow$', '⇔'))
                
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("___BR___", "<br/>")
    
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic: *text*
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code: `code`
    text = re.sub(r'`(.+?)`', rf'<font face="{mono_font}" color="#c5221f" size="8"><b>\1</b></font>', text)
    # Markdown links: [text](url)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<font color="#1a73e8"><u>\1</u></font>', text)
    return text

def parse_markdown_to_flowables(md_text, styles):
    flowables = []
    lines = md_text.split('\n')
    i = 0
    n = len(lines)
    
    table_pattern = re.compile(r'^\s*\|(.+)\|\s*$')
    
    while i < n:
        line = lines[i]
        
        # Mermaid code block
        if line.strip().startswith('```mermaid'):
            mermaid_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                mermaid_lines.append(lines[i])
                i += 1
            i += 1
            mermaid_code = '\n'.join(mermaid_lines)
            png_path = fetch_mermaid_png(mermaid_code)
            if png_path:
                try:
                    with PILImage.open(png_path) as im:
                        w, h = im.size
                    max_w = 520.0
                    max_h = 320.0
                    ratio = min(max_w / w, max_h / h, 1.0)
                    img = Image(png_path, width=w * ratio, height=h * ratio)
                    flowables.append(Spacer(1, 6))
                    flowables.append(img)
                    flowables.append(Spacer(1, 6))
                except Exception as e:
                    print(f"Error sizing Mermaid image: {e}", file=sys.stderr)
            continue
            
        # General code block
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            
            sans_font, sans_bold, mono_font, mono_bold = get_font_names()
            max_line_len = max((len(l) for l in code_lines), default=0)
            if max_line_len > 115:
                font_size = 5.2
                leading = 6.8
            elif max_line_len > 95:
                font_size = 6.0
                leading = 7.6
            elif max_line_len > 80:
                font_size = 6.5
                leading = 8.0
            else:
                font_size = 7.0
                leading = 8.5

            chunk_size = 25
            chunks = [code_lines[j:j+chunk_size] for j in range(0, len(code_lines), chunk_size)] if code_lines else [[]]
            table_cells = []
            for chunk in chunks:
                chunk_text = '\n'.join(chunk)
                chunk_text = (chunk_text.replace(r'$\rightarrow$', '→')
                                        .replace(r'$\leftarrow$', '←')
                                        .replace(r'$\leftrightarrow$', '↔'))
                code_escaped = chunk_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                p = Paragraph(f"<font face='{mono_font}' size='{font_size}'>{code_escaped.replace(chr(10), '<br/>').replace(' ', '&nbsp;')}</font>", styles['CustomCodeBlock'])
                table_cells.append([p])
            
            t = Table(table_cells, colWidths=[530])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#dadce0")),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            flowables.append(Spacer(1, 4))
            flowables.append(t)
            flowables.append(Spacer(1, 5))
            continue
            
        # Markdown table
        if table_pattern.match(line):
            table_rows = []
            while i < n and table_pattern.match(lines[i]):
                row_line = lines[i].strip()
                if re.match(r'^\|[\s\-:\.]+(\|[\s\-:\.]+)+\|$', row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.strip('|').split('|')]
                table_rows.append(cells)
                i += 1
                
            if table_rows:
                num_cols = max(len(r) for r in table_rows)
                norm_rows = []
                for r_idx, row in enumerate(table_rows):
                    while len(row) < num_cols:
                        row.append("")
                    styled_row = []
                    for c_idx, cell in enumerate(row):
                        cell_fmt = clean_inline_md(cell)
                        if r_idx == 0:
                            p = Paragraph(f"<b>{cell_fmt}</b>", styles['CustomTableHeader'])
                        else:
                            p = Paragraph(cell_fmt, styles['CustomTableCell'])
                        styled_row.append(p)
                    norm_rows.append(styled_row)
                
                total_w = 530.0
                if num_cols == 2:
                    col_widths = [140.0, 390.0]
                elif num_cols == 3:
                    col_widths = [120.0, 150.0, 260.0]
                elif num_cols == 4:
                    col_widths = [90.0, 110.0, 110.0, 220.0]
                else:
                    col_widths = [total_w / num_cols] * num_cols
                    
                t = Table(norm_rows, colWidths=col_widths)
                table_style_commands = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e8f0fe")),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#dadce0")),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e8eaed")),
                    ('TOPPADDING', (0, 0), (-1, -1), 4.5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]
                for r_idx in range(1, len(norm_rows)):
                    if r_idx % 2 == 0:
                        table_style_commands.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor("#f8f9fa")))
                    else:
                        table_style_commands.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor("#ffffff")))
                        
                t.setStyle(TableStyle(table_style_commands))
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 6))
            continue
            
        # Alert / Blockquote
        if line.strip().startswith('>'):
            quote_lines = []
            while i < n and lines[i].strip().startswith('>'):
                quote_lines.append(re.sub(r'^>\s?', '', lines[i].strip()))
                i += 1
            quote_text = ' '.join(quote_lines)
            p = Paragraph(clean_inline_md(quote_text), styles['CustomBlockquote'])
            t = Table([[p]], colWidths=[530])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef7e0")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#fbbc04")),
                ('LINELEFT', (0, 0), (0, -1), 3.0, colors.HexColor("#f29900")),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            flowables.append(Spacer(1, 4))
            flowables.append(t)
            flowables.append(Spacer(1, 5))
            continue

        # Horizontal Rule
        if re.match(r'^\s*(\-{3,}|\*{3,}|_{3,})\s*$', line):
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#dadce0"), spaceBefore=3, spaceAfter=4))
            i += 1
            continue
            
        # Headings
        if line.startswith('# '):
            flowables.append(Spacer(1, 8))
            flowables.append(Paragraph(clean_inline_md(line[2:].strip()), styles['CustomH1']))
            flowables.append(Spacer(1, 4))
            i += 1
            continue
        elif line.startswith('## '):
            flowables.append(Spacer(1, 7))
            flowables.append(Paragraph(clean_inline_md(line[3:].strip()), styles['CustomH2']))
            flowables.append(Spacer(1, 3))
            i += 1
            continue
        elif line.startswith('### '):
            flowables.append(Spacer(1, 5))
            flowables.append(Paragraph(clean_inline_md(line[4:].strip()), styles['CustomH3']))
            flowables.append(Spacer(1, 2))
            i += 1
            continue
        elif line.startswith('#### '):
            flowables.append(Spacer(1, 4))
            flowables.append(Paragraph(clean_inline_md(line[5:].strip()), styles['CustomH4']))
            flowables.append(Spacer(1, 2))
            i += 1
            continue
            
        # Bullet list item
        if re.match(r'^\s*[\*\-\+]\s+', line):
            indent_level = (len(line) - len(line.lstrip())) // 2
            bullet_text = re.sub(r'^\s*[\*\-\+]\s+', '', line)
            bullet_style = styles['CustomBullet']
            if indent_level > 0:
                bullet_style = styles['CustomBullet2']
            p = Paragraph(f"• {clean_inline_md(bullet_text)}", bullet_style)
            flowables.append(p)
            i += 1
            continue
            
        # Numbered list item
        if re.match(r'^\s*\d+\.\s+', line):
            num_match = re.match(r'^\s*(\d+\.)\s+(.+)$', line)
            if num_match:
                prefix, num_text = num_match.groups()
                p = Paragraph(f"<b>{prefix}</b> {clean_inline_md(num_text)}", styles['CustomNumberedList'])
                flowables.append(p)
            i += 1
            continue
            
        # Standard paragraph
        if line.strip():
            p = Paragraph(clean_inline_md(line.strip()), styles['CustomBody'])
            flowables.append(p)
            flowables.append(Spacer(1, 3))
            
        i += 1
        
    return flowables

def convert_md_to_pdf(input_md_path, output_pdf_path=None, header_title=None, footer_text=None):
    if not output_pdf_path:
        output_pdf_path = os.path.splitext(input_md_path)[0] + ".pdf"
        
    with open(input_md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Extract first H1 heading as default header title if not provided
    if not header_title:
        h1_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
        if h1_match:
            header_title = h1_match.group(1).strip()
        else:
            header_title = os.path.basename(input_md_path)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = get_custom_styles()
    flowables = parse_markdown_to_flowables(md_text, styles)
    
    def canvas_factory(*args, **kwargs):
        c = NumberedCanvas(*args, **kwargs)
        c._doc_header = header_title
        if footer_text:
            c._doc_footer = footer_text
        return c

    doc.build(flowables, canvasmaker=canvas_factory)
    print(f"Successfully generated: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
    return output_pdf_path
