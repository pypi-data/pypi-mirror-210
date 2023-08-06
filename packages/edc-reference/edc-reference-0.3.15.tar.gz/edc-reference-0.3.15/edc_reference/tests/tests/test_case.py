from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from django.test import TestCase as BaseTestCase
from edc_appointment.models import Appointment
from edc_facility import import_holidays
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from reference_app.models import SubjectConsent, SubjectVisit


class TestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.subject_identifier = "12345"
        self.subject_visits = []

        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=14),
            identity="0123456789",
            confirm_identity="0123456789",
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model("reference_app.onschedule")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

        for appointment in Appointment.objects.all().order_by("timepoint"):
            self.subject_visits.append(
                SubjectVisit.objects.create(
                    appointment=appointment,
                    subject_identifier=self.subject_identifier,
                    report_datetime=appointment.appt_datetime,
                    reason=SCHEDULED,
                    site=Site.objects.get_current(),
                    visit_schedule_name=appointment.visit_schedule_name,
                    schedule_name=appointment.schedule_name,
                )
            )
