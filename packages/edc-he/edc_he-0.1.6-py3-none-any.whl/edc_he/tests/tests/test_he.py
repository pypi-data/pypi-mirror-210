from django.test import TestCase
from edc_constants.constants import NOT_APPLICABLE, SECONDARY
from edc_form_validators import FormValidatorTestCaseMixin
from edc_form_validators.form_validator import FormValidator
from edc_utils import get_utcnow

from edc_he.form_validators import HeEducationFormValidatorMixin

from ..forms import HealthEconomicsForm as BaseHealthEconomicsForm
from ..models import HealthEconomics


class HealthEconomicsFormValidator(HeEducationFormValidatorMixin, FormValidator):
    def clean(self) -> None:
        self.clean_education()

    @property
    def age_in_years(self) -> int:
        return 25


class HealthEconomicsForm(BaseHealthEconomicsForm):
    form_validator_cls = HealthEconomicsFormValidator

    class Meta:
        model = HealthEconomics
        fields = "__all__"


class TestHe(FormValidatorTestCaseMixin, TestCase):
    form_validator_cls = HealthEconomicsFormValidator

    def test_form_validator_education(self):
        # subject_identifier = "1223"
        # appointment = Appointment.objects.create(
        #     subject_identifier=subject_identifier, appt_datetime=get_utcnow()
        # )
        # subject_visit = SubjectVisit.objects.create(
        #     appointment=appointment,
        #     report_datetime=get_utcnow(),
        #     subject_identifier=subject_identifier,
        # )
        cleaned_data = {
            # "subject_visit": subject_visit,
            "report_datetime": get_utcnow(),
            "education_in_years": 0,
            "education_certificate": NOT_APPLICABLE,
            "primary_school": NOT_APPLICABLE,
            "secondary_school": NOT_APPLICABLE,
            "higher_education": NOT_APPLICABLE,
        }
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        cleaned_data.update({"education_in_years": None, "education_certificate": None})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertIn("education_in_years", form._errors)
        self.assertIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 0, "education_certificate": None})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertNotIn("education_in_years", form._errors)
        self.assertIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 0, "education_certificate": SECONDARY})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 0, "education_certificate": "blah"})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 0, "education_certificate": NOT_APPLICABLE})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertNotIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 1, "education_certificate": None})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 1, "education_certificate": "blah"})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertIn("education_certificate", form._errors)

        cleaned_data.update({"education_in_years": 7, "education_certificate": SECONDARY})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertNotIn("education_certificate", form._errors)

        # years of education exceeds age
        cleaned_data.update({"education_in_years": 100, "education_certificate": None})
        form = HealthEconomicsForm(data=cleaned_data)
        form.is_valid()
        self.assertIn("education_in_years", form._errors)
