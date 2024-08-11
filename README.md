# JOB SCRAPER

## Introduction

The goal of this Python app is to scrape data from a well know french IT french website.

This app provides a Rest API integrated to allow users to target exactly what they want to scrap thanks to filters.

### Filters

* Job title
* Contract type (enum: contractor, permanent, fixed-term)
* Location (it must be a city or a french region)

### Tools

* Docker app :
    - Python code (APP & API)
    - MongoDB

For launching the app a simple  command : ``` docker compose up ```

This will set up all necessary.

## How it works ?

### API :

Fast API, here the swagger:

![alt text](<Capture d’écran du 2024-08-11 19-36-39.png>)



To make a search run a POST, for exemple here search for Software engineer jobs with permanent contract in the city of Lyon :
&nbsp;

``` curl -X POST -H "Content-Type: application/json" -d '{"job_title": "Software Engineer", "contracts": ["permanent"], "location": "Lyon"}' http://localhost:80/scrape ```


It returns a session_id. With this string lets call again the API by a GET to get basic infos or additional infos on the adds.
&nbsp;

``` curl -X GET -H "Content-Type: application/json" http://localhost:80/scrape/additional_info/3191d424-1674-4e79-a1d8-847330c9f73c ``` 

* Improvement : adding pagination & limiting data in cache

### Web scraper app

Traditional python webscraper with Selenium.

1. Build the url thanks to filters
2. Launch scraping over pages for basic and additional infos
    - Python Threads to speed up the scraping
    - Pydantic for formating
    - Poetry for package/venv manager

## Next steps

1. Compute data with DuckDB & generate reports for each session id & all the previous search

2. Publish it in the cloud for exemple with AWS
    -  ECS or K8s cluster
    -  API Gateway + Lambda

3. Push metrics in Prometheus/Grafana for performance, or transformed data
