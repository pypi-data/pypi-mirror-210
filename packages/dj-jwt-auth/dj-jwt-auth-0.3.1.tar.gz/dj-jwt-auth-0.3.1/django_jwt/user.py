from django.contrib.auth import get_user_model
from django.http.request import HttpRequest

from django_jwt import settings


class UserHandler:
    def __init__(self, payload: dict, request: HttpRequest):
        # auth0_id should be available if auth0 added in Client Scopes in KeyCloak admin
        self.kwargs = settings.JWT_USER_DEFAULTS.copy()
        self.kwargs.update(
            {ca_key: payload[kc_key] for kc_key, ca_key in settings.JWT_USER_MAPPING.items() if kc_key in payload}
        )
        self.kwargs["email"] = payload["email"].lower()
        self.kwargs[settings.JWT_USER_UID] = payload.get("auth0_id", payload["sub"])

        self.on_create = settings.JWT_USER_ON_CREATE
        self.on_update = settings.JWT_USER_ON_UPDATE
        self.request = request

    def _update_user(self, user):
        """Update user fields if they are changed in KeyCloak"""

        is_changed = False
        for key, val in self.kwargs.items():
            if getattr(user, key) != val:
                setattr(user, key, val)
                is_changed = True
        if is_changed:
            user.save(update_fields=self.kwargs.keys())

    def get_user(self):
        """
        Get user from database by kc_id or email.
        If user is not found, create new user.
        Update user fields if they are changed in KeyCloak.
        """
        model = get_user_model()
        try:
            user = model.objects.get(**{settings.JWT_USER_UID: self.kwargs[settings.JWT_USER_UID]})
        except model.DoesNotExist:
            try:
                user = model.objects.get(email=self.kwargs["email"])
            except model.DoesNotExist:
                user = model.objects.create(**self.kwargs)
                if self.on_create:
                    self.on_create(user, self.request)
                return user

        self._update_user(user)
        if self.on_update:
            self.on_update(user, self.request)
        return user
