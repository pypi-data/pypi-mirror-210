from django.contrib.sessions.models import Session
from django.test import TestCase

from splathash.engine.context.application_context import (
    SessionBasedNALOApplicationContext,
)


class TestSessionBasedNALOApplicationContext(TestCase):
    context = SessionBasedNALOApplicationContext()

    def setup(self):
        self.context.initialize(
            data={
                "MSISDN": "233 0000 000 0000",
                "NETWORK": "MTN",
                "USERDATA": "",
                "MSGTYPE": True,
                "USERID": "USER-1234",
            }
        )

    def test_initialize(self):
        self.setup()
        self.assertTrue(self.context.data.start)

    def test_update(self):
        self.setup()
        self.context.update(key="name", value="Test")
        self.assertTrue(Session.objects.filter(session_key="233 0000 000 0000").exists())

    def test_retrieve(self):
        self.setup()
        self.context.update(key="name", value="Test")
        self.assertEquals("Test", self.context.retrieve(key="name"))

    def test_next(self):
        self.setup()
        self.context.next(route="route")
        self.assertTrue(Session.objects.filter(session_key="233 0000 000 0000").exists())
        self.assertEquals("route", self.context.next())

    def test_input_data(self):
        self.setup()
        data = self.context.input_data()
        self.assertTrue(data.start)

    def test_dispose(self):
        self.setup()
        self.context.next(route="route")
        self.assertTrue(Session.objects.filter(session_key="233 0000 000 0000").exists())
        self.context.dispose()
        self.assertFalse(Session.objects.filter(session_key="233 0000 000 0000").exists())
