from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    return render(
        request,
        "dashboard/home.html"
    )


@login_required(login_url="/login/")
def dashboard(request):

    profile = request.user.profile

    if profile.role == "HR":
        return render(
            request,
            "dashboard/hr_dashboard.html"
        )

    return render(
        request,
        "dashboard/employee_dashboard.html"
    )