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


class TruepeopleSearch(QThread):
    solver = CaptchaSolver()

    dirName = "truepeoplesearch"
    logcallback = pyqtSignal(object, object)
    mutex = QMutex()
    progress_bar = 0
    step_plus = 0

    try:
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists ")

    def __init__(self, searchName, searchAddress):
        QThread.__init__(self)
        self.searchName = searchName
        self.searchAddress = searchAddress
        self.paused = False
        self.default_url = "https://www.truepeoplesearch.com/results?name={0}&citystatezip={1}"
        self.base_url = "https://www.truepeoplesearch.com/results?name={0}&citystatezip={1}&page={2}"

    def _check_task_paused(self):
        while self.paused:
            print('Sleeping')
            self.sleep(1)

    def _intialize(self):
        self.logcallback.emit("### Now making csv file...........................", 2)

        open(self.dirName + "/" + "{}.csv".format(self.searchName), "wb").close()
        header = ["Name", "Address", "Phone1", "phone2", "phone3", "phone4", "phone5", "phone6", "phone7", "phone8",
                  "phone9", "phone10", "email1", "email2", "email3", "email4", "email5", "email6", "email7", "email8",
                  "email9", "email10"]

        with open(self.dirName + "/" + "{}.csv".format(self.searchName), "a", newline="") as f:
            csv_writer = csv.DictWriter(f, fieldnames=header, lineterminator='\n')
            csv_writer.writeheader()

        self.logcallback.emit("### Open Chrome Browser1 now.............", 4)
        self.path = "driver\\chromedriver.exe"

        self.driver = Chrome(executable_path=self.path)

        self.logcallback.emit("### Open Chrome Browser2 now.............", 6)
        self.driver1 = Chrome(executable_path=self.path)

        self.logcallback.emit("### Open Chrome Browser3 now.............", 8)
        self.driver2 = Chrome(executable_path=self.path)

        self.driver.get("https://www.truepeoplesearch.com/")
        self.driver1.maximize_window()
        self.driver2.maximize_window()
        self.driver.maximize_window()

    def parse_page(self):
        self._intialize()

        # Checking task is paused or not
        self._check_task_paused()
        time.sleep(5)
        self.logcallback.emit("### First Page Scraping Start.................", 10)

        driver = self.driver
        driver1 = self.driver1
        driver2 = self.driver2

        url = self.default_url.format(self.searchName, self.searchAddress)

        self.logcallback.emit("### Redirect URL >>> First Browser............", 12)
        # driver.get("https://www.truepeoplesearch.com/results?name=Dasha%20J.%20Arklis&citystatezip=2964%20Brighton%206Th%20St%20Brooklyn%20NY%2011235")
        driver.get(url)
        self._check_task_paused()

        try:
            self.logcallback.emit("### Recaptcha Detecting >>>................", 14)
            recaptcha = driver.find_element_by_class_name("g-recaptcha")
            recaptchaFlag = True
            self.logcallback.emit("### Recaptcha Detection True...............", 16)
        except:
            recaptchaFlag = False
            self.logcallback.emit("### Recaptcha Detection False..............", 16)

        if recaptchaFlag == True:
            self.logcallback.emit("### Recaptcha Solving Now..................", 16)
            self.solver.solve_captcha_for_url(driver, driver.current_url)
            driver.find_element_by_xpath('//button').click()
            self.logcallback.emit("### Recaptcha Solved.......................", 16)

        try:
            itemsInfo = driver.find_element_by_xpath("//html/body/div[2]/div/div[2]/div[3]/div[1]").text
            totals = int((itemsInfo.split(" "))[0])
            page_counts = math.ceil(totals / 11)
            self.logcallback.emit("### Total Item Accounts....................", 18)
            next_flag = False
            self.logcallback.emit("### Total {} PAGE....................".format(page_counts), 20)

            for page in range(1, page_counts + 1):
                self._check_task_paused()
                if page != 1:
                    driver.get(self.base_url.format(self.searchName, self.searchAddress, page))
                    time.sleep(2)
                try:
                    self.logcallback.emit("### Recaptcha Detecting >>>................", 21)
                    recaptcha = driver.find_element_by_class_name("g-recaptcha")
                    recaptchaFlag = True
                    self.logcallback.emit("### Recaptcha Detection True...............", 22)
                except:
                    recaptchaFlag = False
                    self.logcallback.emit("### Recaptcha Detection False..............", 22)

                if recaptchaFlag == True:
                    self.logcallback.emit("### Recaptcha Solving Now..................", 24)
                    self.solver.solve_captcha_for_url(driver, driver.current_url)
                    driver.find_element_by_xpath('//button').click()
                    self.logcallback.emit("### Recaptcha Solved.......................", 26)

                ownerXpaths = driver.find_elements_by_xpath("//div[contains(@class, 'card-summary')]//div[@class='h4']")

                viewButtons = driver.find_elements_by_xpath(
                    "//div[contains(@class, 'card-summary')]//div[contains(@class, 'align-self-center')]/a")

                for ownerXpath, viewButton in zip(ownerXpaths, viewButtons):
                    self._check_task_paused()
                    ownerName = ownerXpath.text

                    flag = self.destinction(ownerName.lower(), self.searchName.lower())

                    if flag == 2:
                        self.logcallback.emit("### First Mode.......................", 30)
                        second_url = viewButton.get_attribute('href')
                        driver1.get(second_url)
                        self._check_task_paused()
                        self.parse_owner(driver1.page_source, driver1)
                        next_flag = True
                        break

                    elif flag == 1:
                        self.logcallback.emit("### Second Mode.......................", 30)
                        second_url = viewButton.get_attribute('href')
                        driver2.get(second_url)
                        self._check_task_paused()
                        self.parse_ownerfind(driver2.page_source, driver2, driver1, self.searchName)
                        next_flag = True
                        break

                if next_flag == True:
                    break
        except:
            print("continue")

    def parse_owner(self, htmlstring, driver1):
        self._check_task_paused()
        self.logcallback.emit("### GET INFOS.......................", 35)
        try:
            self.logcallback.emit("### Recaptcha Detecting >>>................", 36)
            recaptcha = driver1.find_element_by_class_name("g-recaptcha")
            recaptchaFlag = True
            self.logcallback.emit("### Recaptcha Detection True...............", 38)
        except:
            recaptchaFlag = False
            self.logcallback.emit("### Recaptcha Detection False..............", 38)

        if recaptchaFlag == True:
            self.logcallback.emit("### Recaptcha Solving Now..................", 40)
            self.solver.solve_captcha_for_url(driver1, driver1.current_url)
            driver1.find_element_by_xpath('//button').click()
            self.logcallback.emit("### Recaptcha Solved.......................", 44)

        phone_data = {
            "phone1": "",
            "phone2": "",
            "phone3": "",
            "phone4": "",
            "phone5": "",
            "phone6": "",
            "phone7": "",
            "phone8": "",
            "phone9": "",
            "phone10": ""
        }

        email_data = {
            "email1": "",
            "email2": "",
            "email3": "",
            "email4": "",
            "email5": "",
            "email6": "",
            "email7": "",
            "email8": "",
            "email9": "",
            "email10": "",
        }

        with open(self.dirName + "/" + "{}.csv".format(self.searchName), "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            self.logcallback.emit("### Open  {}.csv File...............".format(self.searchName), 45)

            phones = re.findall(r'[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}', driver1.page_source)
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', driver1.page_source)

            for phone in range(1, len(phones) + 1):
                phone_data["phone{}".format(phone)] = phones[phone - 1]

            for email in range(1, len(emails) + 1):
                if 'truepeople' not in emails[email - 1]:
                    email_data["email{}".format(email)] = emails[email - 1]

            writer.writerow(
                [self.searchName, self.searchAddress, phone_data["phone1"], phone_data["phone2"], phone_data["phone3"],
                 phone_data["phone4"], phone_data["phone5"], phone_data["phone6"], phone_data["phone7"],
                 phone_data["phone8"], phone_data["phone9"], phone_data["phone10"], email_data["email1"],
                 email_data["email2"], email_data["email3"], email_data["email4"], email_data["email5"],
                 email_data["email6"], email_data["email7"], email_data["email8"], email_data["email9"],
                 email_data["email10"]])

        self.logcallback.emit("*****************************End*******************************", 100)

    def parse_ownerfind(self, htmlstring, driver2, driver1, original_ownerName):
        try:
            recaptcha = driver2.find_element_by_class_name("g-recaptcha")
            recaptchaFlag = True
        except:
            recaptchaFlag = False

        if recaptchaFlag == True:
            print('Stage2')
            self.solver.solve_captcha_for_url(driver2, driver2.current_url)
            driver2.find_element_by_xpath('//button').click()
            print('Stage2 done')

        infos = driver2.find_elements_by_xpath("//a[contains(@class, 'link-to-more') and contains(@class, 'olnk')]")

        for info in infos:
            relName = info.text
            rel_array = (relName.lower()).split(" ")
            ori_arry = (original_ownerName.lower()).split(" ")

            common = list(set(rel_array).intersection(ori_arry))
            if len(common) == 2:
                owner_url = info.get_attribute("href")
                print("relName----------------------->", relName, owner_url)
                driver2.get(owner_url)
                time.sleep(2)
                try:
                    itemsInfo = driver2.find_element_by_xpath("//html/body/div[2]/div/div[2]/div[3]/div[1]").text
                    totals = int((itemsInfo.split(" "))[0])
                    page_counts = math.ceil(totals / 11)
                    print("Total Items Accounts  2----------------------> : ", page_counts)

                    for page in range(1, page_counts + 1):
                        if page != 1:
                            self.driver.get((owner_url + "&page={}").format(page))
                            time.sleep(2)

                        ownerXpaths = driver2.find_elements_by_xpath(
                            "//div[contains(@class, 'card-summary')]//div[@class='h4']")

                        viewButtons = driver2.find_elements_by_xpath(
                            "//div[contains(@class, 'card-summary')]//div[contains(@class, 'align-self-center')]/a")

                        for ownerXpath, viewButton in zip(ownerXpaths, viewButtons):
                            ownerName = ownerXpath.text
                            # print(ownerName)
                            flag = self.destinction(ownerName.lower(), original_ownerName.lower())

                            if flag == 2:
                                second_url = viewButton.get_attribute('href')
                                driver1.get(second_url)
                                self.parse_owner(driver1.page_source, driver1)
                                break
                except:
                    driver1.get(owner_url)
                    self.parse_owner(driver1.page_source, driver1)

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

        except Exception as e:
            pass
            # if self.driver is not None:
            #     raise e
