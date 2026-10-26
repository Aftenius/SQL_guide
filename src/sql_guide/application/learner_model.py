"""Save and read the model key used by the learning process."""

from dataclasses import dataclass
from datetime import datetime

from sql_guide.domain.errors import InvalidModelKey
from sql_guide.domain.learner_model import LearnerModel
from sql_guide.domain.model_choice import ModelChoice, api_key, key_hint, model_choice
from sql_guide.domain.ports import Clock, ModelKeyCipher, ModelProbe, UnitOfWorkFactory
from sql_guide.domain.user import UserId


@dataclass(frozen=True, slots=True)
class ModelDescription:
    """Profile view of a saved model. The API key itself is absent.

    Attributes:
        provider: Provider slug.
        model: Model name.
        hint: Last four characters of the saved key.
        updated_at: Moment the settings were saved.
    """

    provider: str
    model: str
    hint: str
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class SaveLearnerModelCommand:
    """Model settings submitted from the profile.

    Attributes:
        user_id: Account that owns the settings.
        provider: Provider slug.
        model: Model name.
        api_key: New key, or an empty string to keep the saved key.
    """

    user_id: UserId
    provider: str
    model: str
    api_key: str


@dataclass(frozen=True, slots=True)
class CheckLearnerModelCommand:
    """A key to try against the provider before or after it is saved.

    Attributes:
        user_id: Account performing the check.
        provider: Provider slug.
        model: Model name.
        api_key: Key to try. Empty means the saved key.
    """

    user_id: UserId
    provider: str
    model: str
    api_key: str


class DescribeLearnerModel:
    """Return the saved model without its key."""

    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        """Store the unit-of-work factory.

        Args:
            uow_factory: Opens a read of the saved model.
        """
        self._uow_factory = uow_factory

    async def execute(self, user_id: UserId) -> ModelDescription | None:
        """Load the profile description.

        Args:
            user_id: Account that owns the settings.

        Returns:
            The description, or None when no key is saved.
        """
        async with self._uow_factory() as uow:
            stored = await uow.learner_models.get(user_id)
        if stored is None:
            return None
        return ModelDescription(
            provider=stored.provider,
            model=stored.model,
            hint=stored.hint,
            updated_at=stored.updated_at,
        )


class SaveLearnerModel:
    """Encrypt a model key and keep it on the account."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        cipher: ModelKeyCipher,
        clock: Clock,
    ) -> None:
        """Store the collaborators.

        Args:
            uow_factory: Opens a write of the saved model.
            cipher: Encrypts the API key before storage.
            clock: Source of the save time.
        """
        self._uow_factory = uow_factory
        self._cipher = cipher
        self._clock = clock

    async def execute(self, command: SaveLearnerModelCommand) -> ModelDescription:
        """Save the model choice and, when supplied, a new key.

        Args:
            command: Provider, model, and optional replacement key.

        Returns:
            The description stored for the profile.
        """
        choice = model_choice(command.provider, command.model)
        async with self._uow_factory() as uow:
            stored = await uow.learner_models.get(command.user_id)
            if command.api_key.strip() == "":
                if stored is None:
                    raise InvalidModelKey
                ciphertext = stored.ciphertext
                hint = stored.hint
            else:
                key = api_key(command.api_key)
                ciphertext = self._cipher.encrypt(key)
                hint = key_hint(key)
            saved = LearnerModel(
                user_id=command.user_id,
                provider=choice.provider,
                model=choice.model,
                ciphertext=ciphertext,
                hint=hint,
                updated_at=self._clock.now(),
            )
            await uow.learner_models.save(saved)
            await uow.commit()
        return ModelDescription(
            provider=saved.provider,
            model=saved.model,
            hint=saved.hint,
            updated_at=saved.updated_at,
        )


class ClearLearnerModel:
    """Remove the saved model key."""

    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        """Store the unit-of-work factory.

        Args:
            uow_factory: Opens a delete of the saved model.
        """
        self._uow_factory = uow_factory

    async def execute(self, user_id: UserId) -> None:
        """Delete the saved key. A missing key is ignored.

        Args:
            user_id: Account whose key is removed.
        """
        async with self._uow_factory() as uow:
            await uow.learner_models.delete(user_id)
            await uow.commit()


class CheckLearnerModel:
    """Ask the provider whether the key can be used."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        cipher: ModelKeyCipher,
        probe: ModelProbe,
    ) -> None:
        """Store the collaborators.

        Args:
            uow_factory: Opens a read of the saved key.
            cipher: Decrypts a saved key.
            probe: Calls the provider without logging the key.
        """
        self._uow_factory = uow_factory
        self._cipher = cipher
        self.probe = probe

    async def execute(self, command: CheckLearnerModelCommand) -> None:
        """Check a typed key, or the key already saved on the account.

        Args:
            command: Provider, model, and optional key.

        Raises:
            InvalidModelKey: No key was typed and none is saved.
            ModelKeyUnreadable: The saved key cannot be decrypted.
        """
        choice = model_choice(command.provider, command.model)
        if command.api_key.strip() == "":
            async with self._uow_factory() as uow:
                stored = await uow.learner_models.get(command.user_id)
            if stored is None:
                raise InvalidModelKey
            key = self._cipher.decrypt(stored.ciphertext)
        else:
            key = api_key(command.api_key)
        await self.probe.check(
            base_url=choice.base_url,
            api_key=key,
            model=choice.model,
        )


class ReadLearnerModelKey:
    """Decrypt the saved key for the learning process.

    HTTP responses use :class:`DescribeLearnerModel` and never this key.
    """

    def __init__(self, uow_factory: UnitOfWorkFactory, cipher: ModelKeyCipher) -> None:
        """Store the collaborators.

        Args:
            uow_factory: Opens a read of the saved model.
            cipher: Decrypts the stored key.
        """
        self._uow_factory = uow_factory
        self._cipher = cipher

    async def execute(self, user_id: UserId) -> tuple[ModelChoice, str] | None:
        """Return the choice and plaintext key for a server-side caller.

        Args:
            user_id: Account whose key is needed.

        Returns:
            The choice and key, or None when nothing is saved.
        """
        async with self._uow_factory() as uow:
            stored = await uow.learner_models.get(user_id)
        if stored is None:
            return None
        choice = model_choice(stored.provider, stored.model)
        return choice, self._cipher.decrypt(stored.ciphertext)
