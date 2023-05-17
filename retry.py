# !py -m pip install -U pip
# !py -m pip install Thread
# !py -m pip install undetected_chromedriver
# !py -m pip install selenium


from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
import warnings
from threading import Thread, Lock
import csv
import re
import json


def wait_for_page_load(driver, timeout=10):
    # Wait for the page to load completely
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'list-container')))


def getBrowser():
    # Setup driver
    webdriver.Chrome.get
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Configure additional options e.g. headless mode
    options = webdriver.ChromeOptions()
    # options.add_argument("--log-level=3")
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("enable-automation")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    # Configure browser behavior
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "normal"

    return uc.Chrome(desired_capabilities=caps, chrome_options=options)


def cookie_wall(browser):
    time.sleep(.2)
    try:
        cookie_btn = browser.find_element(By.ID, 'onetrust-accept-btn-handler')
        cookie_btn.click()
    except:
        pass


linkList = []


numLock = Lock()
csvLock = Lock()


def prepareStuff():
    loop = True
    page = 1

    browser = getBrowser()
    browser.get(r'https://huispedia.nl/koopwoningen/den%20haag?searchQueryState=%7B%22searchQuery%22%3A%22Den%20Haag%22%2C%22filter%22%3A%7B%22status%22%3A%7B%22fsa%22%3Atrue%2C%22fso%22%3Atrue%2C%22fsr%22%3Atrue%2C%22ofb%22%3Atrue%2C%22aot%22%3Atrue%7D%2C%22sort%22%3A%22homes_for_you%22%7D%2C%22map%22%3A%7B%22bounds%22%3A%7B%22sw_lon%22%3A4.18162023054353%2C%22sw_lat%22%3A52.00713764247479%2C%22ne_lon%22%3A4.425867974077477%2C%22ne_lat%22%3A52.14272495077694%7D%7D%2C%22options%22%3A%7B%22view%22%3A%22list%22%7D%7D')
    cookie_wall(browser)
    # browser.refresh()
    time.sleep(5.9)
    wait_for_page_load(browser)

    while loop:
        # print(page)
        elements = browser.find_elements(
            By.XPATH, "//article[@class='hsp-photo-card']")
        try:
            for element in elements:
                link = element.find_element(
                    By.CLASS_NAME, 'property-card-container').get_attribute('href')
                linkList.append(link)
        except:
            # pass
            print('error')

        try:
            end_btn = browser.find_element(By.CLASS_NAME, 'p-paginator-last')
            next_btn = browser.find_element(
                By.CSS_SELECTOR, '.p-paginator-page[aria-label="'+str(page)+'"]')
            next_btn.click()
            page += 1
        except:
            loop = False
        time.sleep(4.9)
        wait_for_page_load(browser)


def is_integer(variable):
    return isinstance(variable, int)


def getData(browser: webdriver.Chrome):
    elements = []
    cookie_wall(browser)
    elements.append(
        browser.find_element(By.TAG_NAME, 'h1').get_attribute('innerHTML').split('<')[0].replace('\"', '').replace('\n', ''))  # adres
    container = browser.find_element(By.ID, 'featuresInnerContainer')

    spanJSONs = []
    allAttributes = re.findall('<ul class="property-feature-list-large">(.+?)</ul>', container.get_attribute('innerHTML'), re.DOTALL)
    for ul in allAttributes:
        liList = re.findall('<li class="feature-item">(.+?)</li>', ul, re.DOTALL)
        for li in liList:
            span_match = re.findall('<span class="value"(.+?)</span>', li, re.DOTALL)
            if span_match:
                liValue = re.findall('>(.+?)<', span_match[0], re.DOTALL)
            else:
                liValue = []
            json_obj = {
                'variableName': re.findall('<span class="name">(.+?)</span>', li, re.DOTALL),
                'liValue': liValue
            }
            spanJSONs.append(json_obj)

    return spanJSONs




prepareStuff()

browser = getBrowser()

print(len(linkList))
dataList = []
while len(linkList) > 1:

    numLock.acquire()
    link = linkList.pop()
    numLock.release()

    browser.get(link)
    time.sleep(2.5)
    cookie_wall(browser)

    list1 = getData(browser)

    csvLock.acquire()
    # with open('example2.csv', mode='a', newline='', encoding='UTF8') as csv_file:
    #     fieldnames = ['adres', 'surface', 'energy_label', 'construction_year',
    #                   'rooms', 'type_woning', 'staat_woning', 'geschatte_prijs']
    #     # fieldnames = ['adres']
    #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # for list in list1:
    print(len(list1))
        # writer.writerow({'adres': list1[0]})
        #REGEL 155/156 AANPASSEN WANT HET IS NOG NIET IN STAAT JSON TE VERWERKEN
        #writer.writerow({'adres': str(list1[0]), 'surface': int(list1[1]), 'energy_label': str(list1[2]).replace('\\n', ''), 'construction_year': int(list1[3]), 'rooms': int(
      #      list1[4]), 'type_woning': str(list1[5]).replace('\\n', ''), 'staat_woning': str(list1[6]).replace('\\n', ''), 'geschatte_prijs': str(list1[7]).replace('\\n', '')})
        # writer.writerow({'adres': str(list)})
    dataList.append(list1)
    with open('./retry.json','w') as file:
        json.dump(dataList,file, indent=2)
