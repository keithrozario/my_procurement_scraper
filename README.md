# my_procurement_scraper
Scraper for the myprocurement Website

This replaces the old work I did here https://github.com/keithrozario/MyProcurementDataScrapper

If you're not interested in running the script, data from 19-Dec is in the repository (it's bad practice to include data in a git repo, but what the hell!)


# rundingan.py
Scrapes data from http://myprocurement.treasury.gov.my/custom/p_keputusan_rundingan.php?sort=&by=&page=
Outputs to rundingan.csv (362 rows)

# tender.py
Scrapes data from http://myprocurement.treasury.gov.my/custom/p_keputusan_tender_arkib_new.php?sort=&by=&page=
Outputs to tender.csv (16,615 rows)
  + Every tender that was jointly won by two companies, gets one row per company
  + Total tender value remains the same for both rows
  + An additional 'Jumlah Tender Berjaya' field contains number of companies that won the tender

# tender_perunding.py
Scrapes data from http://myprocurement.treasury.gov.my/custom/p_keputusan_tender_perunding_new.php?sort=&by=&page=
Output to tender-perunding.csv (127 rows)
