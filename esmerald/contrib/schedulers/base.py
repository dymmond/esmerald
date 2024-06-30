from typing import TYPE_CHECKING, Any, Dict

from esmerald.protocols.scheduler import SchedulerProtocol

if TYPE_CHECKING:
    pass


class SchedulerConfig(SchedulerProtocol):

    def __init__(self, **kwargs: Dict[str, Any]):
        super().__init__(**kwargs)

    async def start(self, **kwargs: Dict[str, Any]) -> None:
        raise NotImplementedError("Every scheduler must implement the start method.")

    async def stop(self, **kwargs: Dict[str, Any]) -> None:
        raise NotImplementedError("Every scheduler must implement the stop method.")
