from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class HouseholdModelMixin(models.Model):
    hh_count = models.IntegerField(
        verbose_name="What is the total number of people who live in your household?",
        validators=[MinValueValidator(1), MaxValueValidator(25)],
    )

    hh_minors_count = models.IntegerField(
        verbose_name=(
            "What is the total number of people 14 years or under "
            "who live in your household?"
        ),
        validators=[MinValueValidator(0), MaxValueValidator(25)],
    )

    class Meta:
        abstract = True
