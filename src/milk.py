"""
Gets information about Tipat Halav offices
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
