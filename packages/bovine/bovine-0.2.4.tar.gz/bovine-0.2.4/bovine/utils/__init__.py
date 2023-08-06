from datetime import datetime, timezone
from typing import Optional, Tuple


def webfinger_response_json(name: str, url: str, domain: str) -> dict:
    """helper to generate a webfinger response"""
    return {
        "subject": f"acct:{name}@{domain}",
        "links": [
            {
                "href": url,
                "rel": "self",
                "type": "application/activity+json",
            }
        ],
    }


def parse_fediverse_handle(account: str) -> Tuple[str, Optional[str]]:
    """Splits fediverse handle in name and domain"""
    if account[0] == "@":
        account = account[1:]

    if "@" in account:
        return tuple(account.split("@", 1))
    return account, None


def now_isoformat() -> str:
    return (
        datetime.now(tz=timezone.utc).replace(microsecond=0, tzinfo=None).isoformat()
        + "Z"
    )
