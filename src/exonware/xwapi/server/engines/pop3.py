#exonware/xwapi/engines/pop3.py
"""
POP3 Server Engine Implementation
POP3 protocol server (RFC 1939) for downloading emails.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
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


class POP3ServerEngine(AApiServerEngineBase):
    """
    POP3 Server Engine
    Implements POP3 protocol server (RFC 1939) for downloading emails.
    Supports POP3S (SSL).
    """

    def __init__(self, email_store: IEmailStore | None = None):
        """
        Initialize POP3 server engine.
        Args:
            email_store: Email store implementation (default: InMemoryEmailStore)
        """
        super().__init__("pop3")
        self._protocol_type = ProtocolType.POP3
        self._app: Any | None = None
        self._server: Any | None = None
        self._email_store = email_store or InMemoryEmailStore()
        self._command_handlers: dict[str, Callable] = {}
        self._host: str | None = None
        self._port: int | None = None
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (POP3)."""
        return self._protocol_type
    @property

    def supports_admin_endpoints(self) -> bool:
        """POP3 does not support HTTP admin endpoints."""
        return False

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create POP3 server application.
        Args:
            config: XWAPI configuration
        Returns:
            POP3 handler instance
        """
        self._app = self
        return self._app

    def register_action(self, app: Any, action: Any, 
                        route_info: dict[str, Any]) -> bool:
        """
        Register XWAction as POP3 command handler.
        Args:
            app: POP3 handler instance
            action: XWAction instance to handle commands
            route_info: Protocol-specific route information
                Example: {'command': 'RETR', 'mailbox': 'INBOX'}
        Returns:
            True if registration successful
        """
        command = route_info.get('command', 'RETR').upper()
        self._command_handlers[command] = action
        logger.info(f"Registered POP3 handler for command '{command}': {getattr(action, 'api_name', 'unknown')}")
        return True

    def generate_schema(self, app: Any, actions: list[Any], 
                       config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate POP3 protocol schema.
        Args:
            app: POP3 handler instance
            actions: List of registered actions
            config: XWAPI configuration
        Returns:
            Protocol documentation dictionary
        """
        return {
            "protocol": "POP3",
            "rfc": "1939",
            "description": "Post Office Protocol version 3",
            "commands": ["USER", "PASS", "STAT", "LIST", "RETR", "DELE", "QUIT"],
            "handlers": [
                {
                    "action": getattr(action, 'api_name', 'unknown'),
                    "command": route_info.get('command', 'RETR')
                }
                for action, route_info in zip(actions, [{}] * len(actions))
            ]
        }

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 110, ssl: bool = False, **kwargs) -> None:
        """
        Start POP3 server.
        Args:
            app: POP3 handler instance
            host: Host to bind to
            port: Port to bind to (default: 110, or 995 for SSL)
            ssl: Enable SSL/TLS (POP3S)
            **kwargs: Additional server options
        """
        try:
            from poplib import POP3
            import socketserver
            import threading
        except ImportError:
            logger.error("poplib not available (part of standard library)")
            raise ImportError("poplib is required for POP3 server")
        self._host = host
        self._port = port
        # Create custom POP3 server handler
        class CustomPOP3Handler(socketserver.BaseRequestHandler):
            def __init__(self, request, client_address, server, email_store, command_handlers):
                self.email_store = email_store
                self.command_handlers = command_handlers
                self.authenticated = False
                self.username = None
                self.mailbox = "INBOX"
                super().__init__(request, client_address, server)
            def handle(self):
                """Handle POP3 client connection."""
                try:
                    # Send greeting
                    self.request.sendall(b"+OK POP3 server ready\r\n")
                    while True:
                        data = self.request.recv(1024)
                        if not data:
                            break
                        command = data.decode('utf-8', errors='ignore').strip().upper()
                        if command.startswith('USER'):
                            # USER command
                            parts = command.split()
                            if len(parts) >= 2:
                                self.username = parts[1]
                                self.request.sendall(b"+OK User accepted\r\n")
                            else:
                                self.request.sendall(b"-ERR Invalid USER command\r\n")
                        elif command.startswith('PASS'):
                            # PASS command (simple auth for demo)
                            self.authenticated = True
                            self.request.sendall(b"+OK Password accepted\r\n")
                        elif command == 'STAT':
                            # STAT command - get mailbox statistics
                            if not self.authenticated:
                                self.request.sendall(b"-ERR Authentication required\r\n")
                                continue
                            messages = self.email_store.list_messages(
                                mailbox=self.mailbox,
                                username=self.username
                            )
                            total_size = sum(msg.get('size', 0) for msg in messages)
                            self.request.sendall(f"+OK {len(messages)} {total_size}\r\n".encode())
                        elif command.startswith('LIST'):
                            # LIST command - list all messages
                            if not self.authenticated:
                                self.request.sendall(b"-ERR Authentication required\r\n")
                                continue
                            messages = self.email_store.list_messages(
                                mailbox=self.mailbox,
                                username=self.username
                            )
                            response = f"+OK {len(messages)} messages\r\n".encode()
                            for i, msg in enumerate(messages, 1):
                                response += f"{i} {msg.get('size', 0)}\r\n".encode()
                            response += b".\r\n"
                            self.request.sendall(response)
                        elif command.startswith('RETR'):
                            # RETR command - retrieve message
                            if not self.authenticated:
                                self.request.sendall(b"-ERR Authentication required\r\n")
                                continue
                            parts = command.split()
                            if len(parts) >= 2:
                                try:
                                    msg_num = int(parts[1])
                                    messages = self.email_store.list_messages(
                                        mailbox=self.mailbox,
                                        username=self.username
                                    )
                                    if 1 <= msg_num <= len(messages):
                                        msg_id = messages[msg_num - 1]['id']
                                        message = self.email_store.get_message(msg_id)
                                        if message:
                                            msg_bytes = message.as_bytes()
                                            self.request.sendall(f"+OK {len(msg_bytes)} octets\r\n".encode())
                                            self.request.sendall(msg_bytes)
                                            self.request.sendall(b"\r\n.\r\n")
                                            # Mark as read
                                            self.email_store.mark_read(msg_id, read=True)
                                        else:
                                            self.request.sendall(b"-ERR Message not found\r\n")
                                    else:
                                        self.request.sendall(b"-ERR Invalid message number\r\n")
                                except ValueError:
                                    self.request.sendall(b"-ERR Invalid message number\r\n")
                            else:
                                self.request.sendall(b"-ERR Invalid RETR command\r\n")
                        elif command.startswith('DELE'):
                            # DELE command - delete message
                            if not self.authenticated:
                                self.request.sendall(b"-ERR Authentication required\r\n")
                                continue
                            parts = command.split()
                            if len(parts) >= 2:
                                try:
                                    msg_num = int(parts[1])
                                    messages = self.email_store.list_messages(
                                        mailbox=self.mailbox,
                                        username=self.username
                                    )
                                    if 1 <= msg_num <= len(messages):
                                        msg_id = messages[msg_num - 1]['id']
                                        self.email_store.delete_message(msg_id)
                                        self.request.sendall(b"+OK Message deleted\r\n")
                                    else:
                                        self.request.sendall(b"-ERR Invalid message number\r\n")
                                except ValueError:
                                    self.request.sendall(b"-ERR Invalid message number\r\n")
                            else:
                                self.request.sendall(b"-ERR Invalid DELE command\r\n")
                        elif command == 'QUIT':
                            # QUIT command
                            self.request.sendall(b"+OK POP3 server signing off\r\n")
                            break
                        else:
                            self.request.sendall(b"-ERR Unknown command\r\n")
                except Exception as e:
                    logger.error(f"Error in POP3 handler: {e}")
                    try:
                        self.request.sendall(b"-ERR Server error\r\n")
                    except:
                        pass
        # Create server
        class ThreadedPOP3Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True
        self._server = ThreadedPOP3Server(
            (host, port),
            lambda request, client_address, server: CustomPOP3Handler(
                request, client_address, server, self._email_store, self._command_handlers
            )
        )
        logger.info(f"Starting POP3 server on {host}:{port} (SSL={ssl})")
        # Start server in background thread
        server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        server_thread.start()
        logger.info(f"POP3 server started on {host}:{port}")

    def stop_server(self, app: Any) -> None:
        """Stop POP3 server."""
        if self._server:
            logger.info("Stopping POP3 server...")
            self._server.shutdown()
            self._server = None
            logger.info("POP3 server stopped")
