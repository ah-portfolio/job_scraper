from pydantic_settings import BaseSettings

from selenium.webdriver.chrome.options import Options

class Settings(BaseSettings):
#SELENIUM WEBDRIVER
    options: Options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options_additional_infos: Options = Options()
    options_additional_infos.add_argument("--headless")
    options_additional_infos.add_argument("--no-sandbox")
    options_additional_infos.add_argument("--disable-dev-shm-usage")
    options_additional_infos.add_argument("window-size=1920,1080")


    ## MONGO DB
    mongo_hostname: str = "scraper-mongo"

    mongo_port: int = 27017

    mongo_db: str = "scraper"

    basic_info_collection: str = "scraping_result_basic_info"

    additional_info_collection: str = "scraping_result_additional_info"

    ##
    base_url: str = "https://www.free-work.com/fr/tech-it/jobs?query="

    base_url_location: str = "https://www.free-work.com/api/locations/search?search=" 