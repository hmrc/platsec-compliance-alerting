ARG PYTHON_VERSION
ARG FUNCTION_DIR="/platsec-compliance-alerting"

FROM python:${PYTHON_VERSION}-slim as build-image

RUN sed -i 's/http:/https:/g' /etc/apt/sources.list

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    g++ \
    make \
    cmake \
    autoconf \
    libtool \
    unzip \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
ARG PIP_PIPENV_VERSION
RUN pip install --index-url https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple/  \
    --no-cache-dir pipenv==${PIP_PIPENV_VERSION}

RUN pip install --index-url https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple/  \
    --no-cache-dir --target ${FUNCTION_DIR} awslambdaric==1.2.2

COPY Pipfile.lock ${FUNCTION_DIR}
RUN PIPENV_VENV_IN_PROJECT=1 pipenv sync

FROM python:${PYTHON_VERSION}-slim as dev
COPY --from=build-image . .
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
COPY . .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv sync --dev

FROM python:${PYTHON_VERSION}-slim as production
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
RUN mv ${FUNCTION_DIR}/.venv/lib/python3.11/site-packages/* ${FUNCTION_DIR}
COPY src ${FUNCTION_DIR}/src
COPY handler.py ${FUNCTION_DIR}
RUN useradd alerter
USER alerter
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD ["handler.handler"]
