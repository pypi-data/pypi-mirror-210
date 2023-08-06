from enum import IntEnum


class SpaceTask(IntEnum):

    """
        List of available SpaceTasks on Coretex.ai
    """

    computerVision        = 1
    imageSegmentation     = 2
    tabularDataProcessing = 3
    superResolution       = 4
    videoAnalytics        = 5
    audioAnalytics        = 6
    bodyTracking          = 7
    other                 = 8
    motionRecognition     = 9
    nlp                   = 10  # Natural Language Processing
    bioInformatics        = 11
