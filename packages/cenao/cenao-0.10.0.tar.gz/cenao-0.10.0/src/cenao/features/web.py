import asyncio
from typing import Awaitable, List, Callable

from aiohttp import web
from aiohttp.web_runner import TCPSite, AppRunner
from prometheus_client import generate_latest, Counter, Histogram

from cenao.app import AppFeature
from cenao.view import View


class MetricsView(View):
    ROUTE = '/metrics'

    async def get(self):
        response = generate_latest().decode('utf-8')

        return web.Response(
            status=200,
            text=response,
        )


class WebAppFeature(AppFeature):
    NAME = 'web'

    VIEWS = [MetricsView]

    host: str
    port: int

    aiohttp_app: web.Application
    runner: AppRunner
    _ws: List[web.WebSocketResponse]

    PROMETHEUS_REQUEST_METRIC: Counter
    PROMETHEUS_REQUEST_DURATION_METRIC: Histogram

    def on_init(self):
        self.host = self.config.get('host', '0.0.0.0')
        self.port = int(self.config.get('port', 8000))

        self._ws = []

        self.PROMETHEUS_REQUEST_METRIC = Counter(
            'http_request',
            documentation='Count of HTTP requests processed',
            labelnames=('path', 'method', 'status'),
        )

        self.PROMETHEUS_REQUEST_DURATION_METRIC = Histogram(
            'http_request_duration_seconds',
            documentation='The time server took to handle the request',
            labelnames=('path', 'method'),
        )

        @web.middleware
        async def prometheus_route_call_count(
            request: web.Request,
            handler: Callable[[web.Request], Awaitable[web.StreamResponse]]
        ) -> web.StreamResponse:
            match_info = request.match_info
            uri: str = "__unknown__"

            if match_info.route.resource:
                uri = match_info.route.resource.canonical

            with self.PROMETHEUS_REQUEST_DURATION_METRIC.labels(
                path=uri,
                method=request.method,
            ).time():
                try:
                    resp = await handler(request)
                    status_code = resp.status
                except asyncio.CancelledError:
                    status_code = 499
                    raise
                except asyncio.TimeoutError:
                    status_code = 504
                    raise
                except web.HTTPException as error_resp:
                    status_code = error_resp.status
                    raise
                except BaseException:
                    status_code = 500
                    raise
                finally:
                    self.PROMETHEUS_REQUEST_METRIC.labels(
                        path=uri,
                        method=request.method,
                        status=str(status_code),
                    ).inc()

            return resp

        self.aiohttp_app = web.Application(
            loop=self.app.loop,
            middlewares=[prometheus_route_call_count]
        )
        routes_len = 0
        for ft in self.app.ft:
            for view in ft.VIEWS:
                view.init(ft)
                self.aiohttp_app.router.add_view(view.ROUTE, view)
                routes_len += 1
        self.logger.info('Registered %d routes', routes_len)

        self.runner = AppRunner(self.aiohttp_app, logger=self.logger)

    async def on_startup(self):
        self.logger.info('Starting on %s:%d', self.host, self.port)
        await self.runner.setup()
        site = TCPSite(
            self.runner,
            self.host,
            self.port,
        )
        await site.start()

    async def on_shutdown(self):
        self.logger.info('Stopping webserver')

        for ws in self._ws:
            await ws.close()

        await self.runner.cleanup()

    def get_websocket_response(self) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        self._ws.append(ws)
        return ws
