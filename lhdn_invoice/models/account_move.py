from odoo import models, fields
import requests
import json
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_submit_irbm(self):
        for rec in self:

            # payload = {
            #     "invoice": {
            #         "number": rec.name,
            #         "date": str(rec.invoice_date) if rec.invoice_date else "",
            #         "total": rec.amount_total,
            #         "currency": rec.currency_id.name,
            #     },
            #     "customer": {
            #         "name": rec.partner_id.name,
            #         "email": rec.partner_id.email,
            #         "phone": rec.partner_id.phone,
            #         "tin": rec.partner_id.lhdn_tin,
            #         "id_type": rec.partner_id.lhdn_id_type,
            #         "id_value": rec.partner_id.lhdn_id_value,
            #     },
            #     "company": {
            #         "name": rec.company_id.name,
            #         "email": rec.company_id.email,
            #         "phone": rec.company_id.phone,
            #         "tin": rec.company_id.lhdn_tin,
            #         "id_type": rec.company_id.lhdn_id_type,
            #         "id_value": rec.company_id.lhdn_id_value,
            #         "msic_code": rec.company_id.lhdn_msic_code,
            #         "business_activity": rec.company_id.lhdn_business_activity,
            #     },
            #     "lines": [
            #         {
            #             "description": line.name,
            #             "quantity": line.quantity,
            #             "price": line.price_unit,
            #             "subtotal": line.price_subtotal,
            #             "tax": [t.name for t in line.tax_ids],
            #         }
            #         for line in rec.invoice_line_ids
            #     ]
            # }

            invoice_data = rec.read()[0]
            
            payload = {
                # "invoice": rec.read()[0],
                "invoice": {
                    **invoice_data,
                    "lines": [
                        {
                            **line.read()[0],
                            "taxes": [tax.read()[0] for tax in line.tax_ids]
                        }
                        for line in rec.invoice_line_ids
                    ]
                },

                "partner": rec.partner_id.read()[0] if rec.partner_id else {},

                "company": rec.company_id.read()[0] if rec.company_id else {},

                # "lines": [
                #     {
                #         **line.read()[0],
                #         "taxes": [tax.read()[0] for tax in line.tax_ids]
                #     }
                #     for line in rec.invoice_line_ids
                # ]
            }

            url = "https://espresso-freezable-dealing.ngrok-free.dev/Login/Submit"
            
            headers = {
                "Content-Type": "application/json"
            }

            try:
                # rec.message_post(body=f"IRBM Payload: {json.dumps(payload)}")

                # response = requests.post(
                #     url,
                #     headers=headers,
                #     data=json.dumps(payload),
                #     timeout=10000
                # )
                rec.message_post(body=f"IRBM Payload: {json.dumps(payload, default=str)}")

                response = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload, default=str),
                    timeout=10000
                )

                rec.message_post(body=f"IRBM Response Status: {response.status_code}")
                rec.message_post(body=f"IRBM Response Body: {response.text}")

                # if response.status_code == 200:
                #     data = response.json()

                #     rec.lhdn_status = "Submitted"
                #     rec.lhdn_uuid = data.get("uuid")
                #     rec.lhdn_validation_link = data.get("validation_link")
                #     rec.lhdn_validation_date = datetime.now()
                #     rec.lhdn_rejection_result = False

                #     rec.message_post(body="IRBM Submitted Successfully")

                if response.status_code == 200:
                    data = response.json()

                    rec.lhdn_status = data.get("status")
                    rec.lhdn_uuid = data.get("uuid")
                    rec.lhdn_validation_link = data.get("validation_link")

                    rec.lhdn_validation_date = datetime.now()

                    rec.lhdn_rejection_result = data.get("rejection_result")

                    # UI message
                    if data.get("status") == "Success":
                        rec.message_post(body="IRBM Submitted Successfully")
                    else:
                        rec.message_post(body=f"IRBM Failed: {data.get('message')}")

                # else:
                #     rec.lhdn_status = "Failed"
                #     rec.lhdn_rejection_result = response.text

                #     rec.message_post(body="IRBM Submission Failed")

                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", response.text)
                    except Exception:
                        error_msg = response.text

                    rec.lhdn_status = "Failed"
                    rec.lhdn_rejection_result = error_msg

                    rec.message_post(body=f"IRBM Submission Failed: {error_msg}")

            # except Exception as e:
            #     rec.lhdn_status = "Error"
            #     rec.lhdn_rejection_result = str(e)

            #     rec.message_post(body=f"IRBM Error: {str(e)}")
            except Exception as e:
                rec.lhdn_status = "Error"
                rec.lhdn_rejection_result = str(e)

                rec.message_post(body=f"IRBM Error: {str(e)}")

    lhdn_status = fields.Char(string="Status")
    lhdn_uuid = fields.Char(string="UUID")
    lhdn_validation_date = fields.Datetime(string="Validation Date")
    lhdn_validation_link = fields.Char(string="Validation Link")
    lhdn_rejection_result = fields.Text(string="Rejection Result")