from pydantic import BaseModel, ValidationError, Field, model_validator, validator
from module.yandex_maps import Yandex
from typing import List, Union, Optional
from typing import Any


class Intervals(BaseModel):
    fromm: str = Field(..., alias='from')
    to: str


class TwentyFourHours(BaseModel):
    TwentyFourHours: bool
    Everyday: bool
    Intervals: Any = None
    Monday: Any = None
    Tuesday: Any = None
    Wednesday: Any = None
    Thursday: Any = None
    Friday: Any = None
    Saturday: Any = None
    Sunday: Any = None
    Week: Any = None


class Availabilities(BaseModel):
    TwentyFourHours: Any = False
    Everyday: Any = None
    Intervals: List[Intervals]
    Monday: Any = None
    Tuesday: Any = None
    Wednesday: Any = None
    Thursday: Any = None
    Friday: Any = None
    Saturday: Any = None
    Sunday: Any = None

    @model_validator(mode='after')
    def process_availabilities(cls, value):
        if value.Everyday:
            value.Monday = [interval.dict() for interval in value.Intervals]
            value.Tuesday = [interval.dict() for interval in value.Intervals]
            value.Wednesday = [interval.dict() for interval in value.Intervals]
            value.Thursday = [interval.dict() for interval in value.Intervals]
            value.Friday = [interval.dict() for interval in value.Intervals]
            value.Saturday = [interval.dict() for interval in value.Intervals]
            value.Sunday = [interval.dict() for interval in value.Intervals]
        return value

    @model_validator(mode='after')
    def process_day(cls, value):
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if getattr(value, day, False) is None:
                if value.Monday is True:
                    value.Monday = [interval.dict() for interval in value.Intervals]
                if value.Tuesday is True:
                    value.Tuesday = [interval.dict() for interval in value.Intervals]
                if value.Wednesday is True:
                    value.Wednesday = [interval.dict() for interval in value.Intervals]
                if value.Thursday is True:
                    value.Thursday = [interval.dict() for interval in value.Intervals]
                if value.Friday is True:
                    value.Friday = [interval.dict() for interval in value.Intervals]
                if value.Saturday is True:
                    value.Saturday = [interval.dict() for interval in value.Intervals]
                if value.Sunday is True:
                    value.Sunday = [interval.dict() for interval in value.Intervals]
        return value


class Hours(BaseModel):
    text: str = None
    Availabilities: list[Union[Availabilities, TwentyFourHours]]


class Category(BaseModel):
    class_: Optional[str] = Field("None", alias='class')
    name: Optional[str] = "None"


class CompanyMetaData(BaseModel):
    Categories: list[Category]
    name: str
    address: str
    Hours: Optional[Union[Hours, None]]
    Info: Any = Field(..., alias='Hours')

    @model_validator(mode='before')
    def allow_none_hours(cls, value):
        if "Hours" not in value:
            value.update({"Hours": None, "Info": None})
        return value


class Properties(BaseModel):
    name: str
    description: str
    boundedBy: list
    CompanyMetaData: Optional[Union[CompanyMetaData, None]]


class Point(BaseModel):
    coordinates: list


class Features(BaseModel):
    geometry: Point
    properties: Properties


class Shops(BaseModel):
    features: list[Features]


class Request(BaseModel):
    request: str


class ResponseMetaData(BaseModel):
    SearchRequest: Request


class PropertiesRequest(BaseModel):
    ResponseMetaData: ResponseMetaData


class RequestYandex(BaseModel):
    properties: PropertiesRequest


if __name__ == '__main__':

    try:
        yandex_request = Yandex()
        yandex_info = yandex_request.get_organisation_info(organization="Родны кут",
                                                           bbox="27.496191,53.887953~27.626618,53.935331",
                                                           skip=0)
        # yandex_info = yandex_request.get_organisation_info(organization="Евроопт Market",
        #                                                    api_key='c918925b-ea1f-4e40-a5a5-ca0769f32257',
        #                                                    bbox="27.496191,53.887953~27.626618,53.935331",
        #                                                    skip=0)
        json = yandex_info.text
        basic_information = Shops.parse_raw(json)
        request_information = RequestYandex.parse_raw(json)
        print(basic_information)
        print(request_information)
    except ValidationError as e:
        print("Exception", e.json())
