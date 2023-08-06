from django import forms
from edc_crf.crf_form_validator_mixins import CrfFormValidatorMixin
from edc_form_validators import FormValidatorMixin
from edc_form_validators.form_validator import FormValidator

from edc_he.form_validators import HeEducationFormValidatorMixin

from .models import HealthEconomics


class HealthEconomicsFormValidator(
    CrfFormValidatorMixin, HeEducationFormValidatorMixin, FormValidator
):
    def clean(self) -> None:
        self.clean_education()


class HealthEconomicsForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = HealthEconomicsFormValidator

    class Meta:
        model = HealthEconomics
        fields = "__all__"
