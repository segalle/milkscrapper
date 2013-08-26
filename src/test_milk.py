# -*- coding: utf8 -*-
import unittest
import milk


class Test(unittest.TestCase):

    def test_get_url(self):
        expected = "http://www.health.gov.il/Subjects/vaccines/two_drops/Pages/Vaccination_centers.aspx?WPID=WPQ8&PN=1"

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
        self.assertEquals(table.get('class'), "cqwpGridViewTable cqwpGridViewTableFullVaccines PaymentsGridViewGroup")

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

        row = rows[0]
        station = milk.extract_station_from_row(row)
        self.assertIsInstance(station, dict)
        self.assertEquals(u"אבו גוש", station['city'])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
