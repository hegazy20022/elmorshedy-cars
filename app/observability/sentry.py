from __future__ import annotations
from typing import Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
except Exception:
    sentry_sdk = None
    FastApiIntegration = None
    SqlalchemyIntegration = None


def init_sentry(dsn: Optional[str] = None, environment: str = "development") -> bool:
    if not dsn:
        return False

    if sentry_sdk is None:
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.2,
        profiles_sample_rate=0.1,
    )
    return True
