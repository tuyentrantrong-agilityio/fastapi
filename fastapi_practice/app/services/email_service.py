"""Email service - handles sending emails via SMTP."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP.

    Usage:
        email_svc = EmailService()
        await email_svc.send_email(
            to="user@example.com",
            subject="Welcome!",
            html_content="<h1>Hello</h1>"
        )
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """Initialize SMTP configuration.

        Args:
            smtp_host: SMTP server hostname (defaults from settings)
            smtp_port: SMTP server port (typically 587 for TLS)
            smtp_user: SMTP authentication username (defaults from settings)
            smtp_password: SMTP authentication password (defaults from settings, spaces auto-removed)
            from_email: Sender email address (defaults from settings)
        """
        # Load from settings if not provided (always fresh!)
        self.smtp_host = smtp_host or settings.SMTP_HOST
        self.smtp_port = smtp_port or settings.SMTP_PORT
        self.smtp_user = smtp_user or settings.SMTP_USER
        # Auto-remove spaces from password (Google app passwords have spaces: xxxx xxxx xxxx xxxx)
        password = smtp_password or settings.SMTP_PASSWORD
        self.smtp_password = password.replace(" ", "") if password else ""
        self.from_email = from_email or settings.SMTP_FROM_EMAIL

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """Send an email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: Email body in HTML format
            plain_content: Email body in plain text (optional fallback)

        Returns:
            True if email sent successfully, False otherwise

        Note:
            This runs synchronously in thread pool (called via BackgroundTasks).
            For high volume, consider Celery + Redis in Phase 2.
        """
        try:
            # Create multi-part message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to

            # Attach plain text version (fallback)
            if plain_content:
                part_plain = MIMEText(plain_content, "plain")
                message.attach(part_plain)

            # Attach HTML version (preferred)
            part_html = MIMEText(html_content, "html")
            message.attach(part_html)

            # Send via SMTP (with 10s timeout to avoid hanging)
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()  # Use TLS encryption
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to, message.as_string())

            logger.info(f"Email sent successfully to {to} with subject: {subject}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
