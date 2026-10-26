"""The model a learner chose for explanations."""

from dataclasses import dataclass

from sql_guide.domain.errors import InvalidModelChoice, InvalidModelKey

_PROVIDERS: dict[str, frozenset[str]] = {
    "deepseek": frozenset({"deepseek-chat", "deepseek-reasoner"}),
}
_BASE_URLS = {"deepseek": "https://api.deepseek.com"}


@dataclass(frozen=True, slots=True)
class ModelChoice:
    """A fixed provider and one of its models.

    Attributes:
        provider: Provider slug. The learner cannot supply a base URL.
        model: Model name accepted by that provider.
        base_url: Provider endpoint used by the learning process.
    """

    provider: str
    model: str
    base_url: str


def model_choice(provider: str, model: str) -> ModelChoice:
    """Accept a provider and model from the profile form.

    Args:
        provider: Provider slug.
        model: Model name.

    Returns:
        The catalog entry for that pair.

    Raises:
        InvalidModelChoice: The pair is not in the catalog.
    """
    allowed = _PROVIDERS.get(provider)
    if allowed is None or model not in allowed:
        raise InvalidModelChoice
    return ModelChoice(provider=provider, model=model, base_url=_BASE_URLS[provider])


def api_key(raw: str) -> str:
    """Accept a learner-supplied model key.

    Args:
        raw: Key as pasted into the profile.

    Returns:
        The key without surrounding space.

    Raises:
        InvalidModelKey: The key is empty, too short, or not a token.
    """
    key = raw.strip()
    if len(key) < 20 or len(key) > 200 or not key.startswith("sk-"):
        raise InvalidModelKey
    if any(character.isspace() for character in key) or not key.isascii():
        raise InvalidModelKey
    return key


def key_hint(key: str) -> str:
    """Return the last four characters of a key for display.

    Args:
        key: Validated API key.

    Returns:
        A short suffix that does not reconstruct the key.
    """
    return key[-4:]
