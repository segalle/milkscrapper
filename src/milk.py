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
    tuple_list = zip(rows[1::2],rows[2::2])
    return tuple_list


def extract_station_from_row(row):
    #print etree.tostring(row[0])
    tds = row[0].xpath('td')
    d= {}
    d['city'] = tds[0].xpath("string()")
    d['address'] = tds[1].xpath("string()")
    d['name'] = tds[2].xpath("string()")
    d['owner'] = tds[4].xpath("string()")
    d['notes'] = tds[5].xpath("string()").strip()  
    d['days'] = [x.xpath("string()").strip() for x in row[1].xpath('.//table')[0].xpath('tr[position() >1 ]/td')[1::2]]
    
    return d


def save_station_to_json_file(path, station):
    pass


