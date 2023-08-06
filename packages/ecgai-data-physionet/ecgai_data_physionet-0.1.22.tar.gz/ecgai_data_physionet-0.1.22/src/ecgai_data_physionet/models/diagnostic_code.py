from typing import Optional

from ecgai_data_physionet.models.model_base import MyBaseModel


class DiagnosticCode(MyBaseModel):
    scp_code: str
    description: str
    confidence: Optional[str]

    @classmethod
    # @log
    def create(cls, scp_code: str, description: str, confidence: str = ""):
        d = dict(ScpCode=scp_code, Description=description, Confidence=confidence)
        return cls.from_dict(d)
