from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from uuid import uuid4
from app.scraper import JobScraper
from app.mongo import Database
from app.config import Settings
config = Settings()

app = FastAPI(title='job_scraper API',
              description='IT job scraper')

class ContractType(Enum):
    contractor = "contractor"
    permanent = "permanent"
    fixed_term = "fixed-term"


class Item(BaseModel):
    job_title: str
    contracts: list[ContractType]
    location: str

@app.post("/scrape", tags=["SCRAPER"])
def scrape(item: Item):
    job_scraper = JobScraper(item.job_title,item.contracts,item.location)
    job_scraper.build_base_url()

    nb_of_page = job_scraper.get_number_of_page_to_scrap()
    uuid =  uuid4()
    job_scraper.run(nb_of_page,uuid)
    
    return {"result": uuid}

@app.get("/scrape/basic_info/{session_id}", tags=["SCRAPER"])
def get_basic_info(session_id: str):
    result = Database(config.basic_info_collection).select_by_session_id(str(session_id))
    return {session_id: result}

@app.get("/scrape/additional_info/{session_id}", tags=["SCRAPER"])
def get_basic_info(session_id: str):
    result = Database(config.additional_info_collection).select_by_session_id(str(session_id))
    return {session_id: result}