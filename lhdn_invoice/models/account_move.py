from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_submit_irbm(self):
        for rec in self:
            rec.message_post(body="IRBM Button Clicked")