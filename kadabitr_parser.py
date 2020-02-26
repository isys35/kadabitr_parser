import requests
from requests import Session
import time
import traceback
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup as BS


# headers_main= {
#     'Host': 'kad.arbitr.ru',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#     'Accept-Encoding': 'gzip, deflate',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Cache-Control': 'max-age=0'
# }
# url = 'http://kad.arbitr.ru/Kad/SearchInstances'
# affairs_html_list = []
# for i in range(1, 41):
#     time.sleep(6)
#     data ='{"Page":1,"Count":25,"CaseType":"G","Courts":[],"DateFrom":null,"DateTo":null,"Sides":[],"Judges":[],"CaseNumbers":[],"WithVKSInstances":false}'
#     response = None
#     while not response:
#         try:
#             response = requests.post(url, headers=headers_search, data=data.encode('utf8'))
#         except requests.exceptions.ConnectionError:
#             print('[WARNING] Проблема с подключением')
#             time.sleep(30)
#             print('[INFO] Попытка подключения')
#     if response.status_code == 200:
#         affairs_html_list.append(response.text)
#     else:
#         print('[WARNING] Ошибка ' + str(response.status_code))
#         wasm = input('wasm = :')
#         time.sleep(5)


class ParserKadabitr:
    def __init__(self):
        self.search_url = 'http://kad.arbitr.ru/Kad/SearchInstances'
        self.headers_search = {
            'Host': 'kad.arbitr.ru',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'x-date-format': 'iso',
            'Content-Length': '143',
            'Origin': 'http://kad.arbitr.ru',
            'Connection': 'keep-alive',
            'Referer': 'http://kad.arbitr.ru/',
        }
        self.full_cookies = str(input('Введите cookie: '))
        self.date_from = str(input('Введите первую дату (дд.мм.гггг): '))
        self.date_to = str(input('Введите последнюю дату (дд.мм.гггг): '))
        self.remake_date()
        self.head_cooikies, self.wasm = self.split_cookies()

    def split_cookies(self):
        splited_cookies = self.full_cookies.split('; ')
        wasm = None
        for i in range(0, len(splited_cookies)):
            if 'wasm' in splited_cookies[i]:
                wasm = splited_cookies.pop(i)
                break
        if wasm:
            wasm = wasm.replace('wasm=', '')
            head_cooikies = ''
            for cookie in splited_cookies:
                head_cooikies += cookie + '; '
            return head_cooikies, wasm

    def update_headers(self, wasm):
        self.headers_search['Cookie'] = self.head_cooikies + 'wasm=' + wasm

    def remake_date(self):
        day_from = self.date_from.split('.')[0]
        month_from = self.date_from.split('.')[1]
        year_from = self.date_from.split('.')[2]
        self.date_from = '"%s-%s-%sT00:00:00"' % (year_from, month_from, day_from)
        day_to = self.date_to.split('.')[0]
        month_to = self.date_to.split('.')[1]
        year_to = self.date_to.split('.')[2]
        self.date_to = '"%s-%s-%sT23:59:59"' % (year_to, month_to, day_to)

    def get_data_json(self, page, date_from, date_to):
        data = '{"Page":%i,"Count":25,"CaseType":"G","Courts":[],"DateFrom":%s,"DateTo":%s,"Sides":[],"Judges":[],' \
               '"CaseNumbers":[],"WithVKSInstances":false}' % (page, date_from, date_to)
        return data

    def get_elements_in_data(self):
        time.sleep(5)
        data_json = self.get_data_json(1, self.date_from, self.date_to)
        self.update_headers(self.wasm)
        response = None
        while not response:
            try:
                response = requests.post(self.search_url, headers=self.headers_search, data=data_json.encode('utf8'))
            except Exception as ex:
                print(ex)
                print('[WARNING] Проблема с подключением')
                time.sleep(30)
                print('[INFO] Попытка подключения')
            if response.status_code == 200:
                soup = BS(response.text, 'html.parser')
                count_affairs = soup.select('#documentsTotalCount')[0]['value']
                return count_affairs

    def get_data_low(self):
        count_affairs = int(self.get_elements_in_data())
        print('[INFO] Количество дел ' + str(count_affairs))
        if count_affairs > 1000:
            print('[WARNING] Неполная база, т.к количество данных больше тысячи')
            count_affairs = 1000
        page = count_affairs//25
        print('[INFO] Количество страниц ' + str(page))



parser = ParserKadabitr()
print(parser.get_data_low())
