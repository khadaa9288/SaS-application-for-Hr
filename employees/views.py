from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from .forms import EmployeeForm
from .models import Employee


def admin_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="/"
    )(view_func)


@admin_required
def employee_list(request):

    employees = Employee.objects.all()

    return render(
        request,
        "employees/employee_list.html",
        {
            "employees": employees,
        }
    )


@admin_required
def employee_create(request):

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            employee = form.save()

            messages.success(
                request,
                f"Employee {employee.first_name} {employee.last_name} added successfully."
            )

            return redirect("employee_list")

    else:

        form = EmployeeForm()

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Add Employee",
        }
    )


@admin_required
def employee_detail(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    return render(
        request,
        "employees/employee_detail.html",
        {
            "employee": employee,
        }
    )


@admin_required
def employee_update(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            employee = form.save()

            messages.success(
                request,
                "Employee information updated successfully."
            )

            return redirect(
                "employee_detail",
                pk=employee.pk
            )

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Edit Employee",
            "employee": employee,
        }
    )


@admin_required
def employee_delete(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    if request.method == "POST":

        employee_name = (
            f"{employee.first_name} "
            f"{employee.last_name}"
        )

        employee.delete()

        messages.success(
            request,
            f"{employee_name} deleted successfully."
        )

        return redirect("employee_list")

    return render(
        request,
        "employees/employee_confirm_delete.html",
        {
            "employee": employee,
        }
    )