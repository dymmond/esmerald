from lilya.cli.base import BaseDirective as LilyaBaseDirective

import ravyn
from ravyn.core.terminal.print import Print
from ravyn.parsers import ArbitraryExtraBaseModel

printer = Print()


class BaseDirective(ArbitraryExtraBaseModel, LilyaBaseDirective):
    """The base class from which all directives derive."""

    def get_version(self) -> str:
        """
        Returns the current version of Ravyn.
        """
        return ravyn.__version__
