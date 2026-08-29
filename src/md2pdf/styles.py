"""
Styles and color definitions for md2pdf.
"""

import os
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

_FONTS_REGISTERED = False
_HAS_DEJAVU_SANS = False
_HAS_DEJAVU_MONO = False
_HAS_SYMBOLA = False

def register_system_fonts():
    global _FONTS_REGISTERED, _HAS_DEJAVU_SANS, _HAS_DEJAVU_MONO, _HAS_SYMBOLA
    if _FONTS_REGISTERED:
        return

    font_candidates = {
        'DejaVuSans': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
            '/usr/local/share/fonts/DejaVuSans.ttf',
            os.path.expanduser('~/.fonts/DejaVuSans.ttf'),
        ],
        'DejaVuSans-Bold': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
            '/usr/local/share/fonts/DejaVuSans-Bold.ttf',
            os.path.expanduser('~/.fonts/DejaVuSans-Bold.ttf'),
        ],
        'DejaVuSans-Oblique': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans-Oblique.ttf',
            '/usr/local/share/fonts/DejaVuSans-Oblique.ttf',
            os.path.expanduser('~/.fonts/DejaVuSans-Oblique.ttf'),
        ],
        'DejaVuSans-BoldOblique': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf',
            '/usr/local/share/fonts/DejaVuSans-BoldOblique.ttf',
            os.path.expanduser('~/.fonts/DejaVuSans-BoldOblique.ttf'),
        ],
        'DejaVuSansMono': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
            '/usr/share/fonts/dejavu/DejaVuSansMono.ttf',
            '/usr/local/share/fonts/DejaVuSansMono.ttf',
            os.path.expanduser('~/.fonts/DejaVuSansMono.ttf'),
        ],
        'DejaVuSansMono-Bold': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
            '/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf',
            '/usr/local/share/fonts/DejaVuSansMono-Bold.ttf',
            os.path.expanduser('~/.fonts/DejaVuSansMono-Bold.ttf'),
        ],
        'DejaVuSansMono-Oblique': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf',
            '/usr/share/fonts/dejavu/DejaVuSansMono-Oblique.ttf',
            '/usr/local/share/fonts/DejaVuSansMono-Oblique.ttf',
            os.path.expanduser('~/.fonts/DejaVuSansMono-Oblique.ttf'),
        ],
        'DejaVuSansMono-BoldOblique': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-BoldOblique.ttf',
            '/usr/share/fonts/dejavu/DejaVuSansMono-BoldOblique.ttf',
            '/usr/local/share/fonts/DejaVuSansMono-BoldOblique.ttf',
            os.path.expanduser('~/.fonts/DejaVuSansMono-BoldOblique.ttf'),
        ],
        'Symbola': [
            '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf',
            '/usr/share/fonts/truetype/ancient-scripts/Symbola.ttf',
        ],
    }

    registered = set()
    for font_name, paths in font_candidates.items():
        for p in paths:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, p))
                    registered.add(font_name)
                    break
                except Exception:
                    pass

    if 'DejaVuSans' in registered:
        _HAS_DEJAVU_SANS = True
        bold = 'DejaVuSans-Bold' if 'DejaVuSans-Bold' in registered else 'DejaVuSans'
        italic = 'DejaVuSans-Oblique' if 'DejaVuSans-Oblique' in registered else 'DejaVuSans'
        boldItalic = 'DejaVuSans-BoldOblique' if 'DejaVuSans-BoldOblique' in registered else bold
        try:
            registerFontFamily('DejaVuSans', normal='DejaVuSans', bold=bold, italic=italic, boldItalic=boldItalic)
        except Exception:
            pass

    if 'DejaVuSansMono' in registered:
        _HAS_DEJAVU_MONO = True
        bold = 'DejaVuSansMono-Bold' if 'DejaVuSansMono-Bold' in registered else 'DejaVuSansMono'
        italic = 'DejaVuSansMono-Oblique' if 'DejaVuSansMono-Oblique' in registered else 'DejaVuSansMono'
        boldItalic = 'DejaVuSansMono-BoldOblique' if 'DejaVuSansMono-BoldOblique' in registered else bold
        try:
            registerFontFamily('DejaVuSansMono', normal='DejaVuSansMono', bold=bold, italic=italic, boldItalic=boldItalic)
        except Exception:
            pass

    if 'Symbola' in registered:
        _HAS_SYMBOLA = True

    _FONTS_REGISTERED = True

def get_font_names():
    register_system_fonts()
    sans_font = 'DejaVuSans' if _HAS_DEJAVU_SANS else 'Helvetica'
    sans_bold = 'DejaVuSans-Bold' if _HAS_DEJAVU_SANS else 'Helvetica-Bold'
    mono_font = 'DejaVuSansMono' if _HAS_DEJAVU_MONO else 'Courier'
    mono_bold = 'DejaVuSansMono-Bold' if _HAS_DEJAVU_MONO else 'Courier-Bold'
    return sans_font, sans_bold, mono_font, mono_bold

def get_custom_styles():
    sans_font, sans_bold, mono_font, mono_bold = get_font_names()
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName=sans_bold,
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#1a73e8"),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName=sans_bold,
        fontSize=12.5,
        leading=15.5,
        textColor=colors.HexColor("#202124"),
        spaceBefore=6,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontName=sans_bold,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1967d2"),
        spaceBefore=4,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        'CustomH4',
        parent=styles['Heading4'],
        fontName=sans_bold,
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor("#3c4043"),
        spaceBefore=3,
        spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=sans_font,
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#202124"),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName=sans_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#202124"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=1.5,
    ))
    styles.add(ParagraphStyle(
        'CustomBullet2',
        parent=styles['Normal'],
        fontName=sans_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#202124"),
        leftIndent=24,
        firstLineIndent=-8,
        spaceAfter=1.5,
    ))
    styles.add(ParagraphStyle(
        'CustomNumberedList',
        parent=styles['Normal'],
        fontName=sans_font,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#202124"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=1.5,
    ))
    styles.add(ParagraphStyle(
        'CustomTableHeader',
        parent=styles['Normal'],
        fontName=sans_bold,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1a73e8"),
    ))
    styles.add(ParagraphStyle(
        'CustomTableCell',
        parent=styles['Normal'],
        fontName=sans_font,
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#202124"),
    ))
    styles.add(ParagraphStyle(
        'CustomCodeBlock',
        parent=styles['Normal'],
        fontName=mono_font,
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#202124"),
    ))
    styles.add(ParagraphStyle(
        'CustomBlockquote',
        parent=styles['Normal'],
        fontName=sans_font,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#5f6368"),
    ))

    return styles

