from odoo import api,fields,models


class AgeingReportWizard(models.TransientModel):
    _name = "ageing.report.wizard"

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    account_type = fields.Selection(
        [("asset_receivable", "Receivable"), ("liability_payable", "Payable")],
        string="Account type",
        default="receivable",
    )
    ageing_type = fields.Selection(
        [("days", "Age by days"), ("months", "Age by months")],
        string="Ageing Type",
        default="days",
    )
    sale_rep_id = fields.Many2one('sales.repo', string="Salesman")
    partner_id = fields.Many2one('res.partner', string="Partner")


    def action_ageing_report(self):
        data = {
            'ids': self.ids,
            # 'model': 'salesman.invoice.wizard',
            'start_date': self.start_date,
            'end_date': self.end_date,
            'account_type': self.account_type,
            'ageing_type': self.ageing_type,
            'partner_id': self.partner_id.id,
            'sale_rep_id': self.sale_rep_id.id

        }
        return self.env.ref('ids_ageing_report.report_ageing_xlsx').report_action(self, data=data)