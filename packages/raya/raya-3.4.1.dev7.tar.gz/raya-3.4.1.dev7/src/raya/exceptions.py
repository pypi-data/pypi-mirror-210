class RayaException(Exception):

    def get_raya_file(self):
        return


class RayaAbortException(RayaException):
    pass


class RayaNotStarted(RayaException):
    pass


class RayaAppFinished(RayaException):
    pass


class RayaAppAborted(RayaException):
    pass


class RayaCommandException(RayaException):
    pass


class RayaCommandTimeout(RayaCommandException):
    pass


class RayaApplicationException(RayaException):
    pass


class RayaApplicationAlreadyRegistered(RayaApplicationException):
    pass


class RayaApplicationNotRegistered(RayaApplicationException):
    pass


class RayaAppsAdminException(RayaApplicationException):
    pass


class RayaUnknownServerError(RayaApplicationException):
    pass


class RayaNotAvailableServer(RayaApplicationException):
    pass


class RayaNotServerPermissions(RayaApplicationException):
    pass


class RayaCommandAlreadyRunning(RayaApplicationException):
    pass


class RayaCommandNotRunning(RayaApplicationException):
    pass


class RayaCommandNotCancelable(RayaApplicationException):
    pass


class RayaCommandCanceled(RayaApplicationException):
    pass


class RayaGoalNotAccepted(RayaApplicationException):
    pass


class RayaSignalNotImplemented(RayaApplicationException):
    pass


class RayaSimulatorError(RayaApplicationException):
    pass


class RayaArgumentError(RayaApplicationException):
    pass


class RayaRequiredArgumentError(RayaApplicationException):
    pass


class RayaArgumentNotExists(RayaApplicationException):
    pass


class RayaOutsideSetup(RayaApplicationException):
    pass


class RayaFileSystemException(RayaApplicationException):
    pass


class RayaNotValidPath(RayaFileSystemException):
    pass


class RayaNotDataPath(RayaFileSystemException):
    pass


class RayaFolderDoesNotExist(RayaFileSystemException):
    pass


class RayaFileDoesNotExist(RayaFileSystemException):
    pass


class RayaDownloadError(RayaFileSystemException):
    pass


class RayaWrongFileExtension(RayaFileSystemException):
    pass


class RayaTaskException(RayaException):
    pass


class RayaTaskAlreadyRunning(RayaTaskException):
    pass


class RayaTaskNotRunning(RayaTaskException):
    pass


class RayaTaskWrongFunction(RayaTaskException):
    pass


class RayaTaskNotAvailableReturn(RayaTaskException):
    pass


class RayaValueException(RayaException):
    pass


class RayaInvalidNumericRange(RayaValueException):
    pass


class RayaInvalidRGBRange(RayaValueException):
    pass


class RayaInvalidHSVRange(RayaValueException):
    pass


class RayaWrongArgument(RayaValueException):
    pass


class RayaInterfaceExceptions(RayaException):
    pass


class RayaNotAvailableInterface(RayaInterfaceExceptions):
    pass


class RayaUnknownInterface(RayaInterfaceExceptions):
    pass


class RayaControllerException(RayaException):
    pass


class RayaNotRecognizedController(RayaControllerException):
    pass


class RayaAlreadyEnabledController(RayaControllerException):
    pass


class RayaNeedCallback(RayaControllerException):
    pass


class RayaListenerException(RayaException):
    pass


class RayaListenerAlreadyCreated(RayaListenerException):
    pass


class RayaListenerUnknown(RayaListenerException):
    pass


class RayaInvalidCallback(RayaListenerException):
    pass


class RayaWrongArgumentsNumber(RayaListenerException):
    pass


class RayaSensorsException(RayaControllerException):
    pass


class RayaSensorsUnknownPath(RayaSensorsException):
    pass


class RayaSensorsIncompatiblePath(RayaSensorsException):
    pass


class RayaSensorsInvalidPath(RayaSensorsException):
    pass


class RayaLidarInvalidAngleUnit(RayaApplicationException):
    pass


class RayaLidarNotDataReceived(RayaApplicationException):
    pass


class RayaCamerasException(RayaControllerException):
    pass


class RayaCameraInvalidName(RayaCamerasException):
    pass


class RayaCameraAlreadyEnabled(RayaCamerasException):
    pass


class RayaCameraNotEnabled(RayaCamerasException):
    pass


class RayaCameraWrongType(RayaCamerasException):
    pass


class RayaCameraNotFrameReceived(RayaCamerasException):
    pass


class RayaCVException(RayaControllerException):
    pass


class RayaCVUnkownError(RayaCVException):
    pass


class RayaCVInvalidType(RayaCVException):
    pass


class RayaCVInvalidModel(RayaCVException):
    pass


class RayaCVInvalidModel(RayaCVException):
    pass


class RayaCVNotEnabledType(RayaCVException):
    pass


class RayaCVModelNotEnabled(RayaCVException):
    pass


class RayaCVModelNotDisabled(RayaCVException):
    pass


class RayaCVNotActiveModel(RayaCVException):
    pass


class RayaCVNotValidLabel(RayaCVException):
    pass


class RayaCVWrongModelName(RayaCVException):
    pass


class RayaCVNeedCallback(RayaCVException):
    pass


class RayaCVAlreadyEnabled(RayaCVException):
    pass


class RayaCVNotCameraInterface(RayaCVException):
    pass


class RayaCVTopicNotPublishig(RayaCVException):
    pass


class RayaCVGPUNotAvailable(RayaCVException):
    pass


class RayaCVModelNotRunning(RayaCVException):
    pass


class RayaCVModelLimitReached(RayaCVException):
    pass


class RayaCVNotTrain(RayaCVException):
    pass


class RayaCVWrongAppInfo(RayaCVException):
    pass


class RayaCVWrongModelMode(RayaCVException):
    pass


class RayaCVNotModelMode(RayaCVException):
    pass


class RayaCVCameraStatusFail(RayaCVException):
    pass


class RayaCVWrongCamera(RayaCVException):
    pass


class RayaCVWrongCameraDepth(RayaCVException):
    pass


class RayaCVRunningOtherCamera(RayaCVException):
    pass


class RayaCVRunningOtherTagSize(RayaCVException):
    pass


class RayaCVModelNotPublishing(RayaCVException):
    pass


class RayaCVDiffImageNamesSize(RayaCVException):
    pass


class RayaCVInvalidImageFormat(RayaCVException):
    pass


class RayaCVInvalidModelReturn(RayaCVException):
    pass


class RayaManipulationException(RayaControllerException):
    pass


class RayaManipulationNotManipulation(RayaManipulationException):
    pass


class RayaManipulationAlreadyEnabled(RayaManipulationException):
    pass


class RayaManipulationNotArmName(RayaManipulationException):
    pass


class RayaManipulationObjNotFound(RayaManipulationException):
    pass


class RayaManipulationNotDetections(RayaManipulationException):
    pass


class RayaManipulationProcessFail(RayaManipulationException):
    pass


class RayaManipulationTopicNotPublishing(RayaManipulationException):
    pass


class RayaManipulationSrvNotAvailable(RayaManipulationException):
    pass


class RayaManipulationPickSolutionNotFound(RayaManipulationException):
    pass


class RayaManipulationNotReference(RayaManipulationException):
    pass


class RayaManipulationNotArm(RayaManipulationException):
    pass


class RayaManipulationNotHeight(RayaManipulationException):
    pass


class RayaManipulationNotTag(RayaManipulationException):
    pass


class RayaManipulationPlaceSolutionNotFound(RayaManipulationException):
    pass


class RayaManipulationInvalidPoint(RayaManipulationException):
    pass


class RayaManipulationNotPlaceObject(RayaManipulationException):
    pass


class RayaMotionException(RayaControllerException):
    pass


class RayaAlreadyMoving(RayaMotionException):
    pass


class RayaNotMoving(RayaMotionException):
    pass


class RayaNotValidMotionCommand(RayaMotionException):
    pass


class RayaInteractionsException(RayaControllerException):
    pass


class RayaInteractionsAlreadyRunning(RayaInteractionsException):
    pass


class RayaInteractionsWrongName(RayaInteractionsException):
    pass


class RayaInteractionsNotRunning(RayaInteractionsException):
    pass


class RayaSoundException(RayaInteractionsException):
    pass


class RayaSoundWrongName(RayaSoundException):
    pass


class RayaSoundWrongFormat(RayaSoundException):
    pass


class RayaSoundWrongPath(RayaSoundException):
    pass


class RayaSoundErrorPlatingAudiofile(RayaSoundException):
    pass


class RayaSoundErrorRecording(RayaSoundException):
    pass


class RayaSoundErrorPlayingAudio(RayaSoundException):
    pass


class RayaSoundBufferNotFound(RayaSoundException):
    pass


class RayaLedsException(RayaInteractionsException):
    pass


class RayaLedsWrongGroup(RayaLedsException):
    pass


class RayaLedsWrongColor(RayaLedsException):
    pass


class RayaLedsWrongSpeed(RayaLedsException):
    pass


class RayaLedsWrongAnimationName(RayaLedsException):
    pass


class RayaLedsWrongRepetitions(RayaLedsException):
    pass


class RayaNavException(RayaControllerException):
    pass


class RayaNavUnknownMapName(RayaNavException):
    pass


class RayaNavAlreadyNavigating(RayaNavException):
    pass


class RayaNavNotNavigating(RayaNavException):
    pass


class RayaNavCurrentlyMapping(RayaNavException):
    pass


class RayaNavCantStartMapping(RayaNavException):
    pass


class RayaNavMapAlreadyExist(RayaNavException):
    pass


class RayaNavMapNameRequired(RayaNavException):
    pass


class RayaNavNoMapLoaded(RayaNavException):
    pass


class RayaNavMissingArgument(RayaNavException):
    pass


class RayaNavNotPathFound(RayaNavException):
    pass


class RayaNavNotPathBlocked(RayaNavException):
    pass


class RayaNavCantLocalize(RayaNavException):
    pass


class RayaNavPositionOutsideMap(RayaNavException):
    pass


class RayaNavAlreadyMapping(RayaNavException):
    pass


class RayaNavNotMapping(RayaNavException):
    pass


class RayaNavNotLocated(RayaNavException):
    pass


class RayaNavSortedPointsEmpty(RayaNavException):
    pass


class RayaNavNotPositionReceived(RayaNavException):
    pass


class RayaNavZoneNotFound(RayaNavException):
    pass


class RayaNavZonesNotFound(RayaNavException):
    pass


class RayaNavZoneAlreadyExist(RayaNavException):
    pass


class RayaNavErrorSavingZone(RayaNavException):
    pass


class RayaNavZoneIsNotPolygon(RayaNavException):
    pass


class RayaNavInvalidGoal(RayaNavException):
    pass


class RayaNavUnkownError(RayaNavException):
    pass


class RayaNavNotValidPointFound(RayaNavException):
    pass


class RayaNavErrorReadingYaml(RayaNavException):
    pass


class RayaNavErrorWritingYaml(RayaNavException):
    pass


class RayaNavLocationNotFound(RayaNavException):
    pass


class RayaNavLocationsNotFound(RayaNavException):
    pass


class RayaNavLocationAlreadyExist(RayaNavException):
    pass


class RayaNavNoDataFromMapTopic(RayaNavException):
    pass


class RayaNavUnableToSaveMap(RayaNavException):
    pass


class RayaNavUnableToChangeMap(RayaNavException):
    pass


class RayaUnableToFollowPath(RayaNavException):
    pass


class RayaUnableToComputePath(RayaNavException):
    pass


class RayaNoPathToGoal(RayaNavException):
    pass


class RayaNavIncompletePath(RayaNavException):
    pass


class RayaNavIncorrectPath(RayaNavException):
    pass


class RayaNavBadImageSize(RayaNavException):
    pass


class RayaNavMappingDisabled(RayaNavException):
    pass


class RayaNavFileNotFound(RayaNavException):
    pass


class RayaNavWrongFileFormat(RayaNavException):
    pass


class RayaCommException(RayaControllerException):
    pass


class RayaCommNotRunningApp(RayaCommException):
    pass


class RayaCommRestrictedMethod(RayaCommException):
    pass


class RayaSkillsException(RayaControllerException):
    pass


class RayaSkillsInvalidName(RayaSkillsException):
    pass


class RayaSkillsInvalidParameterName(RayaSkillsException):
    pass


class RayaSkillsMissingMandatoryParameter(RayaSkillsException):
    pass


class RayaArmsException(RayaControllerException):
    pass


class RayaArmsExternalException(RayaArmsException):
    pass


class RayaArmsNumberOfElementsNotMatch(RayaArmsException):
    pass


class RayaArmsInvalidGroupName(RayaArmsException):
    pass


class RayaArmsNotPoseArmDataAvailable(RayaArmsException):
    pass


class RayaArmsNotPredefinedPoseAvailable(RayaArmsException):
    pass


class RayaArmsInvalidNumberOfJoints(RayaArmsException):
    pass


class RayaArmsOutOfLimits(RayaArmsException):
    pass


class RayaArmsPredefinedPoseEmptyName(RayaArmsException):
    pass


class RayaArmsPredefinedPoseNameAlreadyExist(RayaArmsException):
    pass


class RayaArmsPredefinedPoseNameNotExist(RayaArmsException):
    pass


class RayaArmsPredefinedTrajectoryNameNotExist(RayaArmsException):
    pass


class RayaArmsPredefinedTrajectoryNameAlreadyExist(RayaArmsException):
    pass


class RayaArmsErrorParsingPredefinedTrajectory(RayaArmsException):
    pass


class RayaUIException(RayaException):
    pass


class RayaUIMissingValue(RayaUIException):
    pass


class RayaControllerNotFound(RayaUIException):
    pass


class RayaUIInvalidValue(RayaUIException):
    pass


class RayaFleetException(RayaException):
    pass


class RayaFleetMissingValue(RayaFleetException):
    pass


class RayaFleetWrongResponse(RayaFleetException):
    pass


class RayaFleetWrongValue(RayaFleetException):
    pass


class RayaFleetTimeout(RayaFleetException):
    pass
