from django.test import TestCase

from splathash.engine.context.application_context import ApplicationContext
from splathash.engine.router.router import BaseLookupTableRouter
from splathash.node.node import Node
from splathash.response.response_handler import UserResponseHandler


class SubResponseHandler(UserResponseHandler):
    def get_node(self, context: ApplicationContext) -> Node:
        pass


class TestBaseLookupTableRouter(TestCase):
    class SubClassRouter(BaseLookupTableRouter):
        table = {"root": lambda: SubResponseHandler()}

    def test_route(self):
        router = self.SubClassRouter()
        handler = router.route("root")

        self.assertIsInstance(handler, UserResponseHandler)
        self.assertIsInstance(handler, SubResponseHandler)
