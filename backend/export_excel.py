from openpyxl import Workbook 
from django.http import HttpResponse 


def export_data_to_excel(filename, heaers, rows):
    """
     Exports data to an Excel file.
     :param filename: Name of the file to be created.
     :param heaers: List of headers for the Excel file.
     :param rows: List of rows, where each row is a list of cell values.
     :return: HttpResponse with the Excel file.
     
    """

    workbook    = Workbook()
    worksheet   = workbook.active 

    worksheet.title = filename or "Data Export" 
    worksheet.append(heaers) 

    for row in rows:
        try:
            worksheet.append(row)
        except Exception as e:
            raise Exception(f"Error appending row {row}: {e}") 
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    workbook.save(response)
    return response 