from typing import List, Optional

from ecgai_data_physionet.models.diagnostic_code import DiagnosticCode
from ecgai_data_physionet.models.ecg_lead import EcgLeadRecord
from ecgai_data_physionet.models.model_base import MyBaseModel


class EcgRecord(MyBaseModel):
    record_id: int
    record_name: str  # = Field(..., alias='recordId')
    age: Optional[int] = None
    sex: Optional[str] = None
    report: Optional[str] = None
    diagnostic_codes: list[DiagnosticCode] = []
    # record_name: str
    # units:str
    database_name: str  # = Field(..., alias='databaseName')
    sample_rate: int  # = Field(..., alias='sampleRate')
    leads: List[EcgLeadRecord]  # = Field(..., alias='leads')

    @classmethod
    # @log
    def create(
        cls,
        record_id: int,
        record_name: str,
        database_name: str,
        sample_rate: int,
        leads: List[EcgLeadRecord],
        age: int = None,
        sex: str = None,
        report: str = None,
        diagnostic_codes=None,
    ):
        if diagnostic_codes is None:
            diagnostic_codes = []
        d = dict(
            RecordId=record_id,
            RecordName=record_name,
            Age=age,
            Sex=sex,
            Report=report,
            DiagnosticCodes=diagnostic_codes,
            DatabaseName=database_name,
            SampleRate=sample_rate,
            Leads=leads,
        )
        return cls.from_dict(d)
