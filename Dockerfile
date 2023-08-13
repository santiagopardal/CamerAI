FROM python:3.11.4

WORKDIR /app
COPY . .

RUN apt-get update
RUN apt-get -y install cron ffmpeg libsm6 libxext6

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r requirements.txt

RUN echo "0 3 * * * $(which python) /app/merge.py" | crontab -
RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
CMD python -m src.node
