FROM tensorflow/tensorflow:2.14.0

WORKDIR /camerai

COPY requirements-container.txt .

RUN apt-get update
RUN apt-get -y install ffmpeg libsm6 libxext6

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements-container.txt --no-cache-dir
RUN apt-get clean
RUN apt-get autoremove
RUN rm -rf /var/lib/apt/lists/*
RUN pip cache purge

COPY . .

RUN pip install grpcio-tools
RUN python -m grpc_tools.protoc -I ./libs/CamerAIProtos/ --python_out=./src/grpc_protos/ --grpc_python_out=./src/grpc_protos/ ./libs/CamerAIProtos/Node.proto
RUN pip uninstall grpcio-tools -y

CMD ["python", "-m", "src.node"]
