from django.db import models

from employees.models import Employee


class Attendance(models.Model):

    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Half Day", "Half Day"),
        ("Leave", "Leave"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Present"
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-date",
            "-created_at"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="unique_employee_attendance_per_day"
            )
        ]

    def __str__(self):

        return (
            f"{self.employee.first_name} "
            f"{self.employee.last_name} - "
            f"{self.date} - "
            f"{self.status}"
        )

    @property
    def working_hours(self):

        if not self.check_in or not self.check_out:
            return 0

        from datetime import datetime

        start = datetime.combine(
            self.date,
            self.check_in
        )

        end = datetime.combine(
            self.date,
            self.check_out
        )

        difference = end - start

        return round(
            difference.total_seconds() / 3600,
            2
        )