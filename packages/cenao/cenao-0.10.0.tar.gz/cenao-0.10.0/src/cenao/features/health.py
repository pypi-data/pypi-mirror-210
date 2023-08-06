from cenao.app import AppFeature
from cenao.view import View


class HealthView(View):
    ROUTE = '/health'

    async def get(self):
        for ft in self.app.ft:
            try:
                await ft.check_health()
            except Exception as e:
                self.logger.exception('Health check failed', exc_info=e)
                return {'ok': False}

        return {'ok': True}


class HealthAppFeature(AppFeature):
    NAME = 'health'
    VIEWS = [HealthView]
