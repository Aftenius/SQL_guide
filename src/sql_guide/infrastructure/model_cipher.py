"""Fernet encryption for learner model keys."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from sql_guide.domain.errors import ModelKeyUnreadable


class FernetModelCipher:
    """Encrypts API keys with a key derived from the process secret."""

    def __init__(self, secret: str) -> None:
        """Derive a Fernet key from the process secret.

        Args:
            secret: ``MODEL_SECRET``, or the JWT secret when that is unset.
        """
        digest = hashlib.sha256(secret.encode()).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(digest))

    def encrypt(self, secret: str) -> str:
        """Encrypt an API key.

        Args:
            secret: Validated API key.

        Returns:
            A Fernet token.
        """
        return self._fernet.encrypt(secret.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a stored API key.

        Args:
            ciphertext: Fernet token from storage.

        Returns:
            The API key.

        Raises:
            ModelKeyUnreadable: The token does not match this process secret.
        """
        try:
            return self._fernet.decrypt(ciphertext.encode(), ttl=None).decode()
        except (InvalidToken, ValueError) as exc:
            raise ModelKeyUnreadable from exc
