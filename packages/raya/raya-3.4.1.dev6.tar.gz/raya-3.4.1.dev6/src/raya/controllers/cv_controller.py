from rclpy.node import Node
from raya.controllers.base_controller import BaseController
from raya.handlers.cv.model_base import CVModelBase
from raya.handlers.cv.objects_detector_handler import ObjectsDetectorHandler
from raya.handlers.cv.tags_detector_handler import TagsDetectorHandler
from raya.handlers.cv.faces_detector_handler import FacesDetectorHandler
from raya.handlers.cv.faces_recognizer_handler import FacesRecognizerHandler
from raya.handlers.cv.hand_estimator_handler import HandEstimatorHandler
from raya.handlers.cv.objects_classifier_handler import ObjectsClassifierHandler
from raya.handlers.cv.objects_segmentator_handler import ObjectsSegmentatorHandler
from raya.handlers.cv.planes_segmentator_handler import PlanesSegmentatorHandler

HANDLERS_CLASSES = {
    'detector': {
        'object': ObjectsDetectorHandler,
        'tag': TagsDetectorHandler,
        'face': FacesDetectorHandler
    },
    'recognizer': {
        'face': FacesRecognizerHandler
    },
    'estimator': {
        'hand_pose': HandEstimatorHandler
    },
    'classifier': {
        'object': ObjectsClassifierHandler
    },
    'segmentator': {
        'object': ObjectsSegmentatorHandler,
        'plane': PlanesSegmentatorHandler
    }
}


class CVController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info={}):
        pass

    async def get_available_models(self):
        return

    async def enable_model(self,
                           source: str,
                           name: str = '',
                           model: str = '',
                           type: str = '',
                           custom_model_path: str = '',
                           continues_msg: bool = True,
                           model_params: dict = {}):
        return

    async def disable_model(self,
                            model: str = None,
                            type: str = None,
                            model_obj: CVModelBase = None):
        pass

    async def disable_all_models(self):
        return

    async def train_model_folder_path(self,
                                      model_name: str,
                                      data_path: str,
                                      model_params: dict,
                                      model: str = '',
                                      type: str = ''):
        return

    async def train_model(self,
                          model: str,
                          type: str,
                          model_name: str,
                          images: list,
                          names: list,
                          model_params: dict,
                          encoding: str = 'bgr8'):
        return

    async def delete_face(self, faces_to_delete: list, model_name: str):
        return
        return
