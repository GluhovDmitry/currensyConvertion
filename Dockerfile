Dockerfile

FROM python:3.8

WORKDIR /home

COPY requirements.txt

RUN pip install -r requirements.txt

COPY scripts/ .

CMD ["python", "./main.py"]
