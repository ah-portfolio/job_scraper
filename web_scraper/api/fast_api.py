from fastapi import FastAPI
from api import models
from uuid import uuid4
from app.scraper import JobScraper
from app.mongo import Database
from app.config import Settings
config = Settings()

app = FastAPI(title='job_scraper API',
              description='IT job scraper')


@app.post("/scrape", response_model=models.SessionIdResponses, tags=["SCRAPER"])
def scrape(filters: models.JobFilters):
    job_scraper = JobScraper(filters.job_title,filters.contracts,filters.location)
    job_scraper.build_base_url()

    nb_of_page = job_scraper.get_number_of_page_to_scrap()
    uuid =  uuid4()
    job_scraper.run(nb_of_page,uuid)
    
    return {"session_id": uuid}

@app.get("/scrape/basic_info/{session_id}", response_model=models.BasicInfoResponses, tags=["SCRAPER"])
def get_basic_info(session_id: str):
    result = Database(config.basic_info_collection).select_by_session_id(str(session_id))
    return {session_id: result}

@app.get("/scrape/additional_info/{session_id}", response_model=models.AddtionalInfoResponses, tags=["SCRAPER"])
def get_basic_info(session_id: str):
    result = Database(config.additional_info_collection).select_by_session_id(str(session_id))
    return {session_id: result}