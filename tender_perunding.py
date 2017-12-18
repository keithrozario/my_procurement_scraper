import requests
from lxml import etree
import csv
import logging


def init_output_file(filename, fields):
    with open(filename, 'w') as csvfile:
        dict_writer = csv.DictWriter(csvfile, fieldnames=fields)
        dict_writer.writeheader()
    csvfile.close()


########################################################################################################################
#     VARIABLE                                                                                                         #
########################################################################################################################

# Requests headers
chromeHeader = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
headers = {'User-Agent': chromeHeader}

# BaseUrls and Xpaths
base_url = 'http://myprocurement.treasury.gov.my/custom/p_keputusan_tender_perunding_new.php?sort=&by=&page='
base_xpath = "/html/body/table/tr[1]/td/table[1]/tr["

# xpath
bil_xpath = "]/td[1]"
tajuk_xpath = "]/td[2]"
nombortender_xpath = "]/td[3]"
kategori_xpath = "]/td[4]"
kementerian_xpath = "]/td[5]/a"
agensi_xpath = "]/td[6]/a"
petender_xpath = "]/td[7]"
no_daftar_xpath = "]/td[8]"
no_daftar_mof_xpath = "]/td[9]"
hargasetuju_xpath = "]/td[10]"

# FieldNames of csv file
csv_filename = "tender-perunding.csv"
fieldnames = ['Tajuk Tender', 'Nombor Tender', 'Kategori Perolehan',
              'Kementerian', 'Agensi', 'Petender Berjaya',
              'Nombor Daftar Syarikat', 'No Daftar MOF/PKK', 'Harga Setuju']

# Miscellaneous setup
parser = etree.HTMLParser(recover=True) # needed cos HTML on site is malformed
pageCount = 0

# Logging setup
logging.basicConfig(filename='log.txt',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


########################################################################################################################
#     MAIN                                                                                                             #
########################################################################################################################

if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    init_output_file(csv_filename, fieldnames)

    page_count = 0

    while True:
        # Open page
        page_count += 1
        page_url = base_url + str(page_count)

        logger.info("Requesting Site: " + page_url)

        page = requests.get(page_url, headers=headers)
        root = etree.fromstring(page.text, parser=parser)

        try:
            for row in range(2, 12):
                row_xpath = base_xpath + str(row)

                bil = root.xpath(row_xpath + bil_xpath)[0].text
                tajuk = root.xpath(row_xpath + tajuk_xpath)[0].text.strip()
                nombortender = root.xpath(row_xpath + nombortender_xpath)[0].text
                kategori = root.xpath(row_xpath + kategori_xpath)[0].text
                kementerian = root.xpath(row_xpath + kementerian_xpath)[0].text
                agensi = root.xpath(row_xpath + agensi_xpath)[0].text
                petender = root.xpath(row_xpath + petender_xpath)[0].text
                no_daftar = root.xpath(row_xpath + no_daftar_xpath)[0].text
                no_daftar_mof = root.xpath(row_xpath + no_daftar_mof_xpath)[0].text
                harga_setuju = root.xpath(row_xpath + hargasetuju_xpath)[0].text
                harga_setuju= harga_setuju.replace(',', '')  # turn into a number by removing commas

                tender_line = {'Tajuk Tender': tajuk,
                               'Nombor Tender': nombortender,
                               'Kategori Perolehan': kategori,
                               'Kementerian': kementerian,
                               'Agensi': agensi,
                               'Petender Berjaya': petender,
                               'Nombor Daftar Syarikat': no_daftar,
                               'No Daftar MOF/PKK': no_daftar_mof,
                               'Harga Setuju': harga_setuju}

                with open(csv_filename, 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(tender_line)
                csvfile.close()

                logger.info(bil + " processed")


        except IndexError:
            logger.info("Complete")
            exit(0)

