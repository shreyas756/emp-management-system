from django.core.exceptions import ValidationError
from rest_framework.permissions import BasePermission


def validate_limit_offset_value(limit=None, offset=None):

    limit = 5 if limit is None or limit == "" else int(limit)
    offset = 1 if offset is None or offset == "" else int(offset)

    offset = (offset - 1) * limit
    limit = offset + limit
    if len(str(offset)) > 15:
        raise ValidationError({"Page": "Page is beyond limit"})
    elif len(str(limit)) > 15:
        raise ValidationError({"Limit": "Limit is beyond the allowed limit"})
    return limit, offset


class CustomTokenMatchesOASRequirement(BasePermission):

    def has_permission(self, request, view):
        # allow all GET and PATCH requests for anonymous user.
        if request.method == "GET":
            if request.headers.get("Authorization") and request.user.username == "":
                return request.user and request.user.is_authenticated
            return True
        elif request.method == "PATCH":
            if request.headers.get("Authorization") and request.user.username == "":
                return request.user and request.user.is_authenticated
            return True
        return request.user and request.user.is_authenticated
