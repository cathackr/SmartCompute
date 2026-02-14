"""
Tier-gating decorators for SmartCompute features.

Usage::

    from smartcompute.licensing.decorators import requires_tier

    @requires_tier("enterprise")
    def run_xdr_scan():
        ...

    @requires_tier("industrial")
    def analyze_modbus_traffic():
        ...
"""

from __future__ import annotations

import functools
from typing import Callable

from smartcompute.licensing.validator import TIER_HIERARCHY, LicenseValidator

# Module-level singleton so all decorators share the same cache.
_validator = LicenseValidator()


class TierRequiredError(Exception):
    """Raised when a function requires a higher license tier."""

    def __init__(self, required_tier: str, current_tier: str):
        self.required_tier = required_tier
        self.current_tier = current_tier
        super().__init__(
            f"This feature requires a '{required_tier}' license "
            f"(current: '{current_tier}'). "
            f"Upgrade at https://github.com/cathackr/smartcompute#pricing"
        )


def requires_tier(tier: str) -> Callable:
    """Decorator that gates a function behind *tier*.

    The tier hierarchy is: starter < enterprise < industrial.
    A higher tier implicitly grants access to lower-tier features.

    Raises
    ------
    TierRequiredError
        If the active license does not meet the required tier.
    """
    tier_lower = tier.lower()
    if tier_lower not in TIER_HIERARCHY:
        raise ValueError(f"Unknown tier {tier!r}; expected one of {TIER_HIERARCHY}")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _validator.has_tier(tier_lower):
                current = _validator.get_current_tier()
                raise TierRequiredError(tier_lower, current)
            return func(*args, **kwargs)

        # Stash metadata for introspection / CLI help
        wrapper._required_tier = tier_lower  # type: ignore[attr-defined]
        return wrapper

    return decorator
