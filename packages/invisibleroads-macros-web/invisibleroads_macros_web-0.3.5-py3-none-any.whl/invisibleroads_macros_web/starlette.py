from asyncio.exceptions import CancelledError

from starlette.datastructures import MutableHeaders
from starlette.templating import Jinja2Templates


class ExtraResponseHeadersMiddleware:

    def __init__(self, app, headers):
        self.app = app
        self.headers = headers

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        async def send_with_extra_headers(message):
            if message['type'] == 'http.response.start':
                headers = MutableHeaders(scope=message)
                for key, value in self.headers.items():
                    headers.append(key, value)

            await send(message)

        try:
            await self.app(scope, receive, send_with_extra_headers)
        except CancelledError:
            pass


class TemplateResponseFactory(Jinja2Templates):

    def __init__(self, environment, context_processors=None):
        'Assume nothing about the template environment'
        self.env = environment
        self.context_processors = context_processors or []
