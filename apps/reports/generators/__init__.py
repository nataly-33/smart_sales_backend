from .base import BaseReportGenerator, ReportGeneratorFactory
from .pdf_generator import PDFReportGenerator
from .excel_generator import ExcelReportGenerator
from .csv_generator import CSVReportGenerator

# Registrar generadores en la factory
ReportGeneratorFactory.register('pdf', PDFReportGenerator)
ReportGeneratorFactory.register('excel', ExcelReportGenerator)
ReportGeneratorFactory.register('csv', CSVReportGenerator)

__all__ = [
    'BaseReportGenerator',
    'ReportGeneratorFactory',
    'PDFReportGenerator',
    'ExcelReportGenerator',
    'CSVReportGenerator',
]
