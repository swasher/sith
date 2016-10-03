#!/usr/bin/env python

# parser for www.cpu-world.com, using for AMD processors


from bs4 import BeautifulSoup

"""
# Это полностью рабочая функция фетчинга страницы с данными, генерируемыми ява-скриптами.
# Возвращает html.
# В ней используется библиотека dryscrape, которая требует в зависимостях кучу бинарников,
# и из-за этого ее не получается установить на heroku

import sys
import dryscrape
def get_cpu_html(url):
    if 'linux' in sys.platform:
        # start xvfb in case no X is running. Make sure xvfb
        # is installed, otherwise this won't work!
        dryscrape.start_xvfb()

    session = dryscrape.Session()
    session.visit(url)
    html = session.body()

    return html
"""

from selenium import webdriver
from time import sleep

def get_cpu_html(url):
    #driver = webdriver.PhantomJS('/usr/local/lib/node_modules/phantomjs2/lib/phantom/bin/phantomjs')
    driver = webdriver.PhantomJS('/app/node_modules/.bin/phantomjs') # heroku, must be in $PATH
    #driver = webdriver.PhantomJS('/app/vendor/phantomjs/bin/phantomjs') # heroku
    #driver = webdriver.PhantomJS()
    driver.get(url)
    sleep(1)
    html = driver.page_source
    driver.quit()
    return html

def generate_dict_data(html_input):
    """Generate a dictionary based on the HTML provided."""
    #soup = BeautifulSoup(html_input, 'html.parser')
    soup = BeautifulSoup(html_input, 'html5lib')

    # Выбираем из всего списка свойств только нужные
    id_list = ['ProcessorNumber', 'StatusCodeText', 'BornOnDate', 'Lithography', 'Price1KUnits', 'CoreCount',
               'ClockSpeed', 'MaxTDP', 'GraphicsModel', 'SocketsSupported', 'InstructionSet'] #also need Codename!

    table = soup.find('table', attrs={'class':'spec_table'})
    table_body = table.find('tbody')

    data = dict()
    rows = table_body.find_all('tr')
    for row in rows[1:-2]:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        #data.append([ele for ele in cols if ele]) # Get rid of empty values
        cols = [ele.replace(u' \xa0?', u'') for ele in cols]
        #print(cols)
        if len(cols) == 2:
            data[cols[0]] = cols[1]

    return data


def load_amd_data(url):
    """
    Must return a dict with CPU data fetched from Intel Ark
    :param url:
    :return:
    """
    html = get_cpu_html(url)
    data = generate_dict_data(html)
    return data


if __name__ == '__main__':
    #
    # DEBUG
    #
    full_url = 'http://www.cpu-world.com/CPUs/K8/AMD-Athlon%2064%203000+%20-%20ADA3000DIK4BI%20(ADA3000BIBOX).html'

    data = load_amd_data(full_url)

    for key, value in data.items():
        print('{}: {}'.format(key, value))