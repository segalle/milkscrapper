# -*- coding: utf8 -*-
"""
Gets information about Tipat Halav stations
"""
import requests
from lxml import etree
import json
import os
import glob


# def get_url(page):
#     url = "http://www.health.gov.il/Subjects/vaccines/two_drops/Pages/Vaccination_centers.aspx?WPID=WPQ8&PN=%d" % page
#     return url
# 
# 
# def get_full_html(url):
#     html = requests.get(url)
#     return html.text

def get_page(pagenum, path):
    url = "http://www.health.gov.il/Subjects/vaccines/two_drops/Pages/Vaccination_centers.aspx?WPID=WPQ8&PN=%d" % pagenum
    fullpath = os.path.join(path, "page_%d.html" % pagenum)
    if os.path.exists(fullpath):
        with open(fullpath, 'r') as f:
            return f.read()

    html = requests.get(url)
    with open(fullpath, 'w') as f:
        f.write(html.text)
    return html.text
    

def extract_stations_table(url):
    html = etree.HTML(url)
    table = html.xpath('//*[@class="cqwpGridViewTable cqwpGridViewTableFullVaccines PaymentsGridViewGroup"]')
    return table[0] if table else None


def extract_station_rows(table):
    rows = table.xpath('tr')
    tuple_list = zip(rows[1::2], rows[2::2])
    return tuple_list


def extract_station_from_row(row):
    tds = row[0].xpath('td')
    d = {}
    d['id'] = int(row[0].get("id").rsplit('_', 1)[1])
    d['city'] = tds[0].xpath("string()").strip()
    d['address'] = tds[1].xpath("string()").strip()
    d['name'] = tds[2].xpath("string()").strip()
    d['owner'] = tds[4].xpath("string()").strip()
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
    with open(fullfilepath, 'w') as f:
        json.dump(station, f, indent=4)


def geocode(locality, address):
    payload = {"components": "locality:{0}".format(locality), "address": address, "sensor": "false"}
    r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload)
    # print r.url
    return r.json()


def save_geocode_to_file(path, station):
    fullfilepath = os.path.join(path, "%d.json" % station['id'])
    geojason = geocode(station["city"], station['address'])
    with open(fullfilepath, 'w') as f:
        json.dump(geojason, f, indent=4)


def save_station_from_page(page):  #includes geo files
    url = get_url(page)
    html = get_full_html(url)
    table = extract_stations_table(html)
    if table is None:
        return 0
    rows = extract_station_rows(table)
    for row in rows:
        station = extract_station_from_row(row)
        save_station_to_json_file(path, station)
        geo_file_path = "{0}\geo".format(path)
        save_geocode_to_file(geo_file_path, station)
    return len(rows)


def download_all_stations(path):
    """ max pages = max numner of pages on site"""
    downloaded = 0
    pagenum = 66
    while True:
        pagenum += 1
        print "downloading page #{0}...".format(pagenum),
        downloadedTotal = downloaded
        downloaded += save_station_from_page(path, pagenum)
        print "{0} stations.".format(downloaded - downloadedTotal) #prints how much was downloaded from page
        if downloaded == downloadedTotal:
            print "Done"
            break
    return downloaded


def geocode_station(station):
    return geocode(station["city"], station['address'])


def geocode_station_files(stations_path, path):
    """ Reads station_*.json files from stations_path and creates
    geodata_*.json files in path with results from the geocoding service """
    assert False


def retrieve_geodata_from_files(path):
    files = glob.glob(os.path.join(path, "*.json"))
    stations_geo = []
    for x, i in enumerate(files):
        with open(files[x], 'r') as f:
            stations_geo.append(json.load(f))
    return stations_geo


def retreive_data_from_files(path):
    files = glob.glob(os.path.join(path, "*.json"))
    stations = []
    for x, i in enumerate(files):
        with open(files[x], 'r') as f:
            stations.append(json.load(f))
    return stations


def create_geojson_feature(geocoding, station):

    if geocoding['status'] == u"OK":
            properties_dic = {}
#             properties_dic[u"עיר"] = station['city']
#             properties_dic[u"כתובת"] = station['address']
#             properties_dic[u"שם תחנה"] = station['name']
#             properties_dic[u"שעות פעילות"] = station['days']

            geometry_dic = {}
            geometry_dic["type"] = "Point"
            location = geocoding["results"][0]["geometry"]["location"]
            coordinates = [location["lng"], location["lat"]]
            geometry_dic["coordinates"] = coordinates

            feature_dic = {}
            feature_dic["properties"] = station# properties_dic
            feature_dic["type"] = "Feature"
            feature_dic["geometry"] = geometry_dic

            return feature_dic
    else:
        return "problem"


def geojson_generator(stations_geo, station):
    geocontent = {}
    lst_types = []
    non_scrapable = 0

    geocontent["type"] = "FeatureCollection"
    geocontent["features"] = []

    for i, x in enumerate(stations_geo):
        print station[i]
        station_dic = create_geojson_feature(x, station[i])
        if station_dic != "problem":
            lst_types.append(station_dic)
    geocontent["features"] = lst_types

    return geocontent


def save_geojason_to_file(geocontent, path):
    fullfilepath = os.path.join(path, "milk.geojson")
    with open(fullfilepath, 'w') as f:
        json.dump(geocontent, f, indent=4)

def geojson_handler(path):
    stations_geo = retrieve_geodata_from_files(os.path.join(path,"geo"))
    stations = retreive_data_from_files(path)
    geocontent = geojson_generator(stations_geo, stations)
    save_geojason_to_file(geocontent, path)

if __name__ == "__main__":
    download_all_stations("raw")
    geojson_handler("raw")



