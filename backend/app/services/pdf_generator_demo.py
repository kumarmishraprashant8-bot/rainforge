"""
PDF Generator for RainForge Assessments
Generates engineer-signed PDF with QR code for verification
"""

import os
from datetime import datetime
from typing import Any
import io


def generate_assessment_pdf(assessment: Any) -> str:
    """
    Generate assessment PDF with QR code and engineer signature block.
    Returns path to generated PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        # Fallback if reportlab not installed
        return _generate_simple_pdf(assessment)
    
    # Create output directory
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_path = f"{output_dir}/{assessment.assessment_id}.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor('#1a5276')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.grey
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#2874a6')
    )
    
    normal_style = styles['Normal']
    
    # Build content
    content = []
    
    # Header
    content.append(Paragraph("🌧️ RainForge Assessment Report", title_style))
    content.append(Paragraph(
        f"Assessment ID: {assessment.assessment_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        subtitle_style
    ))
    content.append(Spacer(1, 0.3*cm))
    
    # Site Information
    content.append(Paragraph("📍 Site Information", heading_style))
    site_data = [
        ["Site ID", assessment.site_id or "N/A"],
        ["Address", assessment.address or "N/A"],
        ["Coordinates", f"{assessment.lat}, {assessment.lng}" if assessment.lat else "N/A"],
        ["State / City", f"{assessment.state or 'N/A'} / {assessment.city or 'N/A'}"],
        ["Roof Area", f"{assessment.roof_area_sqm} m²"],
        ["Roof Material", assessment.roof_material or "Concrete"],
    ]
    site_table = Table(site_data, colWidths=[4*cm, 14*cm])
    site_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eaf2f8')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(site_table)
    content.append(Spacer(1, 0.4*cm))
    
    # Assessment Results
    content.append(Paragraph("📊 Assessment Results", heading_style))
    results_data = [
        ["Annual Rainfall", f"{assessment.annual_rainfall_mm} mm"],
        ["Annual Water Yield", f"{assessment.annual_yield_liters:,.0f} liters"],
        ["Recommended Tank Size", f"{assessment.recommended_tank_liters:,} liters"],
        ["CO₂ Avoided (Annually)", f"{assessment.co2_avoided_kg:.2f} kg"],
    ]
    results_table = Table(results_data, colWidths=[6*cm, 12*cm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d5f5e3')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(results_table)
    content.append(Spacer(1, 0.4*cm))
    
    # Three Scenarios
    content.append(Paragraph("📋 Recommended Scenarios", heading_style))
    scenarios = assessment.scenarios or {}
    
    scenario_header = ["Scenario", "Tank Size", "Cost (₹)", "Coverage", "ROI"]
    scenario_rows = [scenario_header]
    
    for key, scenario in scenarios.items():
        if isinstance(scenario, dict):
            scenario_rows.append([
                scenario.get("name", key),
                f"{scenario.get('tank_liters', 0):,} L",
                f"₹{scenario.get('cost_inr', 0):,.0f}",
                f"{scenario.get('coverage_days', 0)} days",
                f"{scenario.get('roi_years', 0):.1f} yrs"
            ])
    
    if len(scenario_rows) > 1:
        scenario_table = Table(scenario_rows, colWidths=[4*cm, 3*cm, 3.5*cm, 3*cm, 2.5*cm])
        scenario_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(scenario_table)
    content.append(Spacer(1, 0.4*cm))
    
    # Financial Summary
    content.append(Paragraph("💰 Financial Summary", heading_style))
    financial_data = [
        ["Total System Cost", f"₹{assessment.total_cost_inr:,.0f}"],
        ["Subsidy Available", f"{assessment.subsidy_pct}% (Max ₹{assessment.subsidy_amount_inr:,.0f})"],
        ["Net Cost After Subsidy", f"₹{assessment.net_cost_inr:,.0f}"],
        ["Payback Period", f"{assessment.roi_years:.1f} years"],
    ]
    financial_table = Table(financial_data, colWidths=[6*cm, 12*cm])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef9e7')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    content.append(financial_table)
    content.append(Spacer(1, 0.5*cm))
    
    # QR Code Section
    content.append(Paragraph("🔐 Verification", heading_style))
    
    # Generate QR code
    qr_image = _generate_qr_code(assessment.qr_verification_code)
    if qr_image:
        qr_table = Table([
            [qr_image, Paragraph(
                f"<b>Scan to Verify</b><br/>"
                f"Verification Code: {assessment.qr_verification_code[:8]}...<br/>"
                f"URL: /api/v1/verify/{assessment.qr_verification_code}<br/><br/>"
                f"<i>This QR code links to the verification endpoint where "
                f"you can confirm the authenticity of this assessment.</i>",
                normal_style
            )]
        ], colWidths=[4*cm, 14*cm])
        qr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (1, 0), (1, 0), 12),
        ]))
        content.append(qr_table)
    else:
        content.append(Paragraph(
            f"Verification Code: {assessment.qr_verification_code}",
            normal_style
        ))
    
    content.append(Spacer(1, 0.5*cm))
    
    # Engineer Signature Block
    content.append(Paragraph("✍️ Engineer Certification", heading_style))
    
    signature_data = [
        ["Engineer Name:", "_" * 40],
        ["Registration No:", "_" * 40],
        ["Date:", datetime.now().strftime("%Y-%m-%d")],
        ["Signature:", ""],
        ["", ""],
        ["", "(Authorized Signature & Seal)"],
    ]
    signature_table = Table(signature_data, colWidths=[4*cm, 10*cm])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, -1), (1, -1), 'CENTER'),
        ('FONTSIZE', (1, -1), (1, -1), 8),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.grey),
    ]))
    content.append(signature_table)
    
    content.append(Spacer(1, 0.5*cm))
    
    # Footer
    footer_text = (
        "<i>This assessment was generated by RainForge - India's comprehensive "
        "rainwater harvesting assessment platform. For queries, contact support@rainforge.in. "
        "Report generated with deterministic calculations per BIS standards.</i>"
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    content.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(content)
    
    return pdf_path


def _generate_qr_code(data: str):
    """Generate QR code image for verification URL."""
    try:
        import qrcode
        from reportlab.platypus import Image
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(f"https://rainforge.in/verify/{data}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return Image(img_buffer, width=3*cm, height=3*cm)
    except ImportError:
        return None
    except Exception:
        return None


def _generate_simple_pdf(assessment: Any) -> str:
    """Fallback simple text-based PDF generation."""
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = f"{output_dir}/{assessment.assessment_id}.txt"
    
    with open(pdf_path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("       RAINFORGE ASSESSMENT REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Assessment ID: {assessment.assessment_id}\n")
        f.write(f"Site ID: {assessment.site_id}\n")
        f.write(f"Address: {assessment.address}\n")
        f.write(f"Coordinates: {assessment.lat}, {assessment.lng}\n")
        f.write(f"Roof Area: {assessment.roof_area_sqm} m²\n")
        f.write(f"Annual Rainfall: {assessment.annual_rainfall_mm} mm\n")
        f.write(f"Annual Yield: {assessment.annual_yield_liters:,.0f} L\n")
        f.write(f"Recommended Tank: {assessment.recommended_tank_liters:,} L\n")
        f.write(f"Net Cost: ₹{assessment.net_cost_inr:,.0f}\n")
        f.write(f"ROI: {assessment.roi_years:.1f} years\n")
        f.write(f"CO2 Avoided: {assessment.co2_avoided_kg:.2f} kg\n")
        f.write("\n" + "-" * 60 + "\n")
        f.write(f"Verification: /api/v1/verify/{assessment.qr_verification_code}\n")
        f.write("-" * 60 + "\n")
    
    return pdf_path


# Utility for cm
try:
    from reportlab.lib.units import cm
except ImportError:
    cm = 28.35  # 1 cm in points
