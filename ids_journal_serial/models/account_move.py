from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    seq = fields.Integer(
        string='Seq',
        required=False)

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.move_type == 'entry' and move.move_type != 'out_invoice':
                entry = self.env['account.move'].search(
                    [('move_type', '=', 'entry'), ('journal_id', '=', move.journal_id.id),
                     ('id', '!=', move.id), ('seq', '!=', 0), ('state', '=', 'posted')], order='seq ASC')
                print("!!!!!!!!!!!!!!!!!!!!!!", entry)
                if entry:
                    move.seq = entry[-1].seq + 1
                    code = f"{move.journal_id.code}/{move.seq}"

                    # code = f'{move.journal_id.code}' + '/' + '{0}'.format(
                    #     str(move.seq).zfill(4))
                    move.name = code
                else:
                    move.seq = 1
                    code = f"{move.journal_id.code}/{move.seq}"
                    move.name = code
            invoices = self.env['account.move'].search(
                [('move_type', '=', 'out_invoice'), ('journal_id', '=', move.journal_id.id),
                 ('id', '!=', move.id), ('seq', '!=', 0), ('state', '=', 'posted')], order='seq ASC')
            if move.move_type == 'out_invoice':
                if invoices:
                    move.seq = invoices[-1].seq + 1
                    code = f"{move.journal_id.code}/{move.seq}"
                    move.name = code
                else:
                    move.seq = 1
                    code = f"{move.journal_id.code}/{move.seq}"
                    move.name = code
            bills = self.env['account.move'].search(
                [('move_type', '=', 'in_invoice'), ('journal_id', '=', move.journal_id.id),
                 ('id', '!=', move.id), ('seq', '!=', 0), ('state', '=', 'posted')], order='seq ASC')
            if move.move_type == 'in_invoice':
                if bills:
                    move.seq = bills[-1].seq + 1
                    code = f"{move.journal_id.code}/{move.seq}"
                    move.name = code
                else:
                    move.seq = 1
                    code = f"{move.journal_id.code}/{move.seq}"
                    move.name = code
        return res
