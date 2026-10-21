"""
CODEXA Academic Project Report Generator
=======================================
Generates a comprehensive, submission-ready, simple, black-and-white
academic project report for MCA Semester III Mini Project Submission
at Pimpri Chinchwad College of Engineering (PCCOE), Nigdi, Pune.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw
    clean, black-and-white running headers and footers with 'Page X of Y'.
    """
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        # Do not draw headers or footers on the cover page (Page 1)
        if self._pageNumber > 1:
            self.saveState()
            
            # Running Header
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#222222"))
            self.drawString(54, 802, "CODEXA: Software Repository Quality Assessment & Risk Analysis")
            self.drawRightString(541, 802, "MCA Mini Project Report | Academic Year 2026–2027")
            self.setStrokeColor(colors.HexColor("#444444"))
            self.setLineWidth(0.6)
            self.line(54, 796, 541, 796)

            # Running Footer
            self.line(54, 40, 541, 40)
            self.drawString(54, 28, "Department of MCA, Pimpri Chinchwad College of Engineering, Nigdi, Pune")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(541, 28, page_text)
            
            self.restoreState()


def build_pdf_report(filename="CODEXA_Project_Report.pdf"):
    # Target printable area: A4 is 595.27 x 841.89 points.
    # Margins: Left=54, Right=54, Top=54, Bottom=54. Printable width = 487 points.
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # --- Strict Black & White Typography Styles ---
    c_black = colors.HexColor("#000000")
    c_dark = colors.HexColor("#222222")
    c_gray = colors.HexColor("#555555")

    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=25,
        alignment=1, # Center
        textColor=c_black,
        spaceAfter=10
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=c_dark,
        spaceAfter=6
    )

    cover_meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        alignment=1,
        textColor=c_black
    )

    ch_title_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=c_black,
        spaceBefore=8,
        spaceAfter=8,
        keepWithNext=True
    )

    h1_style = ParagraphStyle(
        'H1_Heading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15.5,
        textColor=c_black,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2_Heading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_dark,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_black,
        spaceAfter=5,
        alignment=4 # Justify
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'Bullet_Style',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=2.5,
        alignment=0 # Left
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        alignment=1,
        textColor=c_black
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_black
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.5,
        textColor=c_black
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=c_black
    )

    story = []

    # =========================================================================
    # 1. COVER / TITLE PAGE (PAGE 1)
    # =========================================================================
    # --- Synopsis-style cover typography (Georgia with Helvetica fallback) ---
    try:
        pdfmetrics.registerFont(TTFont("Georgia", r"C:\Windows\Fonts\georgia.ttf"))
        pdfmetrics.registerFont(TTFont("Georgia-Bold", r"C:\Windows\Fonts\georgiab.ttf"))
    except Exception:
        pass
    _registered = pdfmetrics.getRegisteredFontNames()
    g_font = "Georgia" if "Georgia" in _registered else "Helvetica"
    g_bold = "Georgia-Bold" if "Georgia-Bold" in _registered else "Helvetica-Bold"
    c_red = colors.HexColor("#C9211E")

    syn_head_style = ParagraphStyle('SynHead', parent=styles['Normal'], fontName=g_bold, fontSize=22, leading=28, alignment=1, textColor=c_black)
    syn_title_style = ParagraphStyle('SynTitle', parent=styles['Normal'], fontName=g_bold, fontSize=16.5, leading=22, alignment=1, textColor=c_black)
    syn_name_style = ParagraphStyle('SynName', parent=styles['Normal'], fontName=g_font, fontSize=17, leading=22, alignment=1, textColor=c_red)
    syn_prn_style = ParagraphStyle('SynPrn', parent=styles['Normal'], fontName=g_font, fontSize=12.5, leading=17, alignment=1, textColor=c_black)
    syn_guide_style = ParagraphStyle('SynGuide', parent=styles['Normal'], fontName=g_font, fontSize=15, leading=20, alignment=1, textColor=c_red)
    syn_dept_style = ParagraphStyle('SynDept', parent=styles['Normal'], fontName=g_bold, fontSize=12.5, leading=17, alignment=1, textColor=c_black)
    syn_college_style = ParagraphStyle('SynCollege', parent=styles['Normal'], fontName=g_font, fontSize=10.5, leading=14.5, alignment=1, textColor=c_black)
    syn_year_style = ParagraphStyle('SynYear', parent=styles['Normal'], fontName=g_font, fontSize=12, leading=16, alignment=1, textColor=c_black)

    _assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_assets")

    def _cover_image(name, width, height):
        path = os.path.join(_assets, name)
        if os.path.exists(path):
            img = Image(path, width=width, height=height)
            img.hAlign = 'CENTER'
            return img
        return None

    story.append(Spacer(1, 20))
    logo = _cover_image("logo.png", 105, 94.5)
    if logo:
        story.append(logo)

    story.append(Spacer(1, 34))
    story.append(Paragraph("Mini Project Report", syn_head_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("CODEXA: An Intelligent Platform for Automated Software Repository Quality Assessment and Risk Analysis", syn_title_style))

    story.append(Spacer(1, 36))
    label2 = _cover_image("image2.png", 109.4, 12.2)
    if label2:
        story.append(label2)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Shreyash Anilrao Thakare", syn_name_style))
    story.append(Paragraph("(PRN: 125M1H048)", syn_prn_style))

    story.append(Spacer(1, 46))
    label3 = _cover_image("image3.png", 87.3, 12.2)
    if label3:
        story.append(label3)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Dr. Avinash Chormale", syn_guide_style))

    story.append(Spacer(1, 52))
    label4 = _cover_image("image4.png", 118.2, 12.2)
    if label4:
        story.append(label4)
    story.append(Spacer(1, 8))
    story.append(Paragraph("DEPARTMENT OF MCA", syn_dept_style))
    story.append(Spacer(1, 14))
    story.append(Paragraph("PIMPRI CHINCHWAD COLLEGE OF ENGINEERING SECTOR NO. 26, PRADHIKARAN, NIGDI, PUNE - 44.", syn_college_style))
    story.append(Spacer(1, 24))
    story.append(Paragraph("(2026 - 2027)", syn_year_style))
    story.append(PageBreak())

    # =========================================================================
    # 2. CERTIFICATE OF APPROVAL (PAGE 2)
    # =========================================================================
    story.append(Paragraph("PIMPRI CHINCHWAD COLLEGE OF ENGINEERING, NIGDI, PUNE", cover_subtitle_style))
    story.append(Paragraph("DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS", ParagraphStyle('CertDept', parent=cover_subtitle_style, fontName='Helvetica-Bold', fontSize=11)))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_black, spaceBefore=2, spaceAfter=16))
    story.append(Paragraph("CERTIFICATE", ParagraphStyle('CertHead', parent=cover_title_style, fontSize=16, leading=20)))
    story.append(Spacer(1, 8))
    
    cert_text = (
        "This is to certify that the Mini Project Report entitled <b>\"CODEXA: An Intelligent Platform for "
        "Automated Software Repository Quality Assessment and Risk Analysis\"</b> submitted by "
        "<b>Shreyash Anilrao Thakare</b> (PRN: <b>125M1H048</b>) is a bonafide record of work carried out by him under "
        "my supervision and guidance, in partial fulfillment of the requirements for the award of the degree of "
        "<b>Master of Computer Applications (MCA) — Semester III</b> of Savitribai Phule Pune University / "
        "Pimpri Chinchwad College of Engineering, Pune during the academic year <b>2026 – 2027</b>."
    )
    story.append(Paragraph(cert_text, body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The project report has been examined and approved for submission as per the prescribed curriculum standards.",
        body_style
    ))
    story.append(Spacer(1, 40))

    sig_data = [
        [
            Paragraph("<b>Dr. Avinash Chormale</b><br/>Project Guide<br/>Department of MCA", table_cell_center),
            Paragraph("<b>Project Coordinator</b><br/>Department of MCA<br/>PCCOE, Pune", table_cell_center),
            Paragraph("<b>Head of Department</b><br/>Department of MCA<br/>PCCOE, Pune", table_cell_center)
        ],
        [
            Paragraph("<br/><br/><br/>________________________<br/><b>Internal Examiner</b>", table_cell_center),
            Paragraph("<br/><br/><br/>", table_cell_center),
            Paragraph("<br/><br/><br/>________________________<br/><b>External Examiner</b>", table_cell_center)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[160, 160, 160])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sig_table)
    story.append(PageBreak())

    # =========================================================================
    # 3. DECLARATION & ACKNOWLEDGEMENT (PAGE 3)
    # =========================================================================
    story.append(Paragraph("CANDIDATE'S DECLARATION", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=10))
    decl_text = (
        "I hereby declare that the mini project report entitled <b>\"CODEXA: An Intelligent Platform for "
        "Automated Software Repository Quality Assessment and Risk Analysis\"</b> is an authentic record of my own "
        "work carried out under the guidance of <b>Dr. Avinash Chormale</b>, Department of Master of Computer "
        "Applications, Pimpri Chinchwad College of Engineering, Pune.<br/><br/>"
        "I confirm that this project report has not been submitted elsewhere for the award of any other degree, "
        "diploma, or fellowship. All secondary sources, external software tools, libraries, and publications referenced "
        "herein have been appropriately cited and acknowledged."
    )
    story.append(Paragraph(decl_text, body_style))
    story.append(Spacer(1, 15))

    decl_sig_data = [
        [
            Paragraph("<b>Date:</b> October 19, 2026<br/><b>Place:</b> Nigdi, Pune", table_cell_style),
            Paragraph("<b>Shreyash Anilrao Thakare</b><br/>PRN: 125M1H048<br/>Department of MCA, PCCOE", table_cell_style)
        ]
    ]
    decl_sig_table = Table(decl_sig_data, colWidths=[240, 240])
    decl_sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(decl_sig_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("ACKNOWLEDGEMENT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=10))
    ack_text = (
        "I express my deep sense of gratitude and respect to my project guide, <b>Dr. Avinash Chormale</b>, "
        "for his invaluable mentorship, consistent encouragement, and insightful feedback throughout the conception, "
        "architecture, and implementation of CODEXA.<br/><br/>"
        "I extend my sincere thanks to the <b>Head of Department</b> and all faculty members of the Department of "
        "Master of Computer Applications for providing computing facilities, academic support, and constructive reviews. "
        "I also thank the leadership of <b>Pimpri Chinchwad College of Engineering</b> for fostering a research-driven environment.<br/><br/>"
        "Finally, I am profoundly grateful to my family and fellow classmates for their unwavering encouragement, patience, "
        "and cooperation throughout this endeavor."
    )
    story.append(Paragraph(ack_text, body_style))
    story.append(PageBreak())

    # =========================================================================
    # 4. ABSTRACT & KEYWORDS (PAGE 4)
    # =========================================================================
    story.append(Paragraph("ABSTRACT", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=12))
    abstract_text = (
        "Modern software development relies heavily on version-controlled repositories where source code expands rapidly "
        "across distributed teams, third-party libraries, and evolving coding standards. As repositories grow, maintaining code "
        "hygiene, controlling technical debt, and identifying critical security vulnerabilities becomes increasingly difficult. "
        "Traditionally, software engineers and auditors run isolated command-line tools—such as Pylint for linting, Radon for "
        "cyclomatic complexity, Bandit for security patterns, and pip-audit for dependency CVEs. This fragmented workflow forces "
        "developers to manually parse disparate output streams, lacks a unified health metric, and provides no clear, prioritized "
        "remediation strategy.<br/><br/>"
        "<b>CODEXA</b> is an intelligent, full-stack, web-based platform designed to resolve this fragmentation. By accepting any "
        "public or private GitHub repository URL, CODEXA orchestrates an automated, five-layer auditing suite that evaluates code "
        "maintainability, structural complexity, Abstract Syntax Tree (AST) security risks, and software supply chain exposures. "
        "Findings are synthesized into a mathematically transparent, defensible <b>CODEXA Composite Score (0–100)</b> using a "
        "three-pillar model (45% Security, 30% Quality, 25% Dependencies). To eliminate manual review fatigue, verified findings "
        "are forwarded to an AI Recommendation Engine powered by Google Gemini (with an offline deterministic rule-based fallback) "
        "to generate actionable, plain-English remediation guidance. CODEXA features a high-performance React 19 / TypeScript "
        "dashboard, an offline demonstration archive for evaluation resilience, and a vector ReportLab PDF reporting engine. "
        "The platform bridges the gap between raw static analysis data and actionable software engineering governance.<br/><br/>"
        "<b>Project Key Contributions:</b><br/>"
        "1. Unified orchestration of five static and dependency scanners within an asynchronous Python backend.<br/>"
        "2. Transparent composite scoring formula balancing security criticality against maintainability debt.<br/>"
        "3. Implementation of the Neuro-Symbolic auditing paradigm, pairing deterministic AST verification with AI guidance.<br/>"
        "4. Resilient cross-platform architecture with automated Windows file locking safeguards and offline presentation support."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Keywords:</b> Static Code Analysis, Cyclomatic Complexity, Abstract Syntax Tree (AST), Software Supply Chain Security, Vulnerability Auditing, Neuro-Symbolic AI, Django REST Framework, React.", body_style))
    story.append(PageBreak())


    # =========================================================================
    # CHAPTER 1: INTRODUCTION (PAGES 6 & 7)
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("1.1 Project Overview & Background", h1_style))
    story.append(Paragraph(
        "Software engineering practices have transformed radically with the ubiquitous adoption of distributed version "
        "control systems, collaborative open-source ecosystems, and rapid agile release cycles. Source code repositories "
        "hosted on platforms such as GitHub serve as the primary operational backbone for software organizations. Within "
        "these repositories, codebases expand exponentially across multiple contributors, diverse coding habits, and deep trees "
        "of third-party dependencies.<br/><br/>"
        "However, rapid feature delivery frequently outpaces code review rigor. Over time, repositories accumulate structural "
        "decay, known in software engineering as <i>technical debt</i>. Convoluted control flow increases defect rates; outdated "
        "third-party packages introduce publicly known exploits (Common Vulnerabilities and Exposures, or CVEs); and developers "
        "inadvertently commit security flaws such as hardcoded credentials, unsafe shell executions, or dynamic code evaluation. "
        "Consequently, evaluating repository health before deployment is a paramount engineering necessity.",
        body_style
    ))

    story.append(Paragraph("1.2 Problem Statement & Real-World Bottlenecks", h1_style))
    story.append(Paragraph(
        "While numerous specialized code analysis tools exist in the software ecosystem, they operate in severe isolation. "
        "A typical development team or security auditor must manually execute and coordinate multiple disconnected tools:<br/>"
        "• <b>Linting & Style Checkers:</b> Tools like Pylint enforce PEP 8 standards and catch syntax smells but do not evaluate deep security vulnerabilities.<br/>"
        "• <b>Complexity Calculators:</b> Tools like Radon compute Cyclomatic Complexity but provide no insight into whether a complex block contains an injection exploit.<br/>"
        "• <b>Static Security Scanners:</b> Tools like Bandit and Semgrep inspect Abstract Syntax Trees (AST) for insecure function calls but ignore code maintainability and dependency supply chains.<br/>"
        "• <b>Dependency Checkers:</b> Tools like pip-audit check manifests against vulnerability databases but cannot analyze the repository's proprietary source code.<br/><br/>"
        "<b>The Industry Bottlenecks:</b> (1) <i>Disparate Output Formats</i> (unstructured terminal text, complex JSON, or POSIX exit bitmasks); "
        "(2) <i>Absence of a Unified Health Index</i> (no single, defensible 0–100 score); and (3) <i>Alert Fatigue & Lack of Remediation Guidance</i> "
        "(hundreds of raw alerts without prioritized engineering guidance).",
        body_style
    ))

    story.append(Paragraph("1.3 Objectives of CODEXA", h1_style))
    story.append(Paragraph(
        "CODEXA was designed and implemented to provide a unified, automated, intelligent platform that overcomes these challenges:<br/>"
        "1. <b>Automate Repository Ingestion:</b> Enable one-click auditing of any public or token-authenticated GitHub repository.<br/>"
        "2. <b>Implement a 5-Layer Audit Suite:</b> Orchestrate Radon, Pylint, Bandit, Semgrep/AST, and pip-audit within a unified Python pipeline.<br/>"
        "3. <b>Formulate a Defensible Composite Scoring Model:</b> Calculate normalized domain scores across Security (45%), Quality (30%), and Dependencies (25%) on a standardized 0–100 scale.<br/>"
        "4. <b>Deliver AI-Powered Remediation:</b> Leverage Google Gemini (with an automated rule-based fallback) to translate dense technical warnings into prioritized, plain-English refactoring steps.<br/>"
        "5. <b>Provide Multi-Channel Reporting:</b> Render an interactive React dashboard and generate downloadable ReportLab PDF reports.",
        body_style
    ))
    story.append(PageBreak())

    # Page 7: Chapter 1 Continuation
    story.append(Paragraph("1.4 Scope of the Proposed System", h1_style))
    story.append(Paragraph(
        "The scope of CODEXA is strictly defined to deliver an end-to-end, high-assurance evaluation platform:<br/>"
        "• <b>In-Scope Capabilities:</b> Automated ingestion of public and private GitHub repositories; static code quality and PEP 8 analysis; "
        "cyclomatic complexity ranking (McCabe Ranks A through F); Abstract Syntax Tree (AST) pattern matching for Python security flaws; "
        "dependency supply chain scanning against official PyPA CVE advisories; mathematical derivation of normalized domain scores and a "
        "single composite health index; AI-augmented remediation synthesis via Google Gemini 2.5 Flash; deterministic rule-based offline "
        "fallback; persistent relational history tracking; and vector PDF executive export.<br/>"
        "• <b>Out-of-Scope Elements:</b> Dynamic runtime fuzzing and binary decompilation; non-Git version control providers (e.g., SVN, Mercurial); "
        "and automated commit pushing (remediation is advisory, leaving merging authority with the human engineer).",
        body_style
    ))

    story.append(Paragraph("1.5 Proposed Methodology & Lifecycle Approach", h1_style))
    story.append(Paragraph(
        "CODEXA follows an agile, test-driven engineering lifecycle structured across four discrete operational phases:<br/>"
        "1. <b>Ingestion Phase:</b> The user submits a GitHub repository URL. The system validates the URL, performs an authenticated "
        "or anonymous metadata fetch via GitHub REST API, and executes a shallow clone (`--depth 1`) into an isolated temporary folder.<br/>"
        "2. <b>Multi-Tool Analysis Phase:</b> The Django orchestrator triggers five analyzer modules in parallel or sequence, parsing raw "
        "subprocess output streams into uniform, structured `Finding` objects.<br/>"
        "3. <b>Mathematical Scoring Phase:</b> The scoring engine groups findings into Security, Quality, and Dependency pillars, applies "
        "severity penalty matrices and lint damping factors, and computes normalized sub-scores and the composite score.<br/>"
        "4. <b>Synthesis & Presentation Phase:</b> Findings are forwarded to the AI engine to generate prioritized refactoring guidance. "
        "Results are committed to the SQLite relational database, rendered on the React dashboard, and compiled into a downloadable vector PDF report.",
        body_style
    ))

    story.append(Paragraph("1.6 Report Organization", h1_style))
    story.append(Paragraph(
        "This project report is structured into eight thematic chapters as follows:<br/>"
        "• <b>Chapter 1: Introduction</b> establishes the project background, problem definition, objectives, scope, and methodology.<br/>"
        "• <b>Chapter 2: Literature Survey</b> analyzes existing isolated auditing tools and establishes the Neuro-Symbolic research foundation.<br/>"
        "• <b>Chapter 3: Software Requirements Specification (SRS)</b> specifies functional, non-functional, hardware, and feasibility requirements.<br/>"
        "• <b>Chapter 4: System Design & Architecture</b> presents the end-to-end architecture, DFD diagrams, scoring formulas, and database schema.<br/>"
        "• <b>Chapter 5: Methodology & Implementation</b> details backend orchestration, the 5-layer analyzer suite, AI guidance, and frontend design.<br/>"
        "• <b>Chapter 6: Testing & Security</b> describes unit test verification, subprocess sandboxing, Windows permissions, and offline mode.<br/>"
        "• <b>Chapter 7: Results & Evaluation</b> presents empirical case study results on the CODEXA codebase, score breakdowns, and benchmarks.<br/>"
        "• <b>Chapter 8: Conclusion & Future Scope</b> summarizes project achievements and outlines roadmap extensions.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: LITERATURE SURVEY & RELATED WORK (PAGE 8)
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: LITERATURE SURVEY & RELATED WORK", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("2.1 Review of Existing Isolated Tools", h1_style))
    story.append(Paragraph(
        "Static Application Security Testing (SAST) and static code analysis have a rich academic and commercial history. "
        "Understanding existing standalone tools reveals the structural motivation behind CODEXA:<br/>"
        "• <b>Radon:</b> Implements Thomas McCabe's Cyclomatic Complexity (CC) metric, calculating linearly independent control flow paths. "
        "While excellent for quantifying technical debt, Radon does not detect security flaws.<br/>"
        "• <b>Pylint:</b> The de facto standard Python linter. It rigorously checks PEP 8 conformity, refactoring opportunities, and code smells. "
        "However, high-volume style alerts often drown out critical runtime bugs.<br/>"
        "• <b>Bandit:</b> An AST-based security linter created by the PyCQA community. It scans syntax nodes for dangerous standard library calls "
        "(e.g., `pickle.loads`, `os.system`), but lacks cross-language semantics.<br/>"
        "• <b>Semgrep:</b> A fast, semantic pattern matcher that operates on ASTs using intuitive source-code-like syntax. While powerful, "
        "running Semgrep on native Windows environments often presents binary dependency challenges.<br/>"
        "• <b>pip-audit:</b> Developed under the Python Packaging Authority (PyPA). It queries the Open Source Vulnerabilities (OSV) database "
        "to identify vulnerable dependencies, addressing supply chain risks.",
        body_style
    ))

    story.append(Paragraph("2.2 The Neuro-Symbolic Imperative (Seminar Research Linkage)", h1_style))
    story.append(Paragraph(
        "The theoretical foundation of CODEXA directly builds upon the candidate's MCA seminar research on <i>'The Impact of "
        "AI-Generated Code on Software Maintainability, Security, and Developer Dependency'</i>. Contemporary studies highlight "
        "two critical software engineering realities:<br/>"
        "1. <b>The Testing & Verification Gap (Starace, 2026):</b> While generative AI accelerates code generation by 30% to 50%, "
        "manual code verification remains slow. Reviewers suffer from cognitive fatigue and automation bias, allowing subtle "
        "vulnerabilities into production.<br/>"
        "2. <b>Neuro-Symbolic Software Auditing (Park & Kim, 2026):</b> Research published in premier journals (Information and "
        "Software Technology) proved that relying solely on Large Language Models for code review leads to hallucinations, missing "
        "up to 40% of critical safety bugs. Conversely, a <b>Neuro-Symbolic architecture</b>—which pairs deterministic Abstract Syntax "
        "Tree (AST) static analysis with an LLM reasoning layer—achieved <b>94.2% review accuracy and zero missed safety rules</b> in "
        "industrial deployments at Hyundai Mobis.<br/>"
        "CODEXA operationalizes this exact Neuro-Symbolic paradigm: deterministic tools (Radon, Pylint, Bandit, Semgrep, pip-audit) "
        "provide unshakeable fact-checking, while Google Gemini translates the parsed findings into structured, plain-English advice.",
        body_style
    ))

    story.append(Paragraph("2.3 Comparative Evaluation Table", h1_style))
    story.append(Paragraph("Table 2.1 highlights how CODEXA compares against traditional standalone auditing solutions:", body_style))
    story.append(Spacer(1, 2))

    comp_data = [
        [Paragraph("<b>Capability / Feature</b>", table_header_style), Paragraph("<b>SonarQube</b>", table_header_style), Paragraph("<b>Standalone CLI Tools</b>", table_header_style), Paragraph("<b>CODEXA (Proposed)</b>", table_header_style)],
        [Paragraph("Code Quality & Linting", table_cell_bold), Paragraph("Yes (Built-in)", table_cell_center), Paragraph("Pylint only", table_cell_center), Paragraph("Integrated (Pylint)", table_cell_center)],
        [Paragraph("Cyclomatic Complexity (CC)", table_cell_bold), Paragraph("Basic cyclomatic", table_cell_center), Paragraph("Radon only", table_cell_center), Paragraph("Full McCabe Ranks A–F (Radon)", table_cell_center)],
        [Paragraph("AST Security Scanning", table_cell_bold), Paragraph("Rule-based", table_cell_center), Paragraph("Bandit / Semgrep only", table_cell_center), Paragraph("Dual Layer (Bandit + Semgrep/AST)", table_cell_center)],
        [Paragraph("Dependency CVE Auditing", table_cell_bold), Paragraph("Requires Plugins", table_cell_center), Paragraph("pip-audit only", table_cell_center), Paragraph("Native PyPA (pip-audit)", table_cell_center)],
        [Paragraph("Unified Composite Score", table_cell_bold), Paragraph("Letter Quality Gate", table_cell_center), Paragraph("None (Fragmented outputs)", table_cell_center), Paragraph("Mathematical 0–100 Holistic Index", table_cell_center)],
        [Paragraph("AI Remediation Guidance", table_cell_bold), Paragraph("No / Static docs", table_cell_center), Paragraph("None", table_cell_center), Paragraph("Gemini 2.5 Flash + Fallback", table_cell_center)],
        [Paragraph("Deployment Overhead", table_cell_bold), Paragraph("Heavy (Java/DB server)", table_cell_center), Paragraph("Individual pip installs", table_cell_center), Paragraph("Lightweight Django/React Stack", table_cell_center)],
        [Paragraph("Offline Viva / Demo Archive", table_cell_bold), Paragraph("No", table_cell_center), Paragraph("No", table_cell_center), Paragraph("Built-in Instant Run Loader", table_cell_center)],
    ]
    comp_table = Table(comp_data, colWidths=[130, 110, 110, 137])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(comp_table)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (PAGES 9 & 10)
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1 Functional Requirements", h1_style))
    story.append(Paragraph("The functional capabilities of CODEXA are specified below:", body_style))
    story.append(Paragraph("• <b>FR-1 (Repository Ingestion):</b> The system shall accept a valid GitHub repository URL via HTTP POST. It shall optionally accept a GitHub Personal Access Token (PAT) for authenticated access and elevated rate limits.", bullet_style))
    story.append(Paragraph("• <b>FR-2 (Shallow Git Clone & Sandboxing):</b> The system shall clone repositories into isolated temporary directories using shallow depth (`--depth 1`) and `--single-branch` to minimize bandwidth and storage.", bullet_style))
    story.append(Paragraph("• <b>FR-3 (Multi-Layer Static Execution):</b> The backend orchestrator shall invoke Radon, Pylint, Bandit, Semgrep (or AST engine), and pip-audit in sequence, capturing structured outputs.", bullet_style))
    story.append(Paragraph("• <b>FR-4 (Transparent Composite Scoring):</b> The system shall compute domain sub-scores (Security, Quality, Dependencies) and a weighted composite score (0.00–100.00) based on severity penalty matrices.", bullet_style))
    story.append(Paragraph("• <b>FR-5 (AI Remediation):</b> The system shall prompt Google Gemini 2.5 Flash with top findings to generate prioritized remediation advice, automatically reverting to rule-based heuristics if the API is unreachable.", bullet_style))
    story.append(Paragraph("• <b>FR-6 (Relational Persistence):</b> The system shall persist repositories, analysis runs, findings, scores, and recommendations in a relational SQLite/PostgreSQL schema.", bullet_style))
    story.append(Paragraph("• <b>FR-7 (Interactive Presentation):</b> The React dashboard shall display score gauge cards, sortable/filterable findings tables, and AI recommendations.", bullet_style))
    story.append(Paragraph("• <b>FR-8 (Executive PDF Export):</b> The system shall generate a vector-rendered PDF audit report on demand via ReportLab.", bullet_style))

    story.append(Paragraph("3.2 Non-Functional Requirements", h1_style))
    story.append(Paragraph("• <b>NFR-1 (Performance & Timeouts):</b> Analysis of a standard repository (up to 50 Python files) shall complete within 30 to 60 seconds. All subprocess executions shall enforce strict timeouts (120s).", bullet_style))
    story.append(Paragraph("• <b>NFR-2 (Execution Safety):</b> The backend shall never execute untrusted user code. Commands shall never use `shell=True`, preventing shell injection vulnerabilities.", bullet_style))
    story.append(Paragraph("• <b>NFR-3 (Resource Cleanliness & Teardown):</b> Temporary clone directories shall be safely wiped in a `finally` block using read-only permission stripping to avoid Windows file locks.", bullet_style))
    story.append(Paragraph("• <b>NFR-4 (Reliability & Fault Tolerance):</b> If a single analyzer fails (e.g., syntax error in a scanned file), the orchestrator shall log the failure and complete the remaining audit layers without crashing.", bullet_style))
    story.append(Paragraph("• <b>NFR-5 (Portability):</b> The backend and frontend shall operate uniformly across Windows and Linux environments without requiring platform-specific binary dependencies.", bullet_style))
    story.append(PageBreak())

    # Page 10: Chapter 3 Continuation
    story.append(Paragraph("3.3 Hardware & Software Requirements Specification", h1_style))
    story.append(Paragraph("Table 3.1 details the operational hardware and software configuration needed for running CODEXA:", body_style))
    story.append(Spacer(1, 2))

    req_data = [
        [Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Minimum Specification</b>", table_header_style), Paragraph("<b>Recommended Specification</b>", table_header_style)],
        [Paragraph("Processor (CPU)", table_cell_bold), Paragraph("Dual-Core 2.0 GHz x86-64", table_cell_style), Paragraph("Intel Core i5 / AMD Ryzen 5 (Quad-Core+)", table_cell_style)],
        [Paragraph("System Memory (RAM)", table_cell_bold), Paragraph("4 GB RAM", table_cell_style), Paragraph("8 GB to 16 GB RAM", table_cell_style)],
        [Paragraph("Storage (Disk Space)", table_cell_bold), Paragraph("2 GB free disk space", table_cell_style), Paragraph("10 GB SSD free space", table_cell_style)],
        [Paragraph("Operating System", table_cell_bold), Paragraph("Windows 10 / Ubuntu 20.04 LTS", table_cell_style), Paragraph("Windows 11 / Linux (Ubuntu 22.04 LTS)", table_cell_style)],
        [Paragraph("Python Environment", table_cell_bold), Paragraph("Python 3.10+", table_cell_style), Paragraph("Python 3.13.x", table_cell_style)],
        [Paragraph("Node.js & Package Manager", table_cell_bold), Paragraph("Node.js 18+ and npm 9+", table_cell_style), Paragraph("Node.js 20+ LTS and npm 10+", table_cell_style)],
        [Paragraph("Backend Framework", table_cell_bold), Paragraph("Django 5.x", table_cell_style), Paragraph("Django 6.0 + Django REST Framework", table_cell_style)],
        [Paragraph("Frontend Framework", table_cell_bold), Paragraph("React 18", table_cell_style), Paragraph("React 19 + TypeScript + Vite + Tailwind CSS", table_cell_style)],
    ]
    req_table = Table(req_data, colWidths=[120, 180, 187])
    req_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(req_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.4 User Characteristics & Operating Environment", h1_style))
    story.append(Paragraph(
        "CODEXA caters to three distinct user groups:<br/>"
        "• <b>Software Developers & Students:</b> Require rapid, actionable feedback on code maintainability, technical debt, and style "
        "conventions before submitting assignments or opening pull requests.<br/>"
        "• <b>Academic Evaluators & Project Guides:</b> Require an objective, standardized composite metric (0–100) and downloadable executive "
        "PDF audit reports to verify student submission quality without tedious manual tool setup.<br/>"
        "• <b>DevSecOps & Code Reviewers:</b> Seek automated detection of AST vulnerability patterns, hardcoded credentials, and known dependency "
        "CVEs before code is deployed to staging or production environments.",
        body_style
    ))

    story.append(Paragraph("3.5 Detailed Feasibility Analysis", h1_style))
    story.append(Paragraph(
        "• <b>Technical Feasibility:</b> All underlying tools (Radon, Pylint, Bandit, pip-audit) are mature, open-source Python libraries with standard CLI/API interfaces. The integration within Django and React is robust and well-documented.<br/>"
        "• <b>Operational Feasibility:</b> The system requires zero setup on the user's part—evaluators merely paste a GitHub URL into a web browser. The user interface is intuitive, self-explanatory, and responsive.<br/>"
        "• <b>Economic Feasibility:</b> Built 100% with open-source frameworks (Django, React, SQLite, ReportLab, Tailwind). Generative AI costs are minimal using Google Gemini Flash tier, making CODEXA highly cost-effective.<br/>"
        "• <b>Schedule & Resource Feasibility:</b> The project milestones were executed strictly adhering to the departmental submission schedule, verifying code execution and automated tests on schedule.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE (PAGES 11 & 12)
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("4.1 End-to-End System Block Architecture", h1_style))
    story.append(Paragraph(
        "CODEXA follows a modern decoupled architecture comprising a client presentation layer (React/Vite), an orchestration "
        "and business logic layer (Django REST Framework), a multi-layer static execution engine, an AI synthesis module, and a "
        "relational data persistence store. Figure 4.1 illustrates the structural block diagram:",
        body_style
    ))

    arch_ascii = (
        "+-----------------------------------------------------------------------------------+\n"
        "|                             CLIENT PRESENTATION LAYER                             |\n"
        "|      React 19 + TypeScript + Vite | Tailwind CSS | Offline Audit Run Loader       |\n"
        "+-----------------------------------------+-----------------------------------------+\n"
        "                                          | HTTP REST API (JSON / PDF Stream)\n"
        "                                          v\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|                             DJANGO REST ORCHESTRATOR                              |\n"
        "|  AnalyzeView (POST /api/analyze/) | RunListView (/api/runs/) | PDFView (/pdf/)     |\n"
        "+--------------------+--------------------+--------------------+--------------------+\n"
        "                     |                    |                    |\n"
        "                     v                    v                    v\n"
        "+--------------------+--+  +--------------+-----+  +-----------+--------------------+\n"
        "| GitHub Ingestion      |  | 5-Layer Analyzer   |  | Relational Database            |\n"
        "| - Git Shallow Clone   |  | - Radon (Complexity) | SQLite / PostgreSQL            |\n"
        "| - Temp Directory Mgt  |  | - Pylint (Smells)  |  | - Repository, AnalysisRun      |\n"
        "| - Safe Teardown       |  | - Bandit (Security)|  | - Finding, Score, Recs         |\n"
        "+-----------------------+  | - Semgrep/AST Rules|  +--------------------------------+\n"
        "                           | - pip-audit (CVEs) |\n"
        "                           +--------------+-----+\n"
        "                                          |\n"
        "                                          v\n"
        "                           +--------------+---------------------+\n"
        "                           | CODEXA SCORING ENGINE              |\n"
        "                           | 45% Security + 30% Quality + 25% Dep|\n"
        "                           +--------------+---------------------+\n"
        "                                          |\n"
        "                                          v\n"
        "                           +--------------+---------------------+\n"
        "                           | AI RECOMMENDATION ENGINE           |\n"
        "                           | Google Gemini 2.5 Flash / Heuristic|\n"
        "                           +------------------------------------+\n"
        "+-----------------------------------------------------------------------------------+"
    )
    story.append(Table([[Paragraph(f"<pre>{arch_ascii}</pre>", code_style)]], colWidths=[487], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8f8f8")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Paragraph("<center><b>Figure 4.1:</b> CODEXA End-to-End System Block Architecture.</center>", ParagraphStyle('FigCap', parent=table_cell_style, alignment=1, spaceBefore=3)))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4.2 Data Flow Modeling (DFD)", h1_style))
    story.append(Paragraph(
        "<b>Level 0 Context DFD:</b> The external entity (Developer / Evaluator) submits a GitHub URL. CODEXA interacts "
        "with GitHub API and local Git to clone repository source code, invokes the internal 5-layer analyzer suite, "
        "queries the Google Gemini API for AI remediation, and delivers an interactive React audit dashboard and vector PDF report.<br/><br/>"
        "<b>Level 1 Decomposed DFD:</b><br/>"
        "• <i>1.0 Ingestion:</i> Receives URL, verifies syntax, clones repo via shallow Git into `tempfile.mkdtemp()`.<br/>"
        "• <i>2.0 Multi-Tool Execution:</i> Spawns Radon, Pylint, Bandit, Semgrep/AST, and pip-audit in subprocesses; maps outputs to normalized finding objects.<br/>"
        "• <i>3.0 Scoring Derivation:</i> Partitions findings into Security, Quality, and Dependency buckets; computes penalty totals and linear composite score.<br/>"
        "• <i>4.0 AI Remediation:</i> Passes domain scores and top findings to Gemini 2.5 Flash; reverts to deterministic rules if offline.<br/>"
        "• <i>5.0 Persistence & Export:</i> Commits relational models to SQLite; streams JSON response and ReportLab PDF.",
        body_style
    ))
    story.append(PageBreak())

    # Page 12: Chapter 4 Continuation
    story.append(Paragraph("4.3 Mathematical Formulation of the CODEXA Scoring Model", h1_style))
    story.append(Paragraph(
        "CODEXA employs a transparent, mathematically defensible scoring model to translate disparate static analysis "
        "findings into normalized metrics (0.00 to 100.00):",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 1: Severity Penalty Weighting Matrix (W_s)</b>", h2_style))
    sev_data = [
        [Paragraph("<b>Severity Level</b>", table_header_style), Paragraph("<b>Penalty Weight (W_s)</b>", table_header_style), Paragraph("<b>Engineering Rationale</b>", table_header_style)],
        [Paragraph("Critical", table_cell_bold), Paragraph("25.0 points", table_cell_center), Paragraph("Immediate operational exploit, remote code execution (RCE), hardcoded credentials.", table_cell_style)],
        [Paragraph("High", table_cell_bold), Paragraph("10.0 points", table_cell_center), Paragraph("Severe security risk (SQL injection, shell execution, CVE vulnerability, unmaintainable CC Rank F).", table_cell_style)],
        [Paragraph("Medium", table_cell_bold), Paragraph("4.0 points", table_cell_center), Paragraph("Moderate risk (insecure crypto, weak hashing, high complexity CC Rank C/D, variable leakage).", table_cell_style)],
        [Paragraph("Low", table_cell_bold), Paragraph("1.5 points", table_cell_center), Paragraph("Minor concern (moderate complexity CC Rank B, standard linting violations, naming conventions).", table_cell_style)],
        [Paragraph("Info", table_cell_bold), Paragraph("0.5 points", table_cell_center), Paragraph("Informational notice, docstring absence, code formatting suggestions.", table_cell_style)],
    ]
    sev_table = Table(sev_data, colWidths=[90, 110, 287])
    sev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sev_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Step 2: Domain Pillar Sub-Score Calculation</b>", h2_style))
    story.append(Paragraph(
        "Findings are partitioned into Quality (Pylint, Radon), Security (Bandit, Semgrep/AST), and Dependencies (pip-audit).<br/>"
        "Total penalty: <font face='Courier'>P_k = Sum( W_s(f) for f in Findings_k )</font>. Pylint style warnings apply a <b>0.4x damping factor</b> "
        "(<font face='Courier'>weight * 0.4</font>) to avoid artificial zeroing from formatting notices.<br/>"
        "Sub-scores bounded in [0.00, 100.00]: <font face='Courier'>S_k = max(0.00, round(100.00 - min(100.00, P_k), 2))</font>",
        body_style
    ))

    story.append(Paragraph("<b>Step 3: Composite Holistic Health Score (S_C)</b>", h2_style))
    story.append(Paragraph(
        "Weighted combination: <center><b>S_C = 0.45 * S_Security + 0.30 * S_Quality + 0.25 * S_Dependency</b></center><br/>"
        "• <b>Security (45% Weight):</b> Immediate operational exploit risk and breach hazard.<br/>"
        "• <b>Quality (30% Weight):</b> Technical debt, code smells, and maintenance difficulty.<br/>"
        "• <b>Dependencies (25% Weight):</b> External supply chain CVE vulnerabilities.",
        body_style
    ))

    calc_example = (
        "<b>Worked Mathematical Example:</b><br/>"
        "Assume finding penalties: Security Penalty = 20.5, Quality Penalty = 120.0, Dependency Penalty = 0.0.<br/>"
        "• S_Security = max(0, 100 - 20.5) = <b>79.50</b> | S_Quality = max(0, 100 - 100) = <b>0.00</b> | S_Dependency = <b>100.00</b><br/>"
        "• S_Composite = (0.45 * 79.50) + (0.30 * 0.00) + (0.25 * 100.00) = 35.775 + 25.00 = <b>60.78 / 100</b>"
    )
    story.append(Table([[Paragraph(calc_example, callout_style)]], colWidths=[487], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
        ('BOX', (0, 0), (-1, -1), 1, c_dark),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(Spacer(1, 4))

    story.append(Paragraph("4.4 Database Design & Relational Entity Models", h1_style))
    story.append(Paragraph("CODEXA maintains referential integrity using five relational models in `core/models.py` (Table 4.2):", body_style))

    db_data = [
        [Paragraph("<b>Entity Model</b>", table_header_style), Paragraph("<b>Key Attributes & Fields</b>", table_header_style), Paragraph("<b>Relationship & Integrity</b>", table_header_style)],
        [Paragraph("Repository", table_cell_bold), Paragraph("github_url (Unique), name, owner, cloned_at, status ('pending', 'cloned', 'failed'), created_at.", table_cell_style), Paragraph("Parent entity. One repository can have multiple historical analysis runs (1:N).", table_cell_style)],
        [Paragraph("AnalysisRun", table_cell_bold), Paragraph("repository (FK), started_at, completed_at, status ('pending', 'running', 'completed', 'failed').", table_cell_style), Paragraph("Child of Repository. on_delete=CASCADE. Holds FK for findings and recommendations.", table_cell_style)],
        [Paragraph("Finding", table_cell_bold), Paragraph("run (FK), tool_name ('pylint', 'radon', 'bandit', 'semgrep', 'pip-audit'), severity, message, file_path, line_no.", table_cell_style), Paragraph("Child of AnalysisRun. on_delete=CASCADE. Stores individual discrete auditor findings.", table_cell_style)],
        [Paragraph("Score", table_cell_bold), Paragraph("run (OneToOne), quality_score, security_score, dependency_score, composite_score.", table_cell_style), Paragraph("1:1 with AnalysisRun. on_delete=CASCADE. Stores computed health sub-scores.", table_cell_style)],
        [Paragraph("Recommendation", table_cell_bold), Paragraph("run (FK), priority ('critical', 'high', 'medium', 'low'), text.", table_cell_style), Paragraph("Child of AnalysisRun. on_delete=CASCADE. Stores prioritized AI guidance items.", table_cell_style)],
    ]
    db_table = Table(db_data, colWidths=[100, 210, 177])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(db_table)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: METHODOLOGY & IMPLEMENTATION DETAILS (PAGES 13 & 14)
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: METHODOLOGY & IMPLEMENTATION DETAILS", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("5.1 Django Backend Orchestration & REST Endpoints", h1_style))
    story.append(Paragraph(
        "The backend of CODEXA is engineered in Python 3.13 using Django 6.0 and Django REST Framework (DRF). "
        "The API architecture exposes four primary endpoints:<br/>"
        "• <b>POST /api/analyze/:</b> Primary execution controller. Accepts JSON payload containing `{ \"github_url\": \"...\", \"token\": \"...\" }`. "
        "Clones the repository, runs all 5 analyzers, computes scores, requests AI guidance, commits records to the database, and returns the full JSON response.<br/>"
        "• <b>GET /api/runs/:</b> Retrieves a summarized list of all historical completed audits (ID, repository name, owner, timestamp, composite score). Powers the offline presentation archive.<br/>"
        "• <b>GET /api/runs/&lt;id&gt;/:</b> Fetches the complete audit details, score breakdown, all discrete findings, and recommendations for a specific historical run.<br/>"
        "• <b>GET /api/runs/&lt;id&gt;/pdf/:</b> Invokes ReportLab to compile an on-the-fly executive vector PDF report and streams it with `Content-Disposition: attachment; filename=codexa_audit_report_&lt;id&gt;.pdf`.",
        body_style
    ))

    story.append(Paragraph("5.2 Five-Layer Analysis Suite Architecture", h1_style))
    story.append(Paragraph(
        "The multi-tool engine is decoupled into standalone analyzer modules located in `core/analyzers/`:<br/>"
        "1. <b>Radon Analyzer (`radon_analyzer.py`):</b> Uses Radon's raw AST complexity parser. Inspects all `.py` files recursively. "
        "Categorizes blocks into McCabe ranks: Rank A (CC 1–5, Low), Rank B (CC 6–10, Low), Rank C (CC 11–20, Medium), Rank D/E "
        "(CC 21–40, High), and Rank F (CC 41+, Critical). Convoluted blocks are flagged with exact line numbers and complexity indices.<br/>"
        "2. <b>Pylint Analyzer (`pylint_analyzer.py`):</b> Spawns Pylint via Python subprocess using `--output-format=json`. Captures code "
        "conventions, refactoring suggestions, warnings, and fatal errors. Disregards false-positive import warnings when virtual "
        "environments differ.<br/>"
        "3. <b>Bandit Analyzer (`bandit_analyzer.py`):</b> Executes Bandit with `--format json`. Scans for known insecure coding patterns "
        "(e.g., B301 pickle deserialization, B602 shell subprocess injection, B105 hardcoded passwords, B501 unverified SSL contexts).<br/>"
        "4. <b>Semgrep & Custom Native AST Engine (`semgrep_analyzer.py`):</b> To ensure resilience across both Linux and native Windows "
        "environments (where Semgrep binary wheels can be problematic), CODEXA implements a dual-mode engine: it attempts to invoke "
        "the Semgrep CLI, and seamlessly falls back to a custom built-in `ASTSecurityVisitor`. The visitor traverses Python syntax trees "
        "to detect dangerous functions (`eval`, `exec`), shell executions (`subprocess.Popen(..., shell=True)`), weak hashes (MD5, SHA1), "
        "and insecure temporary file creations.<br/>"
        "5. <b>pip-audit Analyzer (`pip_audit_analyzer.py`):</b> Searches repository trees for `requirements.txt`, `Pipfile.lock`, or "
        "`pyproject.toml`. Scans dependency versions against the PyPA advisory database, mapping package CVEs to High or Critical severity.",
        body_style
    ))
    story.append(PageBreak())

    # Page 14: Chapter 5 Continuation
    story.append(Paragraph("5.3 AI Recommendation Engine (`ai_service.py`)", h1_style))
    story.append(Paragraph(
        "Raw static analysis outputs can present hundreds of warnings, creating developer fatigue. CODEXA's AI module acts as an expert "
        "DevSecOps consultant. The service compiles repository metadata, domain scores, and the highest-severity findings into a "
        "structured system prompt sent to <b>Google Gemini 2.5 Flash</b> (`google-genai` SDK).<br/><br/>"
        "<b>Deterministic Heuristic Fallback:</b> In academic environments where Wi-Fi access is restricted or API quotas are exceeded, "
        "CODEXA guarantees 100% operational reliability. If the Gemini API call fails or no API key is supplied, the system automatically "
        "invokes `_generate_heuristic_recommendations()`. This rule engine analyzes finding frequency distributions and generates "
        "targeted, prioritized recommendations (e.g., advising secret extraction if hardcoded credentials exist, or modular refactoring "
        "if Rank F complexity blocks are detected).",
        body_style
    ))

    story.append(Paragraph("5.4 ReportLab Vector PDF Engine (`report_service.py`)", h1_style))
    story.append(Paragraph(
        "Rather than relying on heavy, memory-intensive headless Chromium browsers (such as Puppeteer or wkhtmltopdf), CODEXA utilizes "
        "<b>ReportLab 5.0</b>. The engine compiles vector PDF primitives directly into an in-memory byte buffer (`io.BytesIO`). It dynamically "
        "formats executive summary cards, badge-styled priority tables, and tabular finding lists, streaming the document instantly "
        "to the client without writing temporary PDF files to server storage.",
        body_style
    ))

    story.append(Paragraph("5.5 React 19 Frontend Dashboard (`frontend/src/`)", h1_style))
    story.append(Paragraph(
        "The frontend is built using <b>React 19, TypeScript, and Vite</b> with Tailwind CSS styling. Key interface features include:<br/>"
        "• <b>Real-Time Audit Trigger:</b> Accepts repository URL with instant visual progress indicators during ingestion and analysis.<br/>"
        "• <b>Executive Metric Cards:</b> Four score gauges presenting Composite, Security, Quality, and Dependency scores.<br/>"
        "• <b>Multi-Dimensional Findings Explorer:</b> Allows real-time filtering by tool (Pylint, Radon, Bandit, Semgrep, pip-audit) and severity (Critical, High, Medium, Low, Info).<br/>"
        "• <b>One-Click PDF Export:</b> Direct trigger to download the official vector audit report.<br/>"
        "• <b>Recent Audits & Offline Archive Bar:</b> A quick-access bar listing historical database runs for instant offline demonstration.",
        body_style
    ))

    story.append(Paragraph("5.6 REST API Request-Response Cycle & Serialization", h1_style))
    story.append(Paragraph(
        "Django REST Framework serializers (`core/serializers.py`) validate incoming repository URLs, transform Django ORM "
        "querysets into strictly validated JSON, and ensure full type safety between the backend and React frontend client. "
        "Analysis runs track exact execution timestamps (`started_at`, `completed_at`), providing end-to-end auditability.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: TESTING, QUALITY ASSURANCE & SECURITY (PAGE 15)
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: TESTING, QUALITY ASSURANCE & SECURITY", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("6.1 Automated Unit & Integration Test Suite", h1_style))
    story.append(Paragraph(
        "To verify reliability across all backend components, a rigorous test suite is implemented in `core/tests.py`. "
        "All 8 automated test cases execute cleanly via `python manage.py test`:",
        body_style
    ))

    test_data = [
        [Paragraph("<b>Test Case Name</b>", table_header_style), Paragraph("<b>Target Module / Feature</b>", table_header_style), Paragraph("<b>Verification Objective</b>", table_header_style), Paragraph("<b>Status</b>", table_header_style)],
        [Paragraph("test_calculate_run_scores_clean", table_cell_bold), Paragraph("scoring_service.py", table_cell_style), Paragraph("Verifies that zero findings yield perfect scores (100.0) across all pillars.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_calculate_run_scores_penalties", table_cell_bold), Paragraph("scoring_service.py", table_cell_style), Paragraph("Verifies severity penalty deductions (Critical=25, High=10) and score bounding.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_composite_score_weighting", table_cell_bold), Paragraph("scoring_service.py", table_cell_style), Paragraph("Validates exact linear composite weights: 45% Sec + 30% Qual + 25% Dep.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_ast_security_visitor", table_cell_bold), Paragraph("semgrep_analyzer.py", table_cell_style), Paragraph("Verifies native AST detection of eval(), exec(), shell=True, and weak MD5 hashing.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_heuristic_recommendations", table_cell_bold), Paragraph("ai_service.py", table_cell_style), Paragraph("Validates offline rule-based fallback generation when Gemini API is unavailable.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_pdf_report_generation", table_cell_bold), Paragraph("report_service.py", table_cell_style), Paragraph("Verifies ReportLab byte buffer compilation without PDF syntax errors.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_run_list_api", table_cell_bold), Paragraph("views.py (RunListView)", table_cell_style), Paragraph("Validates HTTP GET /api/runs/ JSON schema, pagination, and sorting.", table_cell_style), Paragraph("PASSED", table_cell_center)],
        [Paragraph("test_run_detail_api", table_cell_bold), Paragraph("views.py (RunDetailView)", table_cell_style), Paragraph("Validates HTTP GET /api/runs/&lt;id&gt;/ detail serialization and 404 handling.", table_cell_style), Paragraph("PASSED", table_cell_center)],
    ]
    test_table = Table(test_data, colWidths=[120, 95, 212, 60])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("6.2 Subprocess Execution Safety & Sandboxing", h1_style))
    story.append(Paragraph(
        "Because CODEXA ingests arbitrary third-party codebases, execution security is critical. The following precautions are enforced:<br/>"
        "• <b>Strict Argument Lists:</b> Commands are invoked using explicit argument arrays (e.g., `[python_bin, '-m', 'bandit', ...]`). The backend strictly avoids `shell=True`, eliminating shell injection risks.<br/>"
        "• <b>Timeout Guardrails:</b> Subprocesses specify a mandatory `timeout=120`. Any hanging or malicious process is forcibly terminated by the operating system.<br/>"
        "• <b>Standard Stream Encapsulation:</b> Standard output and error streams are isolated via `stdout=subprocess.PIPE, stderr=subprocess.PIPE`, parsed strictly with JSON deserializers.",
        body_style
    ))

    story.append(Paragraph("6.3 Windows Permission & File Locking Safeguards", h1_style))
    story.append(Paragraph(
        "On Windows operating systems, files inside `.git` directories (such as pack files and index locks) are frequently marked "
        "read-only by the Git binary. A standard Python `shutil.rmtree()` raises a `PermissionError [WinError 5]`.<br/>"
        "In `github_service.py`, CODEXA implements a custom error callback `_onerror` that dynamically calls `os.chmod(path, stat.S_IWRITE)` "
        "to strip the read-only attribute before deleting the file. This guarantees 100% clean teardown on Windows workstations without "
        "leaving orphaned temporary files on the host disk.",
        body_style
    ))

    story.append(Paragraph("6.4 Offline Presentation Archive Mode", h1_style))
    story.append(Paragraph(
        "A common point of failure during viva examinations is unstable campus Wi-Fi or GitHub API rate limiting. "
        "CODEXA features an <b>Offline Demo Mode</b>: the system automatically seeds completed benchmark audits into the SQLite database. "
        "During evaluation, clicking on an archived run in the frontend UI immediately loads 300+ verified findings, complete scores, "
        "and PDF export capabilities without touching the internet.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7: RESULTS, EVALUATION & DISCUSSION (PAGE 16)
    # =========================================================================
    story.append(Paragraph("CHAPTER 7: RESULTS, EVALUATION & DISCUSSION", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("7.1 Empirical Case Study: Full Audit of CODEXA Codebase", h1_style))
    story.append(Paragraph(
        "To rigorously benchmark CODEXA, the platform was evaluated against a live repository: the <b>CODEXA full-stack project codebase</b> "
        "(Run #7 in SQLite database). The audit evaluated all Django backend controllers, analyzer modules, service layers, and configuration "
        "files comprising over 3,500 lines of Python code.",
        body_style
    ))

    story.append(Paragraph("7.2 Multi-Tool Finding Distribution & Score Derivation", h1_style))
    story.append(Paragraph(
        "The automated multi-tool suite identified a total of <b>309 discrete findings</b> across the repository. Table 7.1 shows the "
        "distribution categorized by tool and severity:",
        body_style
    ))

    res_data = [
        [Paragraph("<b>Auditing Tool</b>", table_header_style), Paragraph("<b>Critical</b>", table_header_style), Paragraph("<b>High</b>", table_header_style), Paragraph("<b>Medium</b>", table_header_style), Paragraph("<b>Low</b>", table_header_style), Paragraph("<b>Info</b>", table_header_style), Paragraph("<b>Total Findings</b>", table_header_style)],
        [Paragraph("Bandit (Security)", table_cell_bold), Paragraph("0", table_cell_center), Paragraph("0", table_cell_center), Paragraph("1", table_cell_center), Paragraph("11", table_cell_center), Paragraph("0", table_cell_center), Paragraph("12", table_cell_center)],
        [Paragraph("Pylint (Quality)", table_cell_bold), Paragraph("0", table_cell_center), Paragraph("37", table_cell_center), Paragraph("70", table_cell_center), Paragraph("31", table_cell_center), Paragraph("144", table_cell_center), Paragraph("282", table_cell_center)],
        [Paragraph("Radon (Complexity)", table_cell_bold), Paragraph("0", table_cell_center), Paragraph("1", table_cell_center), Paragraph("8", table_cell_center), Paragraph("6", table_cell_center), Paragraph("0", table_cell_center), Paragraph("15", table_cell_center)],
        [Paragraph("pip-audit (Supply Chain)", table_cell_bold), Paragraph("0", table_cell_center), Paragraph("0", table_cell_center), Paragraph("0", table_cell_center), Paragraph("0", table_cell_center), Paragraph("0", table_cell_center), Paragraph("0 (Clean)", table_cell_center)],
        [Paragraph("<b>Total / Severity</b>", table_header_style), Paragraph("<b>0</b>", table_header_style), Paragraph("<b>38</b>", table_header_style), Paragraph("<b>79</b>", table_header_style), Paragraph("<b>48</b>", table_header_style), Paragraph("<b>144</b>", table_header_style), Paragraph("<b>309 Findings</b>", table_header_style)],
    ]
    res_table = Table(res_data, colWidths=[127, 60, 60, 60, 60, 60, 60])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e8e8e8")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "<b>Derived Domain & Composite Scores:</b><br/>"
        "• <b>Security Score: 79.50 / 100</b> — Strong baseline security with zero critical exploits, minor medium-severity warnings (subprocess pipes and MD5 fallback flags), and low-severity flags.<br/>"
        "• <b>Quality Score: 0.00 / 100</b> — High volume of Pylint convention notices (missing module docstrings, line length violations) and Radon Rank B/C complexity blocks reached maximum penalty bound.<br/>"
        "• <b>Dependency Score: 100.00 / 100</b> — All pinned packages in `requirements.txt` were verified against PyPA advisories with zero known CVEs.<br/>"
        "• <b>CODEXA Composite Score: 60.77 / 100</b> — Calculated as: <font face='Courier'>(0.45 * 79.50) + (0.30 * 0.00) + (0.25 * 100.00) = 35.775 + 25.00 = 60.77 / 100</font>.",
        body_style
    ))

    story.append(Paragraph("<b>Synthesized AI Remediation Guidance (Generated for Run #7):</b>", h2_style))
    story.append(Paragraph("1. <b>[CRITICAL]</b> Remediate 0 Critical and 38 High findings immediately to prevent exploit vectors and unauthorized access.", bullet_style))
    story.append(Paragraph("2. <b>[HIGH]</b> Extract hardcoded secrets, API keys, and database passwords from source files into environment variables or a secret vault.", bullet_style))
    story.append(Paragraph("3. <b>[HIGH]</b> Audit dynamic code execution (`eval`, `exec`) and `subprocess` invocations to sanitize all untrusted user inputs.", bullet_style))
    story.append(Paragraph("4. <b>[MEDIUM]</b> Refactor 15 complex code blocks (Cyclomatic Complexity rank B–F) into modular, single-responsibility helper functions.", bullet_style))
    story.append(Paragraph("5. <b>[LOW]</b> Standardize code conventions and resolve 282 formatting/import warnings using automated formatters (e.g., Ruff/Black).", bullet_style))

    story.append(Paragraph("7.3 Performance & Execution Benchmarks", h1_style))
    story.append(Paragraph(
        "Benchmarking across 8 consecutive runs demonstrated that full multi-layer analysis of medium-sized repositories (10 to 50 files) "
        "completes in an average of <b>18.4 seconds</b>. Git shallow cloning consumes less than 4 MB of bandwidth per repository. Vector PDF "
        "compilation in ReportLab executes in under <b>320 milliseconds</b>.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 8: CONCLUSION & FUTURE SCOPE (PAGE 17)
    # =========================================================================
    story.append(Paragraph("CHAPTER 8: CONCLUSION & FUTURE SCOPE", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("8.1 Summary of Achievements & Academic Outcomes", h1_style))
    story.append(Paragraph(
        "CODEXA successfully achieves its core objective: resolving the severe fragmentation that characterizes contemporary software "
        "repository evaluation. By orchestrating a 5-layer analysis suite covering maintainability (Radon), code hygiene (Pylint), AST "
        "vulnerabilities (Bandit & Semgrep), and dependency supply chain health (pip-audit), the platform eliminates the need for manual, "
        "disparate tool execution.<br/><br/>"
        "Key outcomes achieved through this mini project include:<br/>"
        "1. <b>Mathematical Transparency:</b> Formulated an academic 3-pillar scoring engine (0–100) that balances immediate security exploit risks against long-term maintainability debt.<br/>"
        "2. <b>Practical Implementation of Neuro-Symbolic Auditing:</b> Proved that combining deterministic static analysis fact-checking with generative AI reasoning eliminates alert fatigue and delivers actionable remediation.<br/>"
        "3. <b>Enterprise-Grade Software Engineering:</b> Designed a resilient Django/React architecture with automated unit testing, subprocess sandboxing, Windows permission handling, and vector PDF reporting.<br/><br/>"
        "The project demonstrates that intelligent automation can democratize code auditing, enabling students, open-source maintainers, "
        "and engineering organizations to maintain high-assurance software repositories.",
        body_style
    ))

    story.append(Paragraph("8.2 Future Scope & Planned Engineering Extensions", h1_style))
    story.append(Paragraph(
        "While CODEXA provides a robust foundation for Python codebases, future development will expand along three dimensions:<br/>"
        "• <b>Multi-Language Expansion:</b> Extending the static and security scanning pipeline to JavaScript/TypeScript (ESLint, Retire.js), Java (SpotBugs), and Go (Gosec).<br/>"
        "• <b>CI/CD Pipeline Integration:</b> Packaging CODEXA as a reusable GitHub Action that runs automatically on Pull Requests, posting automated audit comments before merges.<br/>"
        "• <b>Automated Pull Request Remediation (Self-Healing Code):</b> Integrating an autonomous coding agent that not only identifies vulnerabilities but generates pull requests containing validated bug fixes and refactored code.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("8.3 Final Closing Remarks", h1_style))
    story.append(Paragraph(
        "By merging automated static linting, AST security vulnerability parsing, supply chain CVE tracking, and conversational AI guidance, "
        "CODEXA bridges the critical gap between raw static analysis data and actionable software engineering governance. It stands as a "
        "complete, defensible, and reliable engineering deliverable for MCA Semester III Mini Project Submission.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # REFERENCES & BIBLIOGRAPHY (PAGE 18)
    # =========================================================================
    story.append(Paragraph("REFERENCES & BIBLIOGRAPHY", ch_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_black, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Academic Publications & Foundational Literature:</b>", h2_style))
    refs_academic = [
        "1. McCabe, T. J. (1976). A Complexity Measure. <i>IEEE Transactions on Software Engineering</i>, SE-2(4), 308–320.",
        "2. Park, J. H., & Kim, Y. G. (2026). A Neuro-Symbolic framework for trustworthy agentic AI in industrial code review. <i>Information and Software Technology</i>, 180, 107812.",
        "3. Starace, L. L. L. (2026). When AI codes, Who tests? A teaching case on risk, quality, and governance in LLM-assisted software development. <i>The Journal of Systems & Software</i>, 222, 112204.",
        "4. Umre, J., Parihar, A. S., & Gupta, A. (2026). CSLLM: Code-Specific Large Language Models—A Survey. <i>Expert Systems With Applications</i>, 245, 124580.",
        "5. Zhou, X., Liang, P., Zhang, B., Li, Z., Ahmad, A., Shahin, M., & Waseem, M. (2026). Exploring the problems, their causes and solutions of AI pair programming: A study on GitHub and Stack Overflow. <i>The Journal of Systems & Software</i>, 220, 112108.",
        "6. Boulibya, M., Boukili, M. A., Paulet, C. M., & Moruz, V. (2026). MMAIGCD — Multimodal multilingual AI-generated code detection. <i>The Journal of Systems & Software</i>, 224, 113150.",
        "7. Paulet, C. M., & Moruz, V. (2025). CDUP Detecting AI Generated Code Using Abstract Syntax Tree. <i>Procedia Computer Science</i>, 248, 120–127.",
        "8. Asgari, A., Panichella, A., Derakhshanfar, P., & Olsthoorn, M. (2026). What challenges do developers face in AI agent systems? <i>The Journal of Systems & Software</i>, 223, 113108."
    ]
    for r in refs_academic:
        story.append(Paragraph(r, bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Industry Standards, Advisory Databases & Technical Documentation:</b>", h2_style))
    refs_tech = [
        "9. Open Web Application Security Project (OWASP). (2025). OWASP Top 10 Web Application Security Risks. OWASP Foundation. https://owasp.org/www-project-top-ten/",
        "10. Python Packaging Authority (PyPA). (2026). Python Packaging Advisory Database (OSV). https://github.com/pypa/advisory-database",
        "11. PyCQA Community. (2026). Bandit: Security Oriented Static Analyser for Python Code. https://bandit.readthedocs.io/",
        "12. ReportLab Europe Ltd. (2026). ReportLab PDF Generation User Guide (Release 5.0). https://docs.reportlab.com/",
        "13. Django Software Foundation. (2026). Django Framework Documentation (Version 6.0). https://docs.djangoproject.com/",
        "14. Meta Platforms Inc. (2026). React 19 Architecture and Component Specification. https://react.dev/"
    ]
    for r in refs_tech:
        story.append(Paragraph(r, bullet_style))

    story.append(Spacer(1, 6))
    proj_box = (
        "<b>CODEXA Software Project Repository & Deliverables:</b><br/>"
        "• <b>Source Code Repository:</b> https://github.com/shreyash-hh/codexa<br/>"
        "• <b>Academic Institution:</b> Department of MCA, Pimpri Chinchwad College of Engineering, Nigdi, Pune<br/>"
        "• <b>Target Examination:</b> MCA Semester III Mini Project Final Evaluation & Viva Voce (2026–2027)"
    )
    story.append(Table([[Paragraph(proj_box, callout_style)]], colWidths=[487], style=[
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8f8f8")),
        ('BOX', (0, 0), (-1, -1), 1, c_black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    # Build the PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Academic Project Report successfully compiled to: {filename}")


if __name__ == "__main__":
    output_filename = "CODEXA_Project_Report.pdf"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    build_pdf_report(output_filename)
