from django.test import TestCase

from splathash.data.output_data import OutputData
from splathash.engine.converter.output_json_converter import NALOOutputJsonConverter


class TestNALOOutputJsonConverter(TestCase):
    def test_to_json(self):
        # setup
        data = OutputData(
            user="USER-1234",
            msisdn="233 000 000 0000",
            message="Test",
            require_response=True,
        )

        # execute
        converter = NALOOutputJsonConverter()
        json = converter.to_json(data)

        self.assertIsInstance(json, dict)
        self.assertEquals(json["MSG"], data.message)
        self.assertTrue(json["MSGTYPE"])
