FROM python:3.11.4

WORKDIR /app
COPY . .

RUN apt-get update
RUN apt-get -y install cron ffmpeg libsm6 libxext6 supervisor

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r requirements.txt

RUN touch /var/log/cron.log
RUN mkdir -p /var/log/supervisor
COPY container/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN echo "3 22 * * * $(which python) /app/merge.py" | crontab -

CMD ["/usr/bin/supervisord", "-n"]
