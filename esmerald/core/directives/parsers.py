from argparse import ArgumentParser
from typing import Any, Dict, Optional

from esmerald.core.management.exceptions import DirectiveError


class DirectiveParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent SystemExit.
    """

    def error(self, message):
        raise DirectiveError(detail="Error: %s" % message)
