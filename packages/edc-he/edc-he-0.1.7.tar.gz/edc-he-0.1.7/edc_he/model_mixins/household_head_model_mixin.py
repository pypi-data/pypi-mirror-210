from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_constants.choices import GENDER, YES_NO
from edc_model_fields.fields import OtherCharField

from ..choices import (
    EDUCATION_CHOICES,
    EMPLOYMENT_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    ETHNICITY_CHOICES,
    MARITAL_CHOICES,
    RELATIONSHIP_CHOICES,
    RELIGION_CHOICES,
)
from ..models import InsuranceTypes


class HouseholdHeadModelMixin(models.Model):
    # head of household
    hoh = models.CharField(
        verbose_name="Are you the household head?",
        max_length=15,
        choices=YES_NO,
    )

    relationship_to_hoh = models.CharField(
        verbose_name="What is your relationship to the household head?",
        max_length=25,
        choices=RELATIONSHIP_CHOICES,
    )

    relationship_to_hoh_other = OtherCharField(
        verbose_name="If OTHER relationship, specify ...",
    )

    hoh_gender = models.CharField(
        verbose_name="Is the household head female or male?",
        max_length=15,
        choices=GENDER,
    )

    hoh_age = models.IntegerField(
        verbose_name="How old is the household head?",
        validators=[MinValueValidator(18), MaxValueValidator(110)],
        help_text="In years",
    )

    hoh_citizen = models.CharField(
        verbose_name="Is the household head a citizen of this country?",
        max_length=15,
        choices=YES_NO,
    )

    hoh_religion = models.CharField(
        verbose_name="How would you describe the household head’s religious orientation?",
        max_length=25,
        choices=RELIGION_CHOICES,
    )

    hoh_religion_other = OtherCharField(
        verbose_name="If OTHER religious orientation, specify ...",
    )

    hoh_ethnicity = models.CharField(
        verbose_name="What is the household head’s ethnic background?",
        max_length=25,
        choices=ETHNICITY_CHOICES,
    )

    hoh_ethnicity_other = OtherCharField(
        verbose_name="If OTHER ethnic background, specify ...",
    )

    hoh_education = models.CharField(
        verbose_name="Highest level of education completed by the household head?",
        max_length=25,
        choices=EDUCATION_CHOICES,
    )

    hoh_education_other = OtherCharField(
        verbose_name="If OTHER education, specify ...",
    )

    hoh_employment = models.CharField(
        verbose_name="Household head’s employment status",
        max_length=25,
        choices=EMPLOYMENT_STATUS_CHOICES,
    )

    hoh_employment_type = models.CharField(
        verbose_name="Household head’s type of employment",
        max_length=25,
        choices=EMPLOYMENT_CHOICES,
    )

    hoh_marital_status = models.CharField(
        verbose_name="Household head’s marital status",
        max_length=25,
        choices=MARITAL_CHOICES,
    )

    hoh_marital_status_other = OtherCharField(
        verbose_name="If OTHER marital status, specify ...",
    )

    hoh_insurance = models.ManyToManyField(
        InsuranceTypes,
        related_name="hohinsurancetypes",
        verbose_name="Household head’s health insurance and ‘club’ status ",
    )

    hoh_insurance_other = OtherCharField(
        verbose_name="If OTHER, specify ...",
    )

    class Meta:
        abstract = True
