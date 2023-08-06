from edc_list_data.model_mixins import ListModelManager, ListModelMixin
from edc_model.models import HistoricalRecords


class InsuranceTypes(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Insurance Types"
        verbose_name_plural = "Insurance Types"


class Nationalities(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Nationalities"
        verbose_name_plural = "Nationalities"


class Religions(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Religions"
        verbose_name_plural = "Religions"


class Ethnicities(ListModelMixin):
    objects = ListModelManager()
    history = HistoricalRecords()

    class Meta(ListModelMixin.Meta):
        verbose_name = "Ethnicities"
        verbose_name_plural = "Ethnicities"
