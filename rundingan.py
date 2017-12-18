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
base_url = 'http://myprocurement.treasury.gov.my/custom/p_keputusan_rundingan.php?sort=&by=&page='
base_xpath = "/html/body/table/tr/td/div/table/tr[1]/td/form/table[2]/tr["

# xpath
bil_xpath = "]/td[1]"
tajuk_xpath = "]/td[2]"
kategori_xpath = "]/td[3]"
kementerian_xpath = "]/td[4]"
agensi_xpath = "]/td[5]"
nama_syarikat_xpath = "]/td[6]"
nilai_xpath = "]/td[7]"
kriteria_xpath = "]/td[8]"
tarikh_xpath = "]/td[9]"

# FieldNames of csv file
csv_filename = "rundingan.csv"
fieldnames = ['Tajuk Perolehan', 'Kategori Perolehan', 'Kementerian',
              'Agensi', 'Nama Syarikat', 'Nilai Perolehan',
              'Kriteria Rundingan Terus', 'Tarikh']

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
                kategori = root.xpath(row_xpath + kategori_xpath)[0].text
                kementerian = root.xpath(row_xpath + kementerian_xpath)[0].text
                agensi = root.xpath(row_xpath + agensi_xpath)[0].text
                nama_syarikat = root.xpath(row_xpath + nama_syarikat_xpath)[0].text
                nilai = root.xpath(row_xpath + nilai_xpath )[0].text
                nilai = nilai.replace(',', '')  # turn into a number by removing commas
                kriteria = root.xpath(row_xpath + kriteria_xpath)[0].text
                tarikh = root.xpath(row_xpath + tarikh_xpath)[0].text

                tender_line = {'Tajuk Perolehan': tajuk,
                               'Kategori Perolehan': kategori,
                               'Kementerian': kementerian,
                               'Agensi': agensi,
                               'Nama Syarikat': nama_syarikat,
                               'Nilai Perolehan': nilai,
                               'Kriteria Rundingan Terus': kriteria,
                               'Tarikh': tarikh}

                with open(csv_filename, 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(tender_line)
                csvfile.close()

                logger.info(bil + " processed")

        except IndexError:
            logger.info("Complete")
            exit(0)

