from http import HTTPStatus
from logging import getLogger

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError

from django_jwt.jwt import verifier
from django_jwt.user import UserHandler

log = getLogger(__name__)


class JWTAuthMiddleware(MiddlewareMixin):
    header_key = "HTTP_AUTHORIZATION"

    def process_request(self, request):
        if self.header_key not in request.META:
            return

        auth_header = request.META[self.header_key]
        if not auth_header.startswith("Bearer "):
            return

        token = auth_header[7:]
        try:
            info = verifier.verify_token(token)
        except ExpiredSignatureError:
            return JsonResponse(status=HTTPStatus.UNAUTHORIZED.value, data={"detail": "expired token"})
        except Exception as exc:
            log.error("Unexpected error", exc)
            return
        request.user = request._cached_user = UserHandler(info, request).get_user()
