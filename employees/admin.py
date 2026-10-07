from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "department",
        "designation",
        "employment_type",
        "salary",
        "status",
        "joining_date",
    )

    list_filter = (
        "department",
        "employment_type",
        "status",
        "gender",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "department",
        "designation",
    )

    ordering = (
        "-created_at",
    )