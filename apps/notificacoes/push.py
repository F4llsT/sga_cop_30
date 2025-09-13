import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"


def _build_auth_header(api_key: str) -> dict:
    """Return proper Authorization header for OneSignal.
    - Chaves novas (v2) iniciam com 'os_' e usam 'Bearer'.
    - Chaves antigas usam 'Basic'.
    """
    if not api_key:
        return {}
    scheme = "Bearer" if api_key.startswith("os_") else "Basic"
    return {"Authorization": f"{scheme} {api_key}"}


def send_push_to_user(user_external_id: str, title: str, message: str, url: str | None = None) -> bool:
    """
    Sends a Web Push notification using OneSignal to a specific user identified by external_id.

    Args:
        user_external_id: The external_id associated with the user in OneSignal (we use Django user.id).
        title: Notification title.
        message: Notification message/body.
        url: Optional URL to open when the notification is clicked.

    Returns:
        True if the request was accepted by OneSignal, False otherwise.
    """
    app_id = getattr(settings, 'ONESIGNAL_APP_ID', '')
    api_key = getattr(settings, 'ONESIGNAL_REST_API_KEY', '')

    if not app_id or not api_key:
        logger.warning("OneSignal credentials are not configured. Skipping push.")
        return False

    payload = {
        "app_id": app_id,
        # Necessário quando usa include_aliases/external_id com a API v16
        "target_channel": "webpush",
        "headings": {"en": title, "pt": title},
        "contents": {"en": message, "pt": message},
        "include_aliases": {"external_id": [str(user_external_id)]},
    }

    if url:
        payload["url"] = url

    headers = {
        **_build_auth_header(api_key),
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            ONESIGNAL_API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        if resp.status_code in (200, 201, 202):
            logger.info("OneSignal push accepted: %s", resp.text)
            return True
        logger.error("OneSignal push failed (%s): %s", resp.status_code, resp.text)
        return False
    except requests.RequestException as exc:
        logger.exception("Error sending OneSignal push: %s", exc)
        return False
