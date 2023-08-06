from typing import Tuple, Optional, List
from tap import Tap

from .base import ProjectCallback
from ..networking import networkManager


class RemoteArgumentParser(Tap):

    refreshToken: str
    experimentId: int

    def configure(self) -> None:
        self.add_argument("--refreshToken", type = str)
        self.add_argument("--experimentId", type = int)


def processRemote(args: Optional[List[str]] = None) -> Tuple[int, ProjectCallback]:
    remoteArgumentParser, unknown = RemoteArgumentParser().parse_known_args(args)

    response = networkManager.authenticateWithRefreshToken(remoteArgumentParser.refreshToken)
    if response.hasFailed():
        raise RuntimeError(">> [Coretex] Failed to authenticate")

    return remoteArgumentParser.experimentId, ProjectCallback.create(remoteArgumentParser.experimentId, remoteArgumentParser.refreshToken)
