from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Q
from oauth2_provider.models import Application
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from service_objects import services

from employee_management_system.db.models import Employee, User

from .serializers import (
    CreateEmployeeDataSerializer, 
    EmployeeListSerializer,
    EMSSignupSerializer
)
from .utils import validate_limit_offset_value


class CreateEmployeeDataService(services.Service):
    def process(self):
        try:
            CreateEmployeeDataSerializer.validate_field(self.data)
            serial = CreateEmployeeDataSerializer(data=self.data)
            if serial.is_valid():
                serial_data = serial.validated_data
                Employee.objects.create(
                    name=serial_data.get("name"),
                    emp_id=serial_data.get("emp_id"),
                    location=serial_data.get("location"),
                    phone_number=serial_data.get("phone_number"),
                    email_id=serial_data.get("email_id"),
                    joining_date=serial_data.get("joining_date"),
                    last_date=serial_data.get("last_date"),
                )
                return serial.data
            raise ValidationError
        except ValidationError as e:
            raise Exception(e)
        except IntegrityError as e:
            raise Exception(e)


class EmployeeListService(services.Service):
    def process(self):
        limit, offset = validate_limit_offset_value(
            self.data.get("limit"), self.data.get("page")
        )
        search = self.data.get("search")
        if search:
            employee = Employee.objects.filter(
                Q(name=search) | Q(email_id=search)
            ).order_by("name")[offset:limit]
        else:
            employee = Employee.objects.all().order_by("name")[offset:limit]
        serial_data = EmployeeListSerializer(employee, many=True)
        return serial_data


class GetEmployeeDetailService(services.Service):
    def process(self):
        try:
            employee = Employee.objects.get(emp_id=self.data)
            if employee:
                serial_data = EmployeeListSerializer(employee)
                return serial_data
        except Employee.DoesNotExist as e:
            raise Exception(e)


class UpdateEmployeeDetailService(services.Service):
    def process(self):
        payload = self.data["payload"]
        employee = self.data["employId"]
        for key, value in payload.items():
            employee.__setattr__(key, value)
        employee.save()
        data = EmployeeListSerializer(employee)
        return data


class EMSSignUpService(services.Service):
    def process(self):
        try:
            request = self.data
            serial = EMSSignupSerializer(data=request)
            if serial.is_valid(raise_exception=True):
                serial_data = serial.validated_data
                user = User.objects.create(
                    username=serial_data["username"],
                    user_role=serial_data.get("user_role"),
                )
                user.set_password(serial_data["password"])
                user.__setattr__(
                    "is_superuser", True
                ) if user.user_role == "admin" else user.__setattr__(
                    "is_superuser", False
                )
                user.save()
                Application.objects.create(
                    user=user,
                    authorization_grant_type="password",
                    client_type="confidential",
                    name=user.user_role,
                )
                return Response(
                    f"{user.username} got signedUp successfully", status=201
                )
            raise ValidationError
        except ValidationError as e:
            return Exception(e)


class EMSSignInService(services.Service):
    def process(self):

        username = self.data["username"]
        password = self.data["password"]
        user = authenticate(username=username, password=password)
        return user, password
