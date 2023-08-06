
from excel_converter import ExcelToCSVConverter
excel_file = '/Users/shambhujha/documents/finance_data/SOM-Consolidated-v3.0.54.xlsx'
output_file = 'output1.csv'
start_row = 5
sheet_name='Export-LRP-Demand'

converter = ExcelToCSVConverter(excel_file, output_file, start_row,sheet_name)
converter.convert()
