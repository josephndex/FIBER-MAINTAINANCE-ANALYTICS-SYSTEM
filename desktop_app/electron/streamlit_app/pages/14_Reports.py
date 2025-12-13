"""
PDF Report Generation - Fiber Maintenance Analytics System
Generate professional PDF reports for management
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
import base64
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    calculate_comprehensive_kpis, filter_non_alarm_data,
    calculate_cluster_performance, calculate_engineer_performance,
    calculate_regional_performance, calculate_service_performance,
    format_duration, get_sla_grade
)
from auth import require_page_access, get_current_user, log_page_visit

# Check page access
require_page_access("14_Reports.py")
log_page_visit("Reports")

# Try to import reportlab for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing, Line
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def create_header():
    """Create page header"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);'>
        <h1 style='color: white; margin: 0; text-align: center;'>📄 Report Generation</h1>
        <p style='color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;'>
            Generate professional PDF reports for management and stakeholders
        </p>
    </div>
    """, unsafe_allow_html=True)


def generate_pdf_report(df, kpis, cluster_perf, engineer_perf, report_type, date_range):
    """Generate PDF report using ReportLab - Different content based on report type"""
    buffer = BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#667eea')
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#1a202c')
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Build content
    story = []
    
    # Title based on report type
    report_titles = {
        "Executive Summary": "Executive Summary Report",
        "Detailed Analysis": "Detailed Analysis Report",
        "Performance Report": "Performance Analysis Report",
        "SLA Report": "SLA Compliance Report"
    }
    
    story.append(Paragraph(report_titles.get(report_type, "Fiber Maintenance Analytics Report"), title_style))
    story.append(Paragraph(f"Report Type: {report_type}", normal_style))
    story.append(Paragraph(f"Period: {date_range}", normal_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Content varies based on report type
    if report_type == "Executive Summary":
        # Executive Summary - High-level overview only
        story.append(Paragraph("Key Performance Indicators", heading_style))
        
        summary_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Tickets', f"{kpis['total_tickets']:,}", 'Info'],
            ['SLA Compliance', f"{kpis['sla_compliance']:.1f}%", kpis['sla_grade']],
            ['Average MTTR', format_duration(kpis['avg_duration']), kpis['performance_grade']],
            ['Breached Tickets', f"{kpis['breached_tickets']:,}", 'Alert' if kpis['breached_tickets'] > 0 else 'Good'],
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 150, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Top 5 clusters only for executive summary
        if cluster_perf is not None and len(cluster_perf) > 0:
            story.append(Paragraph("Top 5 Performing Clusters", heading_style))
            top_clusters = cluster_perf.head(5)
            cluster_data = [['Cluster', 'Tickets', 'SLA %', 'Grade']]
            for _, row in top_clusters.iterrows():
                cluster_data.append([
                    str(row['CLUSTER'])[:30],
                    f"{row['Total_Tickets']:,}",
                    f"{row['SLA_Compliance']:.1f}%",
                    row['Grade']
                ])
            
            cluster_table = Table(cluster_data, colWidths=[180, 80, 80, 60])
            cluster_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(cluster_table)
    
    elif report_type == "Detailed Analysis":
        # Detailed Analysis - Full metrics breakdown
        story.append(Paragraph("Complete Metrics Overview", heading_style))
        
        detailed_data = [
            ['Category', 'Metric', 'Value'],
            ['Volume', 'Total Tickets', f"{kpis['total_tickets']:,}"],
            ['Volume', 'Non-Alarm Tickets', f"{kpis['non_alarm_tickets']:,}"],
            ['Volume', 'Alarm Tickets', f"{kpis['alarm_tickets']:,}"],
            ['SLA', 'Compliance Rate', f"{kpis['sla_compliance']:.2f}%"],
            ['SLA', 'Breached Tickets', f"{kpis['breached_tickets']:,}"],
            ['SLA', 'Grade', kpis['sla_grade']],
            ['Time', 'Average MTTR', format_duration(kpis['avg_duration'])],
            ['Time', 'Median MTTR', format_duration(kpis['median_duration'])],
            ['Time', 'Min MTTR', format_duration(kpis['min_duration'])],
            ['Time', 'Max MTTR', format_duration(kpis['max_duration'])],
            ['Resources', 'Active Engineers', f"{kpis['active_engineers']:,}"],
            ['Resources', 'Active Clusters', f"{kpis['active_clusters']:,}"],
            ['Resources', 'Active Regions', f"{kpis['active_regions']:,}"],
        ]
        
        detailed_table = Table(detailed_data, colWidths=[100, 180, 120])
        detailed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(detailed_table)
        story.append(Spacer(1, 20))
        
        # All clusters
        if cluster_perf is not None and len(cluster_perf) > 0:
            story.append(PageBreak())
            story.append(Paragraph("Complete Cluster Analysis", heading_style))
            cluster_data = [['Cluster', 'Tickets', 'SLA %', 'MTTR', 'Grade']]
            for _, row in cluster_perf.iterrows():
                cluster_data.append([
                    str(row['CLUSTER'])[:25],
                    f"{row['Total_Tickets']:,}",
                    f"{row['SLA_Compliance']:.1f}%",
                    f"{row['Avg_MTTR_Hours']:.2f}h",
                    row['Grade']
                ])
            
            cluster_table = Table(cluster_data, colWidths=[150, 70, 70, 70, 50])
            cluster_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(cluster_table)
    
    elif report_type == "Performance Report":
        # Performance Report - Focus on engineers and clusters
        story.append(Paragraph("Performance Summary", heading_style))
        
        perf_data = [
            ['Metric', 'Value', 'Grade'],
            ['Average MTTR', format_duration(kpis['avg_duration']), kpis['performance_grade']],
            ['Median MTTR', format_duration(kpis['median_duration']), '-'],
            ['SLA Compliance', f"{kpis['sla_compliance']:.1f}%", kpis['sla_grade']],
            ['Active Engineers', f"{kpis['active_engineers']:,}", '-'],
            ['Tickets/Engineer', f"{kpis['total_tickets'] / max(1, kpis['active_engineers']):.1f}", '-'],
        ]
        
        perf_table = Table(perf_data, colWidths=[200, 150, 100])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Top 15 Engineers
        if engineer_perf is not None and len(engineer_perf) > 0:
            story.append(Paragraph("Top 15 Engineers by Performance", heading_style))
            top_engineers = engineer_perf.head(15)
            eng_data = [['Rank', 'Engineer', 'Tickets', 'SLA %', 'MTTR', 'SLA Grade']]
            for idx, (_, row) in enumerate(top_engineers.iterrows(), 1):
                eng_data.append([
                    str(idx),
                    str(row['Engineer'])[:20],
                    f"{row['Total_Tickets']:,}",
                    f"{row['SLA_Compliance']:.1f}%",
                    f"{row['Avg_MTTR_Hours']:.2f}h",
                    row['SLA_Grade']
                ])
            
            eng_table = Table(eng_data, colWidths=[40, 130, 60, 60, 60, 50])
            eng_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(eng_table)
            story.append(Spacer(1, 20))
            
            # Bottom 10 Engineers
            story.append(Paragraph("Engineers Needing Improvement (Bottom 10)", heading_style))
            bottom_engineers = engineer_perf.tail(10).iloc[::-1]
            eng_data2 = [['Engineer', 'Tickets', 'SLA %', 'MTTR', 'SLA Grade']]
            for _, row in bottom_engineers.iterrows():
                eng_data2.append([
                    str(row['Engineer'])[:25],
                    f"{row['Total_Tickets']:,}",
                    f"{row['SLA_Compliance']:.1f}%",
                    f"{row['Avg_MTTR_Hours']:.2f}h",
                    row['SLA_Grade']
                ])
            
            eng_table2 = Table(eng_data2, colWidths=[150, 70, 70, 70, 50])
            eng_table2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
            ]))
            story.append(eng_table2)
    
    elif report_type == "SLA Report":
        # SLA Report - Focus on SLA compliance and breaches
        story.append(Paragraph("SLA Compliance Overview", heading_style))
        
        sla_compliant = kpis['total_tickets'] - kpis['breached_tickets']
        sla_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Tickets', f"{kpis['total_tickets']:,}", '-'],
            ['SLA Compliant', f"{sla_compliant:,}", '✓'],
            ['SLA Breached', f"{kpis['breached_tickets']:,}", '✗' if kpis['breached_tickets'] > 0 else '✓'],
            ['Compliance Rate', f"{kpis['sla_compliance']:.2f}%", kpis['sla_grade']],
            ['Breach Rate', f"{100 - kpis['sla_compliance']:.2f}%", '-'],
            ['Avg Breach Hours', f"{kpis.get('avg_breach_hours', 0):.2f}h", '-'],
            ['SLA Target', '95%', '-'],
            ['Variance from Target', f"{kpis['sla_compliance'] - 95:.2f}%", 'Above' if kpis['sla_compliance'] >= 95 else 'Below'],
        ]
        
        sla_table = Table(sla_data, colWidths=[180, 150, 100])
        sla_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(sla_table)
        story.append(Spacer(1, 20))
        
        # Clusters by SLA
        if cluster_perf is not None and len(cluster_perf) > 0:
            story.append(Paragraph("Clusters Below SLA Target (< 95%)", heading_style))
            below_target = cluster_perf[cluster_perf['SLA_Compliance'] < 95]
            if len(below_target) > 0:
                breach_data = [['Cluster', 'Tickets', 'SLA %', 'Breached', 'Grade']]
                for _, row in below_target.head(15).iterrows():
                    breach_data.append([
                        str(row['CLUSTER'])[:25],
                        f"{row['Total_Tickets']:,}",
                        f"{row['SLA_Compliance']:.1f}%",
                        f"{row['SLA_Breached']:,}",
                        row['Grade']
                    ])
                
                breach_table = Table(breach_data, colWidths=[150, 70, 70, 70, 50])
                breach_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
                ]))
                story.append(breach_table)
            else:
                story.append(Paragraph("All clusters are meeting the SLA target. Excellent!", normal_style))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        "This report was automatically generated by Fiber Maintenance Analytics System",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "Confidential - For Internal Use Only",
        ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer


def generate_html_report(df, kpis, cluster_perf, engineer_perf, report_type, date_range):
    """Generate HTML report (fallback when ReportLab not available) - Different content based on report type"""
    
    report_titles = {
        "Executive Summary": "Executive Summary Report",
        "Detailed Analysis": "Detailed Analysis Report",
        "Performance Report": "Performance Analysis Report",
        "SLA Report": "SLA Compliance Report"
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{report_titles.get(report_type, "Fiber Maintenance Analytics Report")}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #667eea; margin: 0; }}
            .header p {{ color: #666; margin: 5px 0; }}
            .section {{ margin: 30px 0; }}
            .section h2 {{ color: #333; border-left: 4px solid #667eea; padding-left: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            th.orange {{ background: #f97316; }}
            th.green {{ background: #10b981; }}
            th.red {{ background: #ef4444; }}
            th.purple {{ background: #764ba2; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            .metric {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px 30px; border-radius: 10px; margin: 10px; text-align: center; min-width: 120px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; }}
            .metric-label {{ font-size: 12px; opacity: 0.9; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
            .grade-a {{ color: #10b981; font-weight: bold; }}
            .grade-b {{ color: #f59e0b; font-weight: bold; }}
            .grade-c {{ color: #f97316; font-weight: bold; }}
            .grade-d {{ color: #ef4444; font-weight: bold; }}
            .alert {{ background: #fff5f5; }}
            .success {{ background: #f0fdf4; }}
            @media print {{ body {{ margin: 0; }} .container {{ box-shadow: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 {report_titles.get(report_type, "Fiber Maintenance Analytics Report")}</h1>
                <p><strong>Report Type:</strong> {report_type}</p>
                <p><strong>Period:</strong> {date_range}</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
            </div>
    """
    
    if report_type == "Executive Summary":
        # Executive Summary - High-level KPIs only
        html += f"""
            <div class="section">
                <h2>📊 Key Performance Indicators</h2>
                <div style="text-align: center;">
                    <div class="metric">
                        <div class="metric-value">{kpis['total_tickets']:,}</div>
                        <div class="metric-label">Total Tickets</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{kpis['sla_compliance']:.1f}%</div>
                        <div class="metric-label">SLA Compliance</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{format_duration(kpis['avg_duration'])}</div>
                        <div class="metric-label">Avg MTTR</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{kpis['sla_grade']}</div>
                        <div class="metric-label">Overall Grade</div>
                    </div>
                </div>
            </div>
        """
        
        # Top 5 clusters only
        if cluster_perf is not None and len(cluster_perf) > 0:
            html += """
            <div class="section">
                <h2>🏢 Top 5 Performing Clusters</h2>
                <table>
                    <tr><th class="purple">Cluster</th><th class="purple">Tickets</th><th class="purple">SLA %</th><th class="purple">Grade</th></tr>
            """
            for _, row in cluster_perf.head(5).iterrows():
                grade_class = 'a' if row['Grade'] in ['A+', 'A'] else 'b' if row['Grade'] == 'B' else 'c'
                html += f"""
                    <tr>
                        <td>{row['CLUSTER']}</td>
                        <td>{row['Total_Tickets']:,}</td>
                        <td>{row['SLA_Compliance']:.1f}%</td>
                        <td class="grade-{grade_class}">{row['Grade']}</td>
                    </tr>
                """
            html += "</table></div>"
    
    elif report_type == "Detailed Analysis":
        # Detailed Analysis - Full breakdown
        html += f"""
            <div class="section">
                <h2>📈 Complete Metrics Overview</h2>
                <table>
                    <tr><th>Category</th><th>Metric</th><th>Value</th></tr>
                    <tr><td>Volume</td><td>Total Tickets</td><td>{kpis['total_tickets']:,}</td></tr>
                    <tr><td>Volume</td><td>Non-Alarm Tickets</td><td>{kpis['non_alarm_tickets']:,}</td></tr>
                    <tr><td>Volume</td><td>Alarm Tickets</td><td>{kpis['alarm_tickets']:,} ({kpis['alarm_percentage']:.1f}%)</td></tr>
                    <tr><td>SLA</td><td>Compliance Rate</td><td>{kpis['sla_compliance']:.2f}%</td></tr>
                    <tr><td>SLA</td><td>Breached Tickets</td><td>{kpis['breached_tickets']:,}</td></tr>
                    <tr><td>SLA</td><td>Grade</td><td class="grade-{'a' if kpis['sla_compliance'] >= 95 else 'b' if kpis['sla_compliance'] >= 85 else 'c'}">{kpis['sla_grade']}</td></tr>
                    <tr><td>Time</td><td>Average MTTR</td><td>{format_duration(kpis['avg_duration'])}</td></tr>
                    <tr><td>Time</td><td>Median MTTR</td><td>{format_duration(kpis['median_duration'])}</td></tr>
                    <tr><td>Time</td><td>Min MTTR</td><td>{format_duration(kpis['min_duration'])}</td></tr>
                    <tr><td>Time</td><td>Max MTTR</td><td>{format_duration(kpis['max_duration'])}</td></tr>
                    <tr><td>Resources</td><td>Active Engineers</td><td>{kpis['active_engineers']:,}</td></tr>
                    <tr><td>Resources</td><td>Active Clusters</td><td>{kpis['active_clusters']:,}</td></tr>
                    <tr><td>Resources</td><td>Active Regions</td><td>{kpis['active_regions']:,}</td></tr>
                </table>
            </div>
        """
        
        # All clusters
        if cluster_perf is not None and len(cluster_perf) > 0:
            html += """
            <div class="section">
                <h2>🏢 Complete Cluster Analysis</h2>
                <table>
                    <tr><th class="purple">Cluster</th><th class="purple">Tickets</th><th class="purple">SLA %</th><th class="purple">MTTR</th><th class="purple">Grade</th></tr>
            """
            for _, row in cluster_perf.iterrows():
                grade_class = 'a' if row['Grade'] in ['A+', 'A'] else 'b' if row['Grade'] == 'B' else 'c'
                html += f"""
                    <tr>
                        <td>{row['CLUSTER']}</td>
                        <td>{row['Total_Tickets']:,}</td>
                        <td>{row['SLA_Compliance']:.1f}%</td>
                        <td>{row['Avg_MTTR_Hours']:.2f}h</td>
                        <td class="grade-{grade_class}">{row['Grade']}</td>
                    </tr>
                """
            html += "</table></div>"
    
    elif report_type == "Performance Report":
        # Performance Report - Focus on engineers
        html += f"""
            <div class="section">
                <h2>📊 Performance Summary</h2>
                <div style="text-align: center;">
                    <div class="metric">
                        <div class="metric-value">{format_duration(kpis['avg_duration'])}</div>
                        <div class="metric-label">Average MTTR</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{kpis['sla_compliance']:.1f}%</div>
                        <div class="metric-label">SLA Compliance</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{kpis['active_engineers']:,}</div>
                        <div class="metric-label">Active Engineers</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{kpis['total_tickets'] / max(1, kpis['active_engineers']):.1f}</div>
                        <div class="metric-label">Tickets/Engineer</div>
                    </div>
                </div>
            </div>
        """
        
        # Top 15 engineers
        if engineer_perf is not None and len(engineer_perf) > 0:
            html += """
            <div class="section">
                <h2>👷 Top 15 Engineers by Performance</h2>
                <table>
                    <tr><th class="green">Rank</th><th class="green">Engineer</th><th class="green">Tickets</th><th class="green">SLA %</th><th class="green">MTTR</th><th class="green">SLA Grade</th></tr>
            """
            for idx, (_, row) in enumerate(engineer_perf.head(15).iterrows(), 1):
                grade_class = 'a' if row['SLA_Grade'] in ['A+', 'A'] else 'b' if row['SLA_Grade'] == 'B' else 'c'
                html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{row['Engineer']}</td>
                        <td>{row['Total_Tickets']:,}</td>
                        <td>{row['SLA_Compliance']:.1f}%</td>
                        <td>{row['Avg_MTTR_Hours']:.2f}h</td>
                        <td class="grade-{grade_class}">{row['SLA_Grade']}</td>
                    </tr>
                """
            html += "</table></div>"
            
            # Bottom 10 engineers
            html += """
            <div class="section">
                <h2>⚠️ Engineers Needing Improvement</h2>
                <table>
                    <tr><th class="red">Engineer</th><th class="red">Tickets</th><th class="red">SLA %</th><th class="red">MTTR</th><th class="red">SLA Grade</th></tr>
            """
            for _, row in engineer_perf.tail(10).iloc[::-1].iterrows():
                grade_class = 'a' if row['SLA_Grade'] in ['A+', 'A'] else 'b' if row['SLA_Grade'] == 'B' else 'd'
                html += f"""
                    <tr class="alert">
                        <td>{row['Engineer']}</td>
                        <td>{row['Total_Tickets']:,}</td>
                        <td>{row['SLA_Compliance']:.1f}%</td>
                        <td>{row['Avg_MTTR_Hours']:.2f}h</td>
                        <td class="grade-{grade_class}">{row['SLA_Grade']}</td>
                    </tr>
                """
            html += "</table></div>"
    
    elif report_type == "SLA Report":
        # SLA Report - Focus on SLA compliance
        sla_compliant = kpis['total_tickets'] - kpis['breached_tickets']
        status_class = 'success' if kpis['sla_compliance'] >= 95 else 'alert'
        
        html += f"""
            <div class="section">
                <h2>📋 SLA Compliance Overview</h2>
                <div style="text-align: center;">
                    <div class="metric" style="background: {'#10b981' if kpis['sla_compliance'] >= 95 else '#ef4444'};">
                        <div class="metric-value">{kpis['sla_compliance']:.1f}%</div>
                        <div class="metric-label">SLA Compliance</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{sla_compliant:,}</div>
                        <div class="metric-label">Compliant</div>
                    </div>
                    <div class="metric" style="background: #ef4444;">
                        <div class="metric-value">{kpis['breached_tickets']:,}</div>
                        <div class="metric-label">Breached</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{kpis['sla_grade']}</div>
                        <div class="metric-label">Grade</div>
                    </div>
                </div>
                
                <table>
                    <tr><th class="orange">Metric</th><th class="orange">Value</th><th class="orange">Status</th></tr>
                    <tr><td>Total Tickets</td><td>{kpis['total_tickets']:,}</td><td>-</td></tr>
                    <tr class="{status_class}"><td>SLA Compliant</td><td>{sla_compliant:,}</td><td>✓</td></tr>
                    <tr class="{'alert' if kpis['breached_tickets'] > 0 else 'success'}"><td>SLA Breached</td><td>{kpis['breached_tickets']:,}</td><td>{'✗' if kpis['breached_tickets'] > 0 else '✓'}</td></tr>
                    <tr><td>Compliance Rate</td><td>{kpis['sla_compliance']:.2f}%</td><td>{kpis['sla_grade']}</td></tr>
                    <tr><td>Breach Rate</td><td>{100 - kpis['sla_compliance']:.2f}%</td><td>-</td></tr>
                    <tr><td>SLA Target</td><td>95%</td><td>-</td></tr>
                    <tr class="{status_class}"><td>Variance from Target</td><td>{kpis['sla_compliance'] - 95:.2f}%</td><td>{'Above ✓' if kpis['sla_compliance'] >= 95 else 'Below ✗'}</td></tr>
                </table>
            </div>
        """
        
        # Clusters below target
        if cluster_perf is not None and len(cluster_perf) > 0:
            below_target = cluster_perf[cluster_perf['SLA_Compliance'] < 95]
            if len(below_target) > 0:
                html += """
                <div class="section">
                    <h2>⚠️ Clusters Below SLA Target (< 95%)</h2>
                    <table>
                        <tr><th class="red">Cluster</th><th class="red">Tickets</th><th class="red">SLA %</th><th class="red">Breached</th><th class="red">Grade</th></tr>
                """
                for _, row in below_target.head(15).iterrows():
                    html += f"""
                        <tr class="alert">
                            <td>{row['CLUSTER']}</td>
                            <td>{row['Total_Tickets']:,}</td>
                            <td>{row['SLA_Compliance']:.1f}%</td>
                            <td>{row['SLA_Breached']:,}</td>
                            <td class="grade-d">{row['Grade']}</td>
                        </tr>
                    """
                html += "</table></div>"
            else:
                html += """
                <div class="section success" style="padding: 20px; border-radius: 10px;">
                    <h2>✅ All Clusters Meeting Target</h2>
                    <p>Excellent! All clusters are achieving the SLA target of 95% or above.</p>
                </div>
                """
    
    html += f"""
            <div class="footer">
                <p>This report was automatically generated by Fiber Maintenance Analytics System</p>
                <p>Confidential - For Internal Use Only</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


