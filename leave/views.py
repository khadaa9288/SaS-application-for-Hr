from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import LeaveForm
from .models import Leave


# ============================================================
# ROLE HELPER
# ============================================================

def is_hr_or_admin(user):
    """
    Allow Django superuser/staff and HR users
    to manage leave approvals.
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser or user.is_staff:
        return True

    try:
        role = user.profile.role
        return role in ["HR", "ADMIN"]
    except Exception:
        return False


# ============================================================
# EMPLOYEE LEAVE LIST
# ============================================================

@login_required
def leave_list(request):
    """
    Display leave requests.

    HR/Admin can see all leave requests.
    Employees see their own leave requests.
    """

    if is_hr_or_admin(request.user):

        leaves = (
            Leave.objects
            .select_related("employee")
            .all()
            .order_by("-applied_at")
        )

    else:

        try:
            employee = request.user.employee
            leaves = (
                Leave.objects
                .filter(employee=employee)
                .order_by("-applied_at")
            )

        except Exception:

            leaves = Leave.objects.none()

    return render(
        request,
        "leave/leave_list.html",
        {
            "leaves": leaves,
            "is_hr_or_admin": is_hr_or_admin(request.user),
        },
    )


# ============================================================
# CREATE LEAVE
# ============================================================

@login_required
def leave_create(request):

    if request.method == "POST":

        form = LeaveForm(request.POST)

        if form.is_valid():

            leave = form.save(commit=False)

            try:
                employee = request.user.employee
            except Exception:

                messages.error(
                    request,
                    "Employee profile was not found for your account."
                )

                return redirect("dashboard")

            leave.employee = employee
            leave.status = "Pending"
            leave.save()

            messages.success(
                request,
                "Leave request submitted successfully."
            )

            return redirect("leave:list")

    else:

        form = LeaveForm()

    return render(
        request,
        "leave/leave_form.html",
        {
            "form": form,
            "title": "Apply for Leave",
        },
    )


# ============================================================
# LEAVE DETAIL
# ============================================================

@login_required
def leave_detail(request, pk):

    leave = get_object_or_404(
        Leave.objects.select_related("employee"),
        pk=pk,
    )

    return render(
        request,
        "leave/leave_detail.html",
        {
            "leave": leave,
            "is_hr_or_admin": is_hr_or_admin(request.user),
        },
    )


# ============================================================
# UPDATE LEAVE
# ============================================================

@login_required
def leave_update(request, pk):

    leave = get_object_or_404(Leave, pk=pk)

    if leave.status != "Pending":

        messages.error(
            request,
            "Only pending leave requests can be edited."
        )

        return redirect("leave:detail", pk=leave.pk)

    try:
        employee = request.user.employee

        if leave.employee != employee:

            messages.error(
                request,
                "You are not allowed to edit this leave request."
            )

            return redirect("leave:list")

    except Exception:

        messages.error(
            request,
            "Employee profile was not found."
        )

        return redirect("leave:list")

    if request.method == "POST":

        form = LeaveForm(
            request.POST,
            instance=leave,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Leave request updated successfully."
            )

            return redirect(
                "leave:detail",
                pk=leave.pk,
            )

    else:

        form = LeaveForm(instance=leave)

    return render(
        request,
        "leave/leave_form.html",
        {
            "form": form,
            "title": "Edit Leave Request",
            "leave": leave,
        },
    )


# ============================================================
# CANCEL LEAVE
# ============================================================

@login_required
def leave_cancel(request, pk):

    leave = get_object_or_404(Leave, pk=pk)

    if leave.status != "Pending":

        messages.error(
            request,
            "Only pending leave requests can be cancelled."
        )

        return redirect(
            "leave:detail",
            pk=leave.pk,
        )

    try:
        employee = request.user.employee

        if leave.employee != employee:

            messages.error(
                request,
                "You are not allowed to cancel this leave request."
            )

            return redirect("leave:list")

    except Exception:

        messages.error(
            request,
            "Employee profile was not found."
        )

        return redirect("leave:list")

    if request.method == "POST":

        leave.status = "Cancelled"
        leave.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Leave request cancelled successfully."
        )

    return redirect(
        "leave:list"
    )


# ============================================================
# HR / ADMIN — PENDING LEAVE APPROVAL PAGE
# ============================================================

@login_required
def leave_approvals(request):

    if not is_hr_or_admin(request.user):

        messages.error(
            request,
            "You are not authorized to access leave approvals."
        )

        return redirect("leave:list")

    pending_leaves = (
        Leave.objects
        .select_related("employee")
        .filter(status="Pending")
        .order_by("-applied_at")
    )

    return render(
        request,
        "leave/leave_approvals.html",
        {
            "pending_leaves": pending_leaves,
        },
    )


# ============================================================
# HR / ADMIN — APPROVE LEAVE
# ============================================================

@login_required
def leave_approve(request, pk):

    if not is_hr_or_admin(request.user):

        messages.error(
            request,
            "You are not authorized to approve leave requests."
        )

        return redirect("leave:list")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect("leave:approvals")

    with transaction.atomic():

        leave = get_object_or_404(
            Leave.objects.select_for_update(),
            pk=pk,
        )

        if leave.status != "Pending":

            messages.warning(
                request,
                "This leave request has already been processed."
            )

            return redirect("leave:approvals")

        leave.status = "Approved"
        leave.approved_at = timezone.now()

        leave.save(
            update_fields=[
                "status",
                "approved_at",
                "updated_at",
            ]
        )

    messages.success(
        request,
        f"Leave request for {leave.employee} approved successfully."
    )

    return redirect("leave:approvals")


# ============================================================
# HR / ADMIN — REJECT LEAVE
# ============================================================

@login_required
def leave_reject(request, pk):

    if not is_hr_or_admin(request.user):

        messages.error(
            request,
            "You are not authorized to reject leave requests."
        )

        return redirect("leave:list")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request method."
        )

        return redirect("leave:approvals")

    with transaction.atomic():

        leave = get_object_or_404(
            Leave.objects.select_for_update(),
            pk=pk,
        )

        if leave.status != "Pending":

            messages.warning(
                request,
                "This leave request has already been processed."
            )

            return redirect("leave:approvals")

        leave.status = "Rejected"
        leave.approved_at = None

        leave.save(
            update_fields=[
                "status",
                "approved_at",
                "updated_at",
            ]
        )

    messages.success(
        request,
        f"Leave request for {leave.employee} rejected."
    )

    return redirect("leave:approvals")