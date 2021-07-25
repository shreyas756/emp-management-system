from django.urls import path

from . import views

urlpatterns = [
    path("employee/", views.EmployeeView.as_view()),
    path("employee-details/<str:emp_id>/", views.EmployeeDetailView.as_view()),
    path("EMSuser/registration/", views.UserRegistration.as_view()),
    path("EMSuser/login/", views.EMSSignIn.as_view()),
]
