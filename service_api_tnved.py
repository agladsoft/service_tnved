import csv
import time
import json
from service_alta_tnved import ServiceAltaTNVED
from requests import Session, Response, exceptions


class ServiceApiTNVED(ServiceAltaTNVED):
    def __init__(self, goods_name: str, attempts: int):
        super().__init__(goods_name, attempts)
        self.website: str = "https://api.tnved.info"
        self._goods_name: str = goods_name
        self.goods_name: str = goods_name
        self.attempts: int = attempts

    def get_response(self):
        """

        :return:
        """
        try:
            time.sleep(5)
            session: Session = Session()
            session.proxies = self.proxy
            data: dict = {"query": self._goods_name}
            response: Response = session.post(f"{self.website}/api/Search/Search",
                                              headers=self.headers, json=data, timeout=120)
            self.logger.info(f'Наименование товара: {self.goods_name}. Статус запроса: {response.status_code}. '
                             f'Использованный прокси: {session.proxies.get("https")}')
            response.raise_for_status()
            return response
        except exceptions.RequestException as e:
            self.logger.error(f"Во время запроса API произошла ошибка - {e}. Proxy - {self.proxy}")

    def parse_response(self, response):
        """

        :return:
        """
        data_tnveds: list = []
        result: dict = json.loads(response.text)
        for position, dict_tnved in enumerate(result["resultWithDescription"], start=1):
            data: dict = {
                "goods_name": self.goods_name,
                "tnved": dict_tnved["code"],
                "description": dict_tnved["description"],
                "website": self.website,
                "probability": dict_tnved["probability"],
                "position": position
            }
            data_tnveds.append(data)
        return data_tnveds[:3]

    def main(self) -> None:
        """

        :return:
        """
        if self.attempts == 0:
            self.write_to_csv([{'goods_name': self.goods_name, 'tnved': None, 'description': None,
                                'website': self.website, 'probability': None, 'position': None}])
            return
        response: Response = self.get_response()
        tnveds: list = self.parse_response(response)
        self.write_to_csv("goods_name_parse2.csv", tnveds)


if __name__ == "__main__":
    with open("goods_name.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            service_tnved: ServiceApiTNVED = ServiceApiTNVED(row['goods_name'], 3)
            service_tnved.main()
