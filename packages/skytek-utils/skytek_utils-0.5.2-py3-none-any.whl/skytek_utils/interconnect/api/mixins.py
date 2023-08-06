from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser

from .authentication import InterconnectAuthentication
from .permissions import interconnect_module_permission_factory


class _InterconnectApiAccessMixinBase:
    authentication_classes = [InterconnectAuthentication]


class _DebugInterconnectApiAccessMixinBase:
    authentication_classes = [InterconnectAuthentication, SessionAuthentication]


def interconnect_api_access_mixin_factory(*interconnected_module_names):
    base_class = (
        _DebugInterconnectApiAccessMixinBase
        if settings.DEBUG
        else _InterconnectApiAccessMixinBase
    )

    permission_class = interconnect_module_permission_factory(
        interconnected_module_names
    )
    if settings.DEBUG:
        permission_class = permission_class | IsAdminUser

    class InterconnectApiAccessMixin(base_class):
        permission_classes = [permission_class]

    return InterconnectApiAccessMixin
