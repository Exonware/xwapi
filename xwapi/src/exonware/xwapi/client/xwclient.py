#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/client/xwclient.py
XWApiAgent - API Agent Implementation
Concrete implementation of API agent pattern for xwapi library.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
"""

from typing import Any, Optional, Callable, TYPE_CHECKING
from inspect import isfunction
from pathlib import Path
from exonware.xwsystem.io.serialization import JsonSerializer
from urllib.parse import urlparse
from exonware.xwapi.client.base import AApiAgent
from exonware.xwsystem import get_logger
from exonware.xwauth import XWAuth
from exonware.xwauth.clients.oauth_client import OAuth2ClientManager
from exonware.xwauth.clients.entity_session_manager import EntitySessionManager
from exonware.xwaction import XWAction, ActionProfile
# Import agent engines
from exonware.xwapi.client.engines import api_agent_engine_registry, IApiAgentEngine
logger = get_logger(__name__)


class XWApiAgent(AApiAgent):
    """
    Concrete implementation of API Agent pattern.
    Provides a base class for creating API agents that expose XWAction-decorated
    functions as API endpoints via ApiServer.
    Usage:
        >>> from exonware.xwapi import XWApiAgent
        >>> from exonware.xwaction import XWAction
        >>> 
        >>> class MyAgent(XWApiAgent):
        ...     @XWAction(operationId="hello", profile="endpoint")
        ...     def hello(self, name: str = "World") -> dict:
        ...         return {"message": f"Hello, {name}!"}
        ... 
        >>> agent = MyAgent()
        >>> # server = ApiServer()
        >>> # agent.register_to_server(server)
        >>> # server.start(port=8000)
    """
    DEFAULT_AUTH_DIR = "data/xwauth"
    DEFAULT_ENTITY_TYPE = "entity"

    def __init__(
        self, 
        name: Optional[str] = None, 
        auto_discover: bool = True, 
        entity_type: str = DEFAULT_ENTITY_TYPE,
        agent_engine: Optional[str] = None
    ):
        """
        Initialize XWApiAgent instance.
        Args:
            name: Optional name for this agent (defaults to class name)
            auto_discover: If True, automatically discover XWAction-decorated methods
            entity_type: Type name for entities (default: "entity", can be "agency", "account", "user", etc.)
            agent_engine: Optional agent engine name (default: "native")
                Uses agent engine registry to get the engine for action discovery/execution
        """
        super().__init__(name=name)
        self._auto_discover = auto_discover
        self._actions: list[Callable] = []
        self._auth: Optional[Any] = None  # Optional XWAuth instance
        # Store auth configs by platform, then by auth_name
        # Structure: {platform: {auth_name: config_dict}}
        self._auth_configs: dict[str, dict[str, dict[str, Any]]] = {}
        # Generic entity management (using xwauth)
        self._entity_type = entity_type
        self._entities: dict[str, dict[str, Any]] = {}  # Generic entities dict
        # Initialize xwauth client managers
        self._oauth_client_manager = OAuth2ClientManager()
        self._entity_session_manager = EntitySessionManager(self._entities)
        # Get agent engine from registry
        if api_agent_engine_registry:
            self._agent_engine: Optional[IApiAgentEngine] = api_agent_engine_registry.get_engine(agent_engine)
            if not self._agent_engine:
                logger.warning(f"Agent engine '{agent_engine}' not found, using default")
                self._agent_engine = api_agent_engine_registry.get_engine()  # Get default
        else:
            self._agent_engine = None
            logger.warning("Agent engine registry not available, using fallback discovery")
        if auto_discover:
            self._discover_actions()

    def _discover_actions(self) -> None:
        """
        Auto-discover XWAction-decorated methods using agent engine.
        Uses the agent engine's discover_actions method if available,
        otherwise falls back to native discovery logic.
        """
        self._actions = []
        # Use agent engine if available
        if self._agent_engine:
            self._actions = self._agent_engine.discover_actions(self)
            logger.info(f"Discovered {len(self._actions)} actions using {self._agent_engine.name} engine")
        else:
            # Fallback to native discovery
            discovered_names = set()
            # Traverse Method Resolution Order (MRO) to find all @XWAction methods
            for cls in self.__class__.__mro__:
                if cls is object:
                    continue
                # Inspect class dict directly to avoid triggering properties
                for name, attr in cls.__dict__.items():
                    if name.startswith('_'):
                        continue
                    if name in discovered_names:
                        continue
                    # Check if it's a function and has the marker
                    if isfunction(attr) and hasattr(attr, 'xwaction'):
                        # Now we safely bind it to self
                        try:
                            bound_method = getattr(self, name)
                            self._actions.append(bound_method)
                            discovered_names.add(name)
                            logger.debug(f"Discovered action: {name} from class {cls.__name__}")
                        except AttributeError:
                            continue
            logger.info(f"Auto-discovered {len(self._actions)} actions for agent {self._name} (fallback)")

    def get_actions(self) -> list[Callable]:
        """
        Get list of XWAction instances provided by this agent.
        Returns:
            List of XWAction-decorated functions/methods
        """
        return self._actions.copy()

    def add_action(self, action: Callable) -> None:
        """
        Manually add an action to this agent.
        Args:
            action: XWAction-decorated function or method
        """
        if not hasattr(action, 'xwaction'):
            logger.warning(f"Action {getattr(action, '__name__', 'unknown')} does not have xwaction attribute")
            return
        if action not in self._actions:
            self._actions.append(action)
            logger.debug(f"Added action: {getattr(action, '__name__', 'unknown')}")
        else:
            logger.debug(f"Action {getattr(action, '__name__', 'unknown')} already in agent")

    def remove_action(self, action: Callable) -> bool:
        """
        Remove an action from this agent.
        Args:
            action: XWAction-decorated function or method to remove
        Returns:
            True if action was removed, False if not found
        """
        if action in self._actions:
            self._actions.remove(action)
            logger.debug(f"Removed action: {getattr(action, '__name__', 'unknown')}")
            return True
        return False

    def clear_actions(self) -> None:
        """Clear all actions from this agent."""
        self._actions.clear()
        logger.debug(f"Cleared all actions from agent {self._name}")

    def load_auth_config(self, platform: str, auth_name: str, config_path: Optional[str] = None) -> dict[str, Any]:
        """
        Load authentication configuration from JSON file.
        This method loads auth configs from files but doesn't require xwauth.
        Configs are stored and can be used later when xwauth is available.
        Supports multiple platforms and multiple authorizations per platform.
        Directory structure: data/xwauth/{platform}/{auth_name}/config.json
        Args:
            platform: Name of the platform (e.g., 'google', 'liveme')
            auth_name: Name of the authorization/account (e.g., 'service_account', 'ru_karizma')
            config_path: Path to JSON config file. If None, uses default path:
                        data/xwauth/{platform}/{auth_name}/config.json
        Returns:
            Dictionary containing the loaded config
        Example:
            >>> agent.load_auth_config('google', 'service_account')
            >>> agent.load_auth_config('liveme', 'ru_karizma')
            >>> agent.load_auth_config('google', 'another_account', 'custom/path/config.json')
        """
        # If config_path not provided, use default structure
        if config_path is None:
            # Try to determine base directory (usually data/xwauth/)
            # This is a best-effort approach - subclasses can override
            config_path = f"{self.DEFAULT_AUTH_DIR}/{platform}/{auth_name}/config.json"
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Auth config file not found: {config_path}")
        config = JsonSerializer().load_file(config_file)
        # Initialize platform dict if needed
        if platform not in self._auth_configs:
            self._auth_configs[platform] = {}
        self._auth_configs[platform][auth_name] = config
        logger.info(f"Loaded auth config for platform '{platform}' auth '{auth_name}' from {config_path}")
        return config

    def get_auth_config(self, platform: str, auth_name: Optional[str] = None) -> Optional[dict[str, Any] | dict[str, dict[str, Any]]]:
        """
        Get authentication configuration for a platform and optionally specific auth.
        Args:
            platform: Name of the platform (e.g., 'google', 'liveme')
            auth_name: Optional name of the authorization/account.
                      If None, returns all auth configs for the platform.
        Returns:
            Configuration dictionary for specific auth, dict of all auth configs for platform,
            or None if platform/auth not found
        Example:
            >>> agent.get_auth_config('google', 'service_account')  # Get specific auth
            >>> agent.get_auth_config('liveme')  # Get all liveme auths
        """
        platform_configs = self._auth_configs.get(platform)
        if platform_configs is None:
            return None
        if auth_name is None:
            # Return all auth configs for the platform
            return platform_configs
        return platform_configs.get(auth_name)

    def load_all_auth_configs(self, base_path: str = DEFAULT_AUTH_DIR) -> dict[str, dict[str, dict[str, Any]]]:
        """
        Load all authentication configurations from directory structure.
        Scans data/xwauth/{platform}/{auth_name}/config.json structure and loads all configs.
        Args:
            base_path: Base path to xwauth directory (default: "data/xwauth")
        Returns:
            Dictionary of all loaded configs: {platform: {auth_name: config}}
        """
        base_dir = Path(base_path)
        if not base_dir.exists():
            logger.warning(f"Auth config base directory not found: {base_path}")
            return {}
        loaded_count = 0
        for platform_dir in base_dir.iterdir():
            if not platform_dir.is_dir():
                continue
            platform = platform_dir.name
            for auth_dir in platform_dir.iterdir():
                if not auth_dir.is_dir():
                    continue
                auth_name = auth_dir.name
                config_file = auth_dir / "config.json"
                if config_file.exists():
                    try:
                        self.load_auth_config(platform, auth_name, str(config_file))
                        loaded_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to load config {config_file}: {e}")
        logger.info(f"Loaded {loaded_count} auth configs from {base_path}")
        return self._auth_configs.copy()

    def init_xwauth(self, jwt_secret: str, providers: Optional[list[str]] = None, **kwargs) -> Any:
        """
        Initialize XWAuth instance.
        Args:
            jwt_secret: JWT secret key for token signing
            providers: Optional list of provider names to enable
            **kwargs: Additional arguments passed to XWAuth constructor
        Returns:
            XWAuth instance
        Example:
            >>> agent.init_xwauth(jwt_secret='my-secret', providers=['google'])
        """
        self._auth = XWAuth(jwt_secret=jwt_secret, providers=providers or [], **kwargs)
        logger.info(f"Initialized XWAuth for agent {self._name}")
        return self._auth
    @property

    def auth(self) -> Optional[Any]:
        """
        Get XWAuth instance if available.
        Returns:
            XWAuth instance or None if not initialized
        """
        return self._auth

    def has_auth(self) -> bool:
        """Check if XWAuth is available and initialized."""
        return self._auth is not None
    # ============================================================================
    # Authentication Helpers (Category 12) - Token management
    # ============================================================================

    def save_tokens(self, platform: str, auth_name: str, tokens: dict[str, Any], token_path: Optional[str] = None) -> None:
        """
        Save authentication tokens to a JSON file.
        Generic method for persisting authentication tokens. Subclasses can override
        to customize token storage location or format.
        Args:
            platform: Platform name (e.g., 'liveme', 'google')
            auth_name: Authentication name/account identifier
            tokens: Dictionary containing token data
            token_path: Optional custom path for token file. If None, uses default:
                       data/xwauth/{platform}/{auth_name}/token.json
        """
        if token_path is None:
            token_path = f"{self.DEFAULT_AUTH_DIR}/{platform}/{auth_name}/token.json"
        token_file = Path(token_path)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        JsonSerializer().save_file(tokens, token_file, indent=2, sort_keys=True)
        logger.info(f"Saved tokens for platform '{platform}' auth '{auth_name}' to {token_path}")

    def load_tokens(self, platform: str, auth_name: str, token_path: Optional[str] = None) -> Optional[dict[str, Any]]:
        """
        Load authentication tokens from a JSON file.
        Generic method for loading persisted authentication tokens. Returns None
        if token file doesn't exist.
        Args:
            platform: Platform name (e.g., 'liveme', 'google')
            auth_name: Authentication name/account identifier
            token_path: Optional custom path for token file. If None, uses default:
                       data/xwauth/{platform}/{auth_name}/token.json
        Returns:
            Dictionary containing token data, or None if file doesn't exist
        """
        if token_path is None:
            token_path = f"{self.DEFAULT_AUTH_DIR}/{platform}/{auth_name}/token.json"
        token_file = Path(token_path)
        if not token_file.exists():
            logger.debug(f"Token file not found: {token_path}")
            return None
        try:
            tokens = JsonSerializer().load_file(token_file)
            logger.info(f"Loaded tokens for platform '{platform}' auth '{auth_name}' from {token_path}")
            return tokens
        except Exception as e:
            logger.warning(f"Failed to load tokens from {token_path}: {e}")
            return None
    # ============================================================================
    # Authentication Revival (Category 12) - Reload and refresh auth configs
    # ============================================================================
    @XWAction(
        operationId="auth.reviveAuths",
        api_name="revive_auths",
        cmd_shortcut="revive",
        summary="Revive authentication configurations",
        description="Reload all authentication configurations from local path or xwstorage. This reloads auth configs.",
        profile=ActionProfile.COMMAND,
        tags=["authentication", "auth"],
        roles=["admin", "owner"],
        audit=True
    )

    def revive_auths(self, base_path: Optional[str] = None, use_storage: bool = False) -> dict[str, Any]:
            """
            Revive (reload) all authentication configurations.
            This method reloads all authentication configurations from either:
            - Local file system: data/xwauth/{platform}/{auth_name}/config.json
            - xwstorage: If use_storage is True and xwstorage is available
            Args:
                base_path: Optional base path for local auth configs (default: "data/xwauth")
                use_storage: If True, attempt to use xwstorage (requires xwstorage to be available)
            Returns:
                Dictionary containing revival status:
                {
                    "success": bool,
                    "reloaded_count": int,
                    "platforms": list[str],
                    "auths": dict[str, list[str]],  # {platform: [auth_names]}
                    "errors": list[str],
                    "storage_used": bool
                }
            """
            result = {
                "success": True,
                "reloaded_count": 0,
                "platforms": [],
                "auths": {},
                "errors": [],
                "storage_used": False
            }
            try:
                # Try xwstorage if requested
                if use_storage:
                    # Optional xwstorage integration
                    from exonware.xwstorage import XWStorage
                    # If xwstorage is available, could load from storage here
                    # For now, this is a placeholder for future xwstorage integration
                    logger.info("xwstorage integration not yet implemented, falling back to local path")
                    result["storage_used"] = False
                # Use local path (default behavior)
                if base_path is None:
                    base_path = self.DEFAULT_AUTH_DIR
                # Clear existing configs before reloading
                old_count = sum(len(auths) for auths in self._auth_configs.values())
                # Reload all auth configs
                reloaded_configs = self.load_all_auth_configs(base_path=base_path)
                # Count reloaded configs
                result["reloaded_count"] = sum(len(auths) for auths in reloaded_configs.values())
                result["platforms"] = list(reloaded_configs.keys())
                # Build auth names per platform
                for platform, auth_configs in reloaded_configs.items():
                    result["auths"][platform] = list(auth_configs.keys())
                logger.info(f"Revived {result['reloaded_count']} auth configs from {len(result['platforms'])} platforms")
                if result["reloaded_count"] == 0:
                    result["errors"].append(f"No auth configs found in {base_path}")
                    result["success"] = False
            except Exception as e:
                error_msg = f"Failed to revive auth configs: {str(e)}"
                logger.error(error_msg, exc_info=True)
                result["errors"].append(error_msg)
                result["success"] = False
            return result
    # ============================================================================
    # Session Management (Category 4) - Generic session handling
    # ============================================================================

    def session_start(self, session_key: str, **kwargs) -> Any:
        """
        Start a session for the given key.
        This is a generic method that subclasses should override for specific
        session management needs. The default implementation does nothing.
        Args:
            session_key: Unique identifier for the session
            **kwargs: Additional session-specific parameters
        Returns:
            Session object (type depends on implementation)
        """
        logger.debug(f"Starting session for key: {session_key}")
        return None

    def session_is_authenticated(self, session: Any) -> bool:
        """
        Check if a session is authenticated.
        This is a generic method that subclasses should override to implement
        authentication checking logic specific to their API.
        Args:
            session: Session object to check
        Returns:
            True if authenticated, False otherwise
        """
        logger.debug("Checking session authentication (default: False)")
        return False

    def session_ensure_authenticated(self, session: Any) -> bool:
        """
        Ensure a session is authenticated, attempting login if needed.
        This is a generic method that subclasses should override to implement
        authentication logic specific to their API.
        Args:
            session: Session object to ensure authentication for
        Returns:
            True if authenticated (or successfully authenticated), False otherwise
        """
        if self.session_is_authenticated(session):
            return True
        logger.warning("Session not authenticated, login may be required")
        return False
    # ============================================================================
    # Entity Management (Category 5) - Generic multi-entity support using xwauth
    # ============================================================================
    @property

    def session(self) -> Optional[Any]:
        """
        Get default session from first available entity.
        Generic property that works with any entity type (agencies, accounts, users, etc.).
        Uses xwauth EntitySessionManager for session management.
        Returns:
            Session object or None if no entities exist
        """
        return self._entity_session_manager.session
    @property

    def entities(self) -> dict[str, dict[str, Any]]:
        """
        Get entities dictionary (generic - can be agencies, accounts, users, etc.).
        Returns:
            Dictionary of entities managed by xwauth EntitySessionManager
        """
        return self._entities

    def get_entity_session(self, entity_name: str) -> Optional[Any]:
        """
        Get session for a specific entity.
        Args:
            entity_name: Name of the entity
        Returns:
            Session object or None
        """
        return self._entity_session_manager.get_entity_session(entity_name)

    def set_entity(self, entity_name: str, entity_data: dict[str, Any]) -> None:
        """
        Set entity data.
        Args:
            entity_name: Name of the entity
            entity_data: Entity data dictionary
        """
        self._entity_session_manager.set_entity(entity_name, entity_data)

    def get_entity(self, entity_name: str) -> Optional[dict[str, Any]]:
        """
        Get entity data.
        Args:
            entity_name: Name of the entity
        Returns:
            Entity data dictionary or None
        """
        return self._entity_session_manager.get_entity(entity_name)

    def merge_auth_credentials(self, platform: str, data_dir: Optional[str] = None) -> None:
        """
        Merge auth credentials from xwauth configs into entities.
        Generic method that delegates to xwauth OAuth2ClientManager.
        Works with any entity type and platform.
        Args:
            platform: Platform name (e.g., 'liveme', 'google')
            data_dir: Base data directory for token storage (optional)
        """
        auth_configs = self.get_auth_config(platform)
        if auth_configs:
            self._oauth_client_manager.merge_auth_credentials_into_entities(
                self._entities,
                platform,
                auth_configs,
                data_dir
            )
            # Update entity session manager with merged entities (same dict reference)
            self._entity_session_manager = EntitySessionManager(self._entities)

    def request_oauth_token(
        self,
        token_url: str,
        entity_name: str,
        grant_type: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Request OAuth 2.0 token for an entity.
        Generic method that delegates to xwauth OAuth2ClientManager.
        Args:
            token_url: OAuth 2.0 token endpoint URL
            entity_name: Name of the entity
            grant_type: Grant type (defaults to entity's oauth_token_pl grant_type)
        Returns:
            Token response dictionary
        """
        entity = self.get_entity(entity_name)
        if not entity or 'oauth_token_pl' not in entity:
            raise ValueError(f"Entity '{entity_name}' does not have oauth_token_pl configured")
        return self._oauth_client_manager.request_token(
            token_url,
            entity['oauth_token_pl'],
            grant_type
        )
    # ============================================================================
    # HTTP Request Helpers (Category 5) - Generic request methods
    # ============================================================================

    def request_headers_generate(
        self,
        url: str,
        method: str = "GET",
        authorization: Optional[str] = None,
        cookie: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Generate HTTP headers for a request.
        Args:
            url: Request URL
            method: HTTP method (GET, POST, etc.) - unused in standard headers
            authorization: Authorization header value
            cookie: Cookie header value
            **kwargs: Additional header parameters
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
        }
        if authorization:
            headers["authorization"] = authorization
        if cookie:
            headers["cookie"] = cookie
        # Allow subclasses to add custom headers via kwargs
        headers.update(kwargs)
        return headers

    def _validate_session(self, session: Any) -> Any:
        """Validate a session object by capability, not concrete dependency type."""
        if session is None:
            logger.warning("Missing session object")
            return None
        if hasattr(session, "get") and hasattr(session, "post"):
            return session
        logger.warning(f"Unsupported session object (missing get/post): {type(session)}")
        return None

    def request_post(
        self,
        session: Any,
        url: str,
        payload: Optional[dict | str] = None,
        headers: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Perform a generic POST request.
        Args:
            session: Session object (requests.Session or similar)
            url: Request URL
            payload: Request payload (dict for JSON, str for form data)
            headers: Optional custom headers (if None, uses request_headers_generate)
            **kwargs: Additional arguments passed to session.post()
        Returns:
            Response object (type depends on session implementation)
        """
        valid_session = self._validate_session(session)
        if not valid_session:
            return None
        if headers is None:
            headers = self.request_headers_generate(url, "POST")
        if isinstance(payload, dict):
            return valid_session.post(url, headers=headers, json=payload, **kwargs)
        else:
            return valid_session.post(url, headers=headers, data=payload, **kwargs)

    def request_get(
        self,
        session: Any,
        url: str,
        headers: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Perform a generic GET request.
        Args:
            session: Session object (requests.Session or similar)
            url: Request URL
            headers: Optional custom headers (if None, uses request_headers_generate)
            **kwargs: Additional arguments passed to session.get()
        Returns:
            Response object (type depends on session implementation)
        """
        valid_session = self._validate_session(session)
        if not valid_session:
            return None
        if headers is None:
            headers = self.request_headers_generate(url, "GET")
        return valid_session.get(url, headers=headers, **kwargs)

    def request_download(
        self,
        session: Any,
        url: str,
        headers: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Perform a generic download request (GET with binary content).
        Args:
            session: Session object (requests.Session or similar)
            url: Request URL
            headers: Optional custom headers
            **kwargs: Additional arguments passed to session.get()
        Returns:
            Response object with binary content
        """
        return self.request_get(session, url, headers=headers, **kwargs)

    def __repr__(self) -> str:
        """String representation."""
        auth_status = "auth" if self.has_auth() else "no-auth"
        return f"XWApiAgent(name={self._name}, actions={len(self._actions)}, {auth_status})"
