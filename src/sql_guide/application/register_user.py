"""Open an account and its progress root together."""

from sql_guide.application.identity import LearnerView, RegisterCommand
from sql_guide.domain.learner import LearnerProfile
from sql_guide.domain.ports import Clock, IdGenerator, PasswordHasher, UnitOfWorkFactory
from sql_guide.domain.user import Email, User, UserId, require_strong_password


class RegisterUser:
    """Create an account and the progress record that belongs to it."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        hasher: PasswordHasher,
        ids: IdGenerator,
        clock: Clock,
    ) -> None:
        """Store the ports this use case needs.

        Args:
            uow_factory: Opens the transaction for the new account.
            hasher: Turns the plain password into a stored hash.
            ids: Supplies the new account id.
            clock: Supplies the creation time.
        """
        self._uow_factory = uow_factory
        self._hasher = hasher
        self._ids = ids
        self._clock = clock

    async def execute(self, command: RegisterCommand) -> LearnerView:
        """Register a learner.

        Args:
            command: Email and password from the registration form.

        Returns:
            The new account and the moment its progress root was created.

        Raises:
            InvalidEmail: The email is malformed.
            WeakPassword: The password is too short.
            EmailAlreadyRegistered: An account already uses this email.
        """
        email = Email.parse(command.email)
        require_strong_password(command.password)
        created_at = self._clock.now()
        user = User(
            id=UserId(self._ids.new_id()),
            email=email,
            password_hash=self._hasher.hash(command.password),
            created_at=created_at,
        )
        profile = LearnerProfile(user_id=user.id, created_at=created_at)
        async with self._uow_factory() as uow:
            await uow.users.add(user)
            await uow.profiles.add(profile)
            await uow.commit()
        return LearnerView(
            id=user.id.value,
            email=user.email.value,
            profile_created_at=profile.created_at,
        )
