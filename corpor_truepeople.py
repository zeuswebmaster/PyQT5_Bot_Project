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
import re, math
import selenium
import random
import time
import json
import csv
import os

from captcha_solver import CaptchaSolver

class Copor_TrueSearch(QThread):
    solver = CaptchaSolver()

    dirName = 'corporationwiki_truepeople'
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
        self.default_url = "https://www.truepeoplesearch.com/results?name={0}&citystatezip={1}"
        self.base_url = "https://www.truepeoplesearch.com/results?name={0}&citystatezip={1}&page={2}"

    def _check_task_paused(self):
        while self.paused:
            print('Sleeping')
            self.sleep(1)


    def _intialize(self):
        self.logcallback.emit("#Now making csv file...........................", 2)
        # Qtcore

        open(self.dirName + "/" + "{}.csv".format(self.keyword), "wb").close()
        header = ["Company Name", "Name", "Role", "Address", "Age", "Filling Type", "Status", "State", "Foreign State", "County", "State ID", "Date Filed", "DOS Process", "Phone1", "phone2", "phone3", "phone4", "phone5", "phone6", "phone7", "phone8", "phone9", "phone10", "email1", "email2", "email3", "email4", "email5", "email6", "email7", "email8", "email9", "email10"]

        with open(self.dirName + "/" + "{}.csv".format(self.keyword), "a", newline="") as f:
            csv_writer = csv.DictWriter(f, fieldnames=header, lineterminator='\n')
            csv_writer.writeheader()

        
        self.logcallback.emit("#Open chrome browser open now.....", 4)
        self.path = "driver\\chromedriver.exe"
        self.driver = Chrome(executable_path=self.path)
        
        self.logcallback.emit("### Open Chrome Browser2 now.............", 6)
        self.driver1 = Chrome(executable_path=self.path)
        
        self.logcallback.emit("### Open Chrome Browser3 now.............", 8)
        self.driver2 = Chrome(executable_path=self.path)

        self.logcallback.emit("### Open Chrome Browser4 now.............", 10)
        self.driver3 = Chrome(executable_path=self.path)

        self.driver.get("https://www.corporationwiki.com/")
        self.driver.maximize_window()
        self.driver1.maximize_window()
        self.driver2.maximize_window()
        self.driver3.maximize_window()

    def parse_page(self):
        item_urls = []
        companyNames = []

        self._intialize()
        
        self._check_task_paused()
        time.sleep(5)
        self.logcallback.emit("### First Page Scraping Start.................", 10)

        driver = self.driver
        driver1 = self.driver1
        driver2 = self.driver2
        driver3 = self.driver3


        searchKeyword = driver.find_element_by_id("keywords")
        searchKeyword.send_keys(self.keyword)
        searchKeyword.send_keys(Keys.ENTER)

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
            self._check_task_paused()

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

            self.data = {
                "company_name" : "",
                "name" : "",
                "role" : "",
                "address" : "",
                "age" : "",
                "filling_type" : "",
                "status" : "",
                "state" :  "",
                "foreign_state" : "",
                "county" : "",
                "state_id" : "",
                "date_filed" : "",
                "dos_process" : ""    
            }

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

            self.data["company_name"] = companyName
            self.data["name"] = name
            self.data["role"] = role
            self.data["address"] = address
            self.data["age"] = age
            self.data["filling_type"] = filling_type
            self.data["status"] = status
            self.data["state"] = state
            self.data["foreign_state"] = foreign_state
            self.data["county"] = county
            self.data["state_id"] = state_id
            self.data["date_filed"] = date_filed
            self.data["dos_process"] = dos_process

            self.turepeopleSearch(driver1, driver2, driver3, self.data)
    
    def turepeopleSearch(self, driver1, driver2, driver3, data):
        url = self.default_url.format(data["name"], data["address"])
        driver1.get(url)
        self._check_task_paused()

        try:
            self.logcallback.emit("### Recaptcha Detecting >>>................", 24)
            recaptcha = driver1.find_element_by_class_name("g-recaptcha")
            recaptchaFlag = True
            self.logcallback.emit("### Recaptcha Detection True...............", 26)
        except:
            recaptchaFlag = False
            self.logcallback.emit("### Recaptcha Detection False..............", 26)

        if recaptchaFlag == True:
            self.logcallback.emit("### Recaptcha Solving Now..................", 26)
            self.solver.solve_captcha_for_url(driver1, driver1.current_url)
            driver1.find_element_by_xpath('//button').click()
            self.logcallback.emit("### Recaptcha Solved.......................", 26)

        try:
            itemsInfo = driver1.find_element_by_xpath("//html/body/div[2]/div/div[2]/div[3]/div[1]").text
            totals = int((itemsInfo.split(" "))[0])
            page_counts = math.ceil(totals / 11)
            self.logcallback.emit("### Total Item Accounts....................", 28)
            next_flag = False
            self.logcallback.emit("### Total {} PAGE....................".format(page_counts), 20)

            for page in range(1, page_counts + 1):
                self._check_task_paused()
                if page != 1:
                    driver1.get(self.base_url.format(data["name"], data["address"], page))
                    time.sleep(2)
                try:
                    self.logcallback.emit("### Recaptcha Detecting >>>................", 31)
                    recaptcha = driver1.find_element_by_class_name("g-recaptcha")
                    recaptchaFlag = True
                    self.logcallback.emit("### Recaptcha Detection True...............", 32)
                except:
                    recaptchaFlag = False
                    self.logcallback.emit("### Recaptcha Detection False..............", 32)

                if recaptchaFlag == True:
                    self.logcallback.emit("### Recaptcha Solving Now..................", 34)
                    self.solver.solve_captcha_for_url(driver1, driver1.current_url)
                    driver.find_element_by_xpath('//button').click()
                    self.logcallback.emit("### Recaptcha Solved.......................", 36)

                ownerXpaths = driver1.find_elements_by_xpath("//div[contains(@class, 'card-summary')]//div[@class='h4']")

                viewButtons = driver1.find_elements_by_xpath("//div[contains(@class, 'card-summary')]//div[contains(@class, 'align-self-center')]/a")

                for ownerXpath, viewButton in zip(ownerXpaths, viewButtons):
                    self._check_task_paused()
                    ownerName = ownerXpath.text
                    
                    flag = self.destinction(ownerName.lower(), self.data["name"].lower())

                    if flag == 2:
                        self.logcallback.emit("### First Mode.......................", 30)
                        second_url = viewButton.get_attribute('href')
                        driver2.get(second_url)
                        self._check_task_paused()
                        self.parse_owner(driver2.page_source, driver2)
                        next_flag = True
                        break

                    elif flag == 1:
                        self.logcallback.emit("### Second Mode.......................", 30)
                        second_url = viewButton.get_attribute('href')
                        driver3.get(second_url)
                        self._check_task_paused()
                        self.parse_ownerfind(driver3.page_source, driver3, driver2, self.data["name"])
                        next_flag = True
                        break

                if next_flag == True:
                    break

        except:
            print("continue")

    def parse_owner(self, htmlstring, driver2):
        self._check_task_paused()
        self.logcallback.emit("### GET INFOS.......................", 35)
        try:
            self.logcallback.emit("### Recaptcha Detecting >>>................", 36)
            recaptcha = driver2.find_element_by_class_name("g-recaptcha")
            recaptchaFlag = True
            self.logcallback.emit("### Recaptcha Detection True...............", 38)
        except:
            recaptchaFlag = False
            self.logcallback.emit("### Recaptcha Detection False..............", 38)

        if recaptchaFlag == True:
            self.logcallback.emit("### Recaptcha Solving Now..................", 40)
            self.solver.solve_captcha_for_url(driver2, driver2.current_url)
            driver2.find_element_by_xpath('//button').click()
            self.logcallback.emit("### Recaptcha Solved.......................", 44)

        phone_data ={
            "phone1" : "",
            "phone2" : "",
            "phone3" : "",
            "phone4" : "",
            "phone5" : "",
            "phone6" : "",
            "phone7" : "",
            "phone8" : "",
            "phone9" : "",
            "phone10" : ""
        }

        email_data = {
            "email1" : "",
            "email2" : "",
            "email3" : "",
            "email4" : "",
            "email5" : "",
            "email6" : "",
            "email7" : "",
            "email8" : "",
            "email9" : "",
            "email10" : "",
        }

        with open(self.dirName + "/" + "{}.csv".format(self.keyword), "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            self.logcallback.emit("### Open  {}.csv File...............".format(self.keyword), 45)
            
            phones = re.findall(r'[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}', driver2.page_source)
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', driver2.page_source)
            
            for phone in range(1, len(phones) + 1):
                phone_data["phone{}".format(phone)] = phones[phone - 1]
                
            for email in range(1, len(emails) + 1):
                if 'truepeople' not in emails[email - 1]:
                    email_data["email{}".format(email)] = emails[email - 1]
                
            writer.writerow([self.data["company_name"], self.data["name"], self.data["role"], self.data["address"], self.data["age"], self.data["filling_type"], self.data["status"], self.data["state"], self.data["foreign_state"], self.data["county"], self.data["state_id"], self.data["date_filed"], self.data["dos_process"], phone_data["phone1"], phone_data["phone2"], phone_data["phone3"], phone_data["phone4"], phone_data["phone5"], phone_data["phone6"], phone_data["phone7"], phone_data["phone8"], phone_data["phone9"], phone_data["phone10"], email_data["email1"], email_data["email2"], email_data["email3"], email_data["email4"], email_data["email5"], email_data["email6"], email_data["email7"], email_data["email8"], email_data["email9"], email_data["email10"]])

        self.logcallback.emit("*****************************End*******************************", 100)
    
    def parse_ownerfind(self, htmlstring, driver3, driver2, original_ownerName):
        try:
            recaptcha = driver3.find_element_by_class_name("g-recaptcha")
            recaptchaFlag = True
        except:
            recaptchaFlag = False

        if recaptchaFlag == True:
            print('Stage2')
            self.solver.solve_captcha_for_url(driver3, driver3.current_url)
            driver3.find_element_by_xpath('//button').click()
            print('Stage2 done')
        
        infos = driver3.find_elements_by_xpath("//a[contains(@class, 'link-to-more') and contains(@class, 'olnk')]")

        for info in infos:
            relName = info.text
            rel_array = (relName.lower()).split(" ")
            ori_arry = (original_ownerName.lower()).split(" ")
            
            common = list(set(rel_array).intersection(ori_arry))
            if len(common) == 2:
                owner_url = info.get_attribute("href")
                print("relName----------------------->", relName, owner_url)
                driver3.get(owner_url)
                time.sleep(2)
                try:
                    itemsInfo = driver3.find_element_by_xpath("//html/body/div[2]/div/div[2]/div[3]/div[1]").text
                    totals = int((itemsInfo.split(" "))[0])
                    page_counts = math.ceil(totals / 11)
                    print("Total Items Accounts  2----------------------> : ", page_counts)
                
                    for page in range(1, page_counts + 1):
                        if page != 1:
                            driver1.get((owner_url + "&page={}").format(page))
                            time.sleep(2)
                    
                        ownerXpaths = driver3.find_elements_by_xpath("//div[contains(@class, 'card-summary')]//div[@class='h4']")
                        
                        viewButtons = driver3.find_elements_by_xpath("//div[contains(@class, 'card-summary')]//div[contains(@class, 'align-self-center')]/a")
                        
                        for ownerXpath, viewButton in zip(ownerXpaths, viewButtons):
                            ownerName = ownerXpath.text
                            # print(ownerName)
                            flag = destinction(ownerName.lower(), original_ownerName.lower())
                            
                            if flag == 2:
                                second_url = viewButton.get_attribute('href')
                                driver2.get(second_url)
                                parse_owner(driver2.page_source, driver2)
                                break
                except:
                    driver2.get(owner_url)
                    self.parse_owner(driver2.page_source, driver2)
                        
                break


    def destinction(self, ownerName, original_Name):
    
        print("OwnerName-----------> : ", ownerName)
        print("Original_Name-------> : ", original_Name)
        owner_array = ownerName.split(" ")
        original_array = original_Name.split(" ")

        common = list(set(owner_array).intersection(original_array))
        
        if len(common) >= 2:
            return 2
        elif len(common) == 1 and len(common[0]) != 1:
            return 1
        else:
            return False

    def run(self):
        try:
            self.parse_page()
            
            self.driver.close()
            self.driver.quit()
            self.driver1.close()
            self.driver1.quit()
            self.driver2.close()
            self.driver2.quit()
            self.driver3.close()
            self.driver3.quit()
            
        except Exception as e:
            if self.driver is not None:
                raise e