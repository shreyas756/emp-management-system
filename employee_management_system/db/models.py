from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    class Meta:
        db_table = "Employee_Data"

    name = models.CharField(max_length=25)
    emp_id = models.CharField(primary_key=True, unique=True, max_length=10)
    location = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)
    email_id = models.EmailField(max_length=50)
    joining_date = models.DateField()
    last_date = models.DateField(null=True, blank=True)


class User(User):
    class Meta:
        db_table = "user_table"

    user_role = [("admin", "admin"), ("simple_user", "simple_user")]
    user_role = models.CharField(
        choices=user_role, default="simple_user", max_length=20
    )
