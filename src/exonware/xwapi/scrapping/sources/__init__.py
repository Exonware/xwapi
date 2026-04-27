#exonware/xwapi/src/exonware/xwapi/scrapping/sources/__init__.py
"""
Concrete site adapters live here.

Each adapter is a pair: a Scraper class implementing IScraper and a Normalizer
class implementing INormalizer. They are intentionally kept small — one file
per source — and registered through `SOURCE_REGISTRY` so callers can look up
an adapter by its source id.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
from typing import Callable, Mapping

from ..contracts import INormalizer, IScraper

# Adapter factory signature: (kwargs) -> (scraper, normalizer)
AdapterFactory = Callable[..., tuple[IScraper, INormalizer]]

SOURCE_REGISTRY: dict[str, AdapterFactory] = {}


def register_source(source_id: str) -> Callable[[AdapterFactory], AdapterFactory]:
    """Decorator: register an adapter factory under a source id."""
    def deco(factory: AdapterFactory) -> AdapterFactory:
        if source_id in SOURCE_REGISTRY:
            raise RuntimeError(f"source already registered: {source_id}")
        SOURCE_REGISTRY[source_id] = factory
        return factory
    return deco


def build_adapter(source_id: str, **kwargs) -> tuple[IScraper, INormalizer]:
    """Look up + instantiate an adapter pair by source id."""
    if source_id not in SOURCE_REGISTRY:
        raise KeyError(
            f"unknown source: {source_id!r}. "
            f"Registered: {sorted(SOURCE_REGISTRY)}"
        )
    return SOURCE_REGISTRY[source_id](**kwargs)


# Importing the module side-effect-registers each adapter.
from . import aqar_sa    # noqa: F401, E402
from . import bayut      # noqa: F401, E402
from . import synthetic  # noqa: F401, E402


__all__ = ["SOURCE_REGISTRY", "register_source", "build_adapter", "AdapterFactory"]
