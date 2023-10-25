import re
import csv
import time
from __init__ import *
from datetime import datetime
from bs4 import BeautifulSoup, ResultSet
from requests import Session, Response, exceptions


class ServiceAltaTNVED:
    def __init__(self, goods_name: str, attempts: int):
        self.headers: dict = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }
        self.logger: getLogger = get_logger(os.path.basename(__file__).replace(".py", "_") + str(datetime.now().date()))
        self.website: str = "https://www.alta.ru"
        self.proxy: dict = {"https": "http://75fae82583d404fa:RNW78Fm5@185.130.105.109:10000"}
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
            response: Response = session.get(f"{self.website}/tik/?tnfiltr=&srchstr={self._goods_name}",
                                             headers=self.headers, timeout=120)
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
        soup = BeautifulSoup(response.text if response else '', "html.parser")
        ol_element: ResultSet = soup.find_all('ol', class_='list-odd')
        data_tnveds: list = []
        if not ol_element:
            self._goods_name = " ".join(re.findall(r'[А-я]+', self._goods_name))
            self.attempts -= 1
            self.main()
        self.get_tnveds(ol_element, data_tnveds)
        return data_tnveds[:3]

    def get_tnveds(self, ol_element: ResultSet, data_tnveds: list) -> None:
        """

        :param ol_element:
        :param data_tnveds:
        :return:
        """
        position: int = 1
        for ol in ol_element:
            li_elements: ResultSet = ol.find_all('li')
            for li in li_elements:
                data: dict = {
                    'goods_name': self.goods_name, 'tnved': li.find('a', class_='jTnvedCodeTip').text.strip(),
                    'description': li.find_all('div', class_='pTik_c2 jOpen')[0].text.strip(), 'website': self.website,
                    'count': li.find('div', class_='t-right pTik_c3 jOpen').text.strip().split()[0],
                    'position': position
                }
                position += 1
                data_tnveds.append(data)

    def write_to_csv(self, output_file_path: str, data: list) -> None:
        """

        :param output_file_path:
        :param data:
        :return:
        """
        if data:
            if os.path.exists(output_file_path):
                self.to_csv(output_file_path, data, 'a')
            else:
                self.to_csv(output_file_path, data, 'w')

    @staticmethod
    def to_csv(output_file_path: str, data: list, operator: str) -> None:
        """

        :param output_file_path:
        :param data:
        :param operator:
        :return:
        """
        with open(output_file_path, operator, newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(data[0].keys()))
            if operator == 'w':
                writer.writeheader()
            writer.writerows(data)

    def main(self) -> None:
        """

        :return:
        """
        if self.attempts == 0:
            self.write_to_csv([{'goods_name': self.goods_name, 'tnved': None, 'description': None,
                                'website': self.website, 'count': None, 'position': None}])
            return
        response: Response = self.get_response()
        tnveds: list = self.parse_response(response)
        self.write_to_csv("goods_name_parse.csv", tnveds)


if __name__ == "__main__":
    with open("goods_name.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            service_tnved: ServiceAltaTNVED = ServiceAltaTNVED(row["goods_name"], 3)
            service_tnved.main()
