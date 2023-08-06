from rest_framework.authentication import BaseAuthentication

from .jwt import jwt_to_module_user


class InterconnectAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get("Authorization", None)
        if authorization_header and authorization_header.lower().startswith("bearer "):
            _, token = authorization_header.split(" ", maxsplit=1)
            if token:
                user = jwt_to_module_user(token)
                if user:
                    return user, None

        return None
