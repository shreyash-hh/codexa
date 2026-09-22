import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from core.models import AnalysisRun


def generate_pdf_report(run: AnalysisRun) -> io.BytesIO:
    """
    Generates a professional executive audit report PDF using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#64748b')
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    badge_crit_style = ParagraphStyle(
        'BadgeCrit',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#dc2626')
    )
    badge_high_style = ParagraphStyle(
        'BadgeHigh',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#ea580c')
    )
    badge_med_style = ParagraphStyle(
        'BadgeMed',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#d97706')
    )
    badge_low_style = ParagraphStyle(
        'BadgeLow',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2563eb')
    )

    story = []

    # 1. Header Banner
    repo = run.repository
    score = getattr(run, 'score', None)
    
    story.append(Paragraph("CODEXA Security & Quality Audit Report", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Repository: <b>{repo.owner}/{repo.name}</b> | Generated: {run.completed_at.strftime('%Y-%m-%d %H:%M UTC') if run.completed_at else 'In Progress'}", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6'), spaceBefore=4, spaceAfter=14))

    # 2. Executive Score Summary Card
    story.append(Paragraph("Executive Health & Security Scores", h2_style))
    
    score_data = [
        [
            Paragraph("<b>Composite Score</b>", body_style),
            Paragraph("<b>Security Score</b>", body_style),
            Paragraph("<b>Quality Score</b>", body_style),
            Paragraph("<b>Dependency Score</b>", body_style),
        ],
        [
            Paragraph(f"<font size=16 color='#0284c7'><b>{score.composite_score if score else 0.0}/100</b></font>", body_style),
            Paragraph(f"<font size=16 color='#16a34a'><b>{score.security_score if score else 0.0}/100</b></font>", body_style),
            Paragraph(f"<font size=16 color='#6366f1'><b>{score.quality_score if score else 0.0}/100</b></font>", body_style),
            Paragraph(f"<font size=16 color='#8b5cf6'><b>{score.dependency_score if score else 0.0}/100</b></font>", body_style),
        ]
    ]
    
    score_table = Table(score_data, colWidths=[130, 130, 130, 130])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 3. AI Strategic Recommendations
    recs = list(run.recommendations.all())
    if recs:
        story.append(Paragraph("Prioritized AI Remediation Guidance", h2_style))
        rec_table_data = []
        for r in recs:
            p = r.priority.lower()
            badge = badge_crit_style if p == 'critical' else (badge_high_style if p == 'high' else (badge_med_style if p == 'medium' else badge_low_style))
            rec_table_data.append([
                Paragraph(f"<b>[{r.priority.upper()}]</b>", badge),
                Paragraph(r.text, body_style)
            ])

        rec_table = Table(rec_table_data, colWidths=[80, 440])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 14))

    # 4. Findings Summary & Detail Table
    findings = list(run.findings.all())
    story.append(Paragraph(f"Key Findings ({len(findings)} Total Issues Detected)", h2_style))
    
    if findings:
        findings_table_data = [
            [
                Paragraph("<b>Tool</b>", body_style),
                Paragraph("<b>Severity</b>", body_style),
                Paragraph("<b>File : Line</b>", body_style),
                Paragraph("<b>Finding Message</b>", body_style),
            ]
        ]
        
        # Display top 30 findings in report
        for f in findings[:30]:
            p = f.severity.lower()
            badge = badge_crit_style if p in ['critical', 'high'] else (badge_med_style if p == 'medium' else badge_low_style)
            loc = f"{f.file_path}:{f.line_no}" if f.line_no else (f.file_path or "Manifest")
            findings_table_data.append([
                Paragraph(f.tool_name.upper(), body_style),
                Paragraph(f.severity.upper(), badge),
                Paragraph(loc[:30], body_style),
                Paragraph(f.message[:160], body_style),
            ])

        findings_table = Table(findings_table_data, colWidths=[65, 65, 130, 260])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(findings_table)
        
        if len(findings) > 30:
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<i>... and {len(findings) - 30} additional findings available on the interactive CODEXA dashboard.</i>", subtitle_style))
    else:
        story.append(Paragraph("No findings or vulnerabilities identified. Code meets all quality and security criteria.", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
