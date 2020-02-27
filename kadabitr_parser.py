import requests
from requests import Session
import time
import traceback
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup as BS
import xlwt

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
            'Content-Length': '180',
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
        response_txt = self.response_text(1)
        soup = BS(response_txt, 'html.parser')
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
        data_allpages = []
        for p in range(1, page+1):
            data_low = self.get_page_data(p)
            for data in data_low:
                data_allpages.append(data)
        self.save_data_excel(data_allpages)

    def save_data_excel(self, data):
        print(data)
        file_name = 'data.xls'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('sheet')
        ws.col(4).width = 6000
        for i in range(0,9):
            ws.col(i).width = 6000
        ws.write(0, 0, 'Наименование')
        ws.write(0, 1, 'Адрес')
        ws.write(0, 2, 'Телефон 1')
        ws.write(0, 3, 'Телефон 2')
        ws.write(0, 4, 'Телефон 3')
        ws.write(0, 5, 'Телефон 4')
        ws.write(0, 6, 'Истец')
        ws.write(0, 7, 'Сумма исковых требований')
        ws.write(0, 8, 'Номер дела')
        for i in range(0, len(data)):
            ws.write(i + 1, 0, data[i]['defendant_name'])
            ws.write(i + 1, 1, data[i]['defendant_adress'])
            ws.write(i + 1, 6, data[i]['plaintiff_name'])
            ws.write(i + 1, 8, data[i]['num'])
        wb.save(file_name)
        print(f'[INFO] Файл {file_name} создан')

    def response_text(self, page):
        data_json = self.get_data_json(page, self.date_from, self.date_to)
        self.update_headers(self.wasm)
        response = None
        while not response:
            try:
                response = requests.post(self.search_url, headers=self.headers_search, data=data_json.encode('utf8'))
                print(response.status_code)
            except Exception as ex:
                print(ex)
                print('[WARNING] Проблема с подключением')
                time.sleep(30)
                print('[INFO] Попытка подключения')
            if response.status_code == 200:
                return response.text

    def get_page_data(self, page):
        time.sleep(5)
        print('[INFO] Страница ' + str(page))
        response_txt = self.response_text(page)
        with open('page.html', 'wb') as html_file:
            html_file.write(response_txt.encode('cp1251'))
        soup = BS(response_txt, 'html.parser')
        containers = soup.select('.b-container')
        all_split_containers = []
        i = 0
        data = []
        while i != len(containers):
            all_split_containers.append([containers[i], containers[i+1], containers[i+2], containers[i+3]])
            i += 4
        for affair in all_split_containers:
            date = affair[0].select('.civil')
            if date:
                date = date[0].text.replace('\n', '')
            else:
                date = affair[0].select('.civil_simple')[0].text.replace('\n', '')
            num = affair[0].select('.num_case')[0].text.replace('\n', '').strip()
            href = affair[0].select('.num_case')[0]['href']
            judge = affair[1].select('.judge')
            if judge:
                judge = affair[1].select('.judge')[0]['title']
            else:
                judge = None
            instance = affair[1].select('div')[-1]['title']
            plaintiff_name = affair[2].select('.js-rolloverHtml')
            if plaintiff_name:
                plaintiff_name = affair[2].select('.js-rolloverHtml')[0].select('strong')[0].text
                plaintiff_inn = affair[2].select('.js-rolloverHtml')[0].select('div')
                if plaintiff_inn:
                    plaintiff_inn = plaintiff_inn[0].text.replace('\n', '').strip()
                else:
                    plaintiff_inn = 'Данные скрыты'
                plaintiff_adress = affair[2].select('.js-rolloverHtml')[0].text\
                    .replace(plaintiff_name, '').replace(plaintiff_inn,'').replace('\n', '').strip()
            else:
                plaintiff_name = ''
                plaintiff_inn = ''
                plaintiff_adress = ''
            defendant_name = affair[3].select('.js-rolloverHtml')
            if defendant_name:
                defendant_name = affair[3].select('.js-rolloverHtml')[0].select('strong')[0].text
                defendant_inn = affair[3].select('.js-rolloverHtml')[0].select('div')
                if defendant_inn:
                    defendant_inn = defendant_inn[0].text.replace('\n', '').strip()
                else:
                    defendant_inn = 'Данные скрыты'
                defendant_adress = affair[3].select('.js-rolloverHtml')[0].text \
                    .replace(defendant_name, '').replace(defendant_inn, '').replace('\n', '').strip()
            else:
                defendant_name = ''
                defendant_inn = ''
                defendant_adress = ''
            affair_data = {
                'date': date,
                'num': num,
                'href': href,
                'judge': judge,
                'instance': instance,
                'plaintiff_name': plaintiff_name,
                'plaintiff_inn': plaintiff_inn,
                'plaintiff_adress': plaintiff_adress,
                'defendant_name': defendant_name,
                'defendant_inn': defendant_inn,
                'defendant_adress': defendant_adress
            }
            data.append(affair_data)
        return data



parser = ParserKadabitr()
parser.get_data_low()
