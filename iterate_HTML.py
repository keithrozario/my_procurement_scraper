import requests
from bs4 import BeautifulSoup
from lxml import etree


chromeHeader = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
baseUrl = 'http://myprocurement.treasury.gov.my/custom/p_keputusan_tender_perunding_new.php?sort=&by=&page=2'

headers = {'User-Agent': chromeHeader}

page = requests.get(baseUrl, headers=headers)

parser = etree.HTMLParser(recover=True)
root = etree.fromstring(page.text,parser=parser)
children = root.getiterator()

htmlPage = etree.ElementTree(root)
for e in root.iter():
    print(htmlPage.getpath(e))
    print("TEXT: " + str(e.text))


