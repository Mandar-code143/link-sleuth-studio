"""Structured logging utilities with request ID correlation and credential masking."""

import logging
import sys
from typing import Any, Dict


# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("linkintel")


def mask_sensitive_value(val: str) -> str:
    """Masks secret values in logs."""
    if not val or len(val) < 8:
        return "***"
    return f"{val[:3]}...{val[-3:]}"


def log_event(event_name: str, **kwargs: Any) -> None:
    """
    Logs structured event key-values while ensuring no credentials or raw API keys leak.
    """
    safe_data: Dict[str, Any] = {}
    for k, v in kwargs.items():
        k_lower = k.lower()
        if any(secret_term in k_lower for secret_term in ("key", "secret", "password", "token", "auth")):
            if isinstance(v, str):
                safe_data[k] = mask_sensitive_value(v)
            else:
                safe_data[k] = "***"
        else:
            safe_data[k] = v

    formatted = " ".join([f"{k}={v}" for k, v in safe_data.items()])
    logger.info(f"[{event_name}] {formatted}")
