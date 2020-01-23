from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium import webdriver
from lxml import html
import selenium
import random
import time
import json
import csv
import os


class CorporSearch(QThread):
    dirName = 'corporationwiki'
    logcallback = pyqtSignal(object, object)
    mutex = QMutex()
    progress_bar = 0
    step_plus = 0

    try:
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists ")

    def __init__(self, keyword):
        QThread.__init__(self)
        self.keyword = keyword
        # self.logcallback = logcallback
        self.paused = False

    def _check_task_paused(self):
        while self.paused:
            print('Sleeping')
            self.sleep(1)

    def _intialize(self):
        self.logcallback.emit("#Now making csv file...........................", 2)
        # Qtcore

        open(self.dirName + "/" + "{}.csv".format(self.keyword), "wb").close()
        header = ["Company Name", "Name", "Role", "Address", "Age", "Filling Type", "Status", "State", "Foreign State",
                  "County", "State ID", "Date Filed", "DOS Process"]

        with open(self.dirName + "/" + "{}.csv".format(self.keyword), "a", newline="") as f:
            csv_writer = csv.DictWriter(f, fieldnames=header, lineterminator='\n')
            csv_writer.writeheader()

        print("start selenium script")

        self.logcallback.emit("#Open chrome browser open now.....", 4)

        self.path = "driver\\chromedriver.exe"
        self.driver = Chrome(executable_path=self.path)
        self.driver.get("https://www.corporationwiki.com/")
        self.driver.maximize_window()

        # self.parse_page(keyword)

    def parse_page(self):
        self._intialize()
        # Checking task is paused or not
        self._check_task_paused()
        time.sleep(5)
        self.logcallback.emit('Doing Some', 5)
        print("---------------------------------")
        driver = self.driver
        # keyword = "premier metro realty corp"
        item_urls = []
        companyNames = []
            
        searchKeyword = driver.find_element_by_id("keywords")
        searchKeyword.send_keys(self.keyword)
        searchKeyword.send_keys(Keys.ENTER)
        # Checking task is paused or not
        self._check_task_paused()
        self.logcallback.emit("#Input key word... and search....", 10)
        self.progress_bar = 10
        time.sleep(5)

        companyName_xpaths = driver.find_elements_by_xpath("//div[@class='list-group-item']//a[@class='ellipsis']")
        all_counts = len(companyName_xpaths)
        self.step_plus = (100 - self.progress_bar) / 6
        self.logcallback.emit("Search Results---------------> : {}".format(all_counts), self.progress_bar)
        
        for companyName_xpath in companyName_xpaths:
            # Checking task is paused or not
            self._check_task_paused()
            companyName = companyName_xpath.text
            item_url = companyName_xpath.get_attribute("href")
            
            companyNames.append(companyName)
            item_urls.append(item_url)

            print("Company Name-----------------> : ", companyName)
            print("Item URL---------------------> : ", item_url)

        print(companyNames, item_urls)

        for companyName, item_url in zip(companyNames, item_urls):
            # Checking task is paused or not
            self._check_task_paused()
    
            # companyName = ""
            name = ""
            role = ""
            address = ""
            age = ""
            filling_type = ""
            status = ""
            state = ""
            foreign_state = ""
            county = ""
            state_id = ""
            date_filed = ""
            dos_process = ""


            driver.get(item_url)
            self.progress_bar = self.progress_bar + self.step_plus
            self.logcallback.emit("Redirect into {}".format(item_url), self.progress_bar)
            time.sleep(4)

            name = driver.find_element_by_xpath("//a[@class='ellipsis']").text
            role = driver.find_element_by_xpath("//div[contains(@class, 'role-label')]").text

            print("------------------------------------------------------------------------------")

            for i in range(0, 9):
                # Checking task is paused or not
                self._check_task_paused()
                if str(i) in name:
                    name = name.replace(str(i), "")
            
            try:
                streetAddress = driver.find_element_by_xpath("//span[@itemprop='streetAddress']").text
                locality = driver.find_element_by_xpath("//span[@itemprop='addressLocality']").text
                region = driver.find_element_by_xpath("//span[@itemprop='addressRegion']").text
                postalCode = driver.find_element_by_xpath("//span[@itemprop='postalCode']").text

                address = streetAddress + " " + locality + " " + region + " " + postalCode

                background_url = driver.find_element_by_xpath("//table[@class='list-table']//tbody//tr[1]/td[1]/div/a").get_attribute("href")
                print("BackgroundUrl-------------------> : ", background_url)
                # Checking task is paused or not
                self._check_task_paused()
                driver.get(background_url)
                
                # Checking task is paused or not
                self._check_task_paused()
                time.sleep(4)

                age = driver.find_element_by_class_name("display-age").text
            except:
                
                label_xpaths = driver.find_elements_by_xpath("(//table[contains(@class, 'table') and contains(@class, 'table-striped') and contains(@class, 'pad-bottom')])[1]/tbody//tr//th")

                info_xpaths = driver.find_elements_by_xpath("(//table[contains(@class, 'table') and contains(@class, 'table-striped') and contains(@class, 'pad-bottom')])[1]/tbody//tr//td")

                for label_xpath, info_xpath in zip(label_xpaths, info_xpaths):
                    # Checking task is paused or not
                    self._check_task_paused()
                    labelTxt = label_xpath.text
                    infoTxt = info_xpath.text

                    if "Filing Type" in labelTxt:
                        filling_type = infoTxt
                    elif "Status" in  labelTxt:
                        status = infoTxt
                    elif "State" in labelTxt and "ID" not in labelTxt and "Foreign" not in labelTxt:
                        state = infoTxt
                    elif "Foreign State" in labelTxt:
                        foreign_state = infoTxt
                    elif "County" in labelTxt:
                        county = infoTxt
                    elif "State ID" in labelTxt:
                        state_id = infoTxt
                    elif "Date Filed" in labelTxt:
                        date_filed = infoTxt
                    elif "DOS Process" in labelTxt:
                        dos_process = infoTxt

                address = county + " " + state + " " + state_id

                background_url = driver.find_element_by_xpath("//table[@class='list-table']//tbody//tr[1]/td[1]/div/a").get_attribute("href")
                print("BackgroundUrl-------------------> : ", background_url)
                self.progress_bar = self.progress_bar + self.step_plus
                self.logcallback.emit("Background checking...", self.progress_bar)
                # Checking task is paused or not
                self._check_task_paused()
                driver.get(background_url)
                self.progress_bar = self.progress_bar + self.step_plus
                self.logcallback.emit("Redirect into : {}".format(background_url), self.progress_bar)
                # Checking task is paused or not
                self._check_task_paused()
                time.sleep(4)

                age = driver.find_element_by_class_name("display-age").text
            
            self.progress_bar = self.progress_bar + self.step_plus
            self.logcallback.emit("Input Data into CSV file...", self.progress_bar)

            with open(self.dirName + "/" + "{}.csv".format(self.keyword), "a", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)

                print("Company Name------------------> : ", companyName)
                # self.logcallback("#Input key word... and search....")
                print("Name--------------------------> : ", name)
                print("Role--------------------------> : ", role)
                print("Address-----------------------> : ", address)
                print("Age---------------------------> : ", age)

                print("Filling Type------------------> : ", filling_type)
                print("Status------------------------> : ", status)
                print("State-------------------------> : ", state)
                print("Foreign State-----------------> : ", foreign_state)
                print("County------------------------> : ", county)
                print("State ID----------------------> : ", state_id)
                print("Date Filed--------------------> : ", date_filed)
                print("DOS Process-------------------> : ", dos_process)

                writer.writerow([companyName, name, role, address, age, filling_type, status, state, foreign_state, county, state_id, date_filed, dos_process])
            self.progress_bar = self.progress_bar + self.step_plus
            self.logcallback.emit("**************************", self.progress_bar)

        self.logcallback.emit("**********************************End**************************************", 100)
         

    def run(self):
        try:
            self.parse_page()

            self.driver.close()
            self.driver.quit()

        except Exception as e:
            if self.driver is not None:
                raise e
        
