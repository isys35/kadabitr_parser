import requests
from requests import Session
import time
import traceback
from bs4 import BeautifulSoup as BS
import xlwt
import webbrowser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
import sys
import proxy
from requests.exceptions import ProxyError,SSLError


def load_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as read_file:
        rows = read_file.read().split('\n')
        courts_dict = {}
        for row in rows:
            cols = row.split(';')
            courts_dict[cols[0]] = cols[1]
        return courts_dict


COURTS = load_file('courts.txt')
HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
}
SEARCH_URL = 'https://kad.arbitr.ru/Kad/SearchInstances'
MAIN_URL = 'https://kad.arbitr.ru/'


def select_courts():
    add_court = input('Добавить суд (д/н): ') == 'д'
    court_ids = []
    while add_court:
        court_input = input('Введите полное наименование суда: ')
        if court_input.lower() in COURTS:
            court_id = COURTS[court_input.lower()]
            print(court_input, court_id)
            court_ids.append(court_id)
        else:
            print(f'[WARNING] {court_input} не найден')
        add_court = input('Добавить суд (д/н): ') == 'д'
    return court_ids


class ParserKadabitr:
    def __init__(self):
        self.cookies = None
        self.proxie = None
        self.proxie_list = list()
        # self.headers_search = {
        #     'Host': 'kad.arbitr.ru',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        #     'Accept': '*/*',
        #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Content-Type': 'application/json',
        #     'X-Requested-With': 'XMLHttpRequest',
        #     'x-date-format': 'iso',
        #     'Content-Length': '180',
        #     'Origin': 'http://kad.arbitr.ru',
        #     'Connection': 'keep-alive',
        #     'Referer': 'http://kad.arbitr.ru/',
        # }
        # self.headers_price = {
        #     'Host': 'kad.arbitr.ru',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Referer': 'https://kad.arbitr.ru/',
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #     'Connection': 'keep-alive',
        #     'Upgrade-Insecure-Requests': '1',
        #     'Cache-Control': 'max-age=0'
        # }
        # self.headers_price_get = {
        #     'Host': 'kad.arbitr.ru',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        #     'Accept': 'application/json, text/javascript, */*',
        #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Content-Type': 'application/json',
        #     'X-Requested-With': 'XMLHttpRequest',
        #     'Connection': 'keep-alive',
        #     'Pragma': 'no-cache',
        #     'Cache-Control': 'no-cache'
        # }
        # self.headers_phone = {
        #     'Host': 'www.list-org.com',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Connection': 'keep-alive',
        #     'Upgrade-Insecure-Requests': '1',
        #     'TE': 'Trailers'
        # }
        #self.full_cookies = str(input('Введите cookie: '))
        #self.date_from = str(input('Введите первую дату (дд.мм.гггг): '))
        #self.date_to = str(input('Введите последнюю дату (дд.мм.гггг): '))
        #self.party_member = str(input('Введите участгника дела(если не требуется введите Enter): '))
        #self.courts = str(self.get_courts()).replace("'", '"')
        #self.remake_date()
        #self.head_cooikies, self.wasm = self.split_cookies()
        # self.count_affairs = 0
        # self.url_find_phone_by_inn = 'https://www.list-org.com/search?type=inn&val='
        # self.session = Session()

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

    def update_headers(self, wasm, referer=None):
        self.headers_search['Cookie'] = self.head_cooikies + 'wasm=' + wasm
        self.headers_price['Cookie'] = self.head_cooikies + 'wasm=' + wasm
        self.headers_price['Cookie'] = 'notShowTooltip=yes; ' + self.headers_price['Cookie']

    def remake_date(self, date_from, date_to):
        day_from = date_from.split('.')[0]
        month_from = date_from.split('.')[1]
        year_from = date_from.split('.')[2]
        date_from = '%s-%s-%sT00:00:00' % (year_from, month_from, day_from)
        day_to = date_to.split('.')[0]
        month_to = date_to.split('.')[1]
        year_to = date_to.split('.')[2]
        date_to = '%s-%s-%sT23:59:59' % (year_to, month_to, day_to)
        return date_from, date_to

    def get_data(self):
        count_affairs = int(self.get_elements_in_data())
        print('[INFO] Количество дел ' + str(count_affairs))
        if count_affairs > 1000:
            print('[WARNING] Неполная база, т.к количество данных больше тысячи')
            count_affairs = 1000
        self.count_affairs = count_affairs
        page = count_affairs // 25
        if page == 0:
            page = 1
        print('[INFO] Количество страниц ' + str(page))
        data_allpages = []
        for p in range(1, page + 1):
            data_low = self.get_page_data(p)
            for data in data_low:
                data_allpages.append(data)
        for data in data_allpages:
            price = self.get_price(data['href'])
            price = price.replace(',', '.')
            print(price)
            phones = self.get_phone(data['defendant_inn'])
            print(phones)
            try:
                data['price'] = float(price)
            except ValueError:
                data['price'] = None
            data['phones'] = phones
            self.count_affairs -= 1
            print('[INFO] Осталось {} дел '.format(self.count_affairs))
            self.save_data_excel(data_allpages)
        self.save_data_excel(data_allpages)

    def parsing_page(self, response):
        soup = BS(response.content, 'lxml')
        containers = soup.select('.b-container')
        all_split_containers = []
        i = 0
        data = []
        while i != len(containers):
            all_split_containers.append([containers[i], containers[i + 1], containers[i + 2], containers[i + 3]])
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
                plaintiff_adress = affair[2].select('.js-rolloverHtml')[0].text \
                    .replace(plaintiff_name, '').replace(plaintiff_inn, '').replace('\n', '').strip()
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
            if defendant_inn:
                defendant_inn = defendant_inn.split('ИНН: ')[-1]
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

    def get_data_title(self, selected_courts, date_from, date_to, selected_party_member, page):
        if not self.cookies:
            self.cookies = self.get_cookie()
        post_data = {"Page": page,
                     "Count": 25,
                     "CaseType": "G",
                     "Courts": selected_courts,
                     "DateFrom": date_from,
                     "DateTo": date_to,
                     "Sides": selected_party_member,
                     "Judges": [],
                     "CaseNumbers": [],
                     "WithVKSInstances": False}
        r = requests.post(SEARCH_URL, headers=HEADERS, json=post_data, cookies=self.cookies, proxies=self.proxie)
        if r.status_code == 200:
            data = self.parsing_page(r)
            return data
        elif r.status_code == 429:
            self.update_proxie()
        else:
            print(r.status_code)
            sys.exit()

    def get_count_affairs(self, selected_courts, date_from, date_to, selected_party_member):
        if not self.cookies:
            self.cookies = self.get_cookie()
        post_data = {"Page": 1,
                     "Count": 25,
                     "CaseType": "G",
                     "Courts": selected_courts,
                     "DateFrom": date_from,
                     "DateTo": date_to,
                     "Sides": selected_party_member,
                     "Judges": [],
                     "CaseNumbers": [],
                     "WithVKSInstances": False}
        while True:
            try:
                r = requests.post(SEARCH_URL, headers=HEADERS, json=post_data, cookies=self.cookies, proxies=self.proxie)
            except ProxyError:
                print(str(self.proxie) + ' ProxyError')
                self.update_proxie()
                continue
            if r.status_code == 200:
                soup = BS(r.text, 'lxml')
                count_affairs = soup.select('#documentsTotalCount')[0]['value']
                return int(count_affairs)
            elif r.status_code == 429:
                self.update_proxie()
            else:
                print(r.status_code)
                sys.exit()

    def update_proxie(self):
        if not self.proxie_list:
            self.proxie_list = proxy.get_proxies()
        self.proxie = {'https': self.proxie_list.pop()}

    def start(self):
        date_from = str(input('Введите первую дату (дд.мм.гггг): '))
        date_to = str(input('Введите последнюю дату (дд.мм.гггг): '))
        date_from, date_to = self.remake_date(date_from, date_to)
        print(date_from, date_to)
        selected_party_member = str(input('Введите участника дела(если не требуется введите Enter): '))
        if selected_party_member:
            selected_party_member = [{"Name": f"{selected_party_member}", "Type": 1, "ExactMatch": False}]
        else:
            selected_party_member = []
        selected_courts = select_courts()
        if selected_courts:
            print(selected_courts)
        count_affairs = self.get_count_affairs(selected_courts, date_from, date_to, selected_party_member)
        print('[INFO] Количество дел ' + str(count_affairs))
        if count_affairs > 1000:
            print('[WARNING] Неполная база, т.к количество данных больше тысячи')
            count_affairs = 1000
        pages = count_affairs // 25
        if count_affairs % 25 != 0:
            pages += 1
        print('[INFO] Количетсво страниц ' + str(pages))
        data_titles = []
        for page in range(1, pages+1):
            print('[INFO] Страница ' + str(page))
            data_title = self.get_data_title(selected_courts, date_from, date_to, selected_party_member, page)
            data_titles.extend(data_title)
        for data in data_titles:
            print('[INFO] Получение суммы исковых требований для ' + data['href'])
            price = self.get_price(data['href'])
        #     price = price.replace(',', '.')
        #     print(price)
        #     phones = self.get_phone(data['defendant_inn'])
        #     print(phones)
        #     try:
        #         data['price'] = float(price)
        #     except ValueError:
        #         data['price'] = None
        #     data['phones'] = phones
        #     self.count_affairs -= 1
        #     print('[INFO] Осталось {} дел '.format(self.count_affairs))
        #     self.save_data_excel(data_allpages)
        # self.save_data_excel(data_allpages)

    def save_data_excel(self, data):
        file_name = 'data.xls'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('sheet')
        ws.col(4).width = 6000
        for i in range(0, 9):
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
            if 'price' in data[i]:
                ws.write(i + 1, 7, data[i]['price'])
            ws.write(i + 1, 8, data[i]['num'])
            if 'phones' in data[i]:
                for n in range(0, len(data[i]['phones'])):
                    if n < 4:
                        ws.write(i + 1, 2 + n, data[i]['phones'][n])
        wb.save(file_name)
        print(f'[INFO] Файл {file_name} создан')

    def response_text(self, page):
        data_json = self.get_data_json(page, self.date_from, self.date_to)
        self.update_headers(self.wasm)
        response = None
        while not response:
            try:
                response = requests.post(self.search_url, headers=self.headers_search, data=data_json.encode('utf8'))
                print(response)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 451:
                    self.full_cookies = str(input('Введите cookie: '))
                    self.head_cooikies, self.wasm = self.split_cookies()
                    self.update_headers(self.wasm)
            except Exception as ex:
                print(ex)
                print('[WARNING] Проблема с подключением')
                print('[INFO] Попытка подключения')
                time.sleep(30)

    def get_page_data(self, page):
        time.sleep(5)
        print('[INFO] Страница ' + str(page))
        response_txt = self.response_text(page)
        # with open('page.html', 'wb') as html_file:
        # html_file.write(response_txt.encode('cp1251'))
        soup = BS(response_txt, 'html.parser')
        containers = soup.select('.b-container')
        all_split_containers = []
        i = 0
        data = []
        while i != len(containers):
            all_split_containers.append([containers[i], containers[i + 1], containers[i + 2], containers[i + 3]])
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
                plaintiff_adress = affair[2].select('.js-rolloverHtml')[0].text \
                    .replace(plaintiff_name, '').replace(plaintiff_inn, '').replace('\n', '').strip()
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
            if defendant_inn:
                defendant_inn = defendant_inn.split('ИНН: ')[-1]
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

    # def get_price_id(self, url):
    #     self.update_headers(self.wasm)
    #     response = None
    #     while not response:
    #         try:
    #             time.sleep(.3)
    #             response = requests.get(url, headers=self.headers_price)
    #             print(response)
    #             if response.status_code == 200:
    #                 # with open('page2.html', 'w', encoding='utf8') as html_file:
    #                 # html_file.write(response.text)
    #                 soup = BS(response.text, 'html.parser')
    #                 main_id = soup.select('.js-instanceId')[-1]['value']
    #                 return main_id
    #             elif response.status_code == 451:
    #                 self.full_cookies = str(input('Введите cookie: '))
    #                 self.head_cooikies, self.wasm = self.split_cookies()
    #                 self.update_headers(self.wasm)
    #                 self.headers_price_get['Cookie'] = self.headers_search['Cookie']
    #         except Exception as ex:
    #             print(ex)
    #             print('[WARNING] Проблема с подключением')
    #             time.sleep(30)
    #             print('[INFO] Попытка подключения')

    def get_price_request(self, url):
        price_id = self.get_price_id(url)
        case_id = url.split('/')[-1]
        time_id = str(time.time()).replace('.', '')[:-3]
        url_req = 'https://kad.arbitr.ru/Kad/InstanceDocumentsPage?_=%s&id=%s&caseId=%s&withProtocols=true&perPage=30' \
                  '&page=1' % (time_id, price_id, case_id)
        return url_req



    def get_price(self, url):
        #headers = HEADERS
        #headers['Referer'] = url
        response = requests.get(url, headers=HEADERS, cookies=self.cookies)
        if response.status_code == 200:
            soup = BS(response.text, 'html.parser')
            price_id = soup.select('.js-instanceId')[-1]['value']
        if response.status_code == 429:
            self.update_proxie()
        else:
            print(response.status_code)
            sys.exit()
        case_id = url.split('/')[-1]
        time_id = int(time.time() * 1000)
        url_hronoligic_data = 'https://kad.arbitr.ru/Kad/InstanceDocumentsPage?_={}&id={}&caseId={}&withProtocols' \
                              '=true&perPage=30&page=1'.format(time_id, price_id, case_id)




    # def get_price(self, url):
    #     print('[INFO] Получение суммы исковых требований для ' + url)
    #     self.headers_price_get['Referer'] = url
    #     self.headers_price_get['Cookie'] = self.headers_search['Cookie']
    #     response = None
    #     while not response:
    #         try:
    #             req_url = self.get_price_request(url)
    #             time.sleep(.3)
    #             response = requests.get(req_url, headers=self.headers_price_get)
    #             print(response)
    #             if response.status_code == 200:
    #                 return response.json()['Result']['Items'][-1]['AdditionalInfo'].split(' ')[-1]
    #             elif response.status_code == 451:
    #                 self.full_cookies = str(input('Введите cookie: '))
    #                 self.head_cooikies, self.wasm = self.split_cookies()
    #                 self.update_headers(self.wasm)
    #                 self.headers_price_get['Cookie'] = self.headers_search['Cookie']
    #         except Exception as ex:
    #             print(ex)
    #             print('[WARNING] Проблема с подключением')
    #             print('[INFO] Попытка подключения....')
    #             time.sleep(30)

    def get_phone_url(self, inn):
        time.sleep(.2)
        r = self.session.get(self.url_find_phone_by_inn + inn, headers=self.headers_phone)
        if r.status_code == 200:
            Except = True
            soup = BS(r.text, 'html.parser')
            p = None
            while Except:
                try:
                    soup = BS(r.text, 'html.parser')
                    p = soup.select('.org_list')[0].select('p')
                    Except = False
                except Exception as ex:
                    print(self.url_find_phone_by_inn + inn)
                    webbrowser.open(self.url_find_phone_by_inn + inn)
                    input('[WARNING] Пройдите рекапчу')
                    print('[INFO] Пересоздаём ссесию')
                    self.session = Session()
                    r = self.session.get(self.url_find_phone_by_inn + inn, headers=self.headers_phone)
            if p:
                org_url = soup.select('.org_list')[0].select('p')[0].select('a')[0]['href']
                return org_url
            else:
                return None

    def get_phone(self, inn):
        if inn == 'Данные скрыты':
            return []
        if not inn:
            return []
        print('[INFO] Получение телефона для ' + str(inn))
        url = self.get_phone_url(inn)
        if not url:
            return []
        url = 'https://www.list-org.com' + url
        time.sleep(.2)
        r = None
        while not r:
            r = self.session.get(url, headers=self.headers_phone)
            if r.status_code == 200:
                soup = BS(r.text, 'html.parser')
                p = soup.select('p')
                phones = []
                for el in p:
                    if el.select('i'):
                        if 'Телефон:' in el.select('i')[0].text:
                            for a in el.select('a'):
                                phones.append(a.text)
                return phones

    def get_cookie(self):
        print('[INFO] Обновление Сookie из selenium')
        geckodriver_path = os.path.abspath('geckodriver.exe')
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(executable_path=geckodriver_path, options=options)
        driver.get(MAIN_URL)
        page_source = driver.page_source
        if BS(page_source, 'lxml').select_one('a.b-promo_notification-popup-close.js-promo_notification-popup-close'):
            element = driver.find_element_by_css_selector('a.b-promo_notification-popup-close.js-promo_notification-popup-close')
            element.click()
        element = driver.find_element_by_css_selector('.civil')
        element.click()
        while True:
            cookies = driver.get_cookies()
            cookies_name = [cookie['name'] for cookie in cookies]
            if 'wasm' in cookies_name:
                driver.close()
                break
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        print('[INFO] Сookie получены')
        return cookies_dict


if __name__ == '__main__':
    parser = ParserKadabitr()
    parser.start()
