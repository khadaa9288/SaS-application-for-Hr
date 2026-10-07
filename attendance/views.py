from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from .forms import AttendanceForm
from .models import Attendance


# ============================================================
# HR / ADMIN ACCESS
# ============================================================

def admin_required(view_func):

    return user_passes_test(
        lambda user:
            user.is_authenticated
            and (
                user.is_staff
                or user.is_superuser
                or (
                    hasattr(user, "profile")
                    and user.profile.role == "HR"
                )
            ),
        login_url="/login/"
    )(view_func)


# ============================================================
# ATTENDANCE LIST
# ============================================================

@admin_required
def attendance_list(request):

    attendances = Attendance.objects.select_related(
        "employee"
    ).all()

    present_count = attendances.filter(
        status="Present"
    ).count()

    absent_count = attendances.filter(
        status="Absent"
    ).count()

    half_day_count = attendances.filter(
        status="Half Day"
    ).count()

    leave_count = attendances.filter(
        status="Leave"
    ).count()

    context = {
        "attendances": attendances,
        "present_count": present_count,
        "absent_count": absent_count,
        "half_day_count": half_day_count,
        "leave_count": leave_count,
        "total_count": attendances.count(),
    }

    return render(
        request,
        "attendance/attendance_list.html",
        context
    )


# ============================================================
# CREATE ATTENDANCE
# ============================================================

@admin_required
def attendance_create(request):

    if request.method == "POST":

        form = AttendanceForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Attendance recorded successfully."
            )

            return redirect(
                "attendance_list"
            )

    else:

        form = AttendanceForm()

    return render(
        request,
        "attendance/attendance_form.html",
        {
            "form": form,
            "title": "Mark Attendance"
        }
    )


# ============================================================
# UPDATE ATTENDANCE
# ============================================================

@admin_required
def attendance_update(request, pk):

    attendance = get_object_or_404(
        Attendance,
        pk=pk
    )

    if request.method == "POST":

        form = AttendanceForm(
            request.POST,
            instance=attendance
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Attendance updated successfully."
            )

            return redirect(
                "attendance_list"
            )

    else:

        form = AttendanceForm(
            instance=attendance
        )

    return render(
        request,
        "attendance/attendance_form.html",
        {
            "form": form,
            "title": "Edit Attendance"
        }
    )


# ============================================================
# DELETE ATTENDANCE
# ============================================================

@admin_required
def attendance_delete(request, pk):

    attendance = get_object_or_404(
        Attendance,
        pk=pk
    )

    if request.method == "POST":

        attendance.delete()

        messages.success(
            request,
            "Attendance deleted successfully."
        )

        return redirect(
            "attendance_list"
        )

    return render(
        request,
        "attendance/attendance_confirm_delete.html",
        {
            "attendance": attendance
        }
    )
