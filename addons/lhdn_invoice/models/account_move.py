from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_lhdn_status = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('submitted', 'Submitted'),
        ('error', 'Error')
    ], string="LHDN Status", default='draft')

    x_lhdn_uuid = fields.Char(string="LHDN UUID")

    x_lhdn_response = fields.Text(string="LHDN Response")