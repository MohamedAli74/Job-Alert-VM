"""
Sends job alerts to a Telegram channel via the Bot HTTP API.
Used by the VM daemon (notify.py).
"""
import logging
import httpx

logger = logging.getLogger(__name__)

LOADED_MARKER = "[*LOADED*]"


def _norm(chat_id) -> str:
    """Ensure channel IDs have the -100 prefix required by the Bot API."""
    s = str(chat_id).strip()
    if s.startswith("-100"):
        return s
    if s.startswith("-"):
        return f"-100{s[1:]}"
    return f"-100{s}"


def send_telegram(job, bot_token: str, chat_id: str) -> bool:
    """Send a single job alert. Returns True on success, False on any error."""
    text = (
        f"<b>New Job Alert</b>\n\n"
        f"<b>{_esc(job.title)}</b>\n"
        f"\U0001f3e2 {_esc(job.company or 'N/A')}  \U0001f4cd {_esc(job.location or 'Remote')}\n"
        f"\U0001f6e0 {_esc(job.skills or 'N/A')}\n"
        f"\U0001f4e6 <i>{_esc(job.source_name)}</i>\n\n"
        f'<a href="{job.url}">View Job \u2192</a>'
    )
    try:
        resp = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": _norm(chat_id), "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        if resp.status_code != 200:
            logger.warning("Telegram API %s: %s", resp.status_code, resp.text[:200])
            return False
        return True
    except Exception:
        logger.exception("Failed to send Telegram notification")
        return False


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
