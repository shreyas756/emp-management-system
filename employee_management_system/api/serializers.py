from rest_framework import serializers
from rest_framework.response import Response

from employee_management_system.db.models import Employee

from .constants import constant


class ValidateUrlParamSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False)


class CreateEmployeeDataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_null=False, required=True)
    emp_id = serializers.CharField(allow_null=False, required=True)
    location = serializers.CharField(allow_null=False, required=True)
    phone_number = serializers.CharField(allow_null=False, required=True)
    email_id = serializers.EmailField(allow_null=False, required=True)
    joining_date = serializers.DateField(allow_null=False, required=True)
    last_date = serializers.DateField(required=False)

    class Meta:
        model = Employee
        fields = [
            "name",
            "emp_id",
            "location",
            "phone_number",
            "email_id",
            "joining_date",
            "last_date",
        ]

    @staticmethod
    def validate_field(attrs):
        try:
            if attrs.get("joining_date") and attrs.get("last_date"):
                if attrs.get("joining_date") > attrs.get("last_date"):
                    raise serializers.ValidationError(
                        "last_date or joining_date is not correct"
                    )
            if Employee.objects.filter(email_id=attrs.get("email_id")).exists():
                raise serializers.ValidationError("This email address is already used")
            if attrs.get("phone_number"):
                int(attrs.get("phone_number"))
                if (
                    len(attrs.get("phone_number")) < 10
                    or len(attrs.get("phone_number")) > 10
                ):
                    raise serializers.ValidationError("Enter valid phone number")
                elif Employee.objects.filter(
                    phone_number=attrs.get("phone_number")
                ).exists():
                    raise serializers.ValidationError(
                        "This phone number is already used"
                    )
        except ValueError:
            raise serializers.ValidationError("enter valid phone number")


class EMSSignupSerializer(serializers.Serializer):
    USER_ROLE = [("admin", "admin"), ("simple_user", "simple_user")]
    username = serializers.CharField(max_length=25)
    password = serializers.CharField(max_length=25)
    user_role = serializers.ChoiceField(USER_ROLE, default="simple_user")


class EmployeeListSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    emp_id = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    email_id = serializers.EmailField(required=False)
    joining_date = serializers.DateField(required=False)
    last_date = serializers.DateField(required=False)


class ErrorListField(serializers.ListField):
    error = serializers.DictField()


class BaseResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    errors = ErrorListField(required=False)
    data = serializers.JSONField(required=False)
    message = serializers.CharField()
    code = serializers.IntegerField()

    @staticmethod
    def success_response(result, status):
        return Response(
            BaseResponseSerializer(
                {
                    "success": True,
                    "data": result.data
                    if isinstance(result, serializers.ModelSerializer)
                    else result,
                    "code": status,
                    "message": constant["SuccessfullyCreated"]
                    if status == 201
                    else constant["SuccessfullyCompleted"],
                }
            ).data,
            status=status,
        )

    @staticmethod
    def error_response(error, status, message):
        if isinstance(error, Exception):
            return Response(
                BaseResponseSerializer(
                    {
                        "success": False,
                        "code": status,
                        "message": message,
                        "errors": [str(error)],
                        "data": {},
                    }
                ).data,
                status=status,
            )
        if isinstance(error, list):
            return Response(
                BaseResponseSerializer(
                    {
                        "success": False,
                        "message": message,
                        "data": {},
                        "code": status,
                        "errors": error,
                    }
                ).data,
                status=status,
            )
        return Response(
            BaseResponseSerializer(
                {
                    "success": False,
                    "message": message,
                    "data": {},
                    "code": status,
                    "errors": [error],
                }
            ).data,
            status=status,
        )
