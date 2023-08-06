from pathlib import Path

from ..image_dataset import LocalImageDataset
from ...sample import LocalComputerVisionSample


class LocalComputerVisionDataset(LocalImageDataset[LocalComputerVisionSample]):

    """
        Represents the Local Computer Vision Dataset class
        which is used for working locally with Computer Vision Task type
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path, LocalComputerVisionSample)
