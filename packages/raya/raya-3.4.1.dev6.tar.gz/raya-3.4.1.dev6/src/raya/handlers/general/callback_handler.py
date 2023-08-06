import typing


class CallbackHandler():

    def __init__(self,
                 callback_sync: typing.Callable = None,
                 callback_async: typing.Callable = None,
                 min_num_params: int = 0,
                 max_num_params: int = (-1)):
        pass

    async def __call__(self, *args):
        pass
