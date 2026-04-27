# exonware/xwapi/src/exonware/xwapi/reference_parity.py
"""
Industry **reference stacks** surfaced in ``/.../surface`` JSON for ops consoles and parity reviews.

These rows are intentionally lightweight (names + capability hints); domain libraries own full
contract matrices (see e.g. ``xwauth`` competitive parity docs).
"""

from __future__ import annotations

from typing import Any

# Keys match ``service_key`` passed to :func:`~exonware.xwapi.service_surface.register_xw_service_surface_routes`.
_REFERENCE_PRODUCT_ROWS: dict[str, list[dict[str, str]]] = {
    "xwlogin-api": [
        {
            "category": "hosted_login",
            "references": "Auth0 Universal Login, Azure AD B2C, Amazon Cognito Hosted UI",
            "xw_mapping": "OAuth/OIDC redirects + provider callbacks via exonware-xwlogin handlers",
        },
    ],
    "xwauth-api": [
        {
            "category": "identity_provider",
            "references": "Auth0, Okta, Azure AD, Keycloak",
            "xw_mapping": "OAuth 2.0 / OIDC / JWKS / PAR / SCIM hooks (library surface)",
        },
    ],
    "xwstorage-db-api": [
        {
            "category": "document_sql_http",
            "references": "PostgREST, Supabase REST, MongoDB Atlas Data API",
            "xw_mapping": "Engine/query adapters in exonware-xwstorage-db (+ HTTP attach points on this host)",
        },
    ],
    "xwstorage-api": [
        {
            "category": "object_storage_http",
            "references": "Amazon S3, Google Cloud Storage, Azure Blob",
            "xw_mapping": "Connector model + APIServer routes in exonware-xwstorage.connect.api.server",
        },
    ],
    "xwbase-api": [
        {
            "category": "baas",
            "references": "Firebase, Supabase, AWS Amplify Data",
            "xw_mapping": "Entity/BaaS flows via exonware-xwbase (+ shared xwentity/xwmodels)",
        },
    ],
    "xwchat-api": [
        {
            "category": "realtime_chat",
            "references": "Stream Chat, Sendbird, Firebase RTDB messaging patterns",
            "xw_mapping": "Chat transports in exonware-xwchat.api",
        },
    ],
    "xwai-api": [
        {
            "category": "model_gateway",
            "references": "OpenAI API, Anthropic Messages, Google Vertex AI",
            "xw_mapping": "Provider adapters in exonware-xwai",
        },
    ],
    "xwbots-api": [
        {
            "category": "bot_runtime",
            "references": "Microsoft Bot Framework, Slack Bolt, Discord.py hosting",
            "xw_mapping": "Bot connectors + automation in exonware-xwbots",
        },
    ],
}


def extend_surface_reference_products(service_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Merge stable reference-product rows into a surface payload (mutates and returns ``payload``)."""
    rows = _REFERENCE_PRODUCT_ROWS.get(service_key)
    if rows:
        payload["reference_products"] = list(rows)
    return payload
