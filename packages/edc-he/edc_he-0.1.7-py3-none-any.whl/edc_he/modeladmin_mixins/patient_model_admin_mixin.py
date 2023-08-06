from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple


class HealthEconomicsPatientModelAdminMixin:
    form = None

    additional_instructions = [
        "We want to learn about the household and we use these questions "
        "to get an understanding of wealth and opportunities in the community. "
    ]
    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Patient characteristics",
            {
                "fields": (
                    "pat_citizen",
                    "pat_religion",
                    "pat_religion_other",
                    "pat_ethnicity",
                    "pat_ethnicity_other",
                    "pat_education",
                    "pat_education_other",
                    "pat_employment",
                    "pat_employment_type",
                    "pat_marital_status",
                    "pat_marital_status_other",
                    "pat_insurance",
                    "pat_insurance_other",
                )
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "pat_citizen": admin.VERTICAL,
        "pat_education": admin.VERTICAL,
        "pat_employment": admin.VERTICAL,
        "pat_employment_type": admin.VERTICAL,
        "pat_ethnicity": admin.VERTICAL,
        "pat_marital_status": admin.VERTICAL,
        "pat_religion": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
    }

    filter_horizontal = ["pat_insurance"]
