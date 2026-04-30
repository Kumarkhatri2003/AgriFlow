# admin/services.py
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth import get_user_model
from crops.models import Crop
from livestock.models import Animal
from finance.models import Transaction
from .models import Report
import io

User = get_user_model()


class ReportGeneratorService:
    """Service for generating various reports"""
    
    @classmethod
    def generate_report(cls, report_type, format, start_date, end_date, include_details, user):
        """Generate report based on type and format"""
        
        if report_type == 'farmer':
            data = cls.get_farmer_data(start_date, end_date)
            filename = f"farmer_report_{start_date}_{end_date}"
        elif report_type == 'financial':
            data = cls.get_financial_data(start_date, end_date)
            filename = f"financial_report_{start_date}_{end_date}"
        elif report_type == 'crop':
            data = cls.get_crop_data(start_date, end_date)
            filename = f"crop_report_{start_date}_{end_date}"
        elif report_type == 'livestock':
            data = cls.get_livestock_data(start_date, end_date)
            filename = f"livestock_report_{start_date}_{end_date}"
        else:
            data = []
            filename = "custom_report"
        
        # Save report to database
        report = Report.objects.create(
            report_type=report_type,
            format=format,
            title=f"{report_type.title()} Report",
            filters={'start_date': str(start_date), 'end_date': str(end_date)},
            generated_by=user
        )
        
        # Generate file based on format
        if format == 'csv':
            return cls.generate_csv(data, filename, report)
        elif format == 'excel':
            return cls.generate_excel(data, filename, report)
        elif format == 'pdf':
            return cls.generate_pdf(data, filename, report)
        
        return {'error': 'Unsupported format'}
    
    @classmethod
    def get_farmer_data(cls, start_date, end_date):
        """Get farmer data for report"""
        farmers = User.objects.filter(
            is_farmer=True,
            date_joined__date__gte=start_date,
            date_joined__date__lte=end_date
        )
        return [
            {
                'ID': f.id,
                'Username': f.username,
                'Full Name': f.get_full_name(),
                'Email': f.email,
                'Phone': f.phone or '-',
                'Farm Name': f.farm_name or '-',
                'Region': f.get_geographical_region_display() or '-',
                'Status': 'Active' if f.is_active else 'Inactive',
                'Join Date': f.date_joined.strftime('%Y-%m-%d')
            }
            for f in farmers
        ]
    
    @classmethod
    def get_financial_data(cls, start_date, end_date):
        """Get financial data for report"""
        transactions = Transaction.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        return [
            {
                'Date': t.date.strftime('%Y-%m-%d'),
                'Type': t.transaction_type,
                'Category': t.category,
                'Amount': t.amount,
                'User': t.user.get_full_name(),
                'Description': t.description
            }
            for t in transactions
        ]
    
    @classmethod
    def get_crop_data(cls, start_date, end_date):
        """Get crop data for report"""
        crops = Crop.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        return [
            {
                'Crop Name': c.name,
                'Farmer': c.farmer.get_full_name(),
                'Area': f"{c.field_area} {c.area_unit}",
                'Planting Date': c.planting_date.strftime('%Y-%m-%d'),
                'Stage': c.growth_stage,
                'Status': c.status,
                'Profit': c.net_profit
            }
            for c in crops
        ]
    
    @classmethod
    def get_livestock_data(cls, start_date, end_date):
        """Get livestock data for report"""
        animals = Animal.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        return [
            {
                'Type': a.animal_type.name,
                'Tag': a.tag_number,
                'Name': a.name or '-',
                'Farmer': a.farmer.get_full_name(),
                'Health': a.health_status or '-',
                'Status': a.status
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
        
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return response
    
    @classmethod
    def generate_excel(cls, data, filename, report):
        """Generate Excel file"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"
        
        if data:
            # Write headers
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Write data
            for row in data:
                ws.append(list(row.values()))
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        wb.save(response)
        
        return response
    
    @classmethod
    def generate_pdf(cls, data, filename, report):
        """Generate PDF file"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title = Paragraph(f"{report.title}", styles['Title'])
        elements.append(title)
        
        if data:
            # Create table
            headers = list(data[0].keys())
            table_data = [headers]
            for row in data:
                table_data.append(list(row.values()))
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        
        return response