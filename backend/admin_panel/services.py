# admin/services.py
from django.http import HttpResponse
import csv
from decimal import Decimal
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.contrib.auth import get_user_model
from crops.models import Crop
from livestock.models import Animal
from finance.models import Transaction
from .models import Report
import io

User = get_user_model()


def _cell(value):
    """Normalize values for CSV/Excel/PDF export."""
    if value is None:
        return '-'
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d')
    return str(value)


class ReportGeneratorService:
    """Service for generating various reports"""

    @classmethod
    def generate_report(cls, report_type, format, start_date, end_date, include_details, user):
        """Generate report based on type and format"""
        if report_type == 'farmer':
            data = cls.get_farmer_data(start_date, end_date, include_details)
            filename = f"farmer_report_{start_date}_{end_date}"
        elif report_type == 'financial':
            data = cls.get_financial_data(start_date, end_date, include_details)
            filename = f"financial_report_{start_date}_{end_date}"
        elif report_type == 'crop':
            data = cls.get_crop_data(start_date, end_date, include_details)
            filename = f"crop_report_{start_date}_{end_date}"
        elif report_type == 'livestock':
            data = cls.get_livestock_data(start_date, end_date, include_details)
            filename = f"livestock_report_{start_date}_{end_date}"
        else:
            data = [{'Message': 'Unsupported report type'}]
            filename = "custom_report"

        report = Report.objects.create(
            report_type=report_type,
            format=format,
            title=f"{report_type.title()} Report",
            filters={'start_date': str(start_date), 'end_date': str(end_date), 'include_details': include_details},
            generated_by=user
        )

        if format == 'csv':
            return cls.generate_csv(data, filename, report)
        if format == 'excel':
            return cls.generate_excel(data, filename, report)
        if format == 'pdf':
            return cls.generate_pdf(data, filename, report)

        return HttpResponse(
            '{"error": "Unsupported format"}',
            content_type='application/json',
            status=400,
        )

    @classmethod
    def get_farmer_data(cls, start_date, end_date, include_details=True):
        """Get farmer data for report — full list of each registered farmer."""
        farmers = User.objects.filter(is_farmer=True, is_admin=False).order_by('-date_joined')

        if not include_details:
            active = farmers.filter(is_active=True).count()
            inactive = farmers.filter(is_active=False).count()
            return [
                {'Metric': 'Total Farmers', 'Value': farmers.count()},
                {'Metric': 'Active Farmers', 'Value': active},
                {'Metric': 'Inactive Farmers', 'Value': inactive},
                {'Metric': 'Report Period Start', 'Value': str(start_date)},
                {'Metric': 'Report Period End', 'Value': str(end_date)},
            ]

        return [
            {
                'ID': f.id,
                'Username': f.username,
                'Full Name': f.get_full_name(),
                'Email': f.email,
                'Phone': f.phone or '-',
                'District': f.district or '-',
                'Region': f.get_geographical_region_display() or '-',
                'Farm Name': f.farm_name or '-',
                'Farm Area (ha)': _cell(f.total_farm_area),
                'Status': 'Active' if f.is_active else 'Inactive',
                'Email Verified': 'Yes' if f.is_email_verified else 'No',
                'Join Date': _cell(f.date_joined),
            }
            for f in farmers
        ]

    @classmethod
    def get_financial_data(cls, start_date, end_date, include_details=True):
        """Get financial transactions within the selected date range."""
        transactions = Transaction.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
        ).select_related('user', 'crop', 'animal').order_by('-date')

        if not include_details:
            income_total = sum(t.amount for t in transactions if t.is_income)
            expense_total = sum(t.amount for t in transactions if not t.is_income)
            return [
                {'Metric': 'Total Transactions', 'Value': transactions.count()},
                {'Metric': 'Total Income (NPR)', 'Value': _cell(income_total)},
                {'Metric': 'Total Expense (NPR)', 'Value': _cell(expense_total)},
                {'Metric': 'Net (NPR)', 'Value': _cell(income_total - expense_total)},
                {'Metric': 'Period Start', 'Value': str(start_date)},
                {'Metric': 'Period End', 'Value': str(end_date)},
            ]

        rows = []
        for t in transactions:
            linked = '-'
            if t.crop:
                linked = f"Crop: {t.crop.name}"
            elif t.animal:
                linked = f"Animal: {t.animal.name or t.animal.tag_number}"

            rows.append({
                'Date': _cell(t.date),
                'Type': t.get_transaction_type_display(),
                'Category': t.category,
                'Amount (NPR)': _cell(t.amount),
                'Farmer': t.user.get_full_name(),
                'Description': t.description or '-',
                'Linked To': linked,
            })
        return rows

    @classmethod
    def get_crop_data(cls, start_date, end_date, include_details=True):
        """Get crop data — full list of each crop on the platform."""
        crops = Crop.objects.select_related('farmer').order_by('-planting_date')

        if not include_details:
            active = crops.filter(status='active').count()
            harvested = crops.filter(status__in=['harvested', 'done']).count()
            return [
                {'Metric': 'Total Crops', 'Value': crops.count()},
                {'Metric': 'Active Crops', 'Value': active},
                {'Metric': 'Harvested/Done', 'Value': harvested},
                {'Metric': 'Report Period Start', 'Value': str(start_date)},
                {'Metric': 'Report Period End', 'Value': str(end_date)},
            ]

        return [
            {
                'Crop Name': c.name,
                'Variety': c.variety or '-',
                'Field Name': c.field_name,
                'Farmer': c.farmer.get_full_name(),
                'Farmer Email': c.farmer.email,
                'Area': f"{c.field_area} {c.get_area_unit_display()}",
                'Planting Date': _cell(c.planting_date),
                'Expected Harvest': _cell(c.expected_harvest_date),
                'Growth Stage': c.get_growth_stage_display(),
                'Status': c.get_status_display(),
                'Irrigated': 'Yes' if c.is_irrigated else 'No',
                'Total Income (NPR)': _cell(c.total_income),
                'Total Expense (NPR)': _cell(c.total_expense),
                'Net Profit (NPR)': _cell(c.net_profit),
            }
            for c in crops
        ]

    @classmethod
    def get_livestock_data(cls, start_date, end_date, include_details=True):
        """Get livestock data — full list of each animal on the platform."""
        animals = Animal.objects.select_related('farmer', 'animal_type').order_by('-created_at')

        if not include_details:
            active = animals.filter(status='active').count()
            return [
                {'Metric': 'Total Animals', 'Value': animals.count()},
                {'Metric': 'Active Animals', 'Value': active},
                {'Metric': 'Report Period Start', 'Value': str(start_date)},
                {'Metric': 'Report Period End', 'Value': str(end_date)},
            ]

        return [
            {
                'Tag Number': a.tag_number,
                'Name': a.name or '-',
                'Type': a.animal_type.name,
                'Farmer': a.farmer.get_full_name(),
                'Farmer Email': a.farmer.email,
                'Gender': a.get_gender_display(),
                'Status': a.get_status_display(),
                'Birth Date': _cell(a.birth_date),
                'Acquisition Date': _cell(a.acquisition_date),
                'Pregnant': 'Yes' if a.is_pregnant else 'No',
                'Total Income (NPR)': _cell(a.total_income),
                'Total Expense (NPR)': _cell(a.total_expense),
                'Net Profit (NPR)': _cell(a.net_profit),
            }
            for a in animals
        ]

    @classmethod
    def generate_csv(cls, data, filename, report):
        """Generate CSV file"""
        if not data:
            data = [{'Message': 'No data available for the selected period'}]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

        writer = csv.DictWriter(response, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)

        return response

    @classmethod
    def generate_excel(cls, data, filename, report):
        """Generate Excel file"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        if not data:
            data = [{'Message': 'No data available for the selected period'}]

        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append([row.get(h, '') for h in headers])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        wb.save(response)

        return response

    @classmethod
    def generate_pdf(cls, data, filename, report):
        """Generate PDF file with proper text wrapping and sizing"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        elements = []

        styles = getSampleStyleSheet()
        
        # Add custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1  # Center alignment
        ))

        # Title
        title = Paragraph(f"{report.title}", styles['CustomTitle'])
        elements.append(title)

        # Add date range info
        if report.filters:
            date_range = f"Period: {report.filters.get('start_date', 'N/A')} to {report.filters.get('end_date', 'N/A')}"
            elements.append(Paragraph(date_range, styles['Normal']))
            elements.append(Paragraph(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M') if report.generated_at else 'N/A'}", styles['Normal']))
        
        elements.append(Paragraph("<br/>", styles['Normal']))

        if not data:
            data = [{'Message': 'No data available for the selected period'}]

        headers = list(data[0].keys())
        
        # Calculate column widths based on content
        max_col_width = 150  # Maximum width for a single column
        page_width = 7.5 * inch  # Usable page width (letter size minus margins)
        
        # Calculate ideal column widths
        col_widths = []
        for i, header in enumerate(headers):
            # Get max content length for this column
            max_len = len(header)
            for row in data:
                val = str(row.get(header, ''))
                max_len = max(max_len, len(val))
            
            # Width based on content length (rough estimate: 6 points per character)
            width = min(max_col_width, max_len * 6 + 20)
            col_widths.append(width)
        
        # If total width exceeds page width, scale down proportionally
        total_width = sum(col_widths)
        if total_width > page_width:
            scale = page_width / total_width
            col_widths = [w * scale for w in col_widths]
        
        # Ensure minimum column width
        min_width = 40
        col_widths = [max(min_width, w) for w in col_widths]
        
        # Prepare table data with wrapped text
        table_data = []
        
        # Headers with styling
        header_cells = []
        for h in headers:
            # Wrap long headers
            if len(h) > 20:
                h = '<br/>'.join([h[i:i+20] for i in range(0, len(h), 20)])
            header_cells.append(Paragraph(f"<b>{h}</b>", styles['CustomHeader']))
        table_data.append(header_cells)
        
        # Data rows with text wrapping
        for row in data:
            row_cells = []
            for h in headers:
                val = str(row.get(h, ''))
                # Wrap long text
                if len(val) > 30:
                    val = '<br/>'.join([val[i:i+30] for i in range(0, len(val), 30)])
                row_cells.append(Paragraph(val, styles['CustomNormal']))
            table_data.append(row_cells)

        # Create table with calculated column widths
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            
            # Alternating row colors
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            
            # Alignment for numeric columns (adjust based on content)
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(table)
        
        # Build PDF with page breaks if needed
        doc.build(elements, onFirstPage=cls._add_page_number, onLaterPages=cls._add_page_number)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

        return response

    @staticmethod
    def _add_page_number(canvas, doc):
        """Add page numbers to PDF"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(7.5 * 72, 0.5 * 72, text)