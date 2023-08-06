import wfdb
from wfdb import Record
from wfdb.io._url import NetFileNotFoundError

from ecgai_data_physionet.exceptions import InvalidRecordError
from ecgai_data_physionet.models.diagnostic_code import DiagnosticCode
from ecgai_data_physionet.models.ecg import EcgRecord
from ecgai_data_physionet.physionet import PhysioNetDataSet


class FileLoader(PhysioNetDataSet):
    def __init__(self, data_set_name: str):
        super().__init__(data_set_name)

    def is_loaded(self) -> bool:
        pass

    def load(self):
        pass

    def get_record(self, record_path_name: str) -> EcgRecord:
        try:
            # loop = asyncio.get_event_loop()
            # record_task = loop.run_in_executor(
            #     None,
            #     functools.partial(wfdb.rdrecord, record_name=record_path_name),
            # )

            # wfdb_record = await record_task
            wfdb_record = wfdb.rdrecord(record_name=record_path_name)
            if type(wfdb_record) is not Record:
                # Should never be called
                raise InvalidRecordError(record_id=0, data_base_name=self.data_set_name)
            record = self.create_ecg_record(record_id=0, wfdb_record=wfdb_record)
            return record
        except NetFileNotFoundError as e:
            raise InvalidRecordError(record_id=0, data_base_name=self.data_set_name) from e
        except FileNotFoundError as e:
            raise InvalidRecordError(record_id=0, data_base_name=self.data_set_name) from e
        except Exception as e:
            print("Unexpected error:", e.args)
            raise e

    @staticmethod
    def is_valid_sample_rate(sample_rate: int) -> bool:
        pass

    @staticmethod
    def is_valid_record_id(record_id: int) -> bool:
        pass

    def create_ecg_record(self, record_id: int, wfdb_record: Record) -> EcgRecord:
        signal_array = self.create_signal_array(wfdb_record)
        # record_id = int("".join(ch for ch in wfdb_record.record_name if ch.isdigit()))
        # meta_data = self.get_database_metadata(record_id)
        # diagnostic_codes = await self.load_diagnostic_codes(meta_data.scp_codes)
        age = self.get_age(wfdb_record.comments)
        sex = self.get_sex(wfdb_record.comments)
        diagnostic_codes = self.get_diagnostic_codes(wfdb_record.comments)
        # dx = (wfdb_record.comments[2] ['Dx'])

        return EcgRecord.create(
            record_id=record_id,
            record_name=wfdb_record.record_name,
            database_name=self.data_set_name,
            sample_rate=wfdb_record.fs,
            leads=signal_array,
            age=age,
            sex=sex,
            report="",
            diagnostic_codes=diagnostic_codes,
        )

    @staticmethod
    def get_age(comment: list) -> int:
        age_string = comment[0]
        age = int(age_string.split(":")[1])
        return age

    @staticmethod
    def get_sex(comment: list) -> str:
        sex_string = comment[1]
        sex = sex_string.split(":")[1]
        if sex.lower() == "Male".lower():
            return "M"
        elif sex.lower() == "Female".lower():
            return "F"
        else:
            return "U"

    @staticmethod
    def get_diagnostic_codes(comment: list) -> list[DiagnosticCode]:
        diagnostic_codes = comment[2]
        codes_split = diagnostic_codes.split(":")[1]
        codes = codes_split.split(",")
        diagnostic_codes: list[DiagnosticCode] = []

        for item in codes:
            diagnostic_code = DiagnosticCode.create(
                scp_code=item,
                description="",
                confidence="",
            )
            diagnostic_codes.append(diagnostic_code)

        return diagnostic_codes

    # async def load_diagnostic_codes(self, codes):
    #     diagnostic_codes: list[DiagnosticCode] = []
    #     for item in codes:
    #         scp_code = self.get_scp_code_description(item.code)
    #         diagnostic_code = DiagnosticCode.create(
    #             scp_code=scp_code.scp_code,
    #             description=scp_code.description,
    #             confidence=item.confidence,
    #         )
    #         diagnostic_codes.append(diagnostic_code)
    #     return diagnostic_codes
