FROM python:3.10.12

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r requirements.txt

ADD docker/merge-videos-cron-task /etc/cron.d/cron-config
RUN chmod 0644 /etc/cron.d/cron-config
RUN touch /var/log/cron.log

RUN apt-get update
RUN apt-get -y install cron

CMD cron && tail -f /var/log/cron.log
CMD python -m src.node
