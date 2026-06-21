from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

SEVERITY_COLORS = {'red': '#FF6B2B', 'yellow': '#FFA500', 'green': '#4ade80'}


def generate_pdf_report(output_path: str, user_name: str, analysis: dict) -> str:
    """Generate a SwingCheck analysis PDF report. Returns the output path."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    story.append(Paragraph("<b>SwingCheck Analysis Report</b>", styles['Heading1']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>{user_name}</b> | {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("<b>Key Findings</b>", styles['Heading2']))
    flagged_issues = analysis.get('flagged_issues', [])
    if not flagged_issues:
        story.append(Paragraph("No major swing faults detected. Keep up the good work!", styles['Normal']))
    for issue in flagged_issues:
        severity_color = SEVERITY_COLORS.get(issue.get('severity', 'green'), '#4ade80')
        story.append(Paragraph(
            f"<font color='{severity_color}'><b>{issue['issue']}</b></font>: {issue['description']}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.1 * inch))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Metrics</b>", styles['Heading2']))

    def fmt(value):
        return f"{value:.1f}°" if isinstance(value, (int, float)) else "N/A"

    table_data = [
        ['Metric', 'Value'],
        ['Spine Angle (Setup)', fmt(analysis.get('spine_angle_setup'))],
        ['Spine Angle (Impact)', fmt(analysis.get('spine_angle_impact'))],
        ['Hip Turn', fmt(analysis.get('hip_turn'))],
        ['X-Factor', fmt(analysis.get('x_factor'))],
    ]
    table = Table(table_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)

    doc.build(story)
    return output_path
