from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
from bs4 import BeautifulSoup as BS
from selenium.common.exceptions import WebDriverException
"""
Прокси hidemy.name
"""

URL = 'https://hidemy.name/ru/proxy-list/?type=s&anon=4#list'


def get_proxies():
    geckodriver_path = os.path.abspath('geckodriver.exe')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=geckodriver_path, options=options)
    driver.get(URL)
    while True:
        try:
            soup = BS(driver.page_source, 'lxml')
            table_block = soup.select_one('div.table_block')
            if table_block:
                if table_block.select_one('tbody'):
                    break
        except WebDriverException:
            print('WebDriverException')
    driver.close()
    trs = table_block.select_one('tbody').select('tr')
    proxies = [tr.select('td')[0].text + ':' + tr.select('td')[1].text for tr in trs]
    proxies.reverse()
    return proxies


if __name__ == '__main__':
    proxies = get_proxies()