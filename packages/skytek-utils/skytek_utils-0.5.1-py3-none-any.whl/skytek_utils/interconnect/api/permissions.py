from typing import Iterable

from rest_framework.permissions import BasePermission


class _InterconnectModulePermissionBase(BasePermission):
    allowed_modules: tuple[str] = ()

    def has_permission(self, request, view):
        return (
            hasattr(request, "user")
            and getattr(request.user, "is_interconnected_module", False)
            and getattr(request.user, "module_name", None)
            in self.__class__.allowed_modules
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


def interconnect_module_permission_factory(allowed_module_names: Iterable[str]):
    class NamedInterconnectModulePermission(_InterconnectModulePermissionBase):
        allowed_modules = tuple(allowed_module_names)

    return NamedInterconnectModulePermission
