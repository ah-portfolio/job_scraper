FROM python:3.12

RUN apt-get update

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /scraper

COPY google-chrome-stable_current_amd64.deb ./

RUN apt install -yf ./google-chrome-stable_current_amd64.deb 

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install && rm -rf $POETRY_CACHE_DIR

COPY app ./app

COPY api ./api

EXPOSE 80

CMD ["poetry", "run", "uvicorn", "api.fast_api:app", "--host", "0.0.0.0", "--port", "80"]