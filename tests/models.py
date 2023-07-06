from typing import Dict, List, Optional

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel


class Individual(BaseModel):
    first_name: str
    last_name: str
    id: str
    optional: Optional[str]
    complex: Dict[str, List[Dict[str, str]]]


class IndividualFactory(ModelFactory[Individual]):
    __model__ = Individual
