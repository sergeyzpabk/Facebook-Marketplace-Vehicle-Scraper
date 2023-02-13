import json
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import re

with open("setup.json") as fin:
    setup = json.load(fin)

# search queries
location = "mansfield"
query = "r6"
exact = "False"
maxPrice = 2000

sortby = 0  # 0-name, 1-price, 2-mileage, 3-loc


def save_page(url, fname):
    # open page
    options = webdriver.ChromeOptions()
    options.add_argument("--save-page-as-mhtml")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('--allow-profiles-outside-user-dir')
    options.add_argument('--enable-profile-shortcut-manager')
    options.add_argument(r'user-data-dir=\User')
    options.add_argument('--profile-directory=Profile0')
    browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    browser.get(url)

    #write an authorization check
    # Bypass facebook login
    #The user logs in once. After the profile is saved
    print('log in Browser')
    while True:
        try:
            res =str( browser.page_source)
            if res.find('class="x3ajldb"') != -1:
                print('Successfully logged in')
                break
        except:
            pass
        sleep(1)

    sleep(3)

    edit_fullXpath = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div[2]/div/div/div/span/div/div/div/div/label/input'
    edit_priceMinFullXpach = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[3]/div[2]/span[1]/label/input'
    edit_priceMaxFullXpach = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[3]/div[2]/span[2]/label/input'


    browser.find_element(By.XPATH, edit_fullXpath).click()
    browser.find_element(By.XPATH, edit_fullXpath).clear()
    browser.find_element(By.XPATH, edit_fullXpath).send_keys(setup['facebook']['query'])
    browser.find_element(By.XPATH, edit_fullXpath).send_keys(Keys.ENTER)
    sleep(1)

    browser.find_element(By.XPATH, edit_priceMinFullXpach).click()
    browser.find_element(By.XPATH, edit_priceMinFullXpach).clear()
    browser.find_element(By.XPATH, edit_priceMinFullXpach).send_keys(setup['facebook']['minimum_price'])

    browser.find_element(By.XPATH, edit_priceMaxFullXpach).click()
    browser.find_element(By.XPATH, edit_priceMaxFullXpach).clear()
    browser.find_element(By.XPATH, edit_priceMaxFullXpach).send_keys(setup['facebook']['maximum_price'])
    browser.find_element(By.XPATH, edit_priceMaxFullXpach).send_keys(Keys.ENTER)
    sleep(1)

    # scroll
    for i in range(int(setup['facebook']['pageCount'])):
        browser.execute_script(f"window.scrollTo(0, {4000*i})")
        sleep(2)

    # snapshot and save
    #res = send(browser, "Page.captureSnapshot", {"format": "mhtml"})
    res = browser.page_source

    with open(fname, "w",  encoding='utf-8') as file:
        file.write(res)
    return fname


def get_price(pcl):
    # print(pcl[0].get_text().split("$"))
    return "$"+re.sub('\D', '', pcl[0].get_text())


def get_mileage(pcl):
    #In development. rewrite the code.
    return ""
    strmiles = pcl[3].get_text().split(" =")[0].replace(
        " miles", "").replace("K", "000").replace("M", "000000")
    if "." in strmiles:
        strsep = strmiles.replace(".", "")
        return int(strsep)

    if len(strmiles) > 0:
        if str(strmiles) == "Dealership":
            strmiles2 = "Dealership"
        elif int(float(strmiles)) == int(strmiles):
            strmiles2 = int(strmiles)
        else:
            strmiles2 = "N/A"
    else:
        strmiles2 = "N/A"  # (or number = 0 if you prefer)

    return strmiles2


def get_link(p):
    linktmp = p.parent.parent.parent.find("a").get("href")
    if "3D\"" in linktmp[0:3]:
        return linktmp[3:-1]
    return linktmp
