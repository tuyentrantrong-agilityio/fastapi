"""Email service - handles sending emails via SendGrid API.

This service uses SendGrid's REST API for reliable email delivery.
SendGrid is chosen over SMTP because:
1. Railway Free tier blocks all SMTP ports (25, 465, 587, 2525)
2. SendGrid API uses HTTPS on port 443 (allowed on Railway)
3. Free tier: 100 emails/day
4. Industry standard for transactional emails
"""

import json
import logging
from typing import Optional

import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid API.

    SendGrid API Documentation:
    https://docs.sendgrid.com/for-developers/sending-email/quickstart-python

    Usage:
        email_svc = EmailService()
        success = await email_svc.send_email(
            to="user@example.com",
            subject="Welcome!",
            html_content="<h1>Hello</h1>"
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """Initialize SendGrid configuration.

        Args:
            api_key: SendGrid API key (format: SG.xxxxx) - defaults from settings
            from_email: Sender email address - defaults from settings
        """
        self.api_key = api_key or settings.SENDGRID_API_KEY
        self.from_email = from_email or settings.SENDGRID_FROM_EMAIL
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

        if not self.api_key:
            logger.warning(
                "⚠️  SENDGRID_API_KEY not configured! Email sending will fail. "
                "Set SENDGRID_API_KEY in environment variables."
            )
        else:
            logger.info("📧 Email service initialized with SendGrid API")

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """Send an email via SendGrid API.

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: Email body in HTML format
            plain_content: Email body in plain text (optional fallback)

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.api_key:
            logger.error("❌ Cannot send email: SENDGRID_API_KEY is not configured")
            return False

        try:
            # Build SendGrid API request payload
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to}],
                        "subject": subject,
                    }
                ],
                "from": {"email": self.from_email},
                "content": [
                    {
                        "type": "text/plain",
                        "value": plain_content or html_content.replace("<br>", "\n"),
                    },
                    {
                        "type": "text/html",
                        "value": html_content,
                    },
                ],
            }

            # Send via SendGrid API with httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )

            # Check if email was sent successfully (202 Accepted is success)
            if response.status_code == 202:
                logger.info(
                    f"✅ Email sent successfully to {to} with subject: {subject}"
                )
                return True
            else:
                # Log error response from SendGrid
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = json.dumps(error_data, indent=2)
                except Exception:
                    pass
                logger.error(
                    f"❌ SendGrid API error (status {response.status_code}) "
                    f"sending to {to}: {error_msg}"
                )
                return False

        except httpx.RequestError as e:
            logger.error(f"❌ SendGrid request error sending to {to}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email to {to}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
