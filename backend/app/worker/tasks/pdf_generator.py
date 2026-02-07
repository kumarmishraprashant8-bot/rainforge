"""
RainForge PDF Report Generator
==============================
Generates detailed assessment PDFs with BoM and charts.

Owners: Prashant Mishra & Ishita Parmar
"""

import io
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Try to import PDF libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, HRFlowable
    )
    from reportlab.graphics.shapes import Drawing, Rect
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


@dataclass
class ReportData:
    """Data structure for PDF report."""
    project_id: int
    address: str
    lat: float
    lng: float
    roof_area_sqm: float
    roof_material: str
    
    annual_yield_l: float
    monthly_yield_l: list
    tank_recommendation_l: float
    reliability_pct: float
    
    estimated_cost: float
    subsidy_amount: float
    net_cost: float
    roi_years: float
    
    bom: Dict[str, float]
    formulas: Dict[str, str]
    
    state: str
    city: str
    generated_at: str = None
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


class PDFReportGenerator:
    """Generates PDF assessment reports."""
    
    # Brand colors
    PRIMARY_COLOR = colors.HexColor("#0066CC")
    SECONDARY_COLOR = colors.HexColor("#00AA66")
    ACCENT_COLOR = colors.HexColor("#FF9900")
    TEXT_COLOR = colors.HexColor("#333333")
    LIGHT_BG = colors.HexColor("#F5F8FA")
    
    def __init__(self):
        self.styles = None
        if HAS_REPORTLAB:
            self.styles = getSampleStyleSheet()
            self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Add custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            'MainTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=20
        ))
        self.styles.add(ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.PRIMARY_COLOR,
            spaceBefore=15,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_COLOR,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            'Formula',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor("#666666"),
            backColor=self.LIGHT_BG,
            borderPadding=5
        ))
    
    def generate(self, data: ReportData) -> bytes:
        """
        Generate PDF report.
        
        Returns PDF as bytes.
        """
        if not HAS_REPORTLAB:
            return self._generate_fallback_pdf(data)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # Header
        story.extend(self._build_header(data))
        
        # Executive Summary
        story.extend(self._build_summary(data))
        
        # Monthly Breakdown Chart
        story.extend(self._build_monthly_chart(data))
        
        # Bill of Materials
        story.extend(self._build_bom_table(data))
        
        # Financial Analysis
        story.extend(self._build_financials(data))
        
        # Formula Explanations
        story.extend(self._build_formulas(data))
        
        # Footer with audit hash
        story.extend(self._build_footer(data))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def _build_header(self, data: ReportData) -> list:
        """Build report header."""
        elements = []
        
        # Logo and title
        elements.append(Paragraph(
            "🌧️ RainForge Assessment Report",
            self.styles['MainTitle']
        ))
        
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=self.PRIMARY_COLOR
        ))
        elements.append(Spacer(1, 10))
        
        # Project info table
        info_data = [
            ["Project ID:", str(data.project_id), "Generated:", data.generated_at[:10]],
            ["Address:", data.address, "State:", data.state],
            ["Coordinates:", f"{data.lat:.4f}, {data.lng:.4f}", "City:", data.city],
            ["Roof Area:", f"{data.roof_area_sqm} m²", "Material:", data.roof_material.title()],
        ]
        
        info_table = Table(info_data, colWidths=[80, 150, 80, 150])
        info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_summary(self, data: ReportData) -> list:
        """Build executive summary section."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        
        # Key metrics
        metrics = [
            ["Annual Yield", f"{data.annual_yield_l:,.0f} L", "💧"],
            ["Tank Size", f"{data.tank_recommendation_l:,.0f} L", "🛢️"],
            ["Reliability", f"{data.reliability_pct:.1f}%", "✅"],
            ["ROI Period", f"{data.roi_years:.1f} years", "📈"],
        ]
        
        metrics_table = Table(metrics, colWidths=[120, 100, 40])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.LIGHT_BG),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.TEXT_COLOR),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTSIZE', (1, 0), (1, -1), 14),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_monthly_chart(self, data: ReportData) -> list:
        """Build monthly yield chart."""
        elements = []
        
        elements.append(Paragraph("Monthly Yield Breakdown", self.styles['SectionTitle']))
        
        # Create bar chart
        drawing = Drawing(450, 150)
        chart = VerticalBarChart()
        chart.x = 40
        chart.y = 20
        chart.width = 380
        chart.height = 110
        
        chart.data = [data.monthly_yield_l]
        chart.categoryAxis.categoryNames = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        chart.bars[0].fillColor = self.PRIMARY_COLOR
        chart.valueAxis.valueMin = 0
        chart.categoryAxis.labels.fontSize = 8
        chart.valueAxis.labels.fontSize = 8
        
        drawing.add(chart)
        elements.append(drawing)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_bom_table(self, data: ReportData) -> list:
        """Build Bill of Materials table."""
        elements = []
        
        elements.append(Paragraph("Bill of Materials (BoM)", self.styles['SectionTitle']))
        
        # BoM table
        bom_rows = [["Item", "Quantity/Spec", "Cost (₹)"]]
        for item, cost in data.bom.items():
            bom_rows.append([item.replace("_", " ").title(), "As specified", f"₹{cost:,.0f}"])
        
        bom_rows.append(["", "Total", f"₹{sum(data.bom.values()):,.0f}"])
        
        bom_table = Table(bom_rows, colWidths=[200, 120, 100])
        bom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), self.LIGHT_BG),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(bom_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_financials(self, data: ReportData) -> list:
        """Build financial analysis section."""
        elements = []
        
        elements.append(Paragraph("Financial Analysis", self.styles['SectionTitle']))
        
        fin_data = [
            ["Gross Installation Cost", f"₹{data.estimated_cost:,.0f}"],
            ["Government Subsidy", f"-₹{data.subsidy_amount:,.0f}"],
            ["Net Cost to Owner", f"₹{data.net_cost:,.0f}"],
            ["", ""],
            ["Payback Period", f"{data.roi_years:.1f} years"],
        ]
        
        fin_table = Table(fin_data, colWidths=[200, 150])
        fin_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 1), (1, 1), self.SECONDARY_COLOR),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 2), (-1, 2), 1, self.PRIMARY_COLOR),
        ]))
        elements.append(fin_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_formulas(self, data: ReportData) -> list:
        """Build formula explanations section."""
        elements = []
        
        elements.append(Paragraph("Calculation Methodology", self.styles['SectionTitle']))
        
        for name, formula in data.formulas.items():
            elements.append(Paragraph(
                f"<b>{name}</b>: {formula}",
                self.styles['Formula']
            ))
            elements.append(Spacer(1, 5))
        
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "Reference: IS 15797:2008, CPWD Manual, CGWB Guidelines",
            self.styles['BodyText']
        ))
        
        return elements
    
    def _build_footer(self, data: ReportData) -> list:
        """Build footer with audit information."""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
        
        import hashlib
        report_hash = hashlib.sha256(
            f"{data.project_id}:{data.generated_at}:{data.annual_yield_l}".encode()
        ).hexdigest()[:16]
        
        elements.append(Paragraph(
            f"<font size=8 color='gray'>"
            f"Report generated by RainForge | Hash: {report_hash} | "
            f"Timestamp: {data.generated_at}"
            f"</font>",
            self.styles['Normal']
        ))
        
        return elements
    
    def _generate_fallback_pdf(self, data: ReportData) -> bytes:
        """Generate simple text-based PDF when reportlab is unavailable."""
        # Return placeholder PDF bytes
        content = f"""
RainForge Assessment Report
===========================
Project ID: {data.project_id}
Address: {data.address}
Generated: {data.generated_at}

SUMMARY
-------
Annual Yield: {data.annual_yield_l:,.0f} L
Tank Size: {data.tank_recommendation_l:,.0f} L
Net Cost: ₹{data.net_cost:,.0f}
ROI: {data.roi_years:.1f} years

(Full PDF requires reportlab library)
"""
        return content.encode('utf-8')


# Celery task wrapper
from app.worker.celery_app import celery_app

@celery_app.task(name="app.worker.tasks.pdf_generator.generate_report_pdf")
def generate_report_pdf(data: dict) -> bytes:
    """Celery task to generate PDF report."""
    report_data = ReportData(**data)
    generator = PDFReportGenerator()
    return generator.generate(report_data)
