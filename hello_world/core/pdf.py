from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


def generate_certificate_pdf(work):
    """Generate a PDF certificate for a registered work"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_LEFT,
    )
    
    # Certificate Title
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("CERTIFICATE OF CREATION", title_style))
    story.append(Paragraph("Human-Created Work Registration", subtitle_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Certificate details
    cert_text = f"""
    This is to certify that <b>{work.creator.name}</b> has registered the following creative work:
    """
    story.append(Paragraph(cert_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Work details table
    details_data = [
        ['Title:', work.title],
        ['Creator:', work.creator.name],
        ['Email:', work.creator.email],
        ['Category:', work.get_category_display()],
        ['Creation Date:', work.creation_date.strftime('%B %d, %Y')],
        ['Registration ID:', str(work.id)],
        ['Registered On:', work.registered_at.strftime('%B %d, %Y at %I:%M %p')],
    ]
    
    details_table = Table(details_data, colWidths=[1.5*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Description
    if work.description:
        desc_text = f"<b>Description:</b><br/>{work.description}"
        story.append(Paragraph(desc_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "This certificate verifies that the above work has been registered as human-created.<br/>"
        "Certificate generated on " + datetime.now().strftime('%B %d, %Y'),
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
