import json
from datetime import datetime
from typing import Optional, Type

from cqlpy._internal.types.any import CqlAny


class DateTime(CqlAny[object, datetime]):
    def __init__(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        millisecond: Optional[int] = None,
    ):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond

    @property
    def value(self) -> datetime:
        return datetime(
            self.year or 0,
            self.month or 0,
            self.day or 0,
            self.hour or 0,
            self.minute or 0,
            self.second or 0,
        )

    @classmethod
    def parse_cql(cls, cql: str, subtype: Optional[Type[CqlAny]] = None) -> "DateTime":
        if cql:
            cql = cql.replace("@", "").strip()

            year = int(cql[0:4])
            month = int(cql[5:7]) if len(cql) > 6 else 0
            day = int(cql[8:10]) if len(cql) > 9 else 0
            hour = int(cql[11:13]) if len(cql) > 12 else 0
            minute = int(cql[14:16]) if len(cql) > 15 else 0
            second = int(cql[17:19]) if len(cql) > 18 else 0
        else:
            year = 0
            month = 0
            day = 0
            hour = 0
            minute = 0
            second = 0

        return cls(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
        )

    @classmethod
    def parse_fhir_json(
        cls,
        fhir_json: object,
        subtype: Optional[Type["CqlAny"]] = None,
    ) -> "DateTime":
        fhir_value = json.dumps(fhir_json).replace('"', "").strip()

        # 2019-05-30T00:00:00-00:00
        # 0         1         2
        # 012345678901234567890123456789
        year = int(fhir_value[0:4])
        month = int(fhir_value[5:7])
        day = int(fhir_value[8:10])
        hour = int(fhir_value[11:13]) if len(fhir_value) > 12 else 0
        minute = int(fhir_value[14:16]) if len(fhir_value) > 15 else 0
        second = int(fhir_value[17:19]) if len(fhir_value) > 18 else 0

        return cls(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
        )

    @classmethod
    def parse_datetime(cls, value: datetime) -> "DateTime":
        year = value.year
        month = value.month
        day = value.day
        hour = value.hour
        minute = value.minute
        second = value.second

        return cls(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
        )
