FROM tensorflow/tensorflow:2.14.0

WORKDIR /camerai
COPY . .

RUN apt-get update
RUN apt-get -y install cron ffmpeg libsm6 libxext6 supervisor

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements-container.txt --no-cache-dir

RUN touch /var/log/cron.log
RUN mkdir -p /var/log/supervisor
COPY container/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN echo "0 3 * * * $(which python) /camerai/merge.py" | crontab -

RUN python -m grpc_tools.protoc -I ./libs/CamerAIProtos/ --python_out=./src/ --grpc_python_out=./src/ ./libs/CamerAIProtos/Node.proto

CMD ["/usr/bin/supervisord", "-n"]
