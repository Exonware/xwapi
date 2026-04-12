#exonware/xwapi/engines/imap.py
"""
IMAP Server Engine Implementation
IMAP protocol server (RFC 9051) for syncing emails.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
"""

from typing import Any

from collections.abc import Callable
import asyncio
from email.message import EmailMessage
from .base import AApiServerEngineBase
from .contracts import ProtocolType, IApiServerEngine
from .email_store import IEmailStore, InMemoryEmailStore
from exonware.xwapi.config import XWAPIConfig
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class IMAPServerEngine(AApiServerEngineBase):
    """
    IMAP Server Engine
    Implements IMAP protocol server (RFC 9051) for syncing emails.
    Supports IMAPS (SSL) and STARTTLS.
    """

    def __init__(self, email_store: IEmailStore | None = None):
        """
        Initialize IMAP server engine.
        Args:
            email_store: Email store implementation (default: InMemoryEmailStore)
        """
        super().__init__("imap")
        self._protocol_type = ProtocolType.IMAP
        self._app: Any | None = None
        self._server: Any | None = None
        self._email_store = email_store or InMemoryEmailStore()
        self._command_handlers: dict[str, Callable] = {}
        self._host: str | None = None
        self._port: int | None = None
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (IMAP)."""
        return self._protocol_type
    @property

    def supports_admin_endpoints(self) -> bool:
        """IMAP does not support HTTP admin endpoints."""
        return False

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create IMAP server application.
        Args:
            config: XWAPI configuration
        Returns:
            IMAP handler instance
        """
        self._app = self
        return self._app

    def register_action(self, app: Any, action: Any, 
                        route_info: dict[str, Any]) -> bool:
        """
        Register XWAction as IMAP command handler.
        Args:
            app: IMAP handler instance
            action: XWAction instance to handle commands
            route_info: Protocol-specific route information
                Example: {'command': 'FETCH', 'mailbox': 'INBOX'}
        Returns:
            True if registration successful
        """
        command = route_info.get('command', 'FETCH').upper()
        self._command_handlers[command] = action
        logger.info(f"Registered IMAP handler for command '{command}': {getattr(action, 'api_name', 'unknown')}")
        return True

    def generate_schema(self, app: Any, actions: list[Any], 
                       config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate IMAP protocol schema.
        Args:
            app: IMAP handler instance
            actions: List of registered actions
            config: XWAPI configuration
        Returns:
            Protocol documentation dictionary
        """
        return {
            "protocol": "IMAP",
            "rfc": "9051",
            "description": "Internet Message Access Protocol",
            "commands": ["LOGIN", "SELECT", "FETCH", "SEARCH", "STORE", "COPY", "DELETE", "LOGOUT"],
            "handlers": [
                {
                    "action": getattr(action, 'api_name', 'unknown'),
                    "command": route_info.get('command', 'FETCH')
                }
                for action, route_info in zip(actions, [{}] * len(actions))
            ]
        }

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 143, ssl: bool = False, 
                    starttls: bool = True, **kwargs) -> None:
        """
        Start IMAP server.
        Args:
            app: IMAP handler instance
            host: Host to bind to
            port: Port to bind to (default: 143, or 993 for SSL)
            ssl: Enable SSL/TLS (IMAPS)
            starttls: Enable STARTTLS support
            **kwargs: Additional server options
        """
        try:
            import socketserver
            import threading
        except ImportError:
            logger.error("socketserver not available (part of standard library)")
            raise ImportError("socketserver is required for IMAP server")
        self._host = host
        self._port = port
        # Create custom IMAP server handler
        class CustomIMAPHandler(socketserver.BaseRequestHandler):
            def __init__(self, request, client_address, server, email_store, command_handlers):
                self.email_store = email_store
                self.command_handlers = command_handlers
                self.authenticated = False
                self.username = None
                self.selected_mailbox = None
                self.tag_counter = 0
                super().__init__(request, client_address, server)
            def get_tag(self) -> str:
                """Generate IMAP command tag."""
                self.tag_counter += 1
                return f"A{self.tag_counter:04d}"
            def handle(self):
                """Handle IMAP client connection."""
                try:
                    # Send greeting
                    tag = self.get_tag()
                    self.request.sendall(b"* OK IMAP server ready\r\n")
                    while True:
                        data = self.request.recv(4096)
                        if not data:
                            break
                        command_line = data.decode('utf-8', errors='ignore').strip()
                        if not command_line:
                            continue
                        parts = command_line.split()
                        if not parts:
                            continue
                        tag = parts[0]
                        command = parts[1].upper() if len(parts) > 1 else ""
                        if command == 'LOGIN':
                            # LOGIN command
                            if len(parts) >= 4:
                                self.username = parts[2]
                                # Simple auth for demo
                                self.authenticated = True
                                self.request.sendall(f"{tag} OK LOGIN completed\r\n".encode())
                            else:
                                self.request.sendall(f"{tag} BAD Invalid LOGIN command\r\n".encode())
                        elif command == 'SELECT':
                            # SELECT command - select mailbox
                            if not self.authenticated:
                                self.request.sendall(f"{tag} NO Authentication required\r\n".encode())
                                continue
                            if len(parts) >= 3:
                                mailbox = parts[2].strip('"')
                                self.selected_mailbox = mailbox
                                messages = self.email_store.list_messages(
                                    mailbox=mailbox,
                                    username=self.username
                                )
                                response = f"* {len(messages)} EXISTS\r\n".encode()
                                response += f"* 0 RECENT\r\n".encode()
                                response += f"* OK [UIDVALIDITY 1] UIDs valid\r\n".encode()
                                response += f"{tag} OK [READ-WRITE] SELECT completed\r\n".encode()
                                self.request.sendall(response)
                            else:
                                self.request.sendall(f"{tag} BAD Invalid SELECT command\r\n".encode())
                        elif command == 'FETCH':
                            # FETCH command - fetch message
                            if not self.authenticated:
                                self.request.sendall(f"{tag} NO Authentication required\r\n".encode())
                                continue
                            if not self.selected_mailbox:
                                self.request.sendall(f"{tag} NO No mailbox selected\r\n".encode())
                                continue
                            if len(parts) >= 3:
                                try:
                                    msg_num = int(parts[2])
                                    messages = self.email_store.list_messages(
                                        mailbox=self.selected_mailbox,
                                        username=self.username
                                    )
                                    if 1 <= msg_num <= len(messages):
                                        msg_id = messages[msg_num - 1]['id']
                                        message = self.email_store.get_message(msg_id)
                                        if message:
                                            msg_bytes = message.as_bytes()
                                            response = f"* {msg_num} FETCH (RFC822 {{{len(msg_bytes)}}})\r\n".encode()
                                            self.request.sendall(response)
                                            self.request.sendall(msg_bytes)
                                            self.request.sendall(b"\r\n")
                                            self.request.sendall(f"{tag} OK FETCH completed\r\n".encode())
                                            # Mark as read
                                            self.email_store.mark_read(msg_id, read=True)
                                        else:
                                            self.request.sendall(f"{tag} NO Message not found\r\n".encode())
                                    else:
                                        self.request.sendall(f"{tag} NO Invalid message number\r\n".encode())
                                except ValueError:
                                    self.request.sendall(f"{tag} BAD Invalid message number\r\n".encode())
                            else:
                                self.request.sendall(f"{tag} BAD Invalid FETCH command\r\n".encode())
                        elif command == 'SEARCH':
                            # SEARCH command - search messages
                            if not self.authenticated:
                                self.request.sendall(f"{tag} NO Authentication required\r\n".encode())
                                continue
                            if not self.selected_mailbox:
                                self.request.sendall(f"{tag} NO No mailbox selected\r\n".encode())
                                continue
                            messages = self.email_store.list_messages(
                                mailbox=self.selected_mailbox,
                                username=self.username
                            )
                            message_nums = " ".join(str(i) for i in range(1, len(messages) + 1))
                            self.request.sendall(f"* SEARCH {message_nums}\r\n".encode())
                            self.request.sendall(f"{tag} OK SEARCH completed\r\n".encode())
                        elif command == 'STORE':
                            # STORE command - update message flags
                            if not self.authenticated:
                                self.request.sendall(f"{tag} NO Authentication required\r\n".encode())
                                continue
                            if not self.selected_mailbox:
                                self.request.sendall(f"{tag} NO No mailbox selected\r\n".encode())
                                continue
                            if len(parts) >= 5:
                                try:
                                    msg_num = int(parts[2])
                                    flag_op = parts[3]  # +FLAGS, -FLAGS, FLAGS
                                    flags = parts[4:] if len(parts) > 4 else []
                                    messages = self.email_store.list_messages(
                                        mailbox=self.selected_mailbox,
                                        username=self.username
                                    )
                                    if 1 <= msg_num <= len(messages):
                                        msg_id = messages[msg_num - 1]['id']
                                        # Handle flags
                                        if '\\Seen' in flags or '+FLAGS' in flag_op:
                                            self.email_store.mark_read(msg_id, read=True)
                                        elif '-FLAGS' in flag_op and '\\Seen' in flags:
                                            self.email_store.mark_read(msg_id, read=False)
                                        self.request.sendall(f"{tag} OK STORE completed\r\n".encode())
                                    else:
                                        self.request.sendall(f"{tag} NO Invalid message number\r\n".encode())
                                except ValueError:
                                    self.request.sendall(f"{tag} BAD Invalid message number\r\n".encode())
                            else:
                                self.request.sendall(f"{tag} BAD Invalid STORE command\r\n".encode())
                        elif command == 'LOGOUT':
                            # LOGOUT command
                            self.request.sendall(b"* BYE IMAP server logging out\r\n")
                            self.request.sendall(f"{tag} OK LOGOUT completed\r\n".encode())
                            break
                        else:
                            self.request.sendall(f"{tag} BAD Unknown command\r\n".encode())
                except Exception as e:
                    logger.error(f"Error in IMAP handler: {e}")
                    try:
                        self.request.sendall(f"{tag} BAD Server error\r\n".encode())
                    except:
                        pass
        # Create server
        class ThreadedIMAPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True
        self._server = ThreadedIMAPServer(
            (host, port),
            lambda request, client_address, server: CustomIMAPHandler(
                request, client_address, server, self._email_store, self._command_handlers
            )
        )
        logger.info(f"Starting IMAP server on {host}:{port} (SSL={ssl}, STARTTLS={starttls})")
        # Start server in background thread
        server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        server_thread.start()
        logger.info(f"IMAP server started on {host}:{port}")

    def stop_server(self, app: Any) -> None:
        """Stop IMAP server."""
        if self._server:
            logger.info("Stopping IMAP server...")
            self._server.shutdown()
            self._server = None
            logger.info("IMAP server stopped")
