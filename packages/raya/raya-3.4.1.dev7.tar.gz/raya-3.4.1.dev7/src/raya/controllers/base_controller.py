from rclpy.node import Node


class CommandHandler():

    def __init__(self, cb_finish, cb_finish_async, cb_feedback,
                 cb_feedback_async, result_future, result_handler):
        self.cb_finish = cb_finish
        self.cb_finish_async = cb_finish_async
        self.cb_feedback = cb_feedback
        self.cb_feedback_async = cb_feedback_async
        self.result_future = result_future
        self.result_handler = result_handler


class BaseController():

    def __init__(self, name: str, node: Node, interface, extra_info={}):
        pass

    def delete_listener(self, listener_name):
        pass
