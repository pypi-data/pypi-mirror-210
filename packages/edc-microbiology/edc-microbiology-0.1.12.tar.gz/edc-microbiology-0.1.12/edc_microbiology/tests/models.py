from django.db import models
from edc_appointment.model_mixins import AppointmentModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin


class Appointment(AppointmentModelMixin, SiteModelMixin, BaseUuidModel):
    def raise_if_offstudy(self, **kwargs):
        pass

    def timepoint_open_or_raise(self):
        pass

    def update_timepoint(self):
        pass

    class Meta(BaseUuidModel.Meta):
        pass


class SubjectVisit(VisitModelMixin, BaseUuidModel):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.PROTECT, related_name="subjectvisittest"
    )

    def raise_if_offstudy(self):
        pass

    class Meta(VisitModelMixin.Meta, BaseUuidModel.Meta):
        pass
