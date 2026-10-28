import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def generate_invoice_pdf(order_data: dict) -> bytes:
    buffer = io.BytesIO()
    
    if not REPORTLAB_AVAILABLE:
        # Fallback simple text-based PDF representation if reportlab is missing
        text = f"INVOICE FOR ORDER {order_data.get('order_number')}\n"
        text += f"Date: {order_data.get('created_at', str(datetime.utcnow()))}\n"
        text += f"Total Amount: ${order_data.get('total_amount'):.2f}\n"
        text += f"Payment Method: Cash on Delivery\n"
        buffer.write(text.encode('utf-8'))
        return buffer.getvalue()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#232F3E'), # Amazon dark blue
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'InvoiceSub',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#555555'),
        fontName='Helvetica'
    )
    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111111')
    )
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName='Helvetica',
        textColor=colors.HexColor('#333333')
    )

    story = []

    # Header Section
    story.append(Paragraph("<b>AMAZON-AI RETAIL</b>", title_style))
    story.append(Paragraph("AI-Powered Sales Intelligence Platform &bull; Production Invoice", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9900'), spaceAfter=15)) # Amazon Orange accent

    # Order Meta & Customer Address
    order_num = order_data.get('order_number', 'ORD-000000')
    date_str = str(order_data.get('created_at', datetime.utcnow()))[:19]
    addr = order_data.get('delivery_address', {})
    
    meta_data = [
        [
            Paragraph(f"<b>Order Number:</b> {order_num}<br/><b>Date:</b> {date_str}<br/><b>Payment Method:</b> {order_data.get('payment_method', 'Cash on Delivery')}<br/><b>Status:</b> {order_data.get('status', 'Pending')}", normal_style),
            Paragraph(f"<b>Deliver To:</b><br/>{addr.get('full_name', 'Customer')}<br/>{addr.get('street_address', '')}<br/>{addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')}<br/>Phone: {addr.get('phone', '')}", normal_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ('ROUNDEDCORNERS', [4, 4, 4, 4])
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # Items Table Header
    items_data = [
        [Paragraph("<b>Item Description</b>", bold_style), 
         Paragraph("<b>Unit Price</b>", bold_style), 
         Paragraph("<b>Qty</b>", bold_style), 
         Paragraph("<b>Total</b>", bold_style)]
    ]

    for item in order_data.get('items', []):
        prod_title = item.get('product_title', f"Product #{item.get('product_id')}")
        items_data.append([
            Paragraph(prod_title, normal_style),
            Paragraph(f"${item.get('unit_price', 0.0):.2f}", normal_style),
            Paragraph(str(item.get('quantity', 1)), normal_style),
            Paragraph(f"${item.get('total_price', 0.0):.2f}", normal_style)
        ])

    items_table = Table(items_data, colWidths=[260, 90, 60, 110])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#232F3E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
    ]))
    # Change text color of header row paragraphs to white
    for col_idx in range(4):
        items_data[0][col_idx].style.textColor = colors.white
    
    story.append(items_table)
    story.append(Spacer(1, 15))

    # Summary Section (Subtotal, Tax, Delivery, Total)
    subtotal = sum(item.get('total_price', 0.0) for item in order_data.get('items', []))
    tax = order_data.get('tax', 0.0)
    delivery = order_data.get('delivery_charge', 0.0)
    total = order_data.get('total_amount', subtotal + tax + delivery)

    summary_data = [
        ["", "", Paragraph("<b>Subtotal:</b>", normal_style), Paragraph(f"${subtotal:.2f}", normal_style)],
        ["", "", Paragraph("<b>Estimated Tax:</b>", normal_style), Paragraph(f"${tax:.2f}", normal_style)],
        ["", "", Paragraph("<b>Delivery Charge:</b>", normal_style), Paragraph("FREE" if delivery == 0 else f"${delivery:.2f}", normal_style)],
        ["", "", Paragraph("<b>Order Total (COD):</b>", bold_style), Paragraph(f"<b>${total:.2f}</b>", bold_style)]
    ]
    summary_table = Table(summary_data, colWidths=[180, 80, 150, 110])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (2, 3), (3, 3), colors.HexColor('#FFF3E0')), # Light orange highlight for total
        ('BOX', (2, 3), (3, 3), 1, colors.HexColor('#FF9900'))
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceAfter=10))
    story.append(Paragraph("<b>Thank you for shopping with Amazon-AI Retail!</b><br/>Please have exact cash ready at the time of delivery. For support or order tracking, visit our online dashboard.", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
