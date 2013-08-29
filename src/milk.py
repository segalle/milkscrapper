# -*- coding: utf8 -*-
"""
Gets information about Tipat Halav stations
"""
import requests
from lxml import etree
import json
import os
import glob

 
def get_page(pagenum, path):
    url = "http://www.health.gov.il/Subjects/vaccines/two_drops/Pages/Vaccination_centers.aspx?WPID=WPQ8&PN=%d" % pagenum
    fullpath = os.path.join(path, "page_%d.html" % pagenum)
    if os.path.exists(fullpath):
        with open(fullpath, 'r') as f:
            return f.read()

    html = requests.get(url)
    if os.path.exists(path):
        with open(fullpath, 'w') as f:
            f.write(html.text)
    else:
        os.makedirs(path)
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
    d['phones'] = tds[3].xpath("string()").strip()
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
    fullfilepath = os.path.join(path, "station_%d.json" % station['id'])
    with open(fullfilepath, 'w') as f:
        json.dump(station, f, indent=4)


def geocode(locality, address):
    payload = {"components": u"locality:{0}".format(locality), "address": address, "sensor": "false"}
    r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload)
    # print r.url
    return r.json()


def save_station_from_page(path, pagenum, cache_dir):  #includes geo files
    html = get_page(pagenum, cache_dir)
    table = extract_stations_table(html)
    if table is None:
        return 0
    rows = extract_station_rows(table)
    for row in rows:
        station = extract_station_from_row(row)
        save_station_to_json_file(path, station)
#         geo_file_path = "{0}\geo".format(path)
#         save_geocode_to_file(geo_file_path, station)
    return len(rows)


def download_all_stations(path, cache_dir):
    downloaded = 0
    pagenum = 0
    while True:
        pagenum += 1
        print "downloading page #{0}...".format(pagenum),
        downloadedTotal = downloaded
        downloaded += save_station_from_page(path, pagenum, cache_dir)
        print "{0} stations.".format(downloaded - downloadedTotal) #prints how much was downloaded from page
        if downloaded == downloadedTotal:
            break

    print "Downloading completed."

    return downloaded


def geocode_station(station):
    return geocode(station["city"], station['address'])


def save_geocode_to_file(fullfilepath, station):
    geojson = geocode(station["city"], station['address'])
    if not os.path.exists(os.path.dirname(fullfilepath)):
        os.mkdir(os.path.dirname(fullfilepath))

    with open(fullfilepath, 'w') as f:
        json.dump(geojson, f, indent=4)
        
    return geojson


def geocode_station_files(stations_path, path):
    files = glob.glob(os.path.join(stations_path, "station_*.json"))
    n = 0
    for x in files:
        station_id = x.split('.')[-2].split('_')[-1]
        print "Geocoding station #{0}...".format(station_id),
        fullfilepath = os.path.join(path, "geodata_{0}.json".format(station_id))
        if not os.path.exists(fullfilepath):
            with open(x, 'r') as f:
                result = save_geocode_to_file(fullfilepath, json.load(f))
            print result['status']
        else:
            print "Skipped"
        n += 1

    return n


def create_tuple_list(path):
    tuples_full = []
    station_file_names = glob.glob(os.path.join(path, "station_*.json"))
    for filename in station_file_names:
        geo_file_name = filename.replace("station","geodata")
        if os.path.exists(geo_file_name):
            with open(filename, 'r') as f:
                station_content = json.load(f)
            with open(geo_file_name, 'r') as f_geo:
                geo_content = json.load(f_geo)
            
            tuples_full.append((geo_content,station_content))
    return tuples_full


def create_geojson_feature(geocoding, station):

    if geocoding['status'] == u"OK":
            properties_dic = {}

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


def geojson_generator(full_tuple_lst):
    geocontent = {}
    lst_types = []
    non_scrapable = 0

    geocontent["type"] = "FeatureCollection"
    geocontent["features"] = []

    for station, geodata in full_tuple_lst: #station_geo
        feature = create_geojson_feature(station, geodata)
        if feature != "problem":
            lst_types.append(feature)
    geocontent["features"] = lst_types

    return geocontent


def geojson_handler(path, target):
    geocontent = geojson_generator(create_tuple_list(path))
    with open(target, 'w') as f:
        json.dump(geocontent, f, indent=4)

if __name__ == "__main__":
    download_all_stations("cache","cache")
    geocode_station_files("cache", "cache")
    geojson_handler("cache", "milk.geojson")
    print "Done"


