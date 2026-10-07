from django import forms

from .models import Attendance


class AttendanceForm(forms.ModelForm):

    class Meta:

        model = Attendance

        fields = [
            "employee",
            "date",
            "check_in",
            "check_out",
            "status",
            "notes",
        ]

        widgets = {

            "employee": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "check_in": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),

            "check_out": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes"
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        employee = cleaned_data.get("employee")
        date = cleaned_data.get("date")
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        # ----------------------------------------------------
        # CHECK DUPLICATE ATTENDANCE
        # ----------------------------------------------------

        if employee and date:

            duplicate = Attendance.objects.filter(
                employee=employee,
                date=date
            )

            # When editing, exclude the current record
            if self.instance and self.instance.pk:
                duplicate = duplicate.exclude(
                    pk=self.instance.pk
                )

            if duplicate.exists():

                self.add_error(
                    "date",
                    "Attendance has already been recorded for this employee on this date."
                )

        # ----------------------------------------------------
        # CHECK-IN / CHECK-OUT VALIDATION
        # ----------------------------------------------------

        if check_in and check_out:

            if check_out <= check_in:

                self.add_error(
                    "check_out",
                    "Check-out time must be later than check-in time."
                )

        return cleaned_data
