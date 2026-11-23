"""
theme.py - Centralized Formatting & Style System for OsdagBridge LaTeX Reports
=============================================================================
Single Source of Truth (SSOT) for all layout rules, visual attributes, color
palettes, table configurations, header/footer themes, and typography.

All report chapter generators and report_generator.py import from this module
to maintain visual consistency, professional aesthetics, and effortless global
customization.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PageGeometry:
    """Document page dimensions and margins (A4)."""
    paper_size: str = "a4paper"
    top_margin_mm: float = 25.0
    bottom_margin_mm: float = 25.0
    left_margin_mm: float = 20.0
    right_margin_mm: float = 20.0
    head_height_mm: float = 14.5
    head_sep_mm: float = 7.0
    foot_skip_mm: float = 12.0
    # Threshold buffer to prevent rows bleeding into footer (Page 30 G4 fix)
    bottom_threshold_pt: float = 40.0


@dataclass(frozen=True)
class ColorPalette:
    """Standardized color schemes for reports, charts, and table themes."""
    # Institutional colors
    primary_hex: str = "1B365D"       # Deep Osdag/IIT Bombay Navy
    primary_rgb: tuple = (27, 54, 93)
    secondary_hex: str = "006699"     # Steel Blue Accent
    secondary_rgb: tuple = (0, 102, 153)
    dark_neutral_hex: str = "2C3E50"  # Charcoal Body Text
    light_neutral_hex: str = "F8FAFC" # Off-white table alt row
    
    # Status colors
    pass_green_hex: str = "27AE60"    # Forest Green for Passing checks
    pass_green_rgb: tuple = (39, 174, 96)
    fail_red_hex: str = "C0392B"      # Crimson Red for Failing checks
    fail_red_rgb: tuple = (192, 57, 43)
    warning_amber_hex: str = "E67E22" # Amber warning
    
    # Table theme
    table_header_bg: str = "D9E2EC"   # Muted Blue-Gray Header
    table_alt_bg: str = "F0F4F8"      # Light Tint for Alternating Rows
    table_border_hex: str = "9FB3C8"  # Border Gray
    threshold_line_hex: str = "C0392B" # Red dashed reference line for UR=1.0


@dataclass(frozen=True)
class TableTheme:
    """Table layout, cell padding, and header repetition rules."""
    tabcolsep_pt: float = 5.0
    arraystretch: float = 1.25
    header_font_size: str = r"\small\bfseries"
    body_font_size: str = r"\small"
    row_height_pt: float = 18.0
    
    # LaTeX Column Helpers
    col_left_align: str = r"L"
    col_center_align: str = r"C"
    col_right_align: str = r"R"


class ReportTheme:
    """Master theme manager providing unified styling commands to LaTeX generator."""
    geometry = PageGeometry()
    colors = ColorPalette()
    tables = TableTheme()

    @classmethod
    def get_latex_preamble_styling(cls) -> str:
        """Emits LaTeX styling definitions, color declarations, and package options."""
        return r"""
% --- OsdagBridge Centralized Styling (SSOT from theme.py) ---
\usepackage[
    """ + cls.geometry.paper_size + r""",
    top=""" + f"{cls.geometry.top_margin_mm:.1f}mm" + r""",
    bottom=""" + f"{cls.geometry.bottom_margin_mm:.1f}mm" + r""",
    left=""" + f"{cls.geometry.left_margin_mm:.1f}mm" + r""",
    right=""" + f"{cls.geometry.right_margin_mm:.1f}mm" + r""",
    headheight=""" + f"{cls.geometry.head_height_mm:.1f}mm" + r""",
    headsep=""" + f"{cls.geometry.head_sep_mm:.1f}mm" + r""",
    footskip=""" + f"{cls.geometry.foot_skip_mm:.1f}mm" + r""",
    marginparwidth=0mm,
    marginparsep=0mm
]{geometry}

\usepackage{xcolor}
\definecolor{OsdagNavy}{HTML}{""" + cls.colors.primary_hex + r"""}
\definecolor{OsdagBlue}{HTML}{""" + cls.colors.secondary_hex + r"""}
\definecolor{OsdagPass}{HTML}{""" + cls.colors.pass_green_hex + r"""}
\definecolor{OsdagFail}{HTML}{""" + cls.colors.fail_red_hex + r"""}
\definecolor{OsdagHeaderBg}{HTML}{""" + cls.colors.table_header_bg + r"""}
\definecolor{OsdagAltBg}{HTML}{""" + cls.colors.table_alt_bg + r"""}
\definecolor{OsdagBorder}{HTML}{""" + cls.colors.table_border_hex + r"""}

% Spacing and Table Row Protections
\setlength{\tabcolsep}{""" + f"{cls.tables.tabcolsep_pt:.1f}pt" + r"""}
\renewcommand{\arraystretch}{""" + f"{cls.tables.arraystretch:.2f}" + r"""}
\newcommand{\tableheaderfont}{""" + cls.tables.header_font_size + r"""}
\newcommand{\tablebodyfont}{""" + cls.tables.body_font_size + r"""}

% Column alignment wrappers with wrapping support
\usepackage{array}
\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}p{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}p{#1}}

% Prevent orphan rows and footer overlap
\widowpenalty=10000
\clubpenalty=10000
\raggedbottom
"""

    @classmethod
    def make_longtable_headers(cls, caption_text: str, label: str, col_headers: list, col_count: int) -> str:
        """
        Builds standardized longtable headers with \endfirsthead, \endhead, \endfoot, \endlastfoot
        ensuring headers repeat on every page break (FOSSEE Task 1 Requirement 1).
        """
        header_row = " & ".join([f"\\textbf{{{h}}}" for h in col_headers]) + r" \\[4pt]"
        
        return rf"""\caption{{\textbf{{{caption_text}}}}}\label{{{label}}} \\
\hline
\rowcolor{{OsdagHeaderBg}}
{header_row}
\hline
\endfirsthead

\multicolumn{{{col_count}}}{{c}}{{\footnotesize\itshape\color{{OsdagBlue}} \tablename\ \thetable{{}} -- continued from previous page}} \\[4pt]
\hline
\rowcolor{{OsdagHeaderBg}}
{header_row}
\hline
\endhead

\hline
\multicolumn{{{col_count}}}{{r}}{{\footnotesize\itshape\color{{gray}} Continued on next page\dots}} \\
\endfoot

\hline
\endlastfoot
"""

    @classmethod
    def format_status_badge(cls, passed: bool) -> str:
        """Formats Pass / Fail badge with semantic coloring."""
        if passed:
            return r"\textcolor{OsdagPass}{\textbf{Pass}}"
        else:
            return r"\textcolor{OsdagFail}{\textbf{Fail}}"
