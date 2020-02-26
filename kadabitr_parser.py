import requests
from requests import Session
import time
import traceback
from requests.exceptions import ConnectionError

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
        self.first_date = str(input('Введите первую дату: '))
        self.last_date = str(input('Введите последнюю дату: '))
        self.splited_cookies = self.split_cookies()

    def split_cookies(self):
        splited_cookies = self.full_cookies.split('; ')
        wasm = None
        for i in range(0,len(splited_cookies)):
            if 'wasm' in splited_cookies[i]:
                wasm = splited_cookies.pop(i)
                break
        if wasm:
            wasm = wasm.replace('wasm=','')
            head_cooikies = ''
            for cookie in splited_cookies:
                head_cooikies += cookie+'; '
            return head_cooikies, wasm




parser = ParserKadabitr()
