import json

from pydantic import BaseModel
from pydantic.utils import to_camel


class MyBaseModel(BaseModel):
    def __hash__(self):  # make hashable BaseModel subclass
        return hash((type(self),) + tuple(self.__dict__.values()))

    class Config:
        alias_generator = to_camel
        # by_alias = True

    @classmethod
    # @log
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    # @log
    def from_json(cls, j):
        return cls.from_dict(json.loads(j))
