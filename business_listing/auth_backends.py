from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(get_user_model().USERNAME_FIELD)
        if username is None or password is None:
            return None

        UserModel = get_user_model()

        # Try login by email first (case-insensitive).
        email_matches = UserModel.objects.filter(email__iexact=username)
        if email_matches.count() == 1:
            user = email_matches.first()
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user

        # Fallback to default username-based authentication.
        return super().authenticate(request, username=username, password=password, **kwargs)
