import io
import json
from pathlib import Path

from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from ..models.land_lease import LandLeaseEstimate


def clean_pdf_text(text: str) -> str:
    """
    Sanitizes text string for ReportLab PDF rendering, replacing unsupported unicode
    symbols like Rupee (₹) with clean ASCII equivalents ('Rs. ').
    """
    if not text:
        return ""
    cleaned = str(text)
    # Replace Rupee symbol variants
    cleaned = cleaned.replace("₹", "Rs. ")
    cleaned = cleaned.replace("â‚¹", "Rs. ")
    cleaned = cleaned.replace("\u20b9", "Rs. ")
    # Replace unicode dashes with standard hyphen
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    return cleaned


def generate_land_lease_pdf(estimate: LandLeaseEstimate, user_name: str = "Farmer / Landowner") -> bytes:
    """
    Generates an executive, beautifully styled downloadable PDF report for a Land Lease Estimate.
    Returns the PDF binary content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Premium Brand Palette (Emerald, Mint, Amber, Slate)
    brand_dark = colors.HexColor("#064e3b")      # Deep Emerald 900
    brand_primary = colors.HexColor("#15803d")   # Emerald 700
    brand_light = colors.HexColor("#f0fdf4")     # Mint 50
    brand_border = colors.HexColor("#a7f3d0")    # Emerald 200
    text_dark = colors.HexColor("#1f2937")       # Slate 800
    text_muted = colors.HexColor("#4b5563")      # Slate 600
    accent_amber = colors.HexColor("#b45309")    # Amber 700
    amber_bg = colors.HexColor("#fffbeb")        # Amber 50

    # Typography Styles
    brand_title_style = ParagraphStyle(
        'BrandTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=brand_dark,
        fontName='Helvetica-Bold',
        alignment=0
    )

    report_meta_style = ParagraphStyle(
        'ReportMeta',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=text_muted,
        fontName='Helvetica',
        alignment=2
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        leading=15,
        textColor=brand_dark,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=text_dark,
        fontName='Helvetica'
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10.5,
        textColor=text_muted,
        fontName='Helvetica-Oblique'
    )

    def P(txt: str, style=body_style) -> Paragraph:
        return Paragraph(clean_pdf_text(txt), style)

    elements = []

    # Safe Date Formatting
    created_str = (
        estimate.created_at.strftime('%d %b %Y, %I:%M %p')
        if hasattr(estimate, 'created_at') and estimate.created_at
        else datetime.now().strftime('%d %b %Y, %I:%M %p')
    )

    # 1. Header Banner with Clean Logo & Brand Title
    logo_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "static" / "images" / "logo.png"


    logo_cell = P("<font size=18 color='#064e3b'><b>🌱 CropCare</b></font>", brand_title_style)
    if logo_path.exists():
        try:
            logo_img = Image(str(logo_path), width=0.60 * inch, height=0.60 * inch)
            logo_cell = Table(
                [[logo_img, P("<b>CropCare</b><br/><font size=8 color='#15803d'>PRECISION AGRICULTURE & LAND VALUATION</font>", brand_title_style)]],
                colWidths=[0.70 * inch, 3.2 * inch]
            )
            logo_cell.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
        except Exception:
            pass

    meta_text = (
        f"<b>REPORT ID:</b> <font color='#15803d'>{estimate.report_id}</font><br/>"
        f"<b>DATE:</b> {created_str}<br/>"
        f"<b>PREPARED FOR:</b> {user_name}"
    )

    header_table = Table(
        [[logo_cell, P(meta_text, report_meta_style)]],
        colWidths=[4.2 * inch, 2.8 * inch]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=brand_primary, spaceBefore=4, spaceAfter=10))

    # Document Title Subhead
    elements.append(P(
        f"<b>AGRICULTURAL LAND LEASE ESTIMATION REPORT</b> - <font color='#4b5563'>{estimate.district}, {estimate.state}</font>",
        ParagraphStyle('DocSubhead', parent=styles['Heading3'], fontSize=11, leading=14, textColor=brand_dark, fontName='Helvetica-Bold', spaceAfter=10)
    ))

    # 2. Main Hero Valuation Card Box
    min_annual = estimate.calculated_min_price
    max_annual = estimate.calculated_max_price
    acres = max(0.01, estimate.acres)
    min_acre = round(min_annual / acres, -1)
    max_acre = round(max_annual / acres, -1)
    min_month = round(min_annual / 12.0, -1)
    max_month = round(max_annual / 12.0, -1)

    val_box_data = [
        [
            P("<font size=9 color='#064e3b'><b>ESTIMATED FAIR ANNUAL LEASE RANGE</b></font>"),
            P(f"<font size=15 color='#15803d'><b>Rs. {min_annual:,.0f} - Rs. {max_annual:,.0f} / yr</b></font>")
        ],
        [
            P(f"<b>Monthly Rate:</b> Rs. {min_month:,.0f} - Rs. {max_month:,.0f} / month"),
            P(f"<b>Rate Per Acre:</b> Rs. {min_acre:,.0f} - Rs. {max_acre:,.0f} / acre / yr")
        ],
        [
            P(f"<b>Valuation Confidence:</b> <font color='#15803d'><b>{estimate.confidence_score} CONFIDENCE</b></font>"),
            P(f"<b>Total Land Area:</b> {estimate.input_size} {estimate.input_unit} ({estimate.acres} Acres)")
        ]
    ]

    val_table = Table(val_box_data, colWidths=[3.5 * inch, 3.5 * inch])
    val_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), brand_light),
        ('BOX', (0,0), (-1,-1), 1.2, brand_primary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, brand_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(val_table)
    elements.append(Spacer(1, 10))

    # 3. Property Overview Table
    elements.append(P("1. Land Characteristics & Location Attributes", section_heading))

    infra_str = "None specified"
    if estimate.infrastructure_json:
        try:
            infra_list = json.loads(estimate.infrastructure_json)
            if infra_list:
                infra_str = ", ".join(infra_list)
        except Exception:
            pass

    prop_data = [
        [P("<b>State / District:</b>"), P(f"{estimate.state} / {estimate.district}"),
         P("<b>Taluk / Village:</b>"), P(f"{estimate.taluk or 'N/A'} / {estimate.village or 'N/A'}")],
        [P("<b>Land Classification:</b>"), P(f"{estimate.land_type or 'N/A'}"),
         P("<b>Soil Type:</b>"), P(f"{estimate.soil_type or 'N/A'}")],
        [P("<b>Water Availability:</b>"), P(f"{estimate.water_availability}"),
         P("<b>Irrigation Setup:</b>"), P(f"{estimate.irrigation_type or 'N/A'}")],
        [P("<b>Grid Electricity:</b>"), P(f"{'Available (' + str(estimate.electricity_reliability or '') + ')' if estimate.electricity_available else 'No Grid Connection'}"),
         P("<b>Road Access:</b>"), P(f"{estimate.road_access}")],
        [P("<b>Lease Term:</b>"), P(f"{estimate.lease_duration_years} Years"),
         P("<b>Intended Crop/Use:</b>"), P(f"{estimate.intended_use or 'Agricultural'}")],
        [P("<b>Infrastructure:</b>"), P(infra_str), P(""), P("")]
    ]

    prop_table = Table(prop_data, colWidths=[1.4 * inch, 2.1 * inch, 1.4 * inch, 2.1 * inch])
    prop_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f9fafb")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#f9fafb")),
        ('SPAN', (1,5), (3,5)),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(prop_table)
    elements.append(Spacer(1, 10))

    # 4. Positive & Negative Value Factors
    elements.append(P("2. Primary Lease Price Drivers", section_heading))

    pos_lines = []
    neg_lines = []

    if estimate.factors_json:
        try:
            factors_dict = json.loads(estimate.factors_json)
            pos_list = factors_dict.get("positive_factors", [])
            neg_list = factors_dict.get("negative_factors", [])

            for item in pos_list:
                pos_lines.append(f"• <b>{item.get('impact', '')}</b>: {item.get('description', '')}")
            for item in neg_list:
                neg_lines.append(f"• <b>{item.get('impact', '')}</b>: {item.get('description', '')}")
        except Exception:
            pass

    if not pos_lines:
        pos_lines.append("• Standard regional agricultural baseline factors apply.")
    if not neg_lines:
        neg_lines.append("• Standard seasonal weather and market commodity fluctuations.")

    pos_content = P("<b><font color='#15803d'>+ Value Enhancers</font></b><br/>" + "<br/>".join(pos_lines))
    neg_content = P("<b><font color='#b45309'>- Constraints & Risks</font></b><br/>" + "<br/>".join(neg_lines))

    factors_table = Table([[pos_content, neg_content]], colWidths=[3.5 * inch, 3.5 * inch])
    factors_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#d1d5db")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), brand_light),
        ('BACKGROUND', (1,0), (1,0), amber_bg),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(factors_table)
    elements.append(Spacer(1, 10))

    # 5. AI Strategic Assessment & Recommendations
    elements.append(P("3. AI Strategic Assessment & Negotiation Guidance", section_heading))

    if estimate.ai_analysis_json:
        try:
            ai_data = json.loads(estimate.ai_analysis_json)

            summary_text = ai_data.get('summary', '') or ai_data.get('estimated_range_explanation', '')
            summary_p = P(f"<b>Overview:</b> {summary_text}")
            elements.append(summary_p)
            elements.append(Spacer(1, 4))

            recs = ai_data.get("recommendations", [])
            if recs:
                rec_lines = [f"<b>{i+1}.</b> {rec}" for i, rec in enumerate(recs)]
                rec_p = P("<b>Strategic Recommendations:</b><br/>" + "<br/>".join(rec_lines))
                elements.append(rec_p)
                elements.append(Spacer(1, 4))
        except Exception:
            pass

    # 6. Legal Disclaimer Footer Box
    elements.append(Spacer(1, 8))
    disclaimer_box = [
        [P(
            "<b>IMPORTANT ADVISORY & LEGAL DISCLAIMER:</b> This Land Lease Estimation Report is generated by the CropCare automated "
            "valuation algorithm and Groq AI model for informational guidance only. It does not constitute a legally binding property appraisal "
            "or financial guarantee. Lessors and Lessees are strongly advised to conduct physical site inspections, verify Pahani/RTC land records "
            "at the local Sub-Registrar office, and execute a formal registered lease agreement.",
            disclaimer_style
        )]
    ]
    disclaimer_table = Table(disclaimer_box, colWidths=[7.0 * inch])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f3f4f6")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#9ca3af")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(disclaimer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
