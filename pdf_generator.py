from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
import os

def generate_invoice_pdf(data, output_path):
    """
    Generate a professional PDF invoice.
    data: dict containing all invoice details.
    output_path: path to save the PDF.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    style_business_name = ParagraphStyle(
        'BusinessName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1a1a2e")
    )
    
    style_invoice_label = ParagraphStyle(
        'InvoiceLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_RIGHT
    )
    
    style_normal = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2d2d2d")
    )
    
    style_bold = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2d2d2d")
    )
    
    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )

    style_total = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.white,
        alignment=TA_RIGHT
    )

    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.gray,
        alignment=TA_CENTER
    )

    story = []

    # Header section with Logo and Business Name
    header_data = []
    
    # Check for logo
    logo_img = None
    if data.get('logo_path') and os.path.exists(data['logo_path']):
        try:
            logo_img = Image(data['logo_path'], width=60, height=60)
        except:
            pass

    biz_info = [
        Paragraph(data['business_name'], style_business_name),
        Spacer(1, 4),
        Paragraph(data['business_address'], style_normal),
        Paragraph(f"GSTIN: {data['business_gstin']}", style_normal),
        Paragraph(f"Email: {data['business_email']}", style_normal),
        Paragraph(f"Phone: {data['business_phone']}", style_normal),
    ]

    header_col1 = []
    if logo_img:
        header_col1.append(logo_img)
        header_col1.append(Spacer(1, 10))
    header_col1.extend(biz_info)

    header_table = Table(
        [[header_col1, Paragraph("INVOICE", style_invoice_label)]],
        colWidths=[350, 165]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 30))

    # Billing and Invoice Meta Info
    meta_data = [
        [Paragraph("<b>BILL TO:</b>", style_bold), Paragraph("<b>INVOICE DETAILS:</b>", style_bold)],
        [Paragraph(data['client_name'], style_normal), Paragraph(f"Invoice #: {data['invoice_number']}", style_normal)],
    ]
    if data.get('client_email'):
        meta_data.append([Paragraph(data['client_email'], style_normal), Paragraph(f"Date: {data['invoice_date']}", style_normal)])
    else:
        meta_data.append([Paragraph("", style_normal), Paragraph(f"Date: {data['invoice_date']}", style_normal)])
    
    meta_data.append([Paragraph("", style_normal), Paragraph(f"Due Date: {data['due_date']}", style_normal)])
    
    meta_table = Table(meta_data, colWidths=[257, 257])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 30))

    # Services Table
    table_data = [
        [Paragraph("Description", style_table_header), Paragraph("Amount (INR)", style_table_header)]
    ]
    
    table_data.append([
        Paragraph(data['description'], style_normal),
        Paragraph(f"{data['amount']:,.2f}", ParagraphStyle('Right', parent=style_normal, alignment=TA_RIGHT))
    ])
    
    # Conditional GST Rows
    if data.get('gst_applicable'):
        table_data.append([
            Paragraph("CGST (" + str(data['cgst_rate']) + "%)", style_normal),
            Paragraph(f"{data['cgst_amount']:,.2f}", ParagraphStyle('Right', parent=style_normal, alignment=TA_RIGHT))
        ])
        table_data.append([
            Paragraph("SGST (" + str(data['sgst_rate']) + "%)", style_normal),
            Paragraph(f"{data['sgst_amount']:,.2f}", ParagraphStyle('Right', parent=style_normal, alignment=TA_RIGHT))
        ])
    
    # Total Row
    table_data.append([
        Paragraph("TOTAL PAYABLE", style_total),
        Paragraph(f"INR {data['total_payable']:,.2f}", style_total)
    ])

    services_table = Table(table_data, colWidths=[380, 135])
    services_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#1a1a2e")),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(services_table)
    story.append(Spacer(1, 40))

    # Payment Details & Digital Signature Notice
    payment_info = [
        Paragraph("<b>PAYMENT DETAILS:</b>", style_bold),
        Paragraph(f"UPI ID: {data['upi_id']}", style_normal),
        Paragraph(f"Account No: {data['account_no']}", style_normal),
        Paragraph(f"IFSC Code: {data['ifsc_code']}", style_normal),
    ]
    
    payment_table = Table([[payment_info]], colWidths=[300])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))

    # Signature Replacement Text
    sig_notice_style = ParagraphStyle(
        'SigNotice',
        parent=style_normal,
        fontName='Helvetica-BoldOblique',
        fontSize=9,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_RIGHT
    )
    sig_notice = [
        Spacer(1, 50),
        Paragraph("Digitally Generated Invoice \u2013 No Signature Required", sig_notice_style)
    ]

    bottom_table = Table([[payment_table, sig_notice]], colWidths=[300, 215])
    bottom_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(bottom_table)
    
    # Footer
    story.append(Spacer(1, 50))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 10))
    story.append(Paragraph("TERMS & CONDITIONS", style_bold))
    story.append(Paragraph(data.get('terms', "Please make the payment by the due date. Thank you for your business."), style_footer))

    doc.build(story)
