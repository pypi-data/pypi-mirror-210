from abc import ABC, abstractmethod

from splathash.engine.context.application_context import (
    ApplicationContext,
    ApplicationContextFactory,
)
from splathash.engine.converter.menu_output_converter import (
    MenuOutputConverter,
    MenuOutputConverterFactory,
)
from splathash.engine.converter.output_json_converter import (
    OutputJsonConverter,
    OutputJsonConverterFactory,
)
from splathash.engine.pagination.context.pagination_context import (
    PaginationContextFactory,
)
from splathash.engine.pagination.pager.pager import PagerFactory
from splathash.engine.pagination.splitter.message_splitter import MessageSplitterFactory
from splathash.engine.router.router import Router


class Application(ABC):
    """The application is the main engine of the USSD framework"""

    @abstractmethod
    def run(self, request, router: Router) -> dict:
        """Collect the services to use and call them in the right order"""


class BaseApplication(Application):
    """Base application flow"""

    context: ApplicationContext
    converter: MenuOutputConverter
    json_converter: OutputJsonConverter

    def run(self, request, router: Router) -> dict:
        # initialize context
        self.context.initialize(data=request.data)

        # get response handler
        next_route = self.context.next()
        response_handler = router.route(next_route)

        # fetch the correct node and fetch menu
        node = response_handler.get_node(self.context)
        menu, next_route = node.create_menu(self.context)

        # set next route
        self.context.next(route=next_route)

        # convert menu to correct output format
        output = self.converter.convert(node_response=menu, context=self.context)

        # convert output data to json string
        response = self.json_converter.to_json(output_data=output)

        return response


class PagingAwareApplication(BaseApplication):
    """Handles pagination automatically"""

    def run_with_pagination(self, request, router: Router, next_key="#", previous_key="0"):
        """wrap the runner with pagination awareness"""
        message_key = "MSG"

        application_context = ApplicationContextFactory.default()
        paging_context = PaginationContextFactory.default()
        paging_context.initialize(context=application_context, data=request.data)

        data = application_context.getData()
        if paging_context.flag() and data in [next_key, previous_key]:
            pages = paging_context.pages()
            previous_page = paging_context.current_page()
            current_page = (previous_page - 1) if data == previous_key else (previous_page + 1)
            if current_page < 0 or current_page >= len(pages):
                current_page = 0

            response = paging_context.response()
            paging_context.current_page(current_page)
            return {**response, message_key: pages[current_page]}

        paging_context.flag(flag=False)

        response = self.run(request, router)
        message = response.get(message_key)

        splitter = MessageSplitterFactory.default()
        if not splitter.should_split(message):
            return response

        split = splitter.split(message)
        pager = PagerFactory.default()
        pages = pager.create_pages(split, next_key, previous_key)

        paging_context.flag(flag=True)
        paging_context.pages(pages=pages)
        paging_context.response(data=response)

        current_page = 0
        paging_context.current_page(number=current_page)
        return {**response, message_key: pages[current_page]}


class NALOApplication(PagingAwareApplication):
    """Use services that are built for NALO specific data format"""

    context = ApplicationContextFactory.default()
    converter = MenuOutputConverterFactory.default()
    json_converter = OutputJsonConverterFactory.default()
