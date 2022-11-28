from argparse import HelpFormatter
from io import TextIOBase
from typing import Any, Dict, Optional


class EsmeraldHelpFormatter(HelpFormatter):
    show_last = {
        "--version",
        "--verbosity",
        "--traceback",
    }

    def _reordered_actions(self, actions: Any):
        return sorted(actions, key=lambda a: set(a.option_strings) & self.show_last != set())

    def add_usage(self, usage: str, actions: Any, *args: Any, **kwargs: Dict[str, Any]):
        super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

    def add_arguments(self, actions: Any):
        super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
    def __init__(self, out: Any, ending: str = "\n"):
        self._out = out
        self.ending = ending

    def __getattr__(self, name: str):
        return getattr(self._out, name)

    def flush(self) -> Any:
        if hasattr(self._out, "flush"):
            self._out.flush()

    def write(
        self,
        msg: str = "",
        ending: Optional[Any] = None,
    ) -> Any:
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        self._out.write(msg)
