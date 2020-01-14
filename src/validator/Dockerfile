FROM python:3

ADD validator_custom.py /validator/
ADD validator_core.py /validator/

RUN pip install psycopg2-binary
RUN pip install pika

WORKDIR /validator

CMD ["python3", "-u", "./validator_core.py"]


