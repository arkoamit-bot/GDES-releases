"""
Event dispatch tests.

`_run_handlers` used to swallow every handler exception, which made the Celery
task's `self.retry()` unreachable and left `Event.processed` False forever. A
failed recompute therefore disappeared with no retry and no visible backlog.
"""
from django.test import TestCase

from . import dispatcher
from .event_types import LAB_RESULT_CREATED
from .models import Event


class _Boom:
    __name__ = "boom"

    def __call__(self, **kwargs):
        raise RuntimeError("handler exploded")


class _Ok:
    __name__ = "ok"

    def __call__(self, **kwargs):
        return None


class DispatchProcessedFlagTests(TestCase):
    def setUp(self):
        self._saved_handlers = dict(dispatcher._handlers)
        self._saved_async = set(dispatcher._async_event_types)
        dispatcher._handlers.clear()
        dispatcher._async_event_types.clear()

    def tearDown(self):
        dispatcher._handlers.clear()
        dispatcher._handlers.update(self._saved_handlers)
        dispatcher._async_event_types.clear()
        dispatcher._async_event_types.update(self._saved_async)

    def test_successful_dispatch_marks_the_event_processed(self):
        dispatcher.subscribe(LAB_RESULT_CREATED, _Ok())
        dispatcher.dispatch(LAB_RESULT_CREATED, source_model="LabResult",
                            source_pk="1", payload={"patient_id": "BGD-1"})
        event = Event.objects.get(event_type=LAB_RESULT_CREATED)
        self.assertTrue(event.processed)

    def test_failing_handler_leaves_the_event_unprocessed(self):
        dispatcher.subscribe(LAB_RESULT_CREATED, _Boom())
        with self.assertLogs("events.dispatcher", level="ERROR"):
            dispatcher.dispatch(LAB_RESULT_CREATED, source_model="LabResult",
                                source_pk="1", payload={"patient_id": "BGD-1"})
        event = Event.objects.get(event_type=LAB_RESULT_CREATED)
        self.assertFalse(event.processed,
                         "a lost recompute must stay visible in the unprocessed backlog")

    def test_one_failure_among_several_handlers_keeps_event_unprocessed(self):
        dispatcher.subscribe(LAB_RESULT_CREATED, _Ok())
        dispatcher.subscribe(LAB_RESULT_CREATED, _Boom())
        with self.assertLogs("events.dispatcher", level="ERROR"):
            dispatcher.dispatch(LAB_RESULT_CREATED, source_pk="2")
        self.assertFalse(Event.objects.get(event_type=LAB_RESULT_CREATED).processed)

    def test_run_handlers_reports_failures_instead_of_swallowing(self):
        dispatcher.subscribe(LAB_RESULT_CREATED, _Ok())
        dispatcher.subscribe(LAB_RESULT_CREATED, _Boom())
        with self.assertLogs("events.dispatcher", level="ERROR"):
            failures = dispatcher._run_handlers(LAB_RESULT_CREATED, "", "", {})
        self.assertEqual([name for name, _ in failures], ["boom"])

    def test_handler_failure_does_not_propagate_to_the_caller(self):
        # The publisher (a view) must not 500 because a recompute failed.
        dispatcher.subscribe(LAB_RESULT_CREATED, _Boom())
        with self.assertLogs("events.dispatcher", level="ERROR"):
            dispatcher.dispatch(LAB_RESULT_CREATED, source_pk="3")

    def test_mark_event_processed_updates_the_newest_matching_row(self):
        dispatcher.subscribe(LAB_RESULT_CREATED, _Boom())
        with self.assertLogs("events.dispatcher", level="ERROR"):
            dispatcher.dispatch(LAB_RESULT_CREATED, source_pk="4")
        event = Event.objects.get(source_pk="4")
        self.assertFalse(event.processed)
        dispatcher.mark_event_processed(LAB_RESULT_CREATED, source_pk="4",
                                       processed=True)
        event.refresh_from_db()
        self.assertTrue(event.processed)
