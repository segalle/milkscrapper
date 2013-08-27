# -*- coding: utf8 -*-
import glob
import json
import milk
import os.path
import shutil
import tempfile
import unittest


class Test(unittest.TestCase):

    def test_get_url(self):
        expected = "http://www.health.gov.il/Subjects/vaccines/two_drops" \
                   "/Pages/Vaccination_centers.aspx?WPID=WPQ8&PN=1"

        self.assertEquals(expected, milk.get_url(1))

    def test_get_full_html(self):

        url = milk.get_url(1)
        html = milk.get_full_html(url)

        self.assertIn("zebraPhone", html)

    def test_get_stations_table(self):

        url = milk.get_url(1)
        html = milk.get_full_html(url)
        table = milk.extract_stations_table(html)

        self.assertEquals(table.tag, "table")
        self.assertEquals(table.get('class'), "cqwpGridViewTable " \
                         "cqwpGridViewTableFullVaccines PaymentsGridViewGroup")

    def test_get_stations_rows(self):

        url = milk.get_url(1)
        html = milk.get_full_html(url)
        table = milk.extract_stations_table(html)
        rows = milk.extract_station_rows(table)

        self.assertEquals(15, len(rows))
        for row in rows:
            self.assertEquals(2, len(row))

    def test_extract_station_from_row(self):

        url = milk.get_url(1)
        html = milk.get_full_html(url)
        table = milk.extract_stations_table(html)
        rows = milk.extract_station_rows(table)

        row = rows[9]
        station = milk.extract_station_from_row(row)
        self.assertIsInstance(station, dict)
        self.assertEquals(605, station['id'])
        self.assertEquals(u"אבשלום", station['city'])
        self.assertEquals(u"ד.נ. הנגב 85488", station['address'])
        self.assertEquals(u"מרכז אבשלום", station['name'])
        self.assertEquals(u"קופת חולים כללית", station['owner'])
        self.assertEquals(u"", station['notes'])
        self.assertEquals(u"דרום", station['district'])
        self.assertEquals(u"", station['subdistrict'])

        row = rows[0]
        station = milk.extract_station_from_row(row)
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

        url = milk.get_url(2)
        html = milk.get_full_html(url)
        table = milk.extract_stations_table(html)
        rows = milk.extract_station_rows(table)
        row = rows[0]
        station = milk.extract_station_from_row(row)
        self.assertIsInstance(station, dict)
        self.assertEquals(611, station['id'])
        self.assertEquals(u"אום אלפחם ב", station['name'])

    def test_save_station_to_file(self):
        url = milk.get_url(2)
        html = milk.get_full_html(url)
        table = milk.extract_stations_table(html)
        rows = milk.extract_station_rows(table)
        row = rows[0]
        station = milk.extract_station_from_row(row)
        path = tempfile.mkdtemp()
        try:
            milk.save_station_to_json_file(path, station)
            filename = os.path.join(path, "%d.json" % station['id'])
            self.assertTrue(os.path.exists(filename))
            with open(filename) as f:
                self.assertEquals(station, json.load(f))
        finally:
            shutil.rmtree(path)

    def test_save_stations_from_page(self):
        path = tempfile.mkdtemp()
        try:
            count = milk.save_station_from_page(path, 1)
            files = glob.glob(os.path.join(path, "*.json"))
            self.assertEquals(15, count)
            for filename in files:
                with open(filename) as f:
                    d = json.load(f)
                    self.assertEquals(os.path.join(path, "%d.json" % d['id']),
                                      filename)
        finally:
            shutil.rmtree(path)

    def test_download_all_stations(self):
        path = tempfile.mkdtemp()
        try:
            stations = milk.download_all_stations(path)
            files = glob.glob(os.path.join(path, "*.json"))
            self.assertEquals(stations, len(files))
            for filename in files:
                with open(filename) as f:
                    d = json.load(f)
                    self.assertEquals(os.path.join(path, "%d.json" % d['id']),
                                      filename)
        finally:
            shutil.rmtree(path)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
