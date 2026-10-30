"""
Custom authentication backend for DeepShield AI.
Allows login with Email + Password  OR  Name + Password.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrNameBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL using either:
      - email field  (case-insensitive)
      - username field (case-insensitive)
    """

    def authenticate(self, request, identifier=None, password=None, **kwargs):
        if identifier is None or password is None:
            # Fall back to username kwarg used by Django default form
            identifier = kwargs.get('username', None)
        if identifier is None:
            return None

        # Try email first
        try:
            user = User.objects.get(email__iexact=identifier)
        except User.DoesNotExist:
            # Try username (name)
            try:
                user = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
