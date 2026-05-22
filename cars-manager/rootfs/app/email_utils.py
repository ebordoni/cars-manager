import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

OPTIONS_FILE = "/data/options.json"


def get_addon_config():
    """Load the addon options written by Home Assistant."""
    try:
        with open(OPTIONS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def send_quote_email(to_email: str, subject: str, body: str) -> None:
    """Send an email using the SMTP settings from addon options.

    Raises:
        ValueError: if SMTP is not configured.
        RuntimeError: if sending fails.
    """
    cfg = get_addon_config()
    smtp_server = cfg.get("smtp_server") or os.environ.get("SMTP_SERVER", "")
    smtp_port = int(cfg.get("smtp_port") or os.environ.get("SMTP_PORT", 587))
    smtp_username = cfg.get("smtp_username") or os.environ.get("SMTP_USERNAME", "")
    smtp_password = cfg.get("smtp_password") or os.environ.get("SMTP_PASSWORD", "")
    smtp_from = cfg.get("smtp_from") or os.environ.get("SMTP_FROM", smtp_username)
    smtp_use_tls_raw = cfg.get("smtp_use_tls")
    if smtp_use_tls_raw is None:
        smtp_use_tls_raw = os.environ.get("SMTP_USE_TLS", "true")
    smtp_use_tls = str(smtp_use_tls_raw).lower() not in ("false", "0", "no")

    if not smtp_server or not smtp_username:
        raise ValueError(
            "SMTP non configurato. Imposta i parametri SMTP nelle opzioni dell'addon."
        )

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if smtp_use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_from, to_email, msg.as_string())
        else:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                server.ehlo()
                if smtp_username:
                    server.login(smtp_username, smtp_password)
                server.sendmail(smtp_from, to_email, msg.as_string())
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"Errore invio email: {exc}") from exc
