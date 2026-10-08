from django import forms

from .models import Leave


class LeaveForm(forms.ModelForm):

    class Meta:
        model = Leave

        fields = [
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
        ]

        widgets = {
            "employee": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "leave_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter the reason for leave...",
                }
            ),
        }

        labels = {
            "employee": "Employee",
            "leave_type": "Leave Type",
            "start_date": "Start Date",
            "end_date": "End Date",
            "reason": "Reason",
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Employee dropdown ordering
        self.fields["employee"].queryset = (
            self.fields["employee"]
            .queryset
            .order_by("id")
        )

        # Required fields
        self.fields["employee"].required = True
        self.fields["leave_type"].required = True
        self.fields["start_date"].required = True
        self.fields["end_date"].required = True
        self.fields["reason"].required = True

    def clean(self):

        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        reason = cleaned_data.get("reason")

        # --------------------------------------------------
        # Date validation
        # --------------------------------------------------

        if start_date and end_date:

            if end_date < start_date:

                self.add_error(
                    "end_date",
                    "End date cannot be earlier than start date."
                )

        # --------------------------------------------------
        # Reason validation
        # --------------------------------------------------

        if reason:

            if len(reason.strip()) < 5:

                self.add_error(
                    "reason",
                    "Please provide a meaningful reason for leave."
                )

        return cleaned_data