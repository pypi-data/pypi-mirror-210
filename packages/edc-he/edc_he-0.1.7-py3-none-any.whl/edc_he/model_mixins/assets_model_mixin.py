from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_constants.choices import YES_NO, YES_NO_DONT_KNOW_DWTA
from edc_model_fields.fields import OtherCharField

from ..choices import (
    COOKING_FUEL_CHOICES,
    EAVES_CHOICES,
    EXTERNAL_WALL_MATERIALS_CHOICES,
    FLOOR_MATERIALS_CHOICES,
    LIGHTING_CHOICES,
    RESIDENCE_OWNERSHIP_CHOICES,
    ROOF_MATERIAL_CHOICES,
    TOILET_CHOICES,
    WATER_OBTAIN_CHOICES,
    WATER_SOURCE_CHOICES,
    WINDOW_MATERIAL_CHOICES,
    WINDOW_SCREENING_CHOICES,
    WINDOW_SCREENING_TYPE_CHOICES,
)


class AssetsModelMixin(models.Model):
    residence_ownership = models.CharField(
        verbose_name=(
            "Is the house you live in rented, owned by you (either on your own, or "
            "with someone else), or owned by someone else in your family?"
        ),
        max_length=25,
        choices=RESIDENCE_OWNERSHIP_CHOICES,
    )

    dwelling_value_known = models.CharField(
        verbose_name=(
            "If the owner [you] were to sell this dwelling today, do you know the "
            "approximate value?"
        ),
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA,
        help_text="in local currency",
    )

    dwelling_value = models.IntegerField(
        verbose_name="About how much is it worth?",
        validators=[MinValueValidator(0), MaxValueValidator(9999999999)],
        null=True,
        blank=True,
        help_text="in local currency",
    )

    rooms = models.IntegerField(
        verbose_name=(
            "How many rooms does your dwelling have in total, without counting "
            "the bathrooms/ toilets or hallways/passageways?"
        ),
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )

    bedrooms = models.IntegerField(
        verbose_name="How many rooms are used for sleeping in your dwelling?",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    beds = models.IntegerField(
        verbose_name="How many beds does your dwelling have in total?",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    water_source = models.CharField(
        verbose_name="What is the main source of drinking water for the household?",
        max_length=25,
        choices=WATER_SOURCE_CHOICES,
    )

    water_source_other = OtherCharField(verbose_name="If OTHER water source, specify")

    water_obtain_time = models.CharField(
        verbose_name="How long does it take to obtain drinking water?",
        max_length=25,
        choices=WATER_OBTAIN_CHOICES,
    )

    toilet = models.CharField(
        verbose_name="What type of toilet is mainly used in your household?",
        max_length=25,
        choices=TOILET_CHOICES,
        help_text=(
            "Note: 'private' (1-7) is a toilet solely used by the household and 'shared' "
            "(8-14) is a toilet shared by two or more households."
        ),
    )

    toilet_other = OtherCharField(verbose_name="If OTHER type of toilet, specify")

    roof_material = models.CharField(
        verbose_name="What is the major construction material of the roof?",
        max_length=25,
        choices=ROOF_MATERIAL_CHOICES,
    )

    roof_material_other = OtherCharField(verbose_name="If OTHER roof material, specify")

    eaves = models.CharField(
        verbose_name="Are the eaves open, partially or fully closed?",
        max_length=25,
        choices=EAVES_CHOICES,
    )

    external_wall_material = models.CharField(
        verbose_name="What is the major construction material of the external wall?",
        max_length=25,
        choices=EXTERNAL_WALL_MATERIALS_CHOICES,
    )

    external_wall_material_other = OtherCharField(
        verbose_name="If OTHER external wall material, specify",
    )

    external_window_material = models.CharField(
        verbose_name="What is the main material on external windows?",
        max_length=25,
        choices=WINDOW_MATERIAL_CHOICES,
    )

    external_window_material_other = OtherCharField(
        verbose_name="If OTHER external window material, specify",
    )

    window_screens = models.CharField(
        verbose_name="What is the main screening material of external windows?",
        max_length=25,
        choices=WINDOW_SCREENING_CHOICES,
    )

    window_screen_type = models.CharField(
        verbose_name="Type of screening on external windows",
        max_length=25,
        choices=WINDOW_SCREENING_TYPE_CHOICES,
    )

    floor_material = models.CharField(
        verbose_name="What is the major construction material of the floor?",
        max_length=25,
        choices=FLOOR_MATERIALS_CHOICES,
        help_text=(
            "If there are similar amounts of more than one type of flooring, "
            "select the multiple types that apply. Otherwise select the main "
            "type of flooring"
        ),
    )

    floor_material_other = OtherCharField(
        verbose_name="If OTHER floor material, specify",
    )

    electricity = models.CharField(
        verbose_name="Does your household have electricity?",
        max_length=25,
        choices=YES_NO,
    )

    lighting_source = models.CharField(
        verbose_name="What is the main source of lighting?",
        max_length=25,
        choices=LIGHTING_CHOICES,
    )

    lighting_source_other = OtherCharField(
        verbose_name="If OTHER lighting source, specify",
    )

    cooking_fuel = models.CharField(
        verbose_name="What type of fuel do you primarily use for cooking?",
        max_length=25,
        choices=COOKING_FUEL_CHOICES,
    )

    cooking_fuel_other = OtherCharField(
        verbose_name="If OTHER cooking fuel, specify",
    )

    class Meta:
        abstract = True
