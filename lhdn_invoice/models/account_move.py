from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Button action
    def action_submit_irbm(self):
        for rec in self:
            rec.message_post(body="IRBM Button Clicked")

    # Fields
    lhdn_status = fields.Char(string="Status")
    lhdn_uuid = fields.Char(string="UUID")
    lhdn_validation_date = fields.Datetime(string="Validation Date")
    lhdn_validation_link = fields.Char(string="Validation Link")
    lhdn_rejection_result = fields.Text(string="Rejection Result")