FROM quay.io/keboola/docker-custom-python:latest

COPY ./src/ /code/
COPY requirements.txt /code/

RUN python -u -m pip install -r requirements.txt

WORKDIR /data/
CMD ["python", "-u", "/code/main.py"]

