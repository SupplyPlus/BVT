from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PartnerAccount(models.TransientModel):
    _name = "account.partner.statement"

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=False, domain="[('type', 'in', ('bank','cash'))]")
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True)

    def _prepare_report_print(self):
        if self.from_date > self.to_date:
            raise ValidationError(_("From Date Greater than End Date"))
        account_balance_domain = [
            ('date', '<', self.from_date),
            ('parent_state', '=', 'posted'),
            ('partner_id', '=', self.partner_id.id),
        ]
        initial_balance = sum(self.env['account.move.line'].search(
            account_balance_domain, order="id asc").mapped('balance'))
        journal_items_domain = [
            ('date', '>=', self.from_date),
            ('date', '<=', self.to_date),
            ('parent_state', '=', 'posted'),
            ('partner_id', '=', self.partner_id.id),
        ]
        journal_items = self.env['account.move.line'].search(
            journal_items_domain, order="id asc")
        all_data = []
        lines = []
        if journal_items:
            balance = initial_balance
            for item in journal_items:
                balance += item.balance
                lines.append({
                    'journal': item.journal_id.name,
                    'account': item.account_id.name,
                    'label': item.name,
                    'due_date': item.date_maturity,
                    'date': item.date,
                    'matching_number': item.matching_number,
                    'debit': item.debit,
                    'credit': item.credit,
                    'amount_currency': item.currency_id.name,
                    'balance': balance,
                })
        all_data.append(
            [initial_balance, self.from_date, self.to_date, self.env.user.name,
             self.partner_id.name, lines])
        return all_data

    def button_account_book_print(self):
        all_lines = self._prepare_report_print()
        data = {
            'lines': all_lines,
        }
        return self.env.ref('ids_partner_account_statement.account_book_report_id').report_action(
            self, data=data)

    def button_account_book_excel(self):
        all_lines = self._prepare_report_print()
        data = {
            'lines': all_lines,
        }
        return {
            'data': data,
            'type': 'ir.actions.report',
            'report_name': 'ids_partner_account_statement.account_book_excel',
            'report_type': 'xlsx',
            'report_file': "Account Book Excel",
        }
