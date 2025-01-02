from pydantic import BaseModel, ValidationError, Field, model_validator, validator
from module import *
from loguru import logger
import configparser
import urllib.parse
import os
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'module', 'config.ini')


def __get_response_yandex(organization, skip, bbox) -> str:
    """Получение данных от геокодера"""
    try:
        yandex_request = Yandex()
        yandex_info = yandex_request.get_organisation_info(organization=organization,
                                                           bbox=bbox,
                                                           skip=skip)
        return yandex_info.text
    except Exception as e:
        logger.debug(e)


def __processing_response_geocoder(yandex_info: str):
    """Обработка pydantic"""
    try:
        json = yandex_info
        basic_information = Shops.parse_raw(json)
        request_information = RequestYandex.parse_raw(json)
        return basic_information.features, request_information.properties.ResponseMetaData.SearchRequest.request
    except ValidationError as e:
        print("Exception", e.json())
        # logger.error("Exception", e.json())


def __get_request_shop_id_and_push_request_shops(request_information: str) -> int:
    conn = Shops_db(debug_mode=False)
    request_shop_id = conn.push_request_shops(request_information)
    return request_shop_id


def __processing_operation_mode_by_days(info: list):
    """Дополнительная обработка для режима работы по дням"""
    u = 0
    mon = info[u].Monday
    tues = info[u].Tuesday
    wed = info[u].Wednesday
    thurs = info[u].Thursday
    fri = info[u].Friday
    sat = info[u].Saturday
    sun = info[u].Sunday
    if mon is None and len(info) == 2:
        u = 1
        mon = info[u].Monday
    if wed is None and len(info) == 2:
        u = 1
        wed = info[u].Wednesday
    if thurs is None and len(info) == 2:
        u = 1
        thurs = info[u].Thursday
    if fri is None and len(info) == 2:
        u = 1
        fri = info[u].Friday
    if sat is None and len(info) == 2:
        u = 1
        sat = info[u].Saturday
    if sun is None and len(info) == 2:
        u = 1
        sun = info[u].Sunday
    return mon, tues, wed, thurs, fri, sat, sun


def __get_work_mode_id_and_push_operating_mode(basic_information, i):
    if basic_information[i].properties.CompanyMetaData.Hours:
        push_work_mode_db = basic_information[i].properties.CompanyMetaData.Hours.Availabilities
        conn = Shops_db(debug_mode=False)
        if len(push_work_mode_db) >= 2:
            info = basic_information[i].properties.CompanyMetaData.Info
            mon, tues, wed, thurs, fri, sat, sun = __processing_operation_mode_by_days(push_work_mode_db)
            everyday = True
            twenty_four_hours = False
            work_mode_id = conn.push_operating_mode(info=info,
                                                    twenty_four_hours=twenty_four_hours,
                                                    everyday=everyday,
                                                    mon=mon,
                                                    tues=tues,
                                                    wed=wed,
                                                    thurs=thurs,
                                                    fri=fri,
                                                    sat=sat,
                                                    sun=sun)
            return work_mode_id
        elif len(push_work_mode_db) == 1:
            u = 0
            info = basic_information[i].properties.CompanyMetaData.Info
            twenty_four_hours = push_work_mode_db[u].TwentyFourHours
            everyday = push_work_mode_db[u].Everyday
            mon = push_work_mode_db[u].Monday
            tues = push_work_mode_db[u].Tuesday
            wed = push_work_mode_db[u].Wednesday
            thurs = push_work_mode_db[u].Thursday
            fri = push_work_mode_db[u].Friday
            sat = push_work_mode_db[u].Saturday
            sun = push_work_mode_db[u].Sunday
            work_mode_id = conn.push_operating_mode(info=info,
                                                    twenty_four_hours=twenty_four_hours,
                                                    everyday=everyday,
                                                    mon=mon,
                                                    tues=tues,
                                                    wed=wed,
                                                    thurs=thurs,
                                                    fri=fri,
                                                    sat=sat,
                                                    sun=sun)
            return work_mode_id
        else:
            work_mode_id = None
            return work_mode_id


def __get_retail_id_and_push_shop_info(basic_information, i):
    """Заполнение таблицы shop_info и получение retail_id"""
    push_shop_info_db = basic_information[i].properties.CompanyMetaData.Categories
    classes = []
    names = []
    for category in push_shop_info_db:
        classes.append(category.class_)
        names.append(category.name)
    conn = Shops_db(debug_mode=False)
    retail_id = conn.push_shop_info(type=', '.join(classes), name=', '.join(names))
    return retail_id


def __push_info_shops(basic_information, retail_id, request_shop_id, work_mode_id, i):
    if work_mode_id is None:
        work_time = False
    else:
        work_time = True
    coordinate = basic_information[i].geometry.coordinates
    boundedBy = basic_information[i].properties.boundedBy
    address = basic_information[i].properties.CompanyMetaData.address
    response_geocoder = basic_information[i].properties.CompanyMetaData.name

    conn = Shops_db(debug_mode=False)
    conn.push_shops(coordinate=f"{coordinate[0]},{coordinate[1]}",
                    boundedBy=f"{boundedBy[0][0]},{boundedBy[0][1]},{boundedBy[1][0]},{boundedBy[1][1]}",
                    address=address, retail_id=retail_id,
                    work_time=work_time, response_geocoder=response_geocoder, request_shop_id=request_shop_id,
                    work_mode_id=work_mode_id)


def __is_address_country(basic_information: list, i: int) -> bool:
    return "Беларусь" in basic_information[i].properties.description


def main() -> None:
    config = configparser.ConfigParser()
    config.read(config_path)
    organization = config["Organizations"]["ORGANIZATIONS"].encode('Windows-1251')
    bbox = config['Box']['BOX'].replace('"', '')
    for coord in bbox.split(', '):
        normalized_organization = urllib.parse.unquote(organization).split(',')
        for org in normalized_organization:
            skip = 0
            while True:
                print(org, coord)
                response_yandex = __get_response_yandex(organization=org, skip=skip, bbox=coord)
                print(response_yandex)
                print(len(response_yandex))
                basic_information, request_information = __processing_response_geocoder(response_yandex)
                print(basic_information, request_information)
                if not basic_information:
                    logger.info("No more organizations found")
                    break
                for i in range(0, len(basic_information)):
                    if __is_address_country(basic_information, i):
                        request_shop_id = __get_request_shop_id_and_push_request_shops(request_information)
                        work_mode_id = __get_work_mode_id_and_push_operating_mode(basic_information, i)
                        retail_id = __get_retail_id_and_push_shop_info(basic_information, i)
                        __push_info_shops(basic_information, retail_id, request_shop_id, work_mode_id, i)
                        print(org, basic_information[i].properties.CompanyMetaData.address)
                skip += 50


if __name__ == '__main__':
    main()

