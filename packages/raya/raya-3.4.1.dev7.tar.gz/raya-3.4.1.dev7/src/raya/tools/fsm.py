class RayaFSMMissinTick(Exception):
    pass


class RayaFSMNotCallableMethod(Exception):
    pass


class RayaFSMNotAsyncMethod(Exception):
    pass


class RayaFSMInvalidState(Exception):
    pass


class RayaFSMInvalidInitialState(Exception):
    pass


class RayaFSMInvalidEndState(Exception):
    pass


class RayaFSMUnknownState(Exception):
    pass


class RayaFSMInvalidTransition(Exception):
    pass


class RayaFSMNotRunning(Exception):
    pass


class RayaFSMInvalidErrorCode(Exception):
    pass


class BaseTransitions():

    def __init__(self):
        pass

    def set_state(self, state):
        pass

    def abort(self, code, msg):
        pass


class BaseActions():

    def __init__(self):
        pass


class FSM():

    def __init__(self, app, name, log_transitions=False):
        pass

    def get_error(self):
        return

    def get_current_state(self):
        return

    def restart(self):
        pass

    async def tick(self):
        return