# ==================== MAIN PAGE ====================

create_header()

# Check for data
if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.warning("⚠️ No data loaded. Please load data from the sidebar first.")
    st.stop()

df = st.session_state['df']
date_range = f"{st.session_state.get('loaded_start_date', 'N/A')} to {st.session_state.get('loaded_end_date', 'N/A')[:10]}"

# Calculate metrics
kpis = calculate_comprehensive_kpis(df)
cluster_perf = calculate_cluster_performance(df)
engineer_perf = calculate_engineer_performance(df)

# Report configuration
st.markdown("### Report Configuration")

col1, col2 = st.columns(2)

with col1:
    report_type = st.selectbox(
        "Report Type",
        ["Executive Summary", "Detailed Analysis", "Performance Report", "SLA Report"],
        help="Select the type of report to generate"
    )

with col2:
    report_format = st.selectbox(
        "Output Format",
        ["PDF" if REPORTLAB_AVAILABLE else "HTML", "HTML"],
        help="Select output format"
    )

# Report preview
st.markdown("---")
st.markdown("### Report Preview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", f"{kpis['total_tickets']:,}")
with col2:
    st.metric("SLA Compliance", f"{kpis['sla_compliance']:.1f}%")
with col3:
    st.metric("Avg MTTR", format_duration(kpis['avg_duration']))
with col4:
    st.metric("Breached", f"{kpis['breached_tickets']:,}")

st.markdown("---")

# Generate report
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("📄 Generate Report", use_container_width=True, type="primary"):
        with st.spinner("Generating report..."):
            try:
                if report_format == "PDF" and REPORTLAB_AVAILABLE:
                    pdf_buffer = generate_pdf_report(
                        df, kpis, cluster_perf, engineer_perf, report_type, date_range
                    )
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"fiber_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report generated successfully!")
                else:
                    html_content = generate_html_report(
                        df, kpis, cluster_perf, engineer_perf, report_type, date_range
                    )
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download HTML Report",
                        data=html_content,
                        file_name=f"fiber_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                    st.success("✅ HTML report generated successfully!")
                    
                    # Preview
                    with st.expander("Preview Report"):
                        st.components.v1.html(html_content, height=600, scrolling=True)
                        
            except Exception as e:
                st.error(f"Error generating report: {e}")

# Info about formats
st.markdown("---")
st.info("""
**Report Formats:**
- **PDF**: Professional printable format (requires reportlab package)
- **HTML**: Web-based format, can be opened in any browser and printed to PDF

**Tip**: For Streamlit Cloud, HTML format is recommended as it doesn't require additional system dependencies.
""")

if not REPORTLAB_AVAILABLE:
    st.warning("📦 ReportLab is not installed. Using HTML format. To enable PDF, add `reportlab` to requirements.txt")
