from __future__ import annotations

from django.db import models
from edc_constants.choices import YES_NO_DONT_KNOW_DWTA
from edc_constants.constants import NOT_APPLICABLE

from ...choices import INCOME_TIME_ESTIMATE_CHOICES

default_field_data = {
    "wages": "Income from wages, salary from job",
    "selling": "Earnings from selling, trading or hawking products?",
    "rental_income": "Income from rental of property?",
    "pension": (
        (
            "State old-age (veteran's/civil service) pension*, contributory pension "
            "fund, provident fund or social security benefit?"
        ),
        "Pensions by work",
    ),
    "ngo_assistance": "Assistance from nongovernmental organization",
    "interest": (
        "Interest, dividends",
        "(for example, from savings account or fixed deposits)?",
    ),
    "internal_remittance": (
        "Money transfers from family members or friends residing inside the country"
    ),
    "external_remittance": (
        "Money transfers from family members or friends residing outside the country"
    ),
    "more_sources": "Do you have additional sources of income not included above?",
}


def income_model_mixin_factory(field_data: dict[str, str] | None = None):
    field_data = field_data or default_field_data

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {}
    for field_name, prompt in field_data.items():
        try:
            prompt, help_text = prompt
        except ValueError:
            help_text = None
        opts.update(
            {
                field_name: models.CharField(
                    verbose_name=prompt,
                    max_length=15,
                    choices=YES_NO_DONT_KNOW_DWTA,
                    help_text=help_text,
                ),
                f"{field_name}_value_known": models.CharField(
                    verbose_name="Over which <u>time period</u> are you able to estimate?",
                    max_length=15,
                    choices=INCOME_TIME_ESTIMATE_CHOICES,
                    default=NOT_APPLICABLE,
                ),
                f"{field_name}_value": models.IntegerField(
                    verbose_name=(
                        "Estimated <u>total amount of income</u> from this source over the "
                        "time period from above"
                    ),
                    null=True,
                    blank=True,
                ),
            }
        )
    for fld_name, fld_cls in opts.items():
        AbstractModel.add_to_class(fld_name, fld_cls)

    return AbstractModel
