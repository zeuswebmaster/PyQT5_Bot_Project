import selenium
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from lxml import html
import csv
import time
import random
import json
import os


class CorporSearch:

    dirName = 'corporationwiki'
    try:
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists ")

    def __init__(self, keyword, logcallback):
        self.keyword = keyword
        self.logcallback = logcallback
        self.logcallback("#Now making csv file...........................")
        # Qtcore

        open(self.dirName + "/" + "{}.csv".format(self.keyword), "wb").close()
        header = ["Company Name", "Name", "Role", "Address", "Age", "Filling Type", "Status", "State", "Foreign State", "County", "State ID", "Date Filed", "DOS Process"]

        with open(self.dirName + "/" + "{}.csv".format(self.keyword), "a", newline="") as f:
            csv_writer = csv.DictWriter(f, fieldnames=header, lineterminator='\n')
            csv_writer.writeheader()
        
        
        print("start selenium script")
        
        self.logcallback("#Open chrome browser open now.....")
        
        self.path = "driver\\chromedriver.exe"
        self.driver = Chrome(executable_path=self.path)
        self.driver.get("https://www.corporationwiki.com/")
        self.driver.maximize_window()

        # self.parse_page(keyword)

    def parse_page(self):
        print("---------------------------------")
        driver = self.driver
        # keyword = "premier metro realty corp"
        item_urls = []
        companyNames = []
            
        searchKeyword = driver.find_element_by_id("keywords")
        searchKeyword.send_keys(self.keyword)
        searchKeyword.send_keys(Keys.ENTER)
        self.logcallback("#Input key word... and search....")
        time.sleep(5)

        companyName_xpaths = driver.find_elements_by_xpath("//div[@class='list-group-item']//a[@class='ellipsis']")
        
        for companyName_xpath in companyName_xpaths:
            companyName = companyName_xpath.text
            item_url = companyName_xpath.get_attribute("href")
            
            companyNames.append(companyName)
            item_urls.append(item_url)

            print("Company Name-----------------> : ", companyName)
            print("Item URL---------------------> : ", item_url)

        print(companyNames, item_urls)

        for companyName, item_url in zip(companyNames, item_urls):
    
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
            time.sleep(4)

            name = driver.find_element_by_xpath("//a[@class='ellipsis']").text
            role = driver.find_element_by_xpath("//div[contains(@class, 'role-label')]").text

            print("------------------------------------------------------------------------------")

            for i in range(0, 9):
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
                
                driver.get(background_url)
                time.sleep(4)

                age = driver.find_element_by_class_name("display-age").text
            except:
                
                label_xpaths = driver.find_elements_by_xpath("(//table[contains(@class, 'table') and contains(@class, 'table-striped') and contains(@class, 'pad-bottom')])[1]/tbody//tr//th")

                info_xpaths = driver.find_elements_by_xpath("(//table[contains(@class, 'table') and contains(@class, 'table-striped') and contains(@class, 'pad-bottom')])[1]/tbody//tr//td")

                for label_xpath, info_xpath in zip(label_xpaths, info_xpaths):
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

                background_url = driver.find_element_by_xpath("//table[@class='list-table']//tbody//tr[1]/td[1]/div/a").get_attribute("href")
                print("BackgroundUrl-------------------> : ", background_url)
                
                driver.get(background_url)
                time.sleep(4)

                age = driver.find_element_by_class_name("display-age").text


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
        
