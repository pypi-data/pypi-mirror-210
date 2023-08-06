from datetime import datetime
from typing import Optional, Union, List, Dict, Iterable

from attr import define, field
from attrs import validators, asdict

from dicommeta.Utils import validator_pass, validator_parsable_date, validator_parsable_time, Mode, calculate_age


@define(kw_only=True, slots=True, order=True, frozen=True)
class Instance:
    SOPinstanceUID: str = field(factory=str)


@define(kw_only=True, slots=True, order=True, frozen=True)
class Series:
    seriesUID: str = field(factory=str)
    instance_dict: Dict[str, Instance] = field(factory=dict)

    def add_instance(self, instance: Instance):
        if instance.SOPinstanceUID not in self.instance_dict.keys():
            self.instance_dict[instance.SOPinstanceUID] = instance

    def get_instance(self, instance_uid: Instance) -> Instance:
        return self.instance_dict[instance_uid]

    def get_dict(self):
        return asdict(self)

    def get_iter(self) -> Iterable:
        return iter(asdict(self))


@define(kw_only=True, slots=True, order=True, frozen=False)
class Study(dict):
    StudyUID: str = field(factory=str, validator=validator_pass)
    StudyInstanceUID: str = field(factory=str)
    SpecificCharacterSet: str = field(factory=str, validator=validator_pass)
    StudyDate: Optional[Union[str, List]] = field(default=None, validator=validator_parsable_date)
    StudyTime: Optional[Union[str, List]] = field(default=None, validator=validator_parsable_time)
    study_datetime: datetime = field(default=None, init=False, validator=validator_pass)
    AccessionNumber: str = field(factory=str, validator=validator_pass)
    ReferringPhysicianName: str = field(factory=str, validator=validator_pass)
    PatientName: str = field(factory=str, validator=validator_pass)
    PatientID: str = field(factory=str, validator=validator_pass)
    PatientBirthDate: Optional[str] = field(default=None, validator=validator_parsable_date)
    patient_age: int = field(default=None, init=False, validator=validator_pass)
    mode: Optional[Mode] = field(default=None, validator=validators.optional(validators.in_(Mode)))
    series_dict: Dict[str, Series] = field(factory=dict)

    def __attrs_post_init__(self):
        if self.StudyDate is not None and self.StudyTime is not None:
            try:
                if isinstance(self.StudyTime, List):
                    study_time = self.StudyTime[0]
                else:
                    study_time = self.StudyTime

                if isinstance(self.StudyDate, List):
                    study_date = self.StudyDate[0]
                else:
                    study_date = self.StudyDate

                self.study_datetime = datetime.strptime(study_date + " " + study_time, '%Y%m%d %H%M%S')

            except ValueError:
                raise ValueError("Could not parse StudyDate:" + self.StudyDate + " or StudyTime:" + self.StudyTime)

        if self.PatientBirthDate is not None:
            self.patient_age = calculate_age(self.PatientBirthDate)

    def add_series(self, series: Series):
        if series.seriesUID not in self.series_dict.keys():
            self.series_dict[series.seriesUID] = series
        else:
            for instance in series.instance_dict.values():
                self.series_dict[series.seriesUID].add_instance(instance)

    def get_series_ids(self) -> list:
        return list(self.series_dict.keys())

    def get_series(self, seriesUID: str) -> dict:
        if seriesUID in self.series_dict.keys():
            return asdict(self.series_dict[seriesUID])

    def get_dict(self):
        return asdict(self)

    def get_iter(self) -> Iterable:
        return iter(asdict(self))
