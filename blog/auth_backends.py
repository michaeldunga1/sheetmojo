from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate with either username or email in the username field."""

    def user_can_authenticate(self, user):
        if not super().user_can_authenticate(user):
            return False
        profile = getattr(user, "profile", None)
        if not profile:
            return True
        return not profile.is_currently_suspended

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(get_user_model().USERNAME_FIELD)
        if username is None or password is None:
            return None

        UserModel = get_user_model()
        identifier = username.strip()
        if not identifier:
            return None

        # If multiple users share an email, fail closed for safety.
        users = UserModel._default_manager.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        )
        if users.count() != 1:
            return None

        user = users.first()
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
