from lilya.cli.base import BaseDirective as LilyaBaseDirective

import esmerald
from esmerald.core.terminal.print import Print
from esmerald.parsers import ArbitraryExtraBaseModel

printer = Print()


class BaseDirective(ArbitraryExtraBaseModel, LilyaBaseDirective):
    """The base class from which all directives derive."""

    def get_version(self) -> str:
        """
        Returns the current version of Esmerald.
        """
        return esmerald.__version__
