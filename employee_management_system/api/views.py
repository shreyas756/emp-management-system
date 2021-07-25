import requests
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import Application
from rest_framework.response import Response
from rest_framework.views import APIView

from employee_management_system.db.models import Employee
from employee_management_system.settings import HOSTNAME

from .controller import (
    CreateEmployeeDataService, 
    EmployeeListService,
    EMSSignInService, 
    EMSSignUpService,
    GetEmployeeDetailService, 
    UpdateEmployeeDetailService
)
from .serializers import (
    BaseResponseSerializer, 
    CreateEmployeeDataSerializer,
    EmployeeListSerializer, 
    ValidateUrlParamSerializer
)
from .utils import CustomTokenMatchesOASRequirement


class EmployeeView(APIView):
    @staticmethod
    def post(request):
        try:
            result = CreateEmployeeDataService.execute(request.data)
            return Response(
                BaseResponseSerializer.success_response(result, 201).data, 201
            )
        except Exception as e:
            return Response(
                BaseResponseSerializer.error_response(e, 400, "An Error Occurred").data,
                400,
            )

    @staticmethod
    def get(request):
        try:
            serializer = ValidateUrlParamSerializer(data=request.GET)
            if serializer.is_valid(raise_exception=True):
                result = EmployeeListService.execute(serializer.validated_data)
            return Response(
                BaseResponseSerializer.success_response(result.data, 200).data, 200
            )
        except Exception as e:
            return Response(
                BaseResponseSerializer.error_response(
                    e.args, 400, "An Error Occurred"
                ).data,
                400,
            )


class EmployeeDetailView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [CustomTokenMatchesOASRequirement]
    required_alternate_scopes = {"DELETE": [["delete"]]}

    @staticmethod
    def get(_, emp_id):
        try:
            result = GetEmployeeDetailService.execute(emp_id)
            return Response(
                BaseResponseSerializer.success_response(result.data, 200).data, 200
            )
        except Exception as e:
            return Response(
                BaseResponseSerializer.error_response(
                    e, 404, "Employee Id does not exist"
                ).data,
                404,
            )

    @staticmethod
    def patch(request, emp_id):
        try:
            employee = Employee.objects.get(emp_id=emp_id)
            CreateEmployeeDataSerializer.validate_field(request.data)
            if (
                request.data.get("empId") is not None
                or request.data.get("emailId") is not None
            ):
                return Response(
                    BaseResponseSerializer.error_response(
                        {}, 400, "You can not update this field"
                    ).data,
                    404,
                )
            serial = EmployeeListSerializer(data=request.data)
            if serial.is_valid():
                serial_data = serial.validated_data
                result = UpdateEmployeeDetailService.execute(
                    {"employId": employee, "payload": serial_data}
                )
                return Response(
                    BaseResponseSerializer.success_response(result.data, 200).data, 200
                )
            return Response(
                BaseResponseSerializer.error_response(serial, "An Error Occurred").data,
                400,
            )
        except Employee.DoesNotExist as e:
            return Response(
                BaseResponseSerializer.error_response(e, 404, "An Error Occurred").data,
                404,
            )
        except Exception as e:
            return Response(
                BaseResponseSerializer.error_response(e, 400, "An Error Occurred").data,
                400,
            )

    @staticmethod
    def delete(request, emp_id):
        try:
            if request.user.is_superuser:
                Employee.objects.get(emp_id=emp_id).delete()
                return Response(
                    BaseResponseSerializer.success_response({}, 200).data, 200
                )
            return Response(
                BaseResponseSerializer.error_response(
                    {}, 403, "You don't have permission to perform this action"
                ).data,
                403,
            )
        except Employee.DoesNotExist as e:
            return Response(
                BaseResponseSerializer.error_response(
                    e, 404, "Employee Id does not exist"
                ).data,
                404,
            )


class UserRegistration(APIView):
    @staticmethod
    def post(request):
        return EMSSignUpService.execute(request.data)


class EMSSignIn(APIView):
    @staticmethod
    def post(request):
        try:
            user, password = EMSSignInService.execute(request.data)
            if user:
                application = Application.objects.get(user_id=user.id)
                data = {
                    "username": user,
                    "password": password,
                    "grant_type": "password",
                    "client_id": application.client_id,
                    "client_secret": application.client_secret,
                }
                token = requests.post(HOSTNAME + "o/token/", data=data)
                return Response(token.json(), status=200)
        except Exception:
            return Response("Something Went Wrong")
