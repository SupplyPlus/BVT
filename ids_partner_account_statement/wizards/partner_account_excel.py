from odoo import api, fields, models


class AccountBookExcel(models.AbstractModel):
    _name = 'report.ids_partner_account_statement.account_book_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        format1 = workbook.add_format({'font_size': 18, 'align': 'center', 'bold': True, 'border': True})
        head_line_format = workbook.add_format(
            {'font_size': 18, 'bottom': True, 'right': True, 'left': True,
             'top': True, 'align': 'center', 'fg_color': '#2263BB', 'font_color': '#FFFFFF',
             'bold': True, 'border': True})
        header_format = workbook.add_format(
            {'font_size': 16, 'bottom': True, 'right': True, 'left': True,
             'top': True, 'align': 'center', 'fg_color': '#2263BB', 'font_color': '#FFFFFF',
             'bold': True, 'border': True})
        line_format = workbook.add_format(
            {'font_size': 14, 'align': 'center', 'right': True,
             'left': True, 'bottom': True, 'top': True, 'border': True})
        sheet = workbook.add_worksheet('Account Book')
        lines = data['lines']

        row = 1
        for line in lines:
            sheet.merge_range(row, 4, row, 5, 'Account Book', head_line_format)
            row += 1
            sheet.write(row, 4, 'Reported Printed By :', head_line_format)
            sheet.write(row, 5, line[3], head_line_format)
            row += 2
            sheet.write(row, 2, 'From Date :', header_format)
            sheet.write(row, 3, line[1], header_format)
            sheet.write(row, 4, ' To Date :', header_format)
            sheet.write(row, 5, line[2], header_format)
            sheet.write(row, 6, 'Reporting Currency :', header_format)
            sheet.write(row, 7, 'Omani Riyal', header_format)
            row += 1
            sheet.write(row, 1, "Transaction No \n Acc Date", header_format)
            sheet.write(row, 2, "Cheque No", header_format)
            sheet.write(row, 3, "Purpose", header_format)
            sheet.write(row, 4, 'Partner Name', header_format)
            sheet.write(row, 5, 'Payment Type', header_format)
            sheet.write(row, 6, 'Debit Amt', header_format)
            sheet.write(row, 7, 'Credit Amt', header_format)
            sheet.write(row, 8, 'Balance Amt', header_format)
            row += 1
            sheet.write(row, 1, " Account :", header_format)
            sheet.write(row, 2, line[4], header_format)
            sheet.write(row, 3, 'Journal :', header_format)
            sheet.write(row, 4, line[5], header_format)
            sheet.write(row, 5, 'Bank Currency :', header_format)
            sheet.write(row, 6, 'Omani Riyal', header_format)
            sheet.write(row, 7, 'Opening Balance :', header_format)
            sheet.write(row, 8, line[0], header_format)
            row += 1
            for item in line[6]:
                sheet.write(row, 1, f"{item['transaction_no']} \n {item['date']} ", line_format)
                if item['cheque_no']:
                    sheet.write(row, 2, item['cheque_no'], line_format)
                else:
                    sheet.write(row, 2, "", line_format)
                if item['label']:
                    sheet.write(row, 3, item['label'], line_format)
                else:
                    sheet.write(row, 3, "", line_format)
                if item['partner_name']:
                    sheet.write(row, 4, item['partner_name'], line_format)
                else:
                    sheet.write(row, 4, "", line_format)
                if item['payment_type_for_bill'] == 'cheque':
                    sheet.write(row, 5, 'Cheque', line_format)
                if item['payment_type_for_bill'] == 'payment':
                    sheet.write(row, 5, 'Payment', line_format)
                if item['payment_type_for_bill'] == 'transfer':
                    sheet.write(row, 5, 'Transfer', line_format)
                if item['payment_type_for_bill'] == 'visa':
                    sheet.write(row, 5, 'Visa', line_format)
                if not item['payment_type_for_bill']:
                    sheet.write(row, 5, "", line_format)
                sheet.write(row, 6, item['debit'], line_format)
                sheet.write(row, 7, item['credit'], line_format)
                sheet.write(row, 8, item['balance'], line_format)
                row += 1
