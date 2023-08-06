from raya.controllers.base_pseudo_controller import BasePseudoController


class AnalyticsController(BasePseudoController):

    def __init__(self, name: str, interface):
        pass

    async def track(self, event_name: str, parameters: dict):
        pass
