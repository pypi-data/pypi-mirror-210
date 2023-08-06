from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_constants.choices import YES_NO_DONT_KNOW_DWTA, YES_NO_DONT_KNOW_DWTA_NA
from edc_constants.constants import NOT_APPLICABLE


class PropertyModelMixin(models.Model):
    land_owner = models.CharField(
        verbose_name="Do you own any land or other property.",
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA,
    )

    land_value_known = models.CharField(
        verbose_name="Do you know about how much is this worth in total?",
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA_NA,
        default=NOT_APPLICABLE,
        help_text="Use cash equivalent in local currency",
    )

    land_value = models.IntegerField(
        verbose_name="About how much is this worth in total?",
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        null=True,
        blank=True,
        help_text="Use cash equivalent in local currency",
    )

    land_additional = models.CharField(
        verbose_name="Do you own any other property other than your primary dwelling?",
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA,
    )

    land_additional_known = models.CharField(
        verbose_name="Do you know about how much is this worth in total?",
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA_NA,
        default=NOT_APPLICABLE,
        help_text="Use cash equivalent in local currency",
    )

    land_additional_value = models.IntegerField(
        verbose_name="About how much is this worth in total?",
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        null=True,
        blank=True,
        help_text="Use cash equivalent in local currency",
    )

    class Meta:
        abstract = True
