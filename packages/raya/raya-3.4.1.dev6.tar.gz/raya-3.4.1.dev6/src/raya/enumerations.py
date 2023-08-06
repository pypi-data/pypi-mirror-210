from enum import IntEnum, Enum


class INPUT_TYPE(Enum):
    '\n    Enumeration to set input type\n    INPUT_TYPE.TEXT: user can only input a-z or A-Z\n    INPUT_TYPE.NUMERIC: user can only input numbers\n    '
    TEXT = 'text'
    NUMERIC = 'numeric'


class THEME_TYPE(Enum):
    '\n    Enumeration to set the UI theme type\n    THEME_TYPE.DARK : will specify to set background to dark\n    THEME_TYPE.WHITE : will specify to set background to white\n    '
    DARK = 'DARK'
    WHITE = 'WHITE'


class MODAL_TYPE(Enum):
    '\n    Enumeration to set the UI modal type\n    UI_TYPES.INFO : specify that this is an informative componant, No callback\n    UI_TYPES.SUCCESS : showing a messege that the opration was seccessful\n    UI_TYPES.ERROR : showing a messege that will alert of a bad precedere\n    '
    INFO = 'info'
    SUCCESS = 'success'
    ERROR = 'error'


class POS_UNIT(IntEnum):
    '\n    Enumeration to set the unit of the coordinates in a map.\n    POS_UNIT.PIXEL : Based on the pixel of the image map.\n    POS_UNIT.METERS : Meters\n    '
    PIXEL = 0
    METERS = 1


class ANG_UNIT(IntEnum):
    '\n    Enumeration to set the angles unit.\n    ANG_UNIT.DEG : Degrees\n    ANG_UNIT.RAD : Radians\n    '
    DEG = 0
    RAD = 1


class TITLE_SIZE(Enum):
    '\n    Enumeration to set the title size.\n    TITLE_SIZE.SMALL : Small size\n    TITLE_SIZE.MEDIUM : Medium size\n    TITLE_SIZE.LARGE : Large size\n    '
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class TYPE_SHAPES(IntEnum):
    '\n    Enumeration to define the type of shape for obstacles.\n    TYPE_SHAPES.BOX : Box\n    TYPE_SHAPES.SPHERE : Sphere\n    TYPE_SHAPES.CYLINDER : Cylinder\n    TYPE_SHAPES.CONE : Cone\n    '
    BOX = 1
    SPHERE = 2
    CYLINDER = 3
    CONE = 4


class DIMENSION_SHAPES(IntEnum):
    '\n    Enumeration to define the array position to define the shape obstacles dimensions.\n    DIMENSION_SHAPES.BOX_X : Box width\n    DIMENSION_SHAPES.BOX_Y : Box large\n    DIMENSION_SHAPES.BOX_Z : Box height\n\n    DIMENSION_SHAPES.SPHERE_RADIUS : Sphere radius\n\n    DIMENSION_SHAPES.CYLINDER_HEIGHT : Cylinder height\n    DIMENSION_SHAPES.CYLINDER_RADIUS : Cylinder radius\n\n    DIMENSION_SHAPES.CONE_HEIGHT : Cone height\n    DIMENSION_SHAPES.CONE_RADIUS : Cone radius\n    '
    BOX_X = 0
    BOX_Y = 1
    BOX_Z = 2
    SPHERE_RADIUS = 0
    CYLINDER_HEIGHT = 0
    CYLINDER_RADIUS = 1
    CONE_HEIGHT = 0
    CONE_RADIUS = 1


class ANIMATION_TYPE(Enum):
    '\n    ANIMATION_TYPE.LOTTIE : Lottie format\n    Enumeration to set the animation format.\n    ANIMATION_TYPE.PNG : PNG format\n    ANIMATION_TYPE.JPEG : JPEG format\n    ANIMATION_TYPE.GIF : GIF format\n    ANIMATION_TYPE.URL : URL format\n    '
    LOTTIE = 'LOTTIE'
    PNG = 'BASE64'
    JPEG = 'BASE64'
    GIF = 'BASE64'
    URL = 'URL'


class EXECUTION_CONTROL(IntEnum):
    '\n    Enumeration to set the animation to be overriden.\n    EXECUTION_CONTROL.OVERRIDE : Overide current animation.\n    EXECUTION_CONTROL.ADD_TO_QUEUE : Insert animation to serial queue.\n    EXECUTION_CONTROL.AFTER_CURRENT : Run animation at the end of current animation.\n    '
    OVERRIDE = 0
    ADD_TO_QUEUE = 1
    AFTER_CURRENT = 2


class MANAGE_ACTIONS(Enum):
    '\n    Enumeration to set the action to take when the user wants to manage predefined data.\n    '
    GET = 'get'
    EDIT = 'edit'
    REMOVE = 'remove'
    GET_INFORMATION = 'get_info'
    CREATE = 'create'


class FINISH_STATUS(Enum):
    '\n    Enumeration to set indicate whether the app finished successfully or not.\n    FINISH_STATUS.SUCCESS : The app finished successfully.\n    FINISH_STATUS.FAILED : The app finished with errors or did not finish as expected.\n    '
    SUCCESS = 'Done'
    FAILED = 'Failed'


class SPLIT_TYPE(Enum):
    '\n    Emumeration of all the ui methods options.\n    '
    DISPLAY_MODAL = 'Modal'
    DISPLAY_SCREEN = 'DisplayScreen'
    DISPLAY_INTERACTIVE_MAP = 'InteractiveMap'
    DISPLAY_ACTION_SCRENN = 'CallToAction'
    DISPLAY_INPUT_MODAL = 'InputModal'
    DISPLAY_CHOICE_SELECTOR = 'Choice'
    DISPLAY_ANIMATION = 'Animation'


class MODAL_SIZE(Enum):
    '\n    Enumeration to set the size of the modal.\n    '
    NORMAL = 'Normal'
    BIG = 'Big'


class UPDATE_STATUS(Enum):
    '\n    Enumeration indicate how is the progress of the application.\n    UPDATE_STATUS.INFO : General information to the user.\n    UPDATE_STATUS.WARNING : Warning message to the user.\n    UPDATE_STATUS.SUCCESS : Success message to the user.\n    UPDATE_STATUS.ERROR : Error message to the user.\n    '
    INFO = 'Info'
    WARNING = 'Warning'
    SUCCESS = 'Success'
    ERROR = 'Error'
