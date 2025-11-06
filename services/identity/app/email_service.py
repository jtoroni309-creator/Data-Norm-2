"""
Email service for sending user invitations and notifications

Supports:
- SendGrid
- AWS SES
- SMTP (generic)
"""

import logging
import os
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Optional dependencies (install based on provider)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    import boto3
    AWS_SES_AVAILABLE = True
except ImportError:
    AWS_SES_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmailService:
    """
    Unified email service supporting multiple providers

    Configuration via environment variables:
    - EMAIL_PROVIDER: sendgrid|aws_ses|smtp (default: smtp)
    - EMAIL_FROM: sender email address
    - EMAIL_FROM_NAME: sender display name

    SendGrid:
    - SENDGRID_API_KEY: API key

    AWS SES:
    - AWS_ACCESS_KEY_ID: AWS access key
    - AWS_SECRET_ACCESS_KEY: AWS secret key
    - AWS_REGION: AWS region (default: us-east-1)

    SMTP:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP server port (default: 587)
    - SMTP_USERNAME: SMTP username
    - SMTP_PASSWORD: SMTP password
    - SMTP_USE_TLS: Use TLS (default: true)
    """

    def __init__(self):
        self.provider = os.getenv("EMAIL_PROVIDER", "smtp").lower()
        self.from_email = os.getenv("EMAIL_FROM", "noreply@aura-audit.ai")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Aura Audit AI")

        # Validate configuration
        if self.provider == "sendgrid" and not SENDGRID_AVAILABLE:
            raise ImportError("SendGrid SDK not installed. Install with: pip install sendgrid")
        if self.provider == "aws_ses" and not AWS_SES_AVAILABLE:
            raise ImportError("Boto3 not installed. Install with: pip install boto3")

        logger.info(f"EmailService initialized with provider: {self.provider}")

    async def send_invitation_email(
        self,
        to_email: str,
        to_name: str,
        invitation_token: str,
        invited_by: str,
        organization_name: str,
        role: str
    ) -> bool:
        """
        Send user invitation email

        Args:
            to_email: Recipient email
            to_name: Recipient name
            invitation_token: Unique invitation token
            invited_by: Name of person who invited
            organization_name: Organization name
            role: User role

        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate invitation URL
        app_url = os.getenv("APP_URL", "http://localhost:3000")
        invitation_url = f"{app_url}/register?token={invitation_token}"

        # Email subject
        subject = f"You've been invited to join {organization_name} on Aura Audit AI"

        # HTML email body
        html_body = self._generate_invitation_html(
            to_name=to_name,
            invitation_url=invitation_url,
            invited_by=invited_by,
            organization_name=organization_name,
            role=role
        )

        # Plain text fallback
        text_body = f"""
Hello {to_name},

You've been invited by {invited_by} to join {organization_name} as a {role} on Aura Audit AI.

To accept the invitation and create your account, please click the link below:

{invitation_url}

This invitation will expire in 7 days.

If you have any questions, please contact {invited_by} or our support team at support@aura-audit.ai.

Best regards,
Aura Audit AI Team
"""

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send email using configured provider

        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if self.provider == "sendgrid":
                return await self._send_via_sendgrid(to_email, subject, html_body, text_body)
            elif self.provider == "aws_ses":
                return await self._send_via_aws_ses(to_email, subject, html_body, text_body)
            elif self.provider == "smtp":
                return await self._send_via_smtp(to_email, subject, html_body, text_body)
            else:
                logger.error(f"Unknown email provider: {self.provider}")
                return False

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def _send_via_sendgrid(
        self, to_email: str, subject: str, html_body: str, text_body: Optional[str]
    ) -> bool:
        """Send email via SendGrid"""
        try:
            api_key = os.getenv("SENDGRID_API_KEY")
            if not api_key:
                logger.error("SENDGRID_API_KEY not configured")
                return False

            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=to_email,
                subject=subject,
                html_content=html_body,
                plain_text_content=text_body or ""
            )

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)

            logger.info(f"Email sent via SendGrid to {to_email}, status: {response.status_code}")
            return response.status_code in [200, 202]

        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False

    async def _send_via_aws_ses(
        self, to_email: str, subject: str, html_body: str, text_body: Optional[str]
    ) -> bool:
        """Send email via AWS SES"""
        try:
            region = os.getenv("AWS_REGION", "us-east-1")
            ses_client = boto3.client('ses', region_name=region)

            response = ses_client.send_email(
                Source=f"{self.from_name} <{self.from_email}>",
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                        'Text': {'Data': text_body or "", 'Charset': 'UTF-8'}
                    }
                }
            )

            logger.info(f"Email sent via AWS SES to {to_email}, MessageId: {response['MessageId']}")
            return True

        except Exception as e:
            logger.error(f"AWS SES error: {e}")
            return False

    async def _send_via_smtp(
        self, to_email: str, subject: str, html_body: str, text_body: Optional[str]
    ) -> bool:
        """Send email via SMTP"""
        try:
            smtp_host = os.getenv("SMTP_HOST", "localhost")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Attach parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)

            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_use_tls:
                    server.starttls()

                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)

                server.send_message(msg)

            logger.info(f"Email sent via SMTP to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False

    def _generate_invitation_html(
        self,
        to_name: str,
        invitation_url: str,
        invited_by: str,
        organization_name: str,
        role: str
    ) -> str:
        """Generate HTML email template for invitation"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invitation to Aura Audit AI</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e0e0e0;
            border-top: none;
        }}
        .button {{
            display: inline-block;
            padding: 14px 32px;
            background: #667eea;
            color: white !important;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-radius: 0 0 8px 8px;
        }}
        .info-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin: 0;">Aura Audit AI</h1>
        <p style="margin: 10px 0 0 0;">You've been invited!</p>
    </div>

    <div class="content">
        <h2>Hello {to_name},</h2>

        <p><strong>{invited_by}</strong> has invited you to join <strong>{organization_name}</strong> on Aura Audit AI as a <strong>{role}</strong>.</p>

        <p>Aura Audit AI is an enterprise-grade audit platform designed for CPA firms, featuring:</p>
        <ul>
            <li>AI-powered compliance checking (PCAOB, GAAP, GAAS, SEC, AICPA)</li>
            <li>Automated workpaper generation</li>
            <li>Comprehensive audit workflow management</li>
            <li>SOC 2 compliant security</li>
        </ul>

        <div style="text-align: center;">
            <a href="{invitation_url}" class="button">Accept Invitation & Create Account</a>
        </div>

        <div class="info-box">
            <strong>⏰ This invitation expires in 7 days</strong>
        </div>

        <p>If you have any questions, please contact {invited_by} or our support team at <a href="mailto:support@aura-audit.ai">support@aura-audit.ai</a>.</p>

        <p>Best regards,<br>
        <strong>Aura Audit AI Team</strong></p>
    </div>

    <div class="footer">
        <p>This email was sent to {to_name} ({to_email}).</p>
        <p>If you didn't expect this invitation, you can safely ignore this email.</p>
        <p>&copy; 2025 Aura Audit AI. All rights reserved.</p>
    </div>
</body>
</html>
"""


# Singleton instance
_email_service_instance = None


def get_email_service() -> EmailService:
    """Get or create EmailService singleton"""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
