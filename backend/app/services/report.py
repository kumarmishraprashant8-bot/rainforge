"""
RainForge PDF Report Generator - Enhanced
"""

from io import BytesIO
from datetime import datetime


class ReportGenerator:
    """
    Generates PDF reports for RWH assessments.
    Uses reportlab for PDF generation.
    """
    
    @staticmethod
    def generate_pdf(project_data: dict, assessment_data: dict) -> bytes:
        """
        Generate a comprehensive PDF report.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#0891b2')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.HexColor('#1e40af')
            )
            
            # Title
            story.append(Paragraph("🌧️ RainForge Assessment Report", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Project Details
            story.append(Paragraph("Project Details", heading_style))
            project_table = Table([
                ["Address", project_data.get("address", "N/A")],
                ["Roof Area", f"{project_data.get('roof_area_sqm', 0)} m²"],
                ["Roof Material", project_data.get("roof_material", "N/A").title()],
                ["Assessment Date", project_data.get("created_at", "N/A")]
            ], colWidths=[2*inch, 4*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f9ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(project_table)
            story.append(Spacer(1, 20))
            
            # Key Results
            story.append(Paragraph("Assessment Results", heading_style))
            results_table = Table([
                ["Metric", "Value", "Notes"],
                ["Annual Rainfall", f"{assessment_data['rainfall_stats']['annual_mm']} mm", "Historical average"],
                ["Annual Yield", f"{assessment_data['runoff_potential_liters']:,} L", "Harvestable rainwater"],
                ["Tank Size", f"{assessment_data['recommended_tank_size']:,} L", "Recommended capacity"],
                ["System Cost", f"₹{assessment_data['estimated_cost_inr']:,}", "Before subsidy"],
                ["Subsidy", f"₹{assessment_data['subsidy_amount_inr']:,}", "Jal Shakti scheme"],
                ["Net Cost", f"₹{assessment_data['net_cost_inr']:,}", "After subsidy"],
            ], colWidths=[2*inch, 2*inch, 2*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            story.append(results_table)
            story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("System Recommendations", heading_style))
            recommendations = [
                "✅ Install first-flush diverter (20L capacity)",
                "✅ Use 2-stage filtration before tank",
                "✅ Connect overflow to recharge pit",
                "✅ Install float valve for municipal backup"
            ]
            for rec in recommendations:
                story.append(Paragraph(rec, styles['Normal']))
                story.append(Spacer(1, 5))
            
            story.append(Spacer(1, 20))
            
            # Disclaimer
            story.append(Paragraph("Technical References", heading_style))
            story.append(Paragraph(
                "This assessment follows IS 15797:2008 guidelines for rainwater harvesting "
                "and CGWB Manual on Artificial Recharge. Actual yields may vary based on "
                "local rainfall patterns and system maintenance.",
                styles['Normal']
            ))
            
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "Generated by RainForge • Jal Shakti Aligned • rainforge.gov.in",
                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
            ))
            
            doc.build(story)
            return buffer.getvalue()
            
        except ImportError:
            # Fallback if reportlab not installed
            return b"PDF generation requires reportlab. Install with: pip install reportlab"
