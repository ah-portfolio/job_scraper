from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import logging
from concurrent.futures.thread import ThreadPoolExecutor
import requests
import urllib.parse

import app.labels as labels
from app.mongo import Database

from app.config import Settings
config = Settings()

log = logging.getLogger(__name__)


class JobScraper:
    def __init__(self, job_title: str, contracts: list[str], location: str):
        self.job_title = job_title
        self.contracts = contracts
        self.location = location
        self.options = config.options
        self.options_additional_infos = config.options_additional_infos
        
    def build_base_url(self):
        url = config.base_url + urllib.parse.quote(str(self.job_title))
        
        if self.contracts:
            for contract in self.contracts:
                url = url + "&contracts=" + urllib.parse.quote(str(contract))
        
        if self.location:
            url_search_loc = config.base_url_location + self.location
            response = requests.get(url_search_loc)
            data = response.json()
            url_location = data[0]['key']
            url = url + "&locations=" + urllib.parse.quote(str(url_location))
        self.base_url = url    
            
    def get_url(self, page):
        return self.base_url + f"~&page={page}"

    def get_number_of_page_to_scrap(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        log.info(self.get_url(1))
        driver.get(self.get_url(1))
        try:
            nb_pages = driver.find_element(By.XPATH, labels.nb_pages_xpath)
            self.nb_page = int(nb_pages.text[len(nb_pages.text)-1])
        except:
            self.nb_page = 1
        driver.close()
        driver.quit()
        return self.nb_page

    def scraper_basic_infos(self, url, uuid):
        session_id = 0
        output_ads = dict()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        try:
            driver.get(url)
        
            ads = driver.find_elements(By.XPATH, labels.ads_xpath)

            for ad in ads:
                output_ad = dict()
                output_ad["session_id"] = str(uuid)

                company = ad.find_element(By.XPATH, labels.company_xpath).text
                output_ad["company"] = company

                publish_date = ad.find_element(By.XPATH, labels.publish_date_xpath).text
                date = publish_date[len(publish_date) - 10 : len(publish_date)]
                output_ad["date"] = date

                job_type_and_title = ad.find_elements(By.XPATH, labels.job_type_and_title_xpath)
                job_type = job_type_and_title[0].text.split("\n")[0]
                job_title = job_type_and_title[0].text.split("\n")[1]
                output_ad["job_title"] = job_title

                job_description_div = ad.find_element(
                    By.XPATH, labels.job_description_div_xpath
                )
                job_description = job_description_div.find_element(
                    By.XPATH, labels.job_description_xpath
                ).text
                output_ad["job_description"] = job_description

                try:
                    skills_div = ad.find_element(By.XPATH, labels.skill_div_xpath)
                    skills = skills_div.find_elements(By.XPATH, labels.skills_xpath)
                    skills = [skill.text for skill in skills]
                except:
                    skills = []
                output_ad["skills"] = skills

                job_url = ad.find_element(By.XPATH, labels.job_type_and_title_xpath).get_attribute('href')
                output_ad["job_url"] = job_url

                output_ads[session_id] = output_ad
                session_id += 1
        finally:
            driver.quit()        
            log.info(f"Successfull scraping in basic mode of this url: {url}")
            Database(config.basic_info_collection).insert(output_ads)
            


    def get_additional_infos(self, url, uuid):
        session_id = 0
        
        output_ads = dict()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=config.options_additional_infos)

        try:
            driver.get(url)
            
            ads = driver.find_elements(By.XPATH, labels.ads_fullscreen_xpath)
            
            for ad in ads:
                output_ad = dict()

                job_url = ad.find_element(By.XPATH, labels.job_type_and_title_xpath).get_attribute('href')
                output_ad['job_url'] = job_url

                try:
                    info_starting_date =  ad.find_element(By.XPATH,labels.side_ad_fullscreen_xpath2)
                    info_starting_date_bis = info_starting_date.find_element(By.XPATH,labels.side_ad_fullscreen_xpath2bis)
                    log.info(f"starting date founded {info_starting_date_bis}")
                except:
                    pass 

                try:
                    output_ad["session_id"] = str(uuid)
                    infos = ad.find_elements(By.XPATH,labels.side_ad_fullscreen_xpath)  
                    output_ad['additional_info'] = [info.text for info in infos]

                except:
                    log.info(f"No additional info found for this url: {job_url}")
                    pass

                output_ads[session_id] = output_ad
                session_id += 1
        finally:
            driver.close()
            driver.quit()
            log.info(f"Successfull scraping in additional mode of this url: {url}")
            Database(config.additional_info_collection).insert(output_ads)
    
    def run(self, nb_of_page, uuid):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for url in [self.get_url(page) for page in range(1, nb_of_page+1)]:
                executor.submit(self.scraper_basic_infos, url, uuid)
                executor.submit(self.get_additional_infos, url, uuid)
