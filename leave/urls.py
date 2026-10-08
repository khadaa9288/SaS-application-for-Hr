from django.urls import path

from . import views

app_name = "leave"


urlpatterns = [

    # Employee leave
    path(
        "",
        views.leave_list,
        name="list",
    ),

    path(
        "apply/",
        views.leave_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.leave_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.leave_update,
        name="update",
    ),

    path(
        "<int:pk>/cancel/",
        views.leave_cancel,
        name="cancel",
    ),

    # HR/Admin approval
    path(
        "approvals/",
        views.leave_approvals,
        name="approvals",
    ),

    path(
        "<int:pk>/approve/",
        views.leave_approve,
        name="approve",
    ),

    path(
        "<int:pk>/reject/",
        views.leave_reject,
        name="reject",
    ),
]





   