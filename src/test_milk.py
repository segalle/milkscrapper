# -*- coding: utf8 -*-
import glob
import json
import milk
import os.path
import shutil
import tempfile
import unittest
from unittest.case import skip


class Test(unittest.TestCase):

    CACHE_DIR = "cache"

    def test_get_page(self):

        path = tempfile.mkdtemp()
        try:
            html1 = milk.get_page(1, path)
            self.assertIn("zebraPhone", html1)
            self.assertTrue(os.path.exists(os.path.join(path, "page_1.html")))

            # Get from cache, result must be identical.
            html2 = milk.get_page(1, path)
            self.assertEquals(html1, html2)
        finally:        
            shutil.rmtree(path)

    def test_get_stations_table(self):

        html = milk.get_page(1, self.CACHE_DIR)
        table = milk.extract_stations_table(html)

        self.assertEquals(table.tag, "table")
        self.assertEquals(table.get('class'), "cqwpGridViewTable " \
                         "cqwpGridViewTableFullVaccines PaymentsGridViewGroup")

    def test_get_stations_rows(self):

        html = milk.get_page(1, self.CACHE_DIR)
        table = milk.extract_stations_table(html)
        rows = milk.extract_station_rows(table)

        self.assertEquals(15, len(rows))
        for row in rows:
            self.assertEquals(2, len(row))

    def test_extract_station_from_row(self):

        station = self.get_a_station(1, 9)
        self.assertIsInstance(station, dict)
        self.assertEquals(605, station['id'])
        self.assertEquals(u"אבשלום", station['city'])
        self.assertEquals(u"ד.נ. הנגב 85488", station['address'])
        self.assertEquals(u"מרכז אבשלום", station['name'])
        self.assertEquals(u"קופת חולים כללית", station['owner'])
        self.assertEquals(u"", station['notes'])
        self.assertEquals(u"דרום", station['district'])
        self.assertEquals(u"באר שבע", station['subdistrict'])

        station = self.get_a_station(1, 0)
        self.assertIsInstance(station, dict)
        self.assertEquals(595, station['id'])
        self.assertEquals(u"הר אדר, נטף", station['notes'])
        self.assertEqual(6, len(station['days']))
        self.assertEqual("8:00-14:30", station['days'][0])
        self.assertEqual("8:00-14:30", station['days'][1])
        self.assertEqual("סגור", station['days'][2])
        self.assertEqual("8:00-14:30", station['days'][3])
        self.assertEqual("סגור", station['days'][4])
        self.assertEqual("סגור", station['days'][5])
        self.assertEquals(u"ירושלים", station['district'])
        self.assertEquals(u"ירושלים", station['subdistrict'])

        station = self.get_a_station(2, 0)
        self.assertIsInstance(station, dict)
        self.assertEquals(611, station['id'])
        self.assertEquals(u"אום אלפחם ב", station['name'])

        station = self.get_a_station(50, 6)
        self.assertIsInstance(station, dict)
        self.assertEquals(u"האורן", station['name'])
        self.assertEquals(u"ירושלים", station['district'])
        self.assertEquals(u"ירושלים", station['subdistrict'])

    def get_a_station(self, page=1, index=9):
        html = milk.get_page(page, self.CACHE_DIR)
        table = milk.extract_stations_table(html)
        rows = milk.extract_station_rows(table)
        station = milk.extract_station_from_row(rows[index])
        return station

    def test_save_station_to_file(self):
        station = self.get_a_station()
        path = tempfile.mkdtemp()
        try:
            milk.save_station_to_json_file(path, station)
            filename = os.path.join(path, "station_%d.json" % station['id'])
            self.assertTrue(os.path.exists(filename))
            with open(filename) as f:
                self.assertEquals(station, json.load(f))
        finally:
            shutil.rmtree(path)

    def test_save_stations_from_page(self):
        path = tempfile.mkdtemp()
        try:
            count = milk.save_station_from_page(path, 1, self.CACHE_DIR)
            files = glob.glob(os.path.join(path, "station_*.json"))
            self.assertEquals(15, count)
            for filename in files:
                with open(filename) as f:
                    d = json.load(f)
                    self.assertEquals(os.path.join(path, "station_%d.json" % d['id']),
                                      filename)
        finally:
            shutil.rmtree(path)

    def test_download_all_stations(self):
        path = tempfile.mkdtemp()
        try:
            stations = milk.download_all_stations(path, self.CACHE_DIR)
            files = glob.glob(os.path.join(path, "station_*.json"))
            self.assertEquals(stations, len(files))
            for filename in files:
                with open(filename) as f:
                    d = json.load(f)
                    self.assertEquals(os.path.join(path, "station_%d.json" % d['id']),
                                      filename)
        finally:
            shutil.rmtree(path)

    def test_geocode_with_address(self):
        expected = {
                                'lat': 31.9032592,
                                'lng': 35.015447
                    }
        result = milk.geocode(u'מודיעין', u'כליל החורש 16')
        self.assertEquals(result['status'], 'OK')
        self.assertEquals(expected, result['results'][0]['geometry']['location'])

    def test_address_to_latlong_without_address(self):
        expected = {
                                'lat': 32.930354,
                                'lng': 35.54052100000001
                    }
        result = milk.geocode(u'עמיעד', u'')
        self.assertEquals(result['status'], 'OK')
        self.assertEquals(expected, result['results'][0]['geometry']['location'])

    def test_geocode_station(self):
        expected = {
                                'lat': 32.930354,
                                'lng': 35.54052100000001
                    }
        station = {
                   'city': u'עמיעד',
                   'address': 'ד.נ. שטות',
                   }
        result = milk.geocode_station(station)
        self.assertEquals(result['status'], 'OK')
        self.assertEquals(expected, result['results'][0]['geometry']['location'])

    def test_geocode_station_english(self):
        expected = {
                                'lat': 32.930354,
                                'lng': 35.54052100000001
                    }
        station = {
                   'city': u'עמיעד',
                   'address': 'ckv',
                   }
        result = milk.geocode_station(station)
        self.assertEquals(result['status'], 'OK')
        self.assertEquals(expected, result['results'][0]['geometry']['location'])

    def test_geocode_all_stations(self):
        path = tempfile.mkdtemp()
        try:
            station_count = milk.save_station_from_page(path, 1, self.CACHE_DIR)
            count = milk.geocode_station_files(self.CACHE_DIR, path)
            print station_count
            print count
            self.assertEquals(station_count, count)
            files = glob.glob(os.path.join(path, "geodata_*.json"))
            self.assertEquals(station_count, len(files))
            for filename in files:
                with open(filename) as f:
                    d = json.load(f)
                    self.assertIsInstance(d, dict)
                    #self.assertIn(d, 'status')
        finally:
            shutil.rmtree(path)

    def test_create_geojson_feature(self):
        station = self.get_a_station()
        geodata = milk.geocode_station(station)
        feature = milk.create_geojson_feature(geodata, station)
        self.assertIsInstance(feature, dict)
        #self.assertIn(feature, 'type')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
