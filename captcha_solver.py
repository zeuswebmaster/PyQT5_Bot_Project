# -*- coding: utf-8 -*-
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
# from downloader_selenium import DownloaderSelenium
from selenium import webdriver
from selenium.webdriver import Chrome
import time

class CaptchaSolver(object):

    def __init__(self):
        self.api_key = '0193c75c69d14245ca25bd5b2217637f' # anti-captcha.com API KEY HERE

    def solve_captcha(self, url, site_key):
        client = AnticaptchaClient(self.api_key)
        task = NoCaptchaTaskProxylessTask(url, site_key)
        job = client.createTask(task)
        job.join()
        return job.get_solution_response()

    def read_sitekey(self, driver):
        return driver.find_element_by_xpath('//*[@data-sitekey]').get_attribute('data-sitekey')

    def solve_captcha_for_url(self, driver, url):
        site_key = self.read_sitekey(driver)
        print('Solving captcha. site_key={}'.format(site_key))
        if site_key is None:
            raise Exception('Exception->site_key is None')
        response = self.solve_captcha(url, site_key)
        print(response)
        driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(response))
        time.sleep(2)
        
# def click_button():
#     parse_qs(qs, keep_blank_values=False, strict_parsing=False)            

# def main():
#     url = 'https://www.truepeoplesearch.com/InternalCaptcha?returnUrl=%2fresults%3fstreetaddress%3d1343%252056TH%2520ST%26citystatezip%3d%2520BROOKLYN%2c%2520NY%252011219'
#     path = "driver\\chromedriver.exe"
#     driver = Chrome(executable_path=path)
#     solver = CaptchaSolver()
#     # driver = webdriver.Chrome()
#     driver.get(url)


#     time.sleep(10)

#     try:
#         print('Stage1')
#         solver.solve_captcha_for_url(driver, url)
#         driver.find_element_by_id('recaptcha_submit').click()
#         time.sleep(5)
#         print('Stage1 done')
    
#     except:
#         print('Stage2')
#         solver.solve_captcha_for_url(driver, driver.current_url)
#         driver.find_element_by_xpath('//button').click()
#         print('Stage2 done')


# main()