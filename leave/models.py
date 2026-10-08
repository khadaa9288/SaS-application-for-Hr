from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from employees.models import Employee


class Leave(models.Model):

    LEAVE_TYPE_CHOICES = [
        ("Casual Leave", "Casual Leave"),
        ("Sick Leave", "Sick Leave"),
        ("Earned Leave", "Earned Leave"),
        ("Maternity Leave", "Maternity Leave"),
        ("Paternity Leave", "Paternity Leave"),
        ("Unpaid Leave", "Unpaid Leave"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Cancelled", "Cancelled"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    leave_type = models.CharField(
        max_length=50,
        choices=LEAVE_TYPE_CHOICES
    )

    start_date = models.DateField()

    end_date = models.DateField()

    days = models.PositiveIntegerField(
        editable=False,
        default=1
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-applied_at"]
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"

    def clean(self):
        errors = {}

        # Start/end date validation
        if self.start_date and self.end_date:

            if self.end_date < self.start_date:
                errors["end_date"] = (
                    "End date cannot be earlier than start date."
                )

        # Calculate working days
        if self.start_date and self.end_date:

            total_days = (
                self.end_date - self.start_date
            ).days + 1

            working_days = 0

            for day_number in range(total_days):

                current_date = (
                    self.start_date
                    + timedelta(days=day_number)
                )

                # Monday-Friday
                if current_date.weekday() < 5:
                    working_days += 1

            if working_days <= 0:
                errors["start_date"] = (
                    "Leave must contain at least one working day."
                )

        # Prevent overlapping leave
        if (
            self.employee_id
            and self.start_date
            and self.end_date
        ):

            overlapping_leaves = Leave.objects.filter(
                employee_id=self.employee_id,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            ).exclude(
                pk=self.pk
            ).exclude(
                status__in=["Rejected", "Cancelled"]
            )

            if overlapping_leaves.exists():
                errors["start_date"] = (
                    "This employee already has a leave request "
                    "that overlaps with the selected dates."
                )

        # Reason validation
        if self.reason and len(self.reason.strip()) < 5:
            errors["reason"] = (
                "Please provide a meaningful leave reason."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):

        if self.start_date and self.end_date:

            total_days = (
                self.end_date - self.start_date
            ).days + 1

            working_days = 0

            for day_number in range(total_days):

                current_date = (
                    self.start_date
                    + timedelta(days=day_number)
                )

                if current_date.weekday() < 5:
                    working_days += 1

            self.days = working_days

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.employee} - "
            f"{self.leave_type} - "
            f"{self.start_date} to {self.end_date}"
        )