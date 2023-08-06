from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = FormsCollection(Crf(show_order=1, model="reference_app.crfone", required=True))


visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="7-day-clinic",
)

visit1 = Visit(
    code="2000",
    title="Day 2",
    timepoint=1,
    rbase=relativedelta(days=7),
    rlower=relativedelta(days=6),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="7-day-clinic",
)

visit2 = Visit(
    code="3000",
    title="Day 3",
    timepoint=2,
    rbase=relativedelta(days=14),
    rlower=relativedelta(days=6),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="7-day-clinic",
)

schedule = Schedule(
    name="schedule",
    onschedule_model="reference_app.onschedule",
    offschedule_model="reference_app.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="reference_app.subjectconsent",
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)
schedule.add_visit(visit2)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="reference_app.subjectoffstudy",
    death_report_model="reference_app.deathreport",
)

visit_schedule.add_schedule(schedule)

site_visit_schedules.register(visit_schedule)
