#!/usr/bin/env python
# Inspired by github.com/major/arksearch

import requests
from bs4 import BeautifulSoup


def get_cpu_html(url):
    """Connect to Intel's ark website and retrieve HTML."""
    USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")
    headers = {
        'User-Agent': USER_AGENT,
    }
    r = requests.get(url, headers=headers)
    return r.text


def generate_dict_data(html_input):
    """Generate a dictionary based on the HTML provided."""
    soup = BeautifulSoup(html_input, 'html5lib')
    data = dict()

    # Выбираем из всего списка свойств только нужные
    id_list = ['ProcessorNumber', 'StatusCodeText', 'BornOnDate', 'Lithography', 'Price1KUnits', 'CoreCount',
               'ClockSpeed', 'MaxTDP', 'GraphicsModel', 'SocketsSupported', 'InstructionSet'] #also need Codename!

    for table in soup.select('table.specs'):
        rows = table.find_all("tr")
        for row in rows[1:]:
            try:
                need_row = row['id'] in id_list
            except:
                need_row = False
            if need_row:
                cells = [cell.get_text("\n", strip=True)
                         for cell in row.find_all('td')]

                if cells[0] == 'T\nCASE':
                    cells[0] = 'T(CASE)'
                if "\n" in cells[0]:
                    cells[0] = cells[0][:cells[0].index("\n")]

                data[cells[0]] = cells[1]
    return data


def load_intel_data(url):
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
    full_url = 'http://ark.intel.com/ru/products/40478/Intel-Pentium-Processor-E5400-2M-Cache-2_70-GHz-800-MHz-FSB'

    data = load_cpu_data(full_url)

    for key, value in data.items():
        print('{}: {}'.format(key, value))