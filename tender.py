import requests
from lxml import etree
import csv
import logging


def get_no_syarikat(no_daftar_syarikat):

    if no_daftar_syarikat is None:
        return "Null"
    else:
        return no_daftar_syarikat[22:-1]


def get_no_mof(no_daftar_mof):
    if no_daftar_mof is None:
        return "Null"
    else:
        end = no_daftar_mof.find(']', 21)
        return no_daftar_mof[21:end]


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
base_url = 'http://myprocurement.treasury.gov.my/custom/p_keputusan_tender_arkib_new.php?sort=&by=&page='
base_xpath = "/html/body/table/tr/td/table[1]/tr["

# xpath
bil_xpath = "]/td[1]"
tajuk_xpath = "]/td[2]/comment()"
nombortender_xpath = "]/td[3]"
kategori_xpath = "]/td[4]"
kementerian_xpath = "]/td[5]/a"
agensi_xpath = "]/td[6]/a"
first_petendername_xpath = "]/td[7]"
petender_xpath = "]/td[7]/br["
hargasetuju_xpath = "]/td[8]"

# FieldNames of csv file
csv_filename = "tender.csv"
fieldnames = ['Tajuk Tender', 'Nombor Tender', 'Kategori Perolehan',
              'Kementerian', 'Agensi', 'Nama Syarikat',
              'Nombor Daftar Syarikat', 'No Daftar MOF/PKK', 'Harga Setuju',
              'Jumlah Petender Berjaya']

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
                tajuk = root.xpath(row_xpath + tajuk_xpath)[0].tail.strip()
                nombortender = root.xpath(row_xpath + nombortender_xpath)[0].text
                kategori = root.xpath(row_xpath + kategori_xpath)[0].text
                kementerian = root.xpath(row_xpath + kementerian_xpath)[0].text
                agensi = root.xpath(row_xpath + agensi_xpath)[0].text
                harga_setuju = root.xpath(row_xpath + hargasetuju_xpath)[0].text[2:]
                harga_setuju= harga_setuju.replace(',', '')  # turn into a number by removing commas

                company_row = 0
                companies = []

                try:
                    while True:

                        if company_row == 0:
                            nama_syarikat = root.xpath(row_xpath + first_petendername_xpath)[0].text
                        else:
                            nama_syarikat = root.xpath(row_xpath + petender_xpath + str(company_row) + "]")[0].tail

                        temp_field_1 = root.xpath(row_xpath + petender_xpath + str(company_row + 1) + "]")[0].tail
                        temp_field_2 = root.xpath(row_xpath + petender_xpath + str(company_row + 2) + "]")[0].tail

                        if temp_field_1[:22] == "[NO. DAFTAR SYARIKAT: ":
                            no_daftar_syarikat = temp_field_1
                        else:
                            no_daftar_syarikat = None

                        if temp_field_1[:21] == "[NO. DAFTAR MOF/PKK: ":
                            no_daftar_mof = temp_field_1
                            addRow = 3
                        elif temp_field_2[:21] == "[NO. DAFTAR MOF/PKK: ":
                            no_daftar_mof = temp_field_2
                            addRow = 4
                        else:
                            no_daftar_mof = None
                            if no_daftar_syarikat is None:
                                addRow = 2
                            else:
                                addRow = 3

                        company_details = {'nama_syarikat': nama_syarikat,
                                           'no_daftar_syarikat': get_no_syarikat(no_daftar_syarikat),
                                           'no_daftar_mof': get_no_mof(no_daftar_mof)}

                        companies.append(company_details)

                        # add 4 rows to go to next company
                        company_row += addRow

                # exceeded the amount of companies
                except IndexError:
                    pass  # Exit for loop and continue below

                csv_rows = []

                for company in companies:
                    tender_line = {'Tajuk Tender': tajuk,
                                   'Nombor Tender': nombortender,
                                   'Kategori Perolehan': kategori,
                                   'Kementerian': kementerian,
                                   'Agensi': agensi,
                                   'Nama Syarikat': company['nama_syarikat'],
                                   'Nombor Daftar Syarikat': company['no_daftar_syarikat'],
                                   'No Daftar MOF/PKK': company['no_daftar_mof'],
                                   'Harga Setuju': harga_setuju,
                                   'Jumlah Petender Berjaya': len(companies)}
                    csv_rows.append(tender_line)

                with open(csv_filename, 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerows(csv_rows)
                csvfile.close()

                logger.info(bil + " processed")
                logger.info("Total Rows: " + str(len(csv_rows)))

        except IndexError:
            logger.info("Complete")
            exit(0)

