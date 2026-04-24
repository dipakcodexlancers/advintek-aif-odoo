import base64
import qrcode
from io import BytesIO
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    lhdn_qr_code = fields.Binary(
        string="LHDN QR Code",
        compute="_compute_lhdn_qr_code"
        # store=True
    )

    @api.depends('lhdn_validation_link')
    def _compute_lhdn_qr_code(self):
        for rec in self:
            if rec.lhdn_validation_link:
                qr = qrcode.QRCode(
                    version=1,
                    box_size=6,
                    border=2
                )
                qr.add_data(rec.lhdn_validation_link)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                buffer = BytesIO()
                img.save(buffer, format="PNG")

                rec.lhdn_qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.lhdn_qr_code = False