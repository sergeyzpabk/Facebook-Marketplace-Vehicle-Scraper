import collections
import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import *

# type: ignore
collections.Callable = collections.abc.Callable

TEMP_FILE = "tmp.mhtml"

with open('setup.json') as fin:        # type: ignore
    setup = json.load(fin)

def main():
    # open page
    url = 'https://www.facebook.com/marketplace/'
    years, names, models, prices, mileages, locs, links = [], [], [], [], [], [], []

    tempfile = TEMP_FILE
    tempfile = save_page(url, TEMP_FILE)

    with open(tempfile, 'r', encoding='utf-8') as pg:
        content = pg.read().replace("=\n\n", "")                   # read html data
        # create soup object
        soup = BeautifulSoup(content, 'lxml')

        # find class for price
        # type: ignore
        re_price = re.compile("\d[0123456789,]+")
        prices_obj = soup.body.findAll(string=re_price)
        parent_list = []

        for price_obj in prices_obj:
            tmp = price_obj.parent.parent.parent.parent.parent
            try:
                if len(list(tmp.children)) == 4 or len(list(tmp.children)) == 3:
                    parent_list.append(tmp)
            except: pass
        for p in parent_list:
            try:
                # get data in children
                pcl = list(p.children)

                # find details
                #separation of name and date
                name:str
                name = pcl[1].get_text().strip()
                year = ''
                if re.match('^(19|20)\d{2}$', name[:4]):
                    year = name[:4]
                    name = name[5:]
                model = ''
                name_ = name.split(' ')
                if len(name_) >1:
                    name = name_.pop(0)
                    model = ' '.join(name_)

                prices.append(get_price(pcl))
                names.append(name)
                models.append(model)
                years.append(year)
                locs.append(pcl[2].get_text())
                mileages.append(get_mileage(pcl))
                links.append(get_link(p))
            except: pass
    # sort data
    us = list(zip(names, models, years, prices, mileages, locs, links))
    us = sorted(us)
    years, names, models, prices, mileages, locs, links = [], [], [], [], [], [],[]
    for u in us:
        names.append(u[0])
        models.append(u[1])
        years.append(u[2])
        prices.append(u[3])
        mileages.append(u[4])
        locs.append(u[5])
        links.append(u[6])

    # export data
    fname = str(datetime.now()).replace(
        ":", "-")[2:-5].replace(" ", "--")  # datetime file save name
    with open(f"sc_{fname}.csv", 'w', newline='', encoding='utf-8') as f,\
            open(f"sc_{fname}_{setup['facebook']['carBrand']}.csv", 'w', newline='',encoding='utf-8') as fy,\
            open(f"sc_{fname}_desired.csv", 'w', newline='',encoding='utf-8') as fz:

        headers = ["year", "name", "model", "price", "mileage", "location", "link"]
        csw = csv.writer(f)
        csw2 = csv.writer(fy)
        csw3 = csv.writer(fz)
        csw.writerow(headers)
        csw2.writerow(headers)
        csw3.writerow(headers)

        for year, name, model, price, mileage, loc, link in zip(years, names, models,prices, mileages, locs, links):
            csw.writerow([year, name, model, price, mileage, loc, link])
            if setup["facebook"]["carBrand"].lower() in str(name.lower()):   # if car name is in name
                csw2.writerow([year, name, model, price, mileage, loc, link])

                # if mileage is not available - lazy rn sorry
                try:
                    if str(mileage) in ["Dealership", "N/A"]:
                        pass
                    elif int(mileage) < (setup['facebook']['desired_maximum_mileage']) and int(year) > (setup['facebook']['desired_minimum_year']):
                        csw3.writerow([year, name, model, price, mileage, loc, link])
                except:pass

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f'Crash: {err}')
    print('Final parse')
