from raya.controllers.manipulation_controller import ManipulationController
from raya.logger import DEPRECATION_WARNING

DEPRECATION_WARNING(
    "The old module 'grasping_controller' and the old class 'GraspingController' are deprecated, and are just aliases of the new module 'manipulation_controller' and the new class 'ManipulationController'. Please stop using the old ones because they will be removed in the future, and replace them with the new ones."
)


class GraspingController(ManipulationController):
    pass
