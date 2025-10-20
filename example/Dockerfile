FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir grpcio grpcio-tools

COPY . .

EXPOSE 50051

CMD ["python", "calculator_server.py"]
