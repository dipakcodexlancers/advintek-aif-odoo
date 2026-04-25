from odoo import models, fields
import requests
import json
from datetime import datetime
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # IRBM Submission
    def action_submit_irbm(self):
        for rec in self:
            
            if rec.lhdn_status == 'IRBResponseSuccess':
                raise UserError("IRBM submission already completed for this invoice.")

            payload = {
                "invoice": rec.read()[0],

                "partner": rec.partner_id.read()[0] if rec.partner_id else {},

                "company": rec.company_id.read()[0] if rec.company_id else {},

                "lines": [
                    {
                        **line.read()[0],
                        "taxes": [tax.read()[0] for tax in line.tax_ids]
                    }
                    for line in rec.invoice_line_ids
                ]
            }

            invoice_type_map = {
                "out_invoice": "01",
                "out_refund": "02",
                "in_invoice": "11",
                "in_refund": "12",
            }

            invoice_type_code = invoice_type_map.get(rec.move_type)

            try:
                
                login_url = "https://espresso-freezable-dealing.ngrok-free.dev/api/2026.1/OdooInvoiceFactoryExtended/JSONLogin"

                login_payload = {
                    "loginId": "techsupport",
                    "password": "Workflow@007",
                    "domain": "AIF_API_Dev"
                }

                login_headers = {
                    "Content-Type": "application/json"
                }

                login_response = requests.post(
                    login_url,
                    headers=login_headers,
                    json=login_payload,
                    timeout=50
                )
                
                if login_response.status_code == 200:
                    rec.message_post(body="Successfully connected to IRBM")
                
                if login_response.status_code != 200:
                    # rec.message_post(body="Unable to establish a connection with IRBM")
                    raise UserError("Unable to establish a connection with IRBM. Please try again later.")
                
                login_data = login_response.json()
                token = login_data.get("data", {}).get("token")

                if not token:
                    raise Exception("Token not found in login response")
                
                submit_url = "https://espresso-freezable-dealing.ngrok-free.dev/api/2026.1/OdooInvoiceFactoryExtended/JSONSubmitInvoiceDocument"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }

                response = requests.post(
                    submit_url,
                    headers=headers,
                    params={"eInvoiceTypeCode": invoice_type_code},
                    data=json.dumps(payload, default=str),
                    timeout=500
                )

                # rec.message_post(body=f"IRBM Submit Invoice Response:\n{response.text}")
                
                if response.status_code == 200:
                    
                    result = response.json()

                    if result.get("statusCode") == 200 and result.get("isSuccess"):
                        data = result.get("data", {})

                        rec.lhdn_status = data.get("status")
                        rec.lhdn_uuid = data.get("uniquedocumentID")
                        rec.lhdn_validation_link = data.get("validationLink")

                        dt = data.get("dateTimeValidated")
                        if dt:
                            rec.lhdn_validation_date = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
                        
                        if data.get("status") != "IRBResponseSuccess":
                            rec.lhdn_rejection_result = result.get("data", {}).get("validationResults")
                        else:
                            rec.lhdn_rejection_result = False

                        rec.message_post(body="IRBM submission completed successfully")
                
                elif response.status_code != 200:
                    try:
                        result = response.json()
                        rec.lhdn_rejection_result = (
                            result.get("data", {}).get("validationResults")
                            or result.get("message")
                            or False
                        )
                        # rec.lhdn_status= "IRBMResponseFailed"
                        rec.message_post(body="IRBM submission failed")

                    except Exception:
                        rec.lhdn_rejection_result = False
        
            except Exception as e:
                rec.message_post(body=f"IRBM submission failed. Error: {str(e)}")
    
    # Reset IRBM fields for credit note
    def _reverse_moves(self, default_values_list=None, cancel=False):
        moves = super()._reverse_moves(default_values_list, cancel)

        for move in moves:
            if move.move_type == 'out_refund':
                move.write({
                    'lhdn_status': False,
                    'lhdn_uuid': False,
                    'lhdn_validation_date': False,
                    'lhdn_validation_link': False,
                    'lhdn_validation_result': False,
                    'lhdn_rejection_result': False,
                })

        return moves
                
    # IRBM Submission Details Fields
    lhdn_status = fields.Char(string="Status", readonly=True)
    lhdn_uuid = fields.Char(string="UUID", readonly=True)
    lhdn_validation_date = fields.Datetime(string="Validation Date", readonly=True)
    lhdn_validation_link = fields.Char(string="Validation Link", readonly=True)
    lhdn_validation_result = fields.Text(string="Validation Result", readonly=True)
    lhdn_rejection_result = fields.Text(string="Rejection Result", readonly=True)