from odoo import api, fields, models


class AppSegment(models.Model):
    _name = 'app.segment'
    _description = "App Segment"

    name = fields.Char(string='Category', required=True)

    parent_id = fields.Many2one(
        comodel_name='app.segment',
        string='Parent_id',
        required=False)
    code = fields.Char(
        string='Code',
        required=False)
