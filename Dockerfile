ARG PYTHON_VERSION=latest

FROM python:${PYTHON_VERSION}-slim AS base

WORKDIR /build

RUN sed -i 's/http:/https:/g' /etc/apt/sources.list.d/*
RUN apt update && \
    apt -y upgrade && \
    apt -y install curl cmake

RUN pip install \
    --index-url https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple \
    --no-cache-dir \
    poetry==2.1.1

COPY pyproject.toml poetry.lock ./

# create our virtualenvv in the current folder and allow non root users (such as the lambda runner) to read the config file
RUN poetry config virtualenvs.in-project true --local && chmod +r poetry.toml


#---- dev ----
FROM base AS dev
RUN poetry install --no-root --with=dev
COPY . .


#---- lambda ----
FROM  base AS lambda

COPY handler.py .
COPY src/ src/
RUN poetry install --no-root --without=dev

ENTRYPOINT ["poetry", "run", "python", "-m", "awslambdaric" ]
CMD ["handler.handler"]