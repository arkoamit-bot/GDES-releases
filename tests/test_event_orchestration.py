import pytest
from unittest.mock import MagicMock

from events.dispatcher import (
    _handlers,
    dispatch,
    subscribe,
    unsubscribe,
)
from events.event_types import (
    PATIENT_REGISTERED,
    PATIENT_UPDATED,
    LAB_RESULT_CREATED,
    OUTCOME_RECORDED,
    PRESCRIPTION_CREATED,
    SAFETY_ALERT_RAISED,
)
from events.models import Event, EventSubscription


pytestmark = pytest.mark.django_db


class TestEventTypes:
    def test_constants_are_strings(self):
        assert isinstance(PATIENT_REGISTERED, str)
        assert isinstance(OUTCOME_RECORDED, str)

    def test_major_event_types_present(self):
        for ev in [PATIENT_REGISTERED, PATIENT_UPDATED, LAB_RESULT_CREATED,
                   OUTCOME_RECORDED, PRESCRIPTION_CREATED, SAFETY_ALERT_RAISED]:
            assert isinstance(ev, str) and len(ev) > 0


class TestDispatcher:
    def setup_method(self):
        _handlers.clear()

    def test_subscribe_and_dispatch(self):
        handler = MagicMock()
        subscribe(PATIENT_REGISTERED, handler)
        try:
            dispatch(PATIENT_REGISTERED, source_model="Patient", source_pk="1", payload={"name": "test"})
            handler.assert_called_once_with(
                event_type=PATIENT_REGISTERED,
                source_model="Patient",
                source_pk="1",
                payload={"name": "test"},
            )
        finally:
            unsubscribe(PATIENT_REGISTERED, handler)

    def test_unsubscribe(self):
        handler = MagicMock()
        subscribe(PATIENT_REGISTERED, handler)
        unsubscribe(PATIENT_REGISTERED, handler)
        dispatch(PATIENT_REGISTERED, source_model="Patient", source_pk="1")
        handler.assert_not_called()

    def test_multiple_handlers(self):
        h1 = MagicMock()
        h2 = MagicMock()
        subscribe(PATIENT_REGISTERED, h1)
        subscribe(PATIENT_REGISTERED, h2)
        try:
            dispatch(PATIENT_REGISTERED, source_model="Patient", source_pk="99")
            h1.assert_called_once_with(event_type=PATIENT_REGISTERED, source_model="Patient", source_pk="99", payload={})
            h2.assert_called_once_with(event_type=PATIENT_REGISTERED, source_model="Patient", source_pk="99", payload={})
        finally:
            unsubscribe(PATIENT_REGISTERED, h1)
            unsubscribe(PATIENT_REGISTERED, h2)

    def test_dispatch_no_subscribers_does_not_raise(self):
        dispatch(PATIENT_REGISTERED, source_model="Patient", source_pk="1")

    def test_handler_exception_does_not_block(self):
        def failing_handler(**kwargs):
            raise ValueError("handler error")

        h2 = MagicMock()
        subscribe(PATIENT_REGISTERED, failing_handler)
        subscribe(PATIENT_REGISTERED, h2)
        try:
            dispatch(PATIENT_REGISTERED, source_model="Patient", source_pk="1")
            h2.assert_called_once()
        finally:
            unsubscribe(PATIENT_REGISTERED, failing_handler)
            unsubscribe(PATIENT_REGISTERED, h2)


class TestEventModel:
    def test_create_event(self):
        event = Event.objects.create(
            event_type=PATIENT_REGISTERED,
            source_model="Patient",
            source_pk="1",
            payload={"name": "test"},
        )
        assert event.event_type == PATIENT_REGISTERED
        assert event.payload == {"name": "test"}
        assert event.occurred_at is not None

    def test_event_str(self):
        event = Event.objects.create(
            event_type=LAB_RESULT_CREATED,
            source_model="LabResult",
            source_pk="42",
            payload={},
        )
        assert LAB_RESULT_CREATED in str(event)

    def test_event_ordering(self):
        e1 = Event.objects.create(event_type=PATIENT_REGISTERED)
        e2 = Event.objects.create(event_type=PATIENT_UPDATED)
        events = list(Event.objects.all())
        assert events[0] == e2
        assert events[1] == e1

    def test_dispatch_persists_event(self):
        dispatch(PATIENT_REGISTERED, source_model="Patient", source_pk="1", payload={"name": "test"})
        assert Event.objects.filter(event_type=PATIENT_REGISTERED).count() == 1


class TestEventSubscriptionModel:
    def test_create_subscription(self):
        sub = EventSubscription.objects.create(
            event_type=PATIENT_REGISTERED,
            handler_path="tests.test_event_orchestration.dummy_handler",
        )
        assert sub.event_type == PATIENT_REGISTERED
        assert sub.active is True

    def test_subscription_str(self):
        sub = EventSubscription.objects.create(
            event_type=PATIENT_REGISTERED,
            handler_path="tests.test_event_orchestration.dummy_handler",
        )
        assert PATIENT_REGISTERED in str(sub)

    def test_disable_subscription(self):
        sub = EventSubscription.objects.create(
            event_type=LAB_RESULT_CREATED,
            handler_path="tests.test_event_orchestration.dummy_handler",
        )
        sub.active = False
        sub.save()
        sub.refresh_from_db()
        assert sub.active is False

    def test_unique_together(self):
        EventSubscription.objects.create(
            event_type=PATIENT_REGISTERED,
            handler_path="tests.test_event_orchestration.dummy_handler",
        )
        with pytest.raises(Exception):
            EventSubscription.objects.create(
                event_type=PATIENT_REGISTERED,
                handler_path="tests.test_event_orchestration.dummy_handler",
            )


def dummy_handler(**kwargs):
    pass
