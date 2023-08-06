import logging
from typing import TYPE_CHECKING

from aiohttp import hdrs, web

from cenao.errors import ViewError, ServerError

if TYPE_CHECKING:
    from cenao.app import Application, AppFeature


class View(web.View):
    ROUTE: str

    logger: logging.Logger
    ft: 'AppFeature'

    @property
    def app(self) -> 'Application':
        return self.ft.app

    @classmethod
    def init(cls, ft: 'AppFeature'):
        cls.ft = ft
        cls.logger = logging.getLogger(cls.__name__)

    @property
    def remote_ip(self) -> str:
        if xff := self.request.headers.get('X-FORWARDED-FOR', ''):
            return xff
        if xri := self.request.headers.get('X-REAL-IP', ''):
            return xri
        return self.request.remote

    async def _iter(self) -> web.StreamResponse:
        if self.request.method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request.method.lower(), None)
        if method is None:
            self._raise_allowed_methods()

        try:
            resp = await method()
        except ViewError as ve:
            self.logger.warning('Got an error while handling request: %r', ve)
            return web.json_response({
                'ok': False,
                'code': ve.code,
                'error': ve.error_msg(),
                'reason': ve.reason(),
            }, status=ve.status)
        except Exception as e:
            self.logger.warning('Got an exception while handling request: %r', e)
            e = ServerError()
            return web.json_response({
                'ok': False,
                'code': e.code,
                'error': e.error_msg(),
                'reason': e.reason(),
            }, status=e.status)
        if resp is None:
            return web.json_response({'ok': True})

        if isinstance(resp, dict):
            return web.json_response({'ok': True, 'result': resp})

        return resp
