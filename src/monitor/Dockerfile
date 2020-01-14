FROM python:3

ADD monitor_custom.py /monitor/
ADD monitor_core.py /monitor/

RUN pip install requests
RUN pip install pika

WORKDIR /monitor

CMD ["python3", "-u", "./monitor_core.py"]


