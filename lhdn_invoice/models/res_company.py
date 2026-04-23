from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    lhdn_tin = fields.Char(string="TIN")
    # lhdn_id_type = fields.Char(string="Id Type")
    lhdn_id_type = fields.Selection([
        ('BRN', 'BRN'),
        ('NRIC', 'NRIC'),
        ('ARMY', 'ARMY'),
        ('PASSPORT', 'PASSPORT'),
    ], string="ID Type")
    lhdn_id_value = fields.Char(string="Id Value")
    lhdn_business_activity = fields.Char(string="Business Activity Description")
    lhdn_msic_code = fields.Char(string="MSIC Code")
    lhdn_payment_means_code = fields.Char(string="Payment Means Code")
    lhdn_payment_terms = fields.Char(string="Default Payment Terms")