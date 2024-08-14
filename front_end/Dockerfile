FROM python:3.12

RUN apt-get update

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /front_end

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install && rm -rf $POETRY_CACHE_DIR

COPY app ./app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["poetry", "run", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]