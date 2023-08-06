from __future__ import annotations

from django.db import models
from edc_constants.choices import YES_NO

default_field_data = {
    "radio": "Radio",
    "television": "Television",
    "mobile_phone": "Mobile phone",
    "computer": "Computer",
    "telephone": "Non-mobile telephone",
    "fridge": "Fridge",
    "generator": "Generator",
    "iron": "Iron",
    "bicycle": "Bicycle",
    "motorcycle": "Motorcycle/scooter (PikiPiki/Boda Boda)",
    "dala_dala": "Dala Dala",
    "car": "Car",
    "motorboat": "Boat with a motor",
    "large_livestock": "Large Livestock (e.g. cows, bulls, other cattle, horses, donkeys)",
    "small_animals": "Small animals (goats, sheep, chickens or other poultry, etc)",
    "shop": "A business or shop",
}


def assets_model_mixin_factory(field_data: dict[str, str] | None = None):
    field_data = field_data or default_field_data

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {}
    for field_name, prompt in field_data.items():
        opts.update(
            {
                field_name: models.CharField(
                    verbose_name=prompt,
                    max_length=15,
                    choices=YES_NO,
                ),
            }
        )
    for fld_name, fld_cls in opts.items():
        AbstractModel.add_to_class(fld_name, fld_cls)

    return AbstractModel
