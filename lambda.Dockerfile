ARG PYTHON_VERSION
ARG FUNCTION_DIR="/platsec-compliance-alerting"

FROM python:${PYTHON_VERSION}-slim as build-image
RUN apt-get update \
    && apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
RUN pip install --no-cache-dir pipenv==2021.5.29
RUN pip install --no-cache-dir --target ${FUNCTION_DIR} awslambdaric==1.0.0
COPY Pipfile.lock ${FUNCTION_DIR}
RUN PIPENV_VENV_IN_PROJECT=1 pipenv sync

FROM python:${PYTHON_VERSION}-slim
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
RUN mv ${FUNCTION_DIR}/.venv/lib/python3.9/site-packages/* ${FUNCTION_DIR}
COPY src ${FUNCTION_DIR}/src
COPY handler.py ${FUNCTION_DIR}
RUN useradd alerter
USER alerter
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD ["handler.handler"]