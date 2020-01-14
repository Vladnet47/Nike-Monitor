FROM python:3

ADD formatNotification.py /notifier/
ADD notifier_custom.py /notifier/
ADD notifier_core.py /notifier/

RUN pip install psycopg2-binary
RUN pip install requests
RUN pip install pika

WORKDIR /notifier

CMD ["python3", "-u", "./notifier_core.py"]


