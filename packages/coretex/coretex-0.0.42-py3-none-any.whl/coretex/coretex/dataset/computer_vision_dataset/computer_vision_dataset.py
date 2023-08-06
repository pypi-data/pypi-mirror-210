from typing import Dict

from ..image_dataset import ImageDataset
from ...sample import ComputerVisionSample
from ....codable import KeyDescriptor


class ComputerVisionDataset(ImageDataset[ComputerVisionSample]):

    """
        Represents the Computer Vision Dataset class
        which is used for working with Computer Vision Task type
    """

    @classmethod
    def _keyDescriptors(cls) -> Dict[str, KeyDescriptor]:
        descriptors = super()._keyDescriptors()
        descriptors["samples"] = KeyDescriptor("sessions", ComputerVisionSample, list)

        return descriptors
