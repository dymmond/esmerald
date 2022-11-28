from typing import Type, TypeVar, Union

from esmerald.core.management.base import BaseDirective

DiretiveTypeVar = TypeVar("DiretiveTypeVar", bound=BaseDirective)
DirectiveType = Union[Type[DiretiveTypeVar], BaseDirective]
