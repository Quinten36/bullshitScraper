# !py -m pip install -U pip
# !py -m pip install Thread
# !py -m pip install undetected_chromedriver
# !py -m pip install selenium


from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
import warnings
from threading import Thread, Lock
import csv

counter = 0
newPage = False
page = 1
pages = int(2638/20) 
numbers = []
urlAddOn = r'?searchQueryState=%7B%22searchQuery%22%3A%22Den%20Haag%22%2C%22filter%22%3A%7B%22status%22%3A%7B%22fsa%22%3Atrue%2C%22fso%22%3Atrue%2C%22fsr%22%3Atrue%2C%22ofb%22%3Atrue%2C%22aot%22%3Atrue%7D%2C%22sort%22%3A%22homes_for_you%22%7D%2C%22map%22%3A%7B%22bounds%22%3A%7B%22sw_lon%22%3A4.18499848425783%2C%22sw_lat%22%3A52.0148484303233%2C%22ne_lon%22%3A4.42248972036332%2C%22ne_lat%22%3A52.1350362198207%7D%7D%2C%22options%22%3A%7B%22view%22%3A%22list%22%7D%2C%22pagination%22%3A%7B%22currentPage%22%3A'
urlAddOn2 = r'%7D%7D'

numLock = Lock()
csvLock = Lock()

def getBrowser():
  #Setup driver
  webdriver.Chrome.get
  warnings.filterwarnings("ignore", category=DeprecationWarning)
  
  #Configure additional options e.g. headless mode
  options = webdriver.ChromeOptions()
  # options.add_argument("--log-level=3")
  # options.add_experimental_option('excludeSwitches', ['enable-logging'])
  # options.add_argument("--headless")
  options.add_argument("--disable-gpu")
  options.add_argument("enable-automation")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--start-maximized")
  
  #Configure browser behavior
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

               
def getData(browser : webdriver.Chrome, element: WebElement):
  elements = []
  cookie_wall(browser)
  elements.append(element.find_element(By.CLASS_NAME, 'hsp-photo-card-address').get_attribute('innerHTML')) #adres
  try:
    elements.append(element.find_element(By.CLASS_NAME, 'property-card-details-item-surface').get_attribute('innerHTML').split(' ')[0]) #surface
  except:
    elements.append(0)
  try:
    elements.append(element.find_element(By.CLASS_NAME, 'property-card-details-item-plot').get_attribute('innerHTML').split(' ')[0])# plot
  except:
    elements.append(0)
  try:
    elements.append(element.find_element(By.CLASS_NAME, 'property-card-details-item-constructionyear').get_attribute('innerHTML')) #construction_year
  except:
    elements.append(0)
  try:
    elements.append(element.find_element(By.CLASS_NAME, 'property-card-details-item-rooms').get_attribute('innerHTML').split(' ')[0]) #rooms
  except:
    elements.append(0)
  return elements
  
  

def getDataBox(browser : webdriver.Chrome):
  cookie_wall(browser)
  lister = []
  
  elements = browser.find_elements(By.XPATH, "//article[@class='hsp-photo-card']")
  for element in elements:
    print(element)
    lister.append(getData(browser, element))
  return lister
  
class MyThread(Thread):
    
  def __init__(self, name):
    Thread.__init__(self)
    self.name = name

  def run(self):
    threadName = self.name
    #Do stuff here
    # Start a new browser window
    browser = getBrowser()
    while len(numbers) > 0:
      numLock.acquire()
      tt = numbers.pop()
      numLock.release()
      browser.get(r'https://huispedia.nl/koopwoningen/den%20haag/'+str(tt)+'_p'+urlAddOn+''+str(tt)+''+urlAddOn2+'')
      print(browser.current_url)
      time.sleep(2.5)
      cookie_wall(browser)
      
      list1 = getDataBox(browser)
      
      csvLock.acquire()
      with open('example.csv', mode='a', newline='', encoding='UTF8') as csv_file:
        fieldnames = ['adres', 'surface', 'plot', 'construction_year', 'rooms']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for list in list1:
          writer.writerow({'adres': str(list[0]), 'surface': int(list[1]), 'plot': int(list[2]), 'construction_year': int(list[3]), 'rooms': int(list[4])})
      csvLock.release()
    

def create_threads():
  start_time = time.time()
  
  for i in range(int(pages/50)+1): #Spawns a thread for each entry in a list threads (len(urls)) plus one if the list is empty
    name = "Thread #%s" % (i)
    my_thread = MyThread(name)
    my_thread.start()
  my_thread.join() 
  
  end_time = time.time()
  print("Execution time:", (end_time - start_time), "seconds")
  time.sleep(5)
    
if __name__ == "__main__":
  #Setup stuff before threads start here!
  browser = getBrowser()
  with open('example.csv', mode='w', newline='') as csv_file:
    fieldnames = ['adres', 'surface', 'plot', 'construction_year', 'rooms']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
  # Navigate to Huispedia
  print(pages)
  for i in range(pages):
    numbers.append(i)
  create_threads()
  
  # stuff is collected
  
  # do more trhead stuff


