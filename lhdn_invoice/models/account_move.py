from odoo import models, fields
import requests
import json
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_submit_irbm(self):
        for rec in self:

            invoice_data = rec.read()[0]

            payload = {
                "invoice": rec.read()[0],
                # "invoice": {
                #     **invoice_data,
                #     "lines": [
                #         {
                #             **line.read()[0],
                #             "taxes": [tax.read()[0] for tax in line.tax_ids]
                #         }
                #         for line in rec.invoice_line_ids
                #     ]
                # },

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
            
            # rec.message_post(body=payload)

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
                
                if login_response.status_code == 200:(
                    rec.message_post("Successfully connected to IRBM..")
                )
                # rec.message_post(
                #     body=f"IRBM Login | Status: {login_response.status_code} | Body: {login_response.text}"
                # )

                # if login_response.status_code != 200:
                #     raise Exception(f"Login API Failed: {login_response.text}")
                
                if login_response.status_code != 200:
                    raise Exception(f"Unable to establish a connection with IRBM: {login_response.text}")
                
                login_data = login_response.json()
                token = login_data.get("data", {}).get("token")

                if not token:
                    raise Exception("Token not found in login response")
                
                submit_url = "https://espresso-freezable-dealing.ngrok-free.dev/api/2026.1/OdooInvoiceFactoryExtended/JSONSubmitInvoiceDocument"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }

                # response = requests.post(
                #     url,
                #     headers=headers,
                #     params={"InvoiceTypeCode": invoice_type_code},
                #     data=json.dumps(payload, default=str),
                #     timeout=10000
                # )
                
                response = requests.post(
                    submit_url,
                    headers=headers,
                    params={"eInvoiceTypeCode": invoice_type_code},
                    data=json.dumps(payload, default=str),
                    timeout=500
                )

                # rec.message_post(body=f"SubmitInvoiceDocument Response | Status: {response.status_code} | Body: {response.text}")
                rec.message_post(
                    body=(
                        f"IRBM Submit Invoice Response:\n"
                        f"- Status Code: {response.status_code}\n"
                        f"- Response: {response.text}"
                    )
                )

                # if response.status_code == 200:
                #     data = response.json()

                #     rec.lhdn_status = data.get("status")
                #     rec.lhdn_uuid = data.get("uuid")
                #     rec.lhdn_validation_link = data.get("validation_link")

                #     rec.lhdn_validation_date = datetime.now()

                #     rec.lhdn_rejection_result = data.get("rejection_result")

                #     if data.get("status") == "Success":
                #         rec.message_post(body="IRBM submission successful")
                #     else:
                #         rec.message_post(body=f"IRBM submission failed : {data.get('message')}")

                # else:
                #     try:
                #         error_data = response.json()
                #         error_msg = error_data.get("message", response.text)
                #     except Exception:
                #         error_msg = response.text

                #     rec.lhdn_status = "Failed"
                #     rec.lhdn_rejection_result = error_msg

                #     rec.message_post(body=f"IRBM Submission Failed: {error_msg}")
                
            except Exception as e:
                rec.lhdn_status = "Error"
                rec.lhdn_rejection_result = str(e)

                # rec.message_post(body=f"IRBM Error: {str(e)}")
                rec.message_post(body=f"{str(e)}")

    lhdn_status = fields.Char(string="Status")
    lhdn_uuid = fields.Char(string="UUID")
    lhdn_validation_date = fields.Datetime(string="Validation Date")
    lhdn_validation_link = fields.Char(string="Validation Link")
    lhdn_rejection_result = fields.Text(string="Rejection Result")