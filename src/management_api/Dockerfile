FROM python:3

ADD management_api.py /management_api/

RUN pip install psycopg2-binary
RUN pip install flask
RUN pip install flask_restful

WORKDIR /management_api

CMD ["python3", "-u", "./management_api.py"]


