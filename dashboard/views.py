from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from employees.models import Employee


def home(request):

    return render(
        request,
        "dashboard/home.html"
    )


@login_required(login_url="/login/")
def dashboard(request):

    # Django staff/superuser accounts are always treated as HR/Admin.
    if request.user.is_staff or request.user.is_superuser:

        total_employees = Employee.objects.count()

        active_employees = Employee.objects.filter(
            status="Active"
        ).count()

        inactive_employees = Employee.objects.filter(
            status="Inactive"
        ).count()

        on_leave_employees = Employee.objects.filter(
            status="On Leave"
        ).count()

        context = {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": inactive_employees,
            "on_leave_employees": on_leave_employees,
            "present_today": 0,
            "leave_requests": 0,
            "payroll_count": 0,
        }

        return render(
            request,
            "dashboard/hr_dashboard.html",
            context
        )

    # Normal employee
    profile = request.user.profile

    if profile.role == "HR":

        total_employees = Employee.objects.count()

        context = {
            "total_employees": total_employees,
            "active_employees": Employee.objects.filter(
                status="Active"
            ).count(),
            "inactive_employees": Employee.objects.filter(
                status="Inactive"
            ).count(),
            "on_leave_employees": Employee.objects.filter(
                status="On Leave"
            ).count(),
            "present_today": 0,
            "leave_requests": 0,
            "payroll_count": 0,
        }

        return render(
            request,
            "dashboard/hr_dashboard.html",
            context
        )

    return render(
        request,
        "dashboard/employee_dashboard.html"
    )