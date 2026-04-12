#exonware/xwapi/engines/email_store.py
"""
Email Store Abstraction
Protocol-agnostic interface for email storage used by SMTP, POP3, and IMAP engines.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
"""

from typing import Protocol, Optional, List, Dict, Any
from email.message import EmailMessage
from datetime import datetime
import uuid


class IEmailStore(Protocol):
    """
    Email Store Interface
    Protocol-agnostic interface for storing and retrieving emails.
    Used by SMTP, POP3, and IMAP engines to maintain a unified email storage.
    """

    def store_message(self, message: EmailMessage, mailbox: str = "INBOX") -> str:
        """
        Store an email message.
        Args:
            message: EmailMessage instance
            mailbox: Mailbox name (default: "INBOX")
        Returns:
            Message ID (unique identifier)
        """
        ...

    def get_message(self, message_id: str) -> EmailMessage | None:
        """
        Get email message by ID.
        Args:
            message_id: Message identifier
        Returns:
            EmailMessage or None if not found
        """
        ...

    def list_messages(
        self,
        mailbox: str = "INBOX",
        username: str | None = None,
        unread_only: bool = False,
        limit: int | None = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        List emails with optional filters.
        Args:
            mailbox: Mailbox name (default: "INBOX")
            username: Filter by recipient username
            unread_only: Only return unread emails
            limit: Maximum number of results
            offset: Pagination offset
        Returns:
            List of email metadata dictionaries
        """
        ...

    def delete_message(self, message_id: str) -> bool:
        """
        Delete email message.
        Args:
            message_id: Message identifier
        Returns:
            True if deleted, False if not found
        """
        ...

    def mark_read(self, message_id: str, read: bool = True) -> bool:
        """
        Mark email as read/unread.
        Args:
            message_id: Message identifier
            read: True to mark as read, False to mark as unread
        Returns:
            True if updated, False if not found
        """
        ...

    def get_stats(self, username: str | None = None) -> dict[str, Any]:
        """
        Get email statistics.
        Args:
            username: Optional username filter
        Returns:
            Statistics dictionary (total, unread, read, etc.)
        """
        ...


class InMemoryEmailStore:
    """
    In-Memory Email Store Implementation
    Simple in-memory storage for demonstration and testing.
    For production, implement database-backed or filesystem-backed stores.
    """

    def __init__(self):
        """Initialize in-memory email store."""
        self._messages: dict[str, dict[str, Any]] = {}
        self._mailboxes: dict[str, list[str]] = {"INBOX": []}  # mailbox -> [message_ids]

    def store_message(self, message: EmailMessage, mailbox: str = "INBOX") -> str:
        """Store an email message."""
        message_id = str(uuid.uuid4())
        # Extract metadata
        from_addr = message.get("From", "unknown@example.com")
        to_addrs = message.get_all("To", [])
        subject = message.get("Subject", "")
        # Store message with metadata
        self._messages[message_id] = {
            "id": message_id,
            "message": message,
            "mailbox": mailbox,
            "from": from_addr,
            "to": to_addrs if isinstance(to_addrs, list) else [to_addrs] if to_addrs else [],
            "subject": subject,
            "created_at": datetime.now().isoformat(),
            "read": False,
            "deleted": False,
            "size": len(message.as_bytes())
        }
        # Add to mailbox
        if mailbox not in self._mailboxes:
            self._mailboxes[mailbox] = []
        self._mailboxes[mailbox].append(message_id)
        return message_id

    def get_message(self, message_id: str) -> EmailMessage | None:
        """Get email message by ID."""
        entry = self._messages.get(message_id)
        if entry and not entry.get("deleted", False):
            return entry["message"]
        return None

    def list_messages(
        self,
        mailbox: str = "INBOX",
        username: str | None = None,
        unread_only: bool = False,
        limit: int | None = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """List emails with optional filters."""
        # Get message IDs from mailbox
        message_ids = self._mailboxes.get(mailbox, [])
        # Build list of messages
        messages = []
        for msg_id in message_ids:
            entry = self._messages.get(msg_id)
            if not entry or entry.get("deleted", False):
                continue
            # Filter by username (check if username is in 'to' addresses)
            if username:
                to_addrs = entry.get("to", [])
                if not any(username.lower() in addr.lower() for addr in to_addrs):
                    continue
            # Filter by read status
            if unread_only and entry.get("read", False):
                continue
            # Add metadata (without full message)
            messages.append({
                "id": entry["id"],
                "from": entry["from"],
                "to": entry["to"],
                "subject": entry["subject"],
                "created_at": entry["created_at"],
                "read": entry["read"],
                "size": entry["size"]
            })
        # Sort by created_at (newest first)
        messages.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        # Apply pagination
        if limit:
            messages = messages[offset:offset + limit]
        else:
            messages = messages[offset:]
        return messages

    def delete_message(self, message_id: str) -> bool:
        """Delete email message (soft delete)."""
        entry = self._messages.get(message_id)
        if entry:
            entry["deleted"] = True
            return True
        return False

    def mark_read(self, message_id: str, read: bool = True) -> bool:
        """Mark email as read/unread."""
        entry = self._messages.get(message_id)
        if entry and not entry.get("deleted", False):
            entry["read"] = read
            return True
        return False

    def get_stats(self, username: str | None = None) -> dict[str, Any]:
        """Get email statistics."""
        all_messages = [
            entry for entry in self._messages.values()
            if not entry.get("deleted", False)
        ]
        # Filter by username if provided
        if username:
            all_messages = [
                entry for entry in all_messages
                if any(username.lower() in addr.lower() for addr in entry.get("to", []))
            ]
        return {
            "total": len(all_messages),
            "unread": len([e for e in all_messages if not e.get("read", False)]),
            "read": len([e for e in all_messages if e.get("read", False)]),
            "mailboxes": {mb: len(ids) for mb, ids in self._mailboxes.items()}
        }
