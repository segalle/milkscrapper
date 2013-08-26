"""
Gets information about Tipat Halav stations
"""
import requests
from lxml import etree


def get_url(page):
    url = "http://www.health.gov.il/Subjects/vaccines/two_drops/Pages/Vaccination_centers.aspx?WPID=WPQ8&PN=%d" % page
    return url


def get_full_html(url):
    html = requests.get(url)
    return html.text


def extract_stations_table(url):
    html = etree.HTML(url)
    table = html.xpath('//*[@class="cqwpGridViewTable cqwpGridViewTableFullVaccines PaymentsGridViewGroup"]')[0];
    return table


def extract_station_rows(table):
    rows = table.xpath('tr')
    duble_rows = rows[1::2]
    odd_rows = rows[2::2]
    tuple_list = zip(odd_rows, duble_rows)
    return tuple_list


def extract_station_from_row(row):
    pass


def save_station_to_json_file(path, station):
    pass
