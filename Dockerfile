FROM tensorflow/tensorflow:2.14.0

WORKDIR /camerai

COPY requirements-container.txt .

RUN apt-get update
RUN apt-get -y install ffmpeg libsm6 libxext6

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements-container.txt --no-cache-dir

COPY . .

RUN python -m grpc_tools.protoc -I ./libs/CamerAIProtos/ --python_out=./src/ --grpc_python_out=./src/ ./libs/CamerAIProtos/Node.proto

CMD ["python", "-m", "src.node"]
