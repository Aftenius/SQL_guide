"""Check a learner key against a fixed provider endpoint."""

import httpx

from sql_guide.domain.errors import ModelCheckFailed


class HttpxModelProbe:
    """Calls the provider's model list. The key is sent only in the header."""

    def __init__(self, timeout_seconds: float = 10) -> None:
        """Store the request timeout.

        Args:
            timeout_seconds: How long to wait for the provider.
        """
        self._timeout = timeout_seconds

    async def check(self, *, base_url: str, api_key: str, model: str) -> None:
        """Confirm the provider lists the chosen model for this key.

        Args:
            base_url: Catalog endpoint, never a URL typed by the learner.
            api_key: Key to send in the Authorization header.
            model: Model name that must appear in the provider's list.

        Raises:
            ModelCheckFailed: The provider rejected the key or omitted the model.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{base_url.rstrip('/')}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                payload = response.json() if response.content else None
        except httpx.HTTPError as exc:
            raise ModelCheckFailed from exc
        if response.status_code != 200 or not _lists_model(payload, model):
            raise ModelCheckFailed


def _lists_model(payload: object, model: str) -> bool:
    if not isinstance(payload, dict):
        return False
    data = payload.get("data")
    if not isinstance(data, list):
        return False
    return any(isinstance(item, dict) and item.get("id") == model for item in data)
