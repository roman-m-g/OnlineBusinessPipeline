FROM astrocrpublic.azurecr.io/runtime:3.1-14

USER root
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
USER astro

# install soda into a virtual environment
RUN python -m venv soda_venv && \
    soda_venv/bin/pip install --no-cache-dir setuptools && \
    soda_venv/bin/pip install --no-cache-dir soda-core-bigquery==3.5.6

# install dbt into a virtual environment
RUN python -m venv dbt_venv && \
    dbt_venv/bin/pip install --no-cache-dir dbt-bigquery