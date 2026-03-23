from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from typing import Any, Dict


LOGO_PATH = Path(__file__).resolve().parents[2] / "frontend" / "src" / "assets" / "gabani_logo.png"


def _load_logo_base64() -> str:
    try:
        if LOGO_PATH.exists():
            return base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    except Exception:
        return ""
    return ""


LOGO_BASE64 = _load_logo_base64()


BRAND_HEADER = (
    "============================================================\n"
    "GABANI TRANSPORT SOLUTIONS\n"
    "Where Intelligence Meets Logistics\n"
    "============================================================"
)


def _with_branding(body: str, signature: str) -> str:
    return f"{BRAND_HEADER}\n\n{body}\n\n{signature}\nGabani Transport Solutions\nwww.gabanilogistics.com"


def _html_shell(
    *,
    title: str,
    greeting: str,
    intro: str,
    details_html: str = "",
    notice_html: str = "",
    action_url: str = "",
    action_label: str = "",
    signature: str,
) -> str:
    action_block = (
        f"""
        <tr>
            <td align="center" style="padding-top: 12px;">
                <a href="{escape(action_url, quote=True)}" style="display: inline-block; background: #1d4ed8; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">{escape(action_label)}</a>
            </td>
        </tr>
        """
        if action_url and action_label
        else ""
    )
    logo_block = (
        f'<img src="data:image/png;base64,{LOGO_BASE64}" alt="Gabani Transport Solutions" '
        'style="display:block;max-width:220px;width:100%;height:auto;margin:0 auto 14px auto;">'
        if LOGO_BASE64
        else ""
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f7fb;font-family:'Segoe UI',Tahoma,Verdana,sans-serif;color:#1f2937;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f7fb;padding:24px;">
    <tr>
      <td align="center">
        <table width="640" cellpadding="0" cellspacing="0" border="0" style="max-width:640px;background:#ffffff;border-radius:14px;overflow:hidden;">
          <tr>
            <td style="background:#0f172a;padding:28px 24px;text-align:center;">
              {logo_block}
              <div style="color:#ffffff;font-size:28px;font-weight:700;letter-spacing:0.04em;">GABANI TRANSPORT SOLUTIONS</div>
              <div style="color:#cbd5e1;font-size:14px;margin-top:8px;">Where Intelligence Meets Logistics</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px 28px;">
              <h1 style="margin:0 0 16px 0;font-size:26px;color:#111827;">{escape(title)}</h1>
              <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;">{greeting}</p>
              <p style="margin:0 0 22px 0;font-size:16px;line-height:1.6;">{intro}</p>
              {details_html}
              {notice_html}
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {action_block}
              </table>
            </td>
          </tr>
          <tr>
            <td style="border-top:1px solid #e5e7eb;background:#f8fafc;padding:22px 28px;text-align:center;">
              <div style="color:#334155;font-size:14px;font-weight:600;">{escape(signature)}</div>
              <div style="color:#64748b;font-size:13px;margin-top:6px;">Gabani Transport Solutions</div>
              <div style="color:#64748b;font-size:13px;margin-top:4px;"><a href="https://www.gabanilogistics.com" style="color:#1d4ed8;text-decoration:none;">www.gabanilogistics.com</a></div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


SECURITY_LOGIN_SUCCESS_HTML = _html_shell(
    title="Successful Login Detected",
    greeting="Hello <strong>{user_name}</strong>,",
    intro="A successful login to your GTS account was detected.",
    details_html="""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:18px;">
      <tr><td style="padding:18px 20px;">
        <div style="font-size:18px;font-weight:600;margin-bottom:12px;color:#111827;">Login Details</div>
        <div style="font-size:14px;line-height:1.8;color:#374151;">
          <strong>User:</strong> {user_email}<br>
          <strong>Time:</strong> {timestamp}<br>
          <strong>IP Address:</strong> {ip_address}<br>
          <strong>Device:</strong> {device}
        </div>
      </td></tr>
    </table>
    """,
    notice_html="""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;margin-bottom:18px;">
      <tr><td style="padding:18px 20px;font-size:14px;line-height:1.7;color:#9a3412;">
        If this was not you, change your password immediately. If this was you, no further action is required.
      </td></tr>
    </table>
    """,
    action_url="https://www.gabanilogistics.com/account/security",
    action_label="Review Account Security",
    signature="GTS Security Team",
)


SHIPMENT_CREATED_HTML = _html_shell(
    title="New Shipment Created",
    greeting="Hello <strong>{user_name}</strong>,",
    intro="A new shipment has been created and is now available for tracking.",
    details_html="""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:18px;">
      <tr><td style="padding:18px 20px;font-size:14px;line-height:1.8;color:#374151;">
        <strong>Shipment ID:</strong> {shipment_id}<br>
        <strong>Origin:</strong> {origin}<br>
        <strong>Destination:</strong> {destination}<br>
        <strong>Estimated Delivery:</strong> {estimated_delivery}
      </td></tr>
    </table>
    """,
    action_url="{tracking_url}",
    action_label="Track Shipment",
    signature="GTS Logistics Team",
)


FINANCE_INVOICE_CREATED_HTML = _html_shell(
    title="New Invoice Created",
    greeting="Hello <strong>{user_name}</strong>,",
    intro="A new invoice has been created in your account.",
    details_html="""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:18px;">
      <tr><td style="padding:18px 20px;font-size:14px;line-height:1.8;color:#374151;">
        <strong>Invoice Number:</strong> {invoice_number}<br>
        <strong>Amount:</strong> {amount} {currency}<br>
        <strong>Due Date:</strong> {due_date}<br>
        <strong>Customer:</strong> {customer_name}
      </td></tr>
    </table>
    """,
    action_url="{invoice_url}",
    action_label="View Invoice",
    signature="GTS Finance Team",
)


DOCUMENT_UPLOADED_HTML = _html_shell(
    title="New Document Uploaded",
    greeting="Hello <strong>{user_name}</strong>,",
    intro="A new document was uploaded to your account.",
    details_html="""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:18px;">
      <tr><td style="padding:18px 20px;font-size:14px;line-height:1.8;color:#374151;">
        <strong>Document:</strong> {document_name}<br>
        <strong>Type:</strong> {document_type}<br>
        <strong>Uploaded By:</strong> {uploaded_by}<br>
        <strong>Size:</strong> {file_size}
      </td></tr>
    </table>
    """,
    action_url="{document_url}",
    action_label="View Document",
    signature="GTS Documents Team",
)


SAFETY_INCIDENT_REPORTED_HTML = _html_shell(
    title="Safety Incident Reported",
    greeting="Hello <strong>{user_name}</strong>,",
    intro="A safety incident has been reported and requires review.",
    details_html="""
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:18px;">
      <tr><td style="padding:18px 20px;font-size:14px;line-height:1.8;color:#374151;">
        <strong>Incident ID:</strong> {incident_id}<br>
        <strong>Type:</strong> {incident_type}<br>
        <strong>Location:</strong> {location}<br>
        <strong>Severity:</strong> {severity}<br>
        <strong>Reported By:</strong> {reported_by}
      </td></tr>
    </table>
    """,
    action_url="{incident_url}",
    action_label="View Incident",
    signature="GTS Safety Team",
)


NOTIFICATION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "security_login_success": {
        "subject": "Successful Login - GTS Platform",
        "html_template": SECURITY_LOGIN_SUCCESS_HTML,
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A successful login to your GTS account was detected.\n"
            "Time: {timestamp}\n"
            "IP Address: {ip_address}\n"
            "Device: {device}\n\n"
            "If this was not you, change your password immediately.\n\n"
            "Review your account security if anything looks unfamiliar.",
            "GTS Security Team",
        ),
    },
    "security_login_failed": {
        "subject": "Failed Login Attempt - GTS Platform",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A failed login attempt was detected for your account.\n"
            "Time: {timestamp}\n"
            "IP Address: {ip_address}\n"
            "Attempts: {attempt_count}\n\n"
            "If this was not you, review your account security immediately.\n\n"
            "Consider changing your password if failed attempts continue.",
            "GTS Security Team",
        ),
    },
    "security_password_changed": {
        "subject": "Password Changed - GTS Platform",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Your account password was changed.\n"
            "Time: {timestamp}\n"
            "IP Address: {ip_address}\n\n"
            "If you did not make this change, contact support immediately.\n\n"
            "This notice is for your security records.",
            "GTS Security Team",
        ),
    },
    "security_logout": {
        "subject": "Logout Notice - GTS Platform",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Your session was logged out.\n"
            "Time: {timestamp}\n"
            "Reason: {reason}\n\n"
            "No action is required if this logout was expected.",
            "GTS Security Team",
        ),
    },
    "finance_invoice_created": {
        "subject": "New Invoice Created - #{invoice_number}",
        "html_template": FINANCE_INVOICE_CREATED_HTML,
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A new invoice was created.\n"
            "Invoice Number: {invoice_number}\n"
            "Amount: {amount} {currency}\n"
            "Due Date: {due_date}\n"
            "Customer: {customer_name}\n"
            "View Invoice: {invoice_url}\n\n"
            "Please review the invoice details at your earliest convenience.",
            "GTS Finance Team",
        ),
    },
    "finance_invoice_paid": {
        "subject": "Invoice Paid - #{invoice_number}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Invoice #{invoice_number} has been marked as paid.\n"
            "Amount: {amount} {currency}\n"
            "Payment Date: {payment_date}\n"
            "Payment Method: {payment_method}\n"
            "Receipt: {receipt_url}\n\n"
            "Thank you for your payment.",
            "GTS Finance Team",
        ),
    },
    "finance_invoice_overdue": {
        "subject": "Invoice Overdue - #{invoice_number}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Invoice #{invoice_number} is now overdue.\n"
            "Amount: {amount} {currency}\n"
            "Original Due Date: {due_date}\n"
            "Days Overdue: {days_overdue}\n\n"
            "Please arrange payment as soon as possible.",
            "GTS Finance Team",
        ),
    },
    "document_uploaded": {
        "subject": "New Document Uploaded - {document_name}",
        "html_template": DOCUMENT_UPLOADED_HTML,
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A new document was uploaded.\n"
            "Document: {document_name}\n"
            "Type: {document_type}\n"
            "Uploaded By: {uploaded_by}\n"
            "Size: {file_size}\n"
            "View Document: {document_url}\n\n"
            "Please review the uploaded file if action is required.",
            "GTS Documents Team",
        ),
    },
    "document_expiring_soon": {
        "subject": "Document Expiring Soon - {document_name}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "The following document will expire soon.\n"
            "Document: {document_name}\n"
            "Expiry Date: {expiry_date}\n"
            "Days Remaining: {days_remaining}\n\n"
            "Upload an updated version before the expiry date.",
            "GTS Documents Team",
        ),
    },
    "document_signed": {
        "subject": "Document Signed - {document_name}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A document was signed.\n"
            "Document: {document_name}\n"
            "Signed By: {signed_by}\n"
            "Date: {signature_date}\n"
            "Method: {signature_method}\n"
            "View Signed Document: {document_url}\n\n"
            "The signed document is now available for review.",
            "GTS Documents Team",
        ),
    },
    "shipment_created": {
        "subject": "New Shipment Created - #{shipment_id}",
        "html_template": SHIPMENT_CREATED_HTML,
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A new shipment was created.\n"
            "Shipment ID: {shipment_id}\n"
            "Origin: {origin}\n"
            "Destination: {destination}\n"
            "Estimated Delivery: {estimated_delivery}\n"
            "Track Shipment: {tracking_url}\n\n"
            "Tracking is now available for this shipment.",
            "GTS Logistics Team",
        ),
    },
    "shipment_driver_assigned": {
        "subject": "Driver Assigned - Shipment #{shipment_id}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A driver has been assigned to your shipment.\n"
            "Shipment ID: {shipment_id}\n"
            "Driver: {driver_name}\n"
            "Contact: {driver_phone}\n"
            "Vehicle: {vehicle_plate}\n"
            "Track Shipment: {tracking_url}\n\n"
            "Use the tracking link for live shipment visibility.",
            "GTS Logistics Team",
        ),
    },
    "shipment_status_changed": {
        "subject": "Shipment Status Updated - #{shipment_id}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "The status of your shipment has changed.\n"
            "Shipment ID: {shipment_id}\n"
            "New Status: {new_status}\n"
            "Location: {current_location}\n"
            "Estimated Delivery: {estimated_delivery}\n"
            "Track Shipment: {tracking_url}\n\n"
            "Check tracking for the latest movement details.",
            "GTS Logistics Team",
        ),
    },
    "shipment_delayed": {
        "subject": "Shipment Delayed - #{shipment_id}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Your shipment is delayed.\n"
            "Shipment ID: {shipment_id}\n"
            "Reason: {delay_reason}\n"
            "New Estimated Delivery: {new_eta}\n"
            "Track Shipment: {tracking_url}\n\n"
            "We apologize for the delay and are monitoring the shipment closely.",
            "GTS Logistics Team",
        ),
    },
    "shipment_delivered": {
        "subject": "Shipment Delivered - #{shipment_id}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Your shipment was delivered successfully.\n"
            "Shipment ID: {shipment_id}\n"
            "Delivery Time: {delivery_time}\n"
            "Signed By: {recipient_name}\n"
            "Confirmation: {confirmation_url}\n\n"
            "Thank you for choosing GTS.",
            "GTS Logistics Team",
        ),
    },
    "safety_incident_reported": {
        "subject": "Safety Incident Reported - #{incident_id}",
        "html_template": SAFETY_INCIDENT_REPORTED_HTML,
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A safety incident was reported.\n"
            "Incident ID: {incident_id}\n"
            "Type: {incident_type}\n"
            "Location: {location}\n"
            "Severity: {severity}\n"
            "Reported By: {reported_by}\n"
            "View Details: {incident_url}\n\n"
            "Review the incident details and required follow-up actions.",
            "GTS Safety Team",
        ),
    },
    "safety_violation_detected": {
        "subject": "Safety Violation Detected",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "A safety violation was detected.\n"
            "Driver: {driver_name}\n"
            "Vehicle: {vehicle_plate}\n"
            "Violation: {violation_type}\n"
            "Time: {timestamp}\n"
            "Location: {location}\n\n"
            "Please review and address this violation promptly.",
            "GTS Safety Team",
        ),
    },
    "safety_maintenance_reminder": {
        "subject": "Maintenance Reminder - {vehicle_plate}",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "Vehicle maintenance is due.\n"
            "Vehicle: {vehicle_plate}\n"
            "Maintenance Type: {maintenance_type}\n"
            "Due Date: {due_date}\n"
            "Current Mileage: {current_mileage}\n"
            "Recommended By: {recommended_by}\n\n"
            "Schedule maintenance as soon as possible.",
            "GTS Safety Team",
        ),
    },
    "system_alert": {
        "subject": "GTS System Alert",
        "template": _with_branding(
            "Hello {user_name},\n\n"
            "{message}",
            "GTS Platform",
        ),
    },
}
