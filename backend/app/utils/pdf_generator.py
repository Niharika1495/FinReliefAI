import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(filename: str, report_title: str, report_data: dict) -> str:
    """
    Builds a professional PDF document from a report data dictionary.
    Saves and returns the output absolute file path.
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    # Setup styles
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor("#1A365D")
    secondary_color = colors.HexColor("#2B6CB0")
    text_color = colors.HexColor("#2D3748")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        textColor=primary_color,
        fontSize=24,
        leading=28,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        textColor=secondary_color,
        fontSize=12,
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        textColor=primary_color,
        fontSize=14,
        leading=18,
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        textColor=text_color,
        fontSize=10,
        leading=14
    )

    # Add Title and Subtitle
    story.append(Paragraph(report_title, title_style))
    story.append(Paragraph("FinRelief AI - Debt Relief & Financial Recovery Platform", subtitle_style))
    story.append(Spacer(1, 10))

    # Add Sections and Tables
    for section_title, data in report_data.items():
        if not data:
            continue
        
        story.append(Paragraph(section_title, section_style))
        
        if isinstance(data, dict):
            # Create a nice key-value table
            table_data = []
            for k, v in data.items():
                label = str(k).replace("_", " ").title()
                val = f"${v:,.2f}" if isinstance(v, (int, float)) and "count" not in str(k).lower() and "score" not in str(k).lower() and "id" not in str(k).lower() and "months" not in str(k).lower() else str(v)
                table_data.append([
                    Paragraph(f"<b>{label}</b>", body_style),
                    Paragraph(val, body_style)
                ])
            
            t = Table(table_data, colWidths=[200, 300])
            t.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TEXTCOLOR', (0,0), (-1,-1), text_color),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            
        elif isinstance(data, list):
            # Tabular array representation
            if not data:
                story.append(Paragraph("No records found.", body_style))
                story.append(Spacer(1, 15))
                continue
                
            headers = list(data[0].keys())
            display_headers = [str(h).replace("_", " ").title() for h in headers]
            
            table_data = [[Paragraph(f"<b>{h}</b>", body_style) for h in display_headers]]
            for row in data:
                row_cells = []
                for h in headers:
                    val = row[h]
                    cell_str = f"${val:,.2f}" if isinstance(val, (int, float)) and "id" not in str(h).lower() and "rate" not in str(h).lower() and "months" not in str(h).lower() else str(val)
                    row_cells.append(Paragraph(cell_str, body_style))
                table_data.append(row_cells)
                
            num_cols = len(headers)
            col_widths = [512.0 / num_cols] * num_cols if num_cols > 0 else None
            t = Table(table_data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))

    doc.build(story)
    return os.path.abspath(filename)
