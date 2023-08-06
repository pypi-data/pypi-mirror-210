from typing import List

from pydantic import ValidationError

from ecgai_data_physionet.models.model_base import MyBaseModel


class EcgLeadRecord(MyBaseModel):
    lead_name: str  # = Field(..., alias='leadName')
    signal: List[float]  # = Field(..., alias='signal')

    @classmethod
    # @log
    def create(cls, lead_name: str, signal: List[float]):
        try:
            d = dict(LeadName=lead_name, Signal=signal)
            return cls.from_dict(d)
        except ValidationError as e:
            # logging.error(e)
            raise e
