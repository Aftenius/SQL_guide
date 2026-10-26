"""Model probe that records keys and never calls a provider."""

from sql_guide.domain.errors import ModelCheckFailed


class FakeModelProbe:
    """Records check calls and can reject them."""

    def __init__(self, *, fail: bool = False) -> None:
        """Store whether the next checks should fail.

        Args:
            fail: When true, every check raises ModelCheckFailed.
        """
        self.fail = fail
        self.calls: list[tuple[str, str, str]] = []

    async def check(self, *, base_url: str, api_key: str, model: str) -> None:
        """Record the call.

        Args:
            base_url: Provider endpoint.
            api_key: Key the use case decided to check.
            model: Model name.

        Raises:
            ModelCheckFailed: The probe was constructed to fail.
        """
        self.calls.append((base_url, api_key, model))
        if self.fail:
            raise ModelCheckFailed
