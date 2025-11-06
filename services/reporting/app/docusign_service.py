"""DocuSign e-signature integration service"""
import logging
import base64
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from docusign_esign import (
    ApiClient,
    EnvelopesApi,
    EnvelopeDefinition,
    Document,
    Signer,
    SignHere,
    Tabs,
    Recipients,
    CarbonCopy
)
from docusign_esign.client.api_exception import ApiException

from .config import settings
from .schemas import SignerInfo

logger = logging.getLogger(__name__)


class DocuSignService:
    """Service for DocuSign e-signature integration"""

    def __init__(self):
        self.api_client: Optional[ApiClient] = None
        self.account_id = settings.DOCUSIGN_ACCOUNT_ID

    def _get_api_client(self) -> ApiClient:
        """Get authenticated DocuSign API client"""
        if self.api_client is None:
            self.api_client = ApiClient()
            self.api_client.set_base_path(settings.DOCUSIGN_BASE_PATH)

            # TODO: Implement JWT authentication
            # For now, this is a placeholder for the authentication flow
            # In production, you would use JWT authentication with RSA keys

            logger.info("DocuSign API client initialized")

        return self.api_client

    async def create_envelope(
        self,
        document_bytes: bytes,
        document_name: str,
        subject: str,
        message: str,
        signers: List[SignerInfo],
        expires_in_days: int = 30,
        send_immediately: bool = True
    ) -> Dict[str, Any]:
        """
        Create DocuSign envelope with document and signers

        Args:
            document_bytes: PDF document to sign
            document_name: Name of the document
            subject: Email subject
            message: Email message
            signers: List of signers
            expires_in_days: Days until envelope expires
            send_immediately: Send envelope immediately or save as draft

        Returns:
            Dict with envelope_id and status
        """
        logger.info(f"Creating DocuSign envelope: {subject}")

        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            # Create document
            document = Document(
                document_base64=base64.b64encode(document_bytes).decode('utf-8'),
                name=document_name,
                file_extension='pdf',
                document_id='1'
            )

            # Create signers
            envelope_signers = []
            for signer_info in signers:
                # Define signature tabs
                sign_here_tab = SignHere(
                    anchor_string='/sig1/',  # Anchor for signature placement
                    anchor_units='pixels',
                    anchor_y_offset='10',
                    anchor_x_offset='20'
                )

                tabs = Tabs(sign_here_tabs=[sign_here_tab])

                signer = Signer(
                    email=signer_info.email,
                    name=signer_info.name,
                    recipient_id=str(signer_info.routing_order),
                    routing_order=str(signer_info.routing_order),
                    tabs=tabs
                )

                if signer_info.client_user_id:
                    signer.client_user_id = signer_info.client_user_id

                envelope_signers.append(signer)

            # Create recipients
            recipients = Recipients(signers=envelope_signers)

            # Create envelope definition
            envelope_definition = EnvelopeDefinition(
                email_subject=subject,
                email_blurb=message,
                documents=[document],
                recipients=recipients,
                status='sent' if send_immediately else 'created'
            )

            # Set expiration
            if expires_in_days:
                expire_date = datetime.now() + timedelta(days=expires_in_days)
                envelope_definition.notification = {
                    'expirations': {
                        'expire_enabled': 'true',
                        'expire_after': str(expires_in_days),
                        'expire_warn': str(max(1, expires_in_days - 3))
                    }
                }

            # Create envelope
            result = envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition
            )

            envelope_id = result.envelope_id
            status = result.status

            logger.info(f"Envelope created: {envelope_id} (status: {status})")

            return {
                'envelope_id': envelope_id,
                'status': status,
                'uri': result.uri if hasattr(result, 'uri') else None
            }

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}", exc_info=True)
            raise ValueError(f"DocuSign envelope creation failed: {e.body}")

        except Exception as e:
            logger.error(f"Envelope creation failed: {e}", exc_info=True)
            raise

    async def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """
        Get status of envelope

        Args:
            envelope_id: DocuSign envelope ID

        Returns:
            Dict with envelope status information
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            envelope = envelopes_api.get_envelope(
                account_id=self.account_id,
                envelope_id=envelope_id
            )

            return {
                'envelope_id': envelope_id,
                'status': envelope.status,
                'created_date': envelope.created_date_time,
                'sent_date': envelope.sent_date_time,
                'delivered_date': envelope.delivered_date_time,
                'completed_date': envelope.completed_date_time,
                'voided_date': envelope.voided_date_time,
                'voided_reason': envelope.voided_reason
            }

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to get envelope status: {e.body}")

    async def get_envelope_recipients(self, envelope_id: str) -> List[Dict[str, Any]]:
        """
        Get recipients and their signing status

        Args:
            envelope_id: DocuSign envelope ID

        Returns:
            List of recipient information
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            recipients = envelopes_api.list_recipients(
                account_id=self.account_id,
                envelope_id=envelope_id
            )

            recipient_list = []

            # Process signers
            if recipients.signers:
                for signer in recipients.signers:
                    recipient_list.append({
                        'recipient_id': signer.recipient_id,
                        'name': signer.name,
                        'email': signer.email,
                        'role': 'signer',
                        'status': signer.status,
                        'signed_date': signer.signed_date_time,
                        'delivered_date': signer.delivered_date_time
                    })

            # Process carbon copies
            if recipients.carbon_copies:
                for cc in recipients.carbon_copies:
                    recipient_list.append({
                        'recipient_id': cc.recipient_id,
                        'name': cc.name,
                        'email': cc.email,
                        'role': 'cc',
                        'status': cc.status
                    })

            return recipient_list

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to get envelope recipients: {e.body}")

    async def download_signed_document(self, envelope_id: str, document_id: str = '1') -> bytes:
        """
        Download signed document from envelope

        Args:
            envelope_id: DocuSign envelope ID
            document_id: Document ID within envelope

        Returns:
            Signed document as bytes
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            document = envelopes_api.get_document(
                account_id=self.account_id,
                envelope_id=envelope_id,
                document_id=document_id
            )

            logger.info(f"Downloaded signed document: {envelope_id}/{document_id}")

            return document

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to download document: {e.body}")

    async def download_certificate(self, envelope_id: str) -> bytes:
        """
        Download certificate of completion

        Args:
            envelope_id: DocuSign envelope ID

        Returns:
            Certificate as bytes
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            certificate = envelopes_api.get_document(
                account_id=self.account_id,
                envelope_id=envelope_id,
                document_id='certificate'
            )

            logger.info(f"Downloaded certificate: {envelope_id}")

            return certificate

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to download certificate: {e.body}")

    async def void_envelope(self, envelope_id: str, reason: str) -> bool:
        """
        Void an envelope

        Args:
            envelope_id: DocuSign envelope ID
            reason: Reason for voiding

        Returns:
            True if successful
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            envelope_definition = EnvelopeDefinition(
                status='voided',
                voided_reason=reason
            )

            envelopes_api.update(
                account_id=self.account_id,
                envelope_id=envelope_id,
                envelope=envelope_definition
            )

            logger.info(f"Voided envelope: {envelope_id} (reason: {reason})")

            return True

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to void envelope: {e.body}")

    async def resend_envelope(self, envelope_id: str) -> bool:
        """
        Resend envelope notification to recipients

        Args:
            envelope_id: DocuSign envelope ID

        Returns:
            True if successful
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            # Update envelope to resend
            envelope_definition = EnvelopeDefinition(
                resend_envelope='true'
            )

            envelopes_api.update(
                account_id=self.account_id,
                envelope_id=envelope_id,
                envelope=envelope_definition
            )

            logger.info(f"Resent envelope: {envelope_id}")

            return True

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to resend envelope: {e.body}")

    def get_embedded_signing_url(
        self,
        envelope_id: str,
        signer_email: str,
        signer_name: str,
        return_url: str,
        client_user_id: str
    ) -> str:
        """
        Get URL for embedded signing (signing within your application)

        Args:
            envelope_id: DocuSign envelope ID
            signer_email: Signer email
            signer_name: Signer name
            return_url: URL to return to after signing
            client_user_id: Unique client user ID

        Returns:
            Signing URL
        """
        try:
            api_client = self._get_api_client()
            envelopes_api = EnvelopesApi(api_client)

            recipient_view_request = {
                'return_url': return_url,
                'authentication_method': 'none',
                'email': signer_email,
                'user_name': signer_name,
                'client_user_id': client_user_id
            }

            result = envelopes_api.create_recipient_view(
                account_id=self.account_id,
                envelope_id=envelope_id,
                recipient_view_request=recipient_view_request
            )

            return result.url

        except ApiException as e:
            logger.error(f"DocuSign API error: {e}")
            raise ValueError(f"Failed to get signing URL: {e.body}")


# Global DocuSign service instance
docusign_service = DocuSignService()
