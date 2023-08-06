import pandas as pd

class ExcelToCSVConverter:
    def __init__(self, input_file, output_file, start_row, sheet_name):
        self.input_file = input_file
        self.output_file = output_file
        self.start_row = start_row
        self.sheet_name = sheet_name

    def convert(self):
        df = pd.read_excel(self.input_file, sheet_name=self.sheet_name, skiprows=self.start_row - 1)
        df.to_csv(self.output_file, index=False)
        print("Conversion complete!")

# Example usage:
converter = ExcelToCSVConverter("/Users/shambhujha/documents/finance_data/SOM-Consolidated-v3.0.54.xlsx", "output.csv", 2, "Export-LRP-Demand")
converter.convert()
