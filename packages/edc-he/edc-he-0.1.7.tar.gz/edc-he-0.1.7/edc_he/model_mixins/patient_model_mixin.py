from django.db import models
from edc_constants.choices import YES_NO
from edc_model_fields.fields import OtherCharField

from ..choices import (
    EDUCATION_CHOICES,
    EMPLOYMENT_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    ETHNICITY_CHOICES,
    MARITAL_CHOICES,
    RELIGION_CHOICES,
)
from ..models import InsuranceTypes


class PatientModelMixin(models.Model):
    pat_citizen = models.CharField(
        verbose_name="Is the patient a citizen of this country?",
        max_length=15,
        choices=YES_NO,
    )

    pat_religion = models.CharField(
        verbose_name="How would you describe your religious orientation?",
        max_length=25,
        choices=RELIGION_CHOICES,
    )

    pat_religion_other = OtherCharField(
        verbose_name="If OTHER religious orientation, specify ...",
    )

    pat_ethnicity = models.CharField(
        verbose_name="What is your ethnic background?",
        max_length=25,
        choices=ETHNICITY_CHOICES,
    )

    pat_ethnicity_other = OtherCharField(
        verbose_name="If OTHER ethnic background, specify ...",
    )

    pat_education = models.CharField(
        verbose_name="Highest level of education completed?",
        max_length=25,
        choices=EDUCATION_CHOICES,
    )
    pat_education_other = OtherCharField(
        verbose_name="If OTHER level of education, specify ...",
    )

    pat_employment = models.CharField(
        verbose_name="What is your employment status?",
        max_length=25,
        choices=EMPLOYMENT_STATUS_CHOICES,
    )

    pat_employment_type = models.CharField(
        verbose_name="What is your type of employment?",
        max_length=25,
        choices=EMPLOYMENT_CHOICES,
    )

    pat_marital_status = models.CharField(
        verbose_name="What is your marital status?",
        max_length=25,
        choices=MARITAL_CHOICES,
    )
    pat_marital_status_other = OtherCharField(
        verbose_name="If OTHER marital status, specify ...",
    )

    pat_insurance = models.ManyToManyField(
        InsuranceTypes,
        related_name="patinsurancetypes",
        verbose_name="What is your health insurance status?",
    )

    pat_insurance_other = OtherCharField(
        verbose_name="If OTHER health insurance status, specify ...",
    )

    class Meta:
        abstract = True
