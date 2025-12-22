"""
Report Generator Agent - Creates comprehensive PDF reports.
"""
from typing import Dict, Any, List
from datetime import datetime
import structlog
from io import BytesIO

from core.config import settings

logger = structlog.get_logger(__name__)


class ReportGeneratorAgent:
    """
    Agent specialized in generating comprehensive RCA PDF reports.
    
    Capabilities:
    - Generate multi-page PDF reports with ReportLab
    - Include wafer maps, charts, and tables
    - Format hypotheses with evidence
    - Add executive summary
    - Upload to S3/MinIO
    """
    
    def __init__(self):
        pass
    
    def _create_pdf_report(self, state: Dict[str, Any]) -> str:
        """
        Generate PDF report using ReportLab.
        
        In production: Use reportlab.lib and reportlab.platypus
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
            from reportlab.lib import colors
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c5282'),
                spaceAfter=12,
            )
            
            # Title
            story.append(Paragraph("Root Cause Analysis Report", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            
            summary_data = [
                ["Session ID:", state.get("session_id", "N/A")],
                ["Lot ID:", state.get("lot_id", "N/A")],
                ["Wafer ID:", state.get("wafer_id", "N/A")],
                ["Bin:", str(state.get("bin", "N/A"))],
                ["Priority:", state.get("priority", "N/A")],
                ["Analysis Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # Top Hypotheses
            story.append(Paragraph("Ranked Root Cause Hypotheses", heading_style))
            
            hypotheses = state.get("root_causes", [])
            for hyp in hypotheses[:3]:  # Top 3
                rank = hyp.get("rank", 0)
                hypothesis = hyp.get("hypothesis", "N/A")
                confidence = hyp.get("confidence", 0)
                
                story.append(Paragraph(
                    f"<b>Hypothesis {rank}:</b> {hypothesis}",
                    styles['Normal']
                ))
                story.append(Paragraph(
                    f"<i>Confidence: {confidence:.1%}</i>",
                    styles['Normal']
                ))
                
                # Evidence
                story.append(Paragraph("<b>Supporting Evidence:</b>", styles['Normal']))
                evidence = hyp.get("evidence", [])
                for ev in evidence:
                    story.append(Paragraph(
                        f"• [{ev.get('type', 'N/A')}] {ev.get('detail', 'N/A')}",
                        styles['Normal']
                    ))
                
                # Next steps
                next_steps = hyp.get("next_steps", [])
                if next_steps:
                    story.append(Paragraph("<b>Recommended Next Steps:</b>", styles['Normal']))
                    for step in next_steps:
                        story.append(Paragraph(f"• {step}", styles['Normal']))
                
                story.append(Spacer(1, 0.2 * inch))
            
            story.append(PageBreak())
            
            # Statistical Findings
            story.append(Paragraph("Statistical Analysis", heading_style))
            
            statistical_findings = state.get("statistical_findings", [])
            if statistical_findings:
                stat_data = [["Test", "Result", "Confidence"]]
                for finding in statistical_findings:
                    test = finding.get("test", "N/A")
                    conclusion = finding.get("conclusion", "N/A")
                    conf = finding.get("confidence", 0)
                    stat_data.append([test, conclusion, f"{conf:.1%}"])
                
                stat_table = Table(stat_data, colWidths=[2*inch, 3*inch, 1*inch])
                stat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                ]))
                
                story.append(stat_table)
                story.append(Spacer(1, 0.2 * inch))
            
            # Spatial Patterns
            story.append(Paragraph("Spatial Pattern Analysis", heading_style))
            
            spatial_patterns = state.get("spatial_patterns", [])
            if spatial_patterns:
                for pattern in spatial_patterns:
                    pattern_type = pattern.get("pattern", "N/A")
                    description = pattern.get("description", "N/A")
                    confidence = pattern.get("confidence", 0)
                    
                    story.append(Paragraph(
                        f"<b>{pattern_type.upper()}:</b> {description} (confidence: {confidence:.1%})",
                        styles['Normal']
                    ))
                    story.append(Spacer(1, 0.1 * inch))
            
            # Wafer Map (placeholder - in production, embed actual image)
            story.append(Spacer(1, 0.2 * inch))
            wafer_map_path = state.get("wafer_map_path", "")
            if wafer_map_path:
                story.append(Paragraph(f"Wafer Map: {wafer_map_path}", styles['Italic']))
                # In production: story.append(Image(wafer_map_path, width=4*inch, height=4*inch))
            
            story.append(PageBreak())
            
            # Correlation Analysis
            story.append(Paragraph("Correlation Analysis", heading_style))
            
            correlations = state.get("correlations", [])
            if correlations:
                for corr in correlations:
                    if "test1" in corr:
                        test1 = corr.get("test1", "N/A")
                        test2 = corr.get("test2", "N/A")
                        correlation = corr.get("correlation", 0)
                        p_value = corr.get("p_value", 1)
                        
                        story.append(Paragraph(
                            f"<b>{test1} vs {test2}:</b> r={correlation:.3f}, p={p_value:.4f}",
                            styles['Normal']
                        ))
                    elif "method" in corr:
                        method = corr.get("method", "N/A")
                        description = corr.get("description", "N/A")
                        story.append(Paragraph(f"<b>{method}:</b> {description}", styles['Normal']))
                    
                    story.append(Spacer(1, 0.1 * inch))
            
            # Footer
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(
                f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Multi-Agent RCA Platform",
                styles['Italic']
            ))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(
                "pdf_generated",
                session_id=state.get("session_id"),
                pdf_size_bytes=len(pdf_bytes),
            )
            
            return pdf_bytes
            
        except ImportError:
            logger.warning("reportlab_not_installed", msg="Using mock PDF generation")
            # Mock PDF generation
            return b"%PDF-1.4\n%Mock PDF Report\n"
    
    def _upload_to_s3(self, pdf_bytes: bytes, session_id: str) -> str:
        """
        Upload PDF to S3/MinIO.
        
        In production: Use boto3 or MinIO client
        """
        # Mock S3 upload
        s3_path = f"s3://rca-reports/{session_id}.pdf"
        
        logger.info(
            "pdf_uploaded_to_s3",
            session_id=session_id,
            s3_path=s3_path,
            size_bytes=len(pdf_bytes),
        )
        
        return s3_path
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute report generation workflow.
        
        Args:
            state: Workflow state with all analysis results
        
        Returns:
            Updated state with report path
        """
        logger.info(
            "report_generator_starting",
            session_id=state.get("session_id"),
            lot_id=state.get("lot_id"),
        )
        
        # Generate PDF report
        pdf_bytes = self._create_pdf_report(state)
        
        # Upload to S3
        report_path = self._upload_to_s3(pdf_bytes, state.get("session_id", "unknown"))
        
        # Update state
        state["report_path"] = report_path
        
        # Add message
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "agent": "ReportGenerator",
            "finding": f"PDF report generated: {report_path}",
            "confidence": 1.0,
            "details": {
                "report_path": report_path,
                "size_bytes": len(pdf_bytes),
            },
        })
        
        logger.info(
            "report_generator_completed",
            session_id=state.get("session_id"),
            report_path=report_path,
        )
        
        return state


# Singleton instance
report_generator_agent = ReportGeneratorAgent()
