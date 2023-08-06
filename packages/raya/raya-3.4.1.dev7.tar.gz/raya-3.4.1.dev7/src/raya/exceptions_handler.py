from raya.exceptions import *

ALREADY_RUNNING_ERROR = 20


def check_raya_exception(map, response):
    pass


def check_raya_exception_code(map, error_code, error_msg):
    pass


EXCEPTIONS_MAP_GENERAL = {
    1: (RayaApplicationAlreadyRegistered, ''),
    2: (RayaApplicationNotRegistered, ''),
    3: (RayaApplicationException, ''),
    4: (RayaNotAvailableServer, ''),
    5: (RayaNotServerPermissions, ''),
    14: (RayaSimulatorError, ''),
    15: (RayaSignalNotImplemented, ''),
    16: (RayaUnknownServerError, ''),
    17: (RayaGoalNotAccepted, ''),
    18: (RayaCommandCanceled, ''),
    19: (RayaWrongArgument, ''),
    119: (RayaUnknownServerError, ''),
    219: (RayaUnknownServerError, ''),
    126: (RayaNoPathToGoal, '')
}
EXCEPTIONS_MAP_COMMUNICATION = {
    **EXCEPTIONS_MAP_GENERAL, 21: (RayaCommNotRunningApp, 'GGS not running')
}
EXCEPTIONS_MAP_COMMUNICATION_SERVER = {
    **EXCEPTIONS_MAP_GENERAL, 21: (RayaCommNotRunningApp, '')
}
EXCEPTIONS_MAP_CAMERAS = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaCameraAlreadyEnabled, ''),
    21: (RayaCameraNotEnabled, ''),
    22: (RayaCameraInvalidName, ''),
    23: (RayaCameraWrongType, '')
}
EXCEPTIONS_MAP_INTERACTIONS = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaInteractionsAlreadyRunning, ''),
    21: (RayaInteractionsWrongName, ''),
    120: (RayaSoundWrongName, ''),
    121: (RayaLedsWrongGroup, ''),
    122: (RayaLedsWrongColor, ''),
    123: (RayaLedsWrongAnimationName, ''),
    124: (RayaLedsWrongRepetitions, ''),
    125: (RayaLedsWrongSpeed, ''),
    126: (RayaSoundWrongPath, ''),
    127: (RayaSoundErrorPlatingAudiofile, ''),
    128: (RayaSoundErrorRecording, ''),
    129: (RayaSoundErrorPlayingAudio, ''),
    130: (RayaSoundBufferNotFound, '')
}
EXCEPTIONS_MAP_MOTION = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaAlreadyMoving, ''),
    21: (RayaNotValidMotionCommand, ''),
    22: (RayaNotValidMotionCommand, '')
}
EXCEPTIONS_MAP_NAV = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaNavAlreadyNavigating, ''),
    22: (RayaNavNotMapping, ''),
    23: (RayaNavLocationAlreadyExist, ''),
    24: (RayaNavErrorReadingYaml, ''),
    25: (RayaNavErrorWritingYaml, ''),
    26: (RayaNavLocationNotFound, ''),
    27: (RayaNavLocationsNotFound, ''),
    28: (RayaNavNoMapLoaded, ''),
    29: (RayaNavNoDataFromMapTopic, ''),
    30: (RayaNavZoneNotFound, ''),
    31: (RayaNavNotLocated, ''),
    32: (RayaNavSortedPointsEmpty, ''),
    33: (RayaNavZoneAlreadyExist, ''),
    34: (RayaNavErrorSavingZone, ''),
    35: (RayaNavZoneIsNotPolygon, ''),
    36: (RayaNavNotValidPointFound, ''),
    115: (RayaUnableToFollowPath, ''),
    116: (RayaUnableToComputePath, ''),
    121: (RayaNavUnableToSaveMap, ''),
    122: (RayaNavNoDataFromMapTopic, ''),
    123: (RayaNavUnableToChangeMap, ''),
    124: (RayaNavInvalidGoal, ''),
    125: (RayaUnableToFollowPath, ''),
    126: (RayaNoPathToGoal, ''),
    127: (RayaNavIncompletePath, ''),
    128: (RayaNavIncorrectPath, ''),
    129: (RayaNavBadImageSize, ''),
    130: (RayaNavMappingDisabled, ''),
    140: (RayaNavFileNotFound, ''),
    141: (RayaNavWrongFileFormat, '')
}
EXCEPTIONS_MAP_CV = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaCVAlreadyEnabled, ''),
    21: (RayaCVNotCameraInterface, ''),
    22: (RayaCVTopicNotPublishig, ''),
    23: (RayaCVGPUNotAvailable, ''),
    24: (RayaCVModelNotRunning, ''),
    25: (RayaCVModelLimitReached, ''),
    26: (RayaCVNotTrain, ''),
    27: (RayaCVWrongAppInfo, ''),
    28: (RayaCVWrongModelMode, ''),
    29: (RayaCVNotModelMode, ''),
    30: (RayaCVCameraStatusFail, ''),
    31: (RayaCVUnkownError, ''),
    32: (RayaCVWrongCamera, ''),
    33: (RayaCVWrongCameraDepth, ''),
    34: (RayaCVRunningOtherCamera, ''),
    35: (RayaCVRunningOtherTagSize, '')
}
EXCEPTIONS_MAP_ARMS = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaAlreadyMoving, ''),
    21: (RayaArmsInvalidGroupName, ''),
    22: (RayaArmsNotPoseArmDataAvailable, ''),
    23: (RayaArmsNotPredefinedPoseAvailable, ''),
    24: (RayaArmsInvalidNumberOfJoints, ''),
    25: (RayaArmsOutOfLimits, ''),
    26: (RayaArmsPredefinedPoseEmptyName, ''),
    27: (RayaArmsPredefinedPoseNameAlreadyExist, ''),
    28: (RayaArmsPredefinedPoseNameNotExist, ''),
    29: (RayaArmsPredefinedTrajectoryNameAlreadyExist, ''),
    30: (RayaArmsPredefinedTrajectoryNameNotExist, ''),
    31: (RayaArmsErrorParsingPredefinedTrajectory, ''),
    121: (RayaArmsExternalException, ''),
    122: (RayaArmsExternalException, ''),
    123: (RayaArmsExternalException, ''),
    124: (RayaArmsExternalException, ''),
    125: (RayaArmsExternalException, ''),
    126: (RayaArmsExternalException, ''),
    127: (RayaArmsExternalException, ''),
    130: (RayaArmsExternalException, ''),
    131: (RayaArmsExternalException, ''),
    132: (RayaArmsExternalException, ''),
    133: (RayaArmsExternalException, ''),
    134: (RayaArmsExternalException, ''),
    136: (RayaArmsExternalException, ''),
    137: (RayaArmsExternalException, ''),
    138: (RayaArmsExternalException, ''),
    139: (RayaArmsExternalException, ''),
    141: (RayaArmsExternalException, ''),
    142: (RayaArmsExternalException, ''),
    143: (RayaArmsExternalException, ''),
    144: (RayaArmsExternalException, ''),
    145: (RayaArmsExternalException, ''),
    151: (RayaArmsExternalException, ''),
    152: (RayaArmsExternalException, ''),
    161: (RayaArmsExternalException, ''),
    162: (RayaArmsExternalException, ''),
    163: (RayaArmsExternalException, ''),
    164: (RayaArmsExternalException, '')
}
EXCEPTIONS_MAP_MANIPULATION = {
    **EXCEPTIONS_MAP_GENERAL, 20: (RayaManipulationAlreadyEnabled, ''),
    21: (RayaManipulationNotArmName, ''),
    22: (RayaManipulationObjNotFound, ''),
    23: (RayaManipulationNotDetections, ''),
    24: (RayaManipulationProcessFail, ''),
    25: (RayaManipulationTopicNotPublishing, ''),
    26: (RayaManipulationSrvNotAvailable, ''),
    27: (RayaManipulationPickSolutionNotFound, ''),
    28: (RayaManipulationNotReference, ''),
    29: (RayaManipulationNotArm, ''),
    30: (RayaManipulationNotHeight, ''),
    31: (RayaManipulationPlaceSolutionNotFound, ''),
    32: (RayaManipulationNotTag, ''),
    33: (RayaManipulationPlaceSolutionNotFound, ''),
    34: (RayaManipulationInvalidPoint, ''),
    35: (RayaManipulationNotPlaceObject, '')
}
