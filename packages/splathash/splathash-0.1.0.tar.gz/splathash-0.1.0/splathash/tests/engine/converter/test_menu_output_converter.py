from django.test import TestCase

from splathash.data.node_response import NodeResponse
from splathash.engine.context.application_context import ApplicationContextFactory
from splathash.engine.converter.menu_output_converter import DefaultOutputConverter


class TestDefaultOutputConverter(TestCase):
    context = ApplicationContextFactory.default()
    menu: NodeResponse

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

        self.menu = NodeResponse(message="Hello USSD")

        self.menu.add_multiple_options(
            options={
                "1": "Continue",
                "2": "Quit",
            }
        )

    def test_convert(self):
        # setup
        self.setup()

        converter = DefaultOutputConverter()
        output = converter.convert(node_response=self.menu, context=self.context)

        self.assertEquals(output.user, "USER-1234")
