FROM python:3.10.7-alpine3.16

# this is required for the psycopg2 python library to work
RUN /sbin/apk add --no-cache libpq

# create a new user inside the container so we don't have to run as root
RUN /usr/sbin/adduser -g python -D python

# switch to the user we just created
USER python

# create a python virtual environment for the project
RUN /usr/local/bin/python -m venv /home/python/venv

# copy requirements.txt into the image and install with pip
COPY --chown=python:python requirements.txt /home/python/lead-update/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/lead-update/requirements.txt

# set some environment variables
ENV PATH="/home/python/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

# image labels
LABEL org.opencontainers.image.authors="William Jackson <wjackson@informatica.com>" \
      org.opencontainers.image.source="https://github.com/informatica-na-presales-ops/lead-update"

# copy application code into the image
COPY --chown=python:python run.py /home/python/lead-update/run.py
COPY --chown=python:python lead_update /home/python/lead-update/lead_update

# what to run by default with the container starts
ENTRYPOINT ["/home/python/venv/bin/python", "/home/python/lead-update/run.py"]
