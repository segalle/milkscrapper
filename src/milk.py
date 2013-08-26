# -*- coding: utf8 -*-
"""
Gets information about Tipat Halav stations
"""
import requests
from lxml import etree
import json
import os
import tempfile
import urllib2


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
    d['district'] = row[1].xpath('.//table')[1].xpath('tr')[0].xpath('td')[1].xpath("string()").strip()
    row_subdistrict = row[1].xpath('.//table')[1].xpath('tr')[1]
    if row_subdistrict.xpath('td')[0].xpath("string()").strip() != u"נפה:":
        d['subdistrict'] = ""
    else:
        d['subdistrict'] = row_subdistrict.xpath('td')[1].xpath("string()").strip()
    return d

def save_station_to_json_file(path, station):
    fullfilepath = os.path.join(path, "%d.json" % station['id'])
    print fullfilepath
    with open(fullfilepath, 'w') as file:
        file.write(json.dumps(station))
    pass


def save_station_from_page(path, page):
    url = get_url(page)
    html = get_full_html(url)
    table = extract_stations_table(html)
    rows = extract_station_rows(table)
    
    countfiles = 0
    for row in rows:
        station = extract_station_from_row(row)
        save_station_to_json_file(path,station)
        countfiles +=1

    return countfiles

def save_station_from_all_pages(path,maxpages):
    """ max pages = max numner of pages on site"""
    for page in range(1,maxpages+1):
        save_station_from_page(path, page)


def address_to_latlong (address, path, station_id):
    location_url = "http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false".format(address);
    data = urllib2.urlopen(location_url)
    
    j = json.load(data)
    l = json.dumps(j)
    
    lat = j['results'][0]['geometry']['location']['lat']
    lng = j['results'][0]['geometry']['location']['lng']
    filename = "{0}lat{1}long{2}".format(station_id,lat,lng)
    fullfilepath = os.path.join(path, "%s.json" % filename)
    with open(fullfilepath, 'w') as file:
        file.write(json.dumps(l))
    
   
