from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    lhdn_tin = fields.Char(string="TIN")
    lhdn_id_type = fields.Selection([
        ('brn', 'BRN')
        ('nric', 'NRIC'),
        ('passport', 'Passport'),
        ('business', 'Business Registration'),
    ], string="ID Type")
    lhdn_id_value = fields.Char(string="ID Value")