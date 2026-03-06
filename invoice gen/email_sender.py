"""
email_sender.py — Sends the generated invoice PDF to the client via Gmail SMTP.

Requirements:
  - Python's built-in smtplib (no extra install needed)
  - A Gmail App Password in config.json
    (NOT your real Gmail password — see "_email_instructions" in config.json)
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_invoice_email(config: dict, invoice_data: dict, pdf_path: str) -> tuple[bool, str]:
    """
    Compose and send an invoice email with the PDF attached.

    Parameters
    ----------
    config       : dict  — loaded from config.json (must have sender_email, app_password, sender_name)
    invoice_data : dict  — the invoice data dict from invoice_gui.py (client_name, client_email, etc.)
    pdf_path     : str   — absolute path to the generated PDF file

    Returns
    -------
    (success: bool, message: str)
    """

    # ── Gather sender credentials ────────────────────────────────────────────
    sender_email  = config.get("sender_email", "").strip()
    app_password  = config.get("app_password", "").strip()
    sender_name   = config.get("sender_name", config.get("business_name", "")).strip()

    # ── Gather recipient info ────────────────────────────────────────────────
    client_email  = invoice_data.get("client_email", "").strip()
    client_name   = invoice_data.get("client_name", "Client")
    invoice_number = invoice_data.get("invoice_number", "")
    description   = invoice_data.get("description", "")
    total_payable = invoice_data.get("total_payable", 0)
    due_date      = invoice_data.get("due_date", "")

    # Payment details for body
    upi_id    = invoice_data.get("upi_id", config.get("upi_id", ""))
    account_no = invoice_data.get("account_no", config.get("account_no", ""))
    ifsc_code = invoice_data.get("ifsc_code", config.get("ifsc_code", ""))

    # ── Basic validation ─────────────────────────────────────────────────────
    if not sender_email or sender_email == "your@gmail.com":
        return False, "Sender email is not configured. Please update 'sender_email' in config.json."

    if not app_password or app_password == "your_gmail_app_password":
        return False, "Gmail App Password is not set. Please update 'app_password' in config.json."

    if not client_email:
        return False, "Client email address is missing. Please fill in the Client Email field."

    if not os.path.exists(pdf_path):
        return False, f"PDF file not found at: {pdf_path}"

    # ── Build email subject & body ───────────────────────────────────────────
    subject = f"Invoice {invoice_number} from {sender_name}"

    body = (
        f"Hi {client_name},\n\n"
        f"Please find your invoice {invoice_number} attached for {description}.\n\n"
        f"Amount Due: \u20b9{total_payable:,.2f}\n"
        f"Due Date: {due_date}\n\n"
        f"Payment Details:\n"
        f"  UPI ID     : {upi_id}\n"
        f"  Account No : {account_no}\n"
        f"  IFSC Code  : {ifsc_code}\n\n"
        f"Thank you for your business.\n\n"
        f"{sender_name}"
    )

    # ── Compose the MIME message ─────────────────────────────────────────────
    msg = MIMEMultipart()
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = client_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Attach the PDF
    with open(pdf_path, "rb") as pdf_file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(pdf_file.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{os.path.basename(pdf_path)}"'
    )
    msg.attach(part)

    # ── Send via Gmail SMTP (TLS on port 587) ────────────────────────────────
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()          # Upgrade to TLS
            server.ehlo()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, client_email, msg.as_string())

        return True, f"Invoice sent successfully to {client_email}"

    except smtplib.SMTPAuthenticationError:
        return False, (
            "Authentication failed.\n"
            "Make sure you are using a Gmail App Password (not your real Gmail password).\n"
            "See '_email_instructions' in config.json for setup steps."
        )
    except smtplib.SMTPException as e:
        return False, f"SMTP error while sending email: {e}"
    except TimeoutError:
        return False, "Connection timed out. Check your internet connection and try again."
    except Exception as e:
        return False, f"Unexpected error: {e}"
