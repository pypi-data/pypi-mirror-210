from django.conf import settings

JWT_ALGORITHM = getattr(settings, "JWT_ALGORITHM", "ES256")
JWT_AUDIENCE = getattr(settings, "JWT_AUDIENCE", ["account", "broker"])
JWT_CERTS_URL = getattr(settings, "JWT_CERTS_URL", None)

# key from KeyCloak; value is user model
JWT_USER_MAPPING = getattr(
    settings,
    "JWT_USER_MAPPING",
    {
        "given_name": "first_name",
        "family_name": "last_name",
        "name": "username",
    },
)
JWT_USER_UID = getattr(settings, "JWT_USER_UID", "kc_id")
JWT_USER_DEFAULTS = getattr(
    settings,
    "JWT_USER_DEFAULTS",
    {
        "is_active": True,
    },
)
JWT_USER_ON_CREATE = getattr(
    settings,
    "JWT_USER_ON_CREATE",
    None,
)
JWT_USER_ON_UPDATE = getattr(
    settings,
    "JWT_USER_ON_UPDATE",
    None,
)
