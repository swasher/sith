#!/usr/bin/env python

#
# Inspired by github.com/major/arksearch
#


#from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup



USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")

#
#  possibly deprecated
#
def find_quick_url(search_term):
    url = "http://ark.intel.com/search/AutoComplete?term={0}"
    headers = {
        'User-Agent': USER_AGENT,
    }
    r = requests.get(url.format(search_term, headers=headers))
    return r.json()


def get_cpu_html(quickurl):
    """Connect to Intel's ark website and retrieve HTML."""
    full_url = "http://ark.intel.com{0}".format(quickurl)
    headers = {
        'User-Agent': USER_AGENT,
    }
    r = requests.get(full_url, headers=headers)
    return r.text


# def generate_table_data(html_output):
#     """Generate an ASCII table based on the HTML provided."""
#     soup = BeautifulSoup(html_output, 'html.parser')
#
#     table_data = [
#         ['Parameter', 'Value']
#     ]
#
#     for table in soup.select('table.specs'):
#         rows = table.find_all("tr")
#         for row in rows[1:]:
#             cells = [cell.get_text("\n", strip=True)
#                      for cell in row.find_all('td')]
#
#             if cells[0] == 'T\nCASE':
#                 cells[0] = 'T(CASE)'
#             if "\n" in cells[0]:
#                 cells[0] = cells[0][:cells[0].index("\n")]
#
#             table_data.append(cells)
#
#     return table_data

def generate_dict_data(html_output):
    """Generate an ASCII table based on the HTML provided."""
    soup = BeautifulSoup(html_output, 'html.parser')

    table_data = [
        ['Parameter', 'Value']
    ]

    for table in soup.select('table.specs'):
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = [cell.get_text("\n", strip=True)
                     for cell in row.find_all('td')]

            if cells[0] == 'T\nCASE':
                cells[0] = 'T(CASE)'
            if "\n" in cells[0]:
                cells[0] = cells[0][:cells[0].index("\n")]

            table_data.append(cells)

    return table_data


if __name__ == '__main__':
    p0 = "E5300"
    p1 = "Intel Celeron G540"
    p2 = "Intel Core i3 4160"
    p3 = "Intel Pentium E5400"

    full_url = '/products/77489/Intel-Core-i3-4160T-Processor-3M-Cache-3_10-GHz'

    html = get_cpu_html(full_url)
    table = generate_table_data(html)

    print(table)

    #a = find_quick_url(p0)
    #print(a)
