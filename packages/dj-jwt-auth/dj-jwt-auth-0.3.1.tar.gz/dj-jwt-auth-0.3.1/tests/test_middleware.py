from http import HTTPStatus
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from jwt.api_jwt import ExpiredSignatureError

from django_jwt import settings
from django_jwt.middleware import JWTAuthMiddleware

kc_payload = {
    "sub": "12345",
    "auth0_id": "1234",
    "email": "example@bk.com",
    "name": "UserName",
    "given_name": "1st name",
    "family_name": "LastName",
    "realm_access": {
        "roles": [],
    },
}
User = get_user_model()


def _on_create(user, request):
    user.username = "on_create"
    user.save()


def _on_update(user, request):
    user.username = "on_update"
    user.save()


@patch("django_jwt.jwt.KCVerifier.verify_token", return_value=kc_payload)
class KeyCloakAuthTest(TestCase):
    def setUp(self):
        self.middleware = JWTAuthMiddleware()
        self.request = Mock()
        self.request.META = {"HTTP_AUTHORIZATION": "Bearer 1234"}

    def assertUserWithPayload(self):
        self.assertEqual(self.request.user.first_name, kc_payload["given_name"])
        self.assertEqual(self.request.user.last_name, kc_payload["family_name"])
        self.assertEqual(self.request.user.username, kc_payload["name"])
        self.assertEqual(self.request.user.email, kc_payload["email"])

    def test_keycloak_new_user(self, verify_token):
        """User is created if it doesn't exist in database"""
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.user.kc_id, "1234")
        self.assertUserWithPayload()

    def test_exists_kc_id_user(self, verify_token):
        """User exists in database by kc_id"""
        user = User.objects.create(kc_id="1234", first_name="", last_name="", username="")
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.user, user)

        # fields are updated if they are changed in KeyCloak
        self.assertUserWithPayload()

    def test_exists_email_user(self, verify_token):
        """User exists in database by email"""
        user = User.objects.create(email="example@bk.com")
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.user, user)

        # fields are updated if they are changed in KeyCloak
        self.assertUserWithPayload()

    # def test_roles(self, verify_token):
    #     """User has admin and staff roles"""
    #     verify_token.return_value["realm_access"]["roles"] = ["admin", "staff"]
    #     self.middleware.process_request(self.request)
    #     self.assertTrue(self.request.user.is_staff)
    #     self.assertTrue(self.request.user.is_superuser)

    def test_profile_info(self, verify_token):
        """User has profile info"""

        headers = {"HTTP_AUTHORIZATION": "Bearer 1234"}
        response = self.client.get(reverse("profile"), **headers)
        self.assertContains(response, kc_payload["email"])

    def test_expired_token(self, _):
        """A token has been expired"""
        with patch(
            "django_jwt.jwt.KCVerifier.verify_token",
            side_effect=ExpiredSignatureError(),
        ):
            res = self.middleware.process_request(self.request)
            self.assertEqual(HTTPStatus.UNAUTHORIZED.value, res.status_code)
            self.assertEqual(b'{"error": "expired token"}', res.content)

    def test_user_on_create(self, _):
        """User is created on create"""

        settings.JWT_USER_ON_CREATE = _on_create
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.user.username, "on_create")

    def test_user_on_update(self, _):
        """User is updated on update"""

        settings.JWT_USER_ON_UPDATE = _on_update
        User.objects.create(kc_id="1234", first_name="", last_name="", username="")
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.user.username, "on_update")
