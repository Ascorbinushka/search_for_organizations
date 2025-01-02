from requests import Session, Response
from requests.exceptions import RequestException
from loguru import logger
import configparser
import os
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
API_KEY = config['Key']['KEY'].split(',')


CONNECT_TIMEOUT = 5
SEND_TIMEOUT = 5


class Yandex(Session):
    def __init__(self):
        super().__init__()
        self.url = 'https://search-maps.yandex.ru/v1/'
        self.timeout = (SEND_TIMEOUT, CONNECT_TIMEOUT)
        self.api_keys = API_KEY

    def get_organisation_info(self, organization: str, bbox: str, skip: int) -> Response:
        for api_key in self.api_keys:
            try:
                response = self.get(url=self.url,
                                    params={"text": organization,
                                            "apikey": api_key,
                                            "lang": "ru_RU",
                                            "bbox": bbox,
                                            "rspn": 1,
                                            "results": 50,
                                            "skip": skip,
                                            "type": 'biz'},
                                    timeout=self.timeout)
                if response.status_code == 200:
                    return response
                if response.json().get("message") == "Invalid key" or response.json().get("message") == "Limit is exceeded":
                    logger.warning(response.json().get("message"))
                    continue
                if response.status_code == 403:
                    logger.error(response.json().get("message"))
                if response.status_code == 400:
                    logger.error(response.json().get("message"))
                    return response.json().get("message")
                if response.status_code == 409:
                    logger.error(response.json().get("message"))
                    return response.json().get("message")
            except RequestException as e:
                logger.error(f'Yandex services error {e}')
        logger.info("Все ключи API недействительны")


if __name__ == '__main__':
    yandex_request = Yandex()
    try:
        yandex_info = yandex_request.get_organisation_info(organization="Евроопт",
                                                           bbox="27.465445,53.816394~27.745609,53.939726",
                                                           skip=0)
        print(yandex_info.json())
    except Exception as e:
        print(e)
