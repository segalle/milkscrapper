# -*- coding: utf8 -*-
"""
Gets information about Tipat Halav stations
"""
import requests
from lxml import etree
import json
import os


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
    tuple_list = zip(rows[1::2], rows[2::2])
    return tuple_list


def extract_station_from_row(row):
    tds = row[0].xpath('td')
    d = {}
    d['id'] = int(row[0].get("id").rsplit('_',1)[1])
    d['city'] = tds[0].xpath("string()")
    d['address'] = tds[1].xpath("string()")
    d['name'] = tds[2].xpath("string()")
    d['owner'] = tds[4].xpath("string()")
    d['notes'] = tds[5].xpath("string()").strip()
    d['days'] = [x.xpath("string()").strip() for x in row[1].xpath('.//table')[0].xpath('tr[position() >1 ]/td')[1::2]]

    d['district'] = ""
    d['subdistrict'] = ""

    trs = row[1].xpath('.//table')[1].xpath('tr')
    for tr in trs:
        title, content = [td.xpath("string()").strip() for td in tr.xpath('td')]
        if title == u"מחוז:":
            d['district'] = content
        if title == u"נפה:":
            d['subdistrict'] = content

    return d


def save_station_to_json_file(path, station):
    fullfilepath = os.path.join(path, "%d.json" % station['id'])
    print fullfilepath
    with open(fullfilepath, 'w') as f:
        json.dump(station, f, indent=4)


def save_station_from_page(path, page):
    url = get_url(page)
    html = get_full_html(url)
    table = extract_stations_table(html)
    rows = extract_station_rows(table)
    for row in rows:
        station = extract_station_from_row(row)
        save_station_to_json_file(path, station)
    return len(rows)


def download_all_stations(path):
    """ max pages = max numner of pages on site"""
    # TODO: auto stop
    downloaded = 0
    pagenum = 0
    for page in range(1, 3):
        pagenum += 1
        print pagenum
        downloaded += save_station_from_page(path, page)
    return downloaded


def geocode(location, address):
    payload = {"components":"locality:{0}".format(location), "address":address, "sensor":"false"}
    r = requests.get("http://maps.googleapis.com/maps/api/geocode/json",params=payload)
    #print r.url
    return r.json()
    
def geocode_station(station):
    return geocode(station["city"],station['address'])


#     j = data
#     l = json.dumps(j)
# 
#     filename = station["id"]
#     fullfilepath = os.path.join(path, "%sxy.json" % filename)
#     with open(fullfilepath, 'w') as f:
#         f.write(json.dumps(l))

# if __name__ == "__main__":
#     # import sys;sys.argv = ['', 'Test.testName']
#     unittest.main()
