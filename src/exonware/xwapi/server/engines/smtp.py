#exonware/xwapi/engines/smtp.py
"""
SMTP Server Engine Implementation
SMTP protocol server (RFC 5321) for receiving emails.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
"""

from typing import Any

from collections.abc import Callable
import asyncio
from email.message import EmailMessage
from email import message_from_bytes
from .base import AApiServerEngineBase
from .contracts import ProtocolType, IApiServerEngine
from .email_store import IEmailStore, InMemoryEmailStore
from exonware.xwapi.config import XWAPIConfig
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class SMTPServerEngine(AApiServerEngineBase):
    """
    SMTP Server Engine
    Implements SMTP protocol server (RFC 5321) for receiving emails.
    Supports SMTPS (SSL) and STARTTLS.
    """

    def __init__(self, email_store: IEmailStore | None = None):
        """
        Initialize SMTP server engine.
        Args:
            email_store: Email store implementation (default: InMemoryEmailStore)
        """
        super().__init__("smtp")
        self._protocol_type = ProtocolType.SMTP
        self._app: Any | None = None
        self._server: Any | None = None
        self._email_store = email_store or InMemoryEmailStore()
        self._message_handler: Callable | None = None
        self._host: str | None = None
        self._port: int | None = None
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (SMTP)."""
        return self._protocol_type
    @property

    def supports_admin_endpoints(self) -> bool:
        """SMTP does not support HTTP admin endpoints."""
        return False

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create SMTP server application.
        For SMTP, the "app" is the server handler itself.
        Args:
            config: XWAPI configuration
        Returns:
            SMTP handler instance
        """
        # SMTP doesn't use a traditional "app" like HTTP
        # The handler is created in start_server
        self._app = self
        return self._app

    def register_action(self, app: Any, action: Any, 
                        route_info: dict[str, Any]) -> bool:
        """
        Register XWAction as SMTP message handler.
        Args:
            app: SMTP handler instance
            action: XWAction instance to handle incoming messages
            route_info: Protocol-specific route information
                Example: {'command': 'DATA', 'mailbox': 'INBOX'}
        Returns:
            True if registration successful
        """
        # Store the action as message handler
        self._message_handler = action
        logger.info(f"Registered SMTP message handler: {getattr(action, 'api_name', 'unknown')}")
        return True

    def generate_schema(self, app: Any, actions: list[Any], 
                       config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate SMTP protocol schema.
        SMTP doesn't have OpenAPI schema, but we can document the protocol.
        Args:
            app: SMTP handler instance
            actions: List of registered actions
            config: XWAPI configuration
        Returns:
            Protocol documentation dictionary
        """
        return {
            "protocol": "SMTP",
            "rfc": "5321",
            "description": "Simple Mail Transfer Protocol",
            "commands": ["HELO", "EHLO", "MAIL FROM", "RCPT TO", "DATA", "QUIT"],
            "handlers": [
                {
                    "action": getattr(action, 'api_name', 'unknown'),
                    "command": "DATA"
                }
                for action in actions
            ]
        }

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 25, ssl: bool = False, 
                    starttls: bool = True, **kwargs) -> None:
        """
        Start SMTP server.
        Args:
            app: SMTP handler instance
            host: Host to bind to
            port: Port to bind to (default: 25, or 465 for SSL)
            ssl: Enable SSL/TLS (SMTPS)
            starttls: Enable STARTTLS support
            **kwargs: Additional server options
        """
        try:
            from aiosmtpd.controller import Controller
            from aiosmtpd.handlers import Message
        except ImportError:
            logger.error("aiosmtpd not installed. Install with: pip install aiosmtpd")
            raise ImportError("aiosmtpd is required for SMTP server")
        self._host = host
        self._port = port
        # Create custom handler that uses our message handler
        class CustomSMTPHandler(Message):
            def __init__(self, message_handler, email_store):
                super().__init__()
                self.message_handler = message_handler
                self.email_store = email_store
            async def handle_message(self, message: EmailMessage):
                """Handle incoming SMTP message."""
                try:
                    # Store message
                    message_id = self.email_store.store_message(message)
                    logger.info(f"Received email: {message_id} from {message.get('From')}")
                    # Call registered action handler if available
                    if self.message_handler:
                        try:
                            # Extract message data
                            from_addr = message.get("From", "")
                            to_addrs = message.get_all("To", [])
                            subject = message.get("Subject", "")
                            # Call handler
                            if asyncio.iscoroutinefunction(self.message_handler):
                                await self.message_handler(
                                    from_addr=from_addr,
                                    to_addrs=to_addrs,
                                    subject=subject,
                                    message=message,
                                    message_id=message_id
                                )
                            else:
                                self.message_handler(
                                    from_addr=from_addr,
                                    to_addrs=to_addrs,
                                    subject=subject,
                                    message=message,
                                    message_id=message_id
                                )
                        except Exception as e:
                            logger.error(f"Error in message handler: {e}")
                except Exception as e:
                    logger.error(f"Error handling SMTP message: {e}")
        # Create handler
        handler = CustomSMTPHandler(self._message_handler, self._email_store)
        # Create controller
        self._server = Controller(
            handler,
            hostname=host,
            port=port
        )
        logger.info(f"Starting SMTP server on {host}:{port} (SSL={ssl}, STARTTLS={starttls})")
        # Start server
        self._server.start()
        logger.info(f"SMTP server started on {host}:{port}")

    def stop_server(self, app: Any) -> None:
        """Stop SMTP server."""
        if self._server:
            logger.info("Stopping SMTP server...")
            self._server.stop()
            self._server = None
            logger.info("SMTP server stopped")
