# gRPC Python — Quick Setup & Workflow

This README walks you through creating, compiling, and using .proto definitions for Python gRPC services, plus running the service locally and inside Docker. It’s tailored for a Calculator example (calculator.proto, calculator_server.py, calculator_client.py) included in this repository.

## What you'll find here
- How gRPC works (quick overview)
- Creating a `.proto` service definition
- Compiling `.proto` into Python code using grpcio-tools
- Using generated code in `calculator_server.py` and `calculator_client.py`
- Running and testing locally
- Building, running, and publishing a Docker image
- Troubleshooting and tips

---

## Quick overview
gRPC allows a client to call methods on a remote server as if the methods were local. You define your service with Protocol Buffers (.proto), then generate language-specific client/server code. The server implements the service interface and runs a gRPC server. The client uses a generated stub to call remote methods.

This guide follows the calculator example with procedures like Add, Sub, Multiply and Divide.

## Prerequisites
- Python 3.8+ (macOS, Linux or Windows) installed and on PATH
- pip (Python package manager)
- Docker (for container steps)

Install gRPC and tools:

```bash
python -m pip install --upgrade pip
python -m pip install grpcio grpcio-tools
```

Confirm installation:

```bash
python -c "import grpc; print('grpc:', grpc.__version__)"
python -c "import grpc_tools.protoc; print('grpc_tools:', grpc_tools.protoc.__name__)"
```

## 1) Define your service: `calculator.proto`
Create a file named `calculator.proto` in the repository root. Example content (simple calculator service):

```
syntax = "proto3";

package calculator;

service Calculator {
  rpc Add (BinaryOp) returns (UnaryResult) {}
  rpc Sub (BinaryOp) returns (UnaryResult) {}
  rpc Multiply (BinaryOp) returns (UnaryResult) {}
  rpc Divide (BinaryOp) returns (UnaryResult) {}
}

message BinaryOp {
  double a = 1;
  double b = 2;
}

message UnaryResult {
  double result = 1;
}
```

Notes:
- `syntax = "proto3"` is recommended for modern protobuf usage.
- `package` helps avoid symbol collisions.

## 2) Compile `.proto` into Python
From the project root (where `calculator.proto` is located), run:

```bash
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. {YOUR_PROTO_FILE}.proto
```

What this generates:
- `calculator_pb2.py` — Protobuf message classes
- `calculator_pb2.pyi` — Optional type hint stub
- `calculator_pb2_grpc.py` — gRPC service classes (stubs and servicers)

If you prefer to generate code into a subpackage (recommended for larger projects):
- Create a package directory `proto/` and add `__init__.py`.
- Run the protoc command with `--python_out=./proto --grpc_python_out=./proto` and update imports in your app accordingly.

Common errors:
- "grpc_tools.protoc: not found" — ensure `grpcio-tools` is installed in the same Python environment that runs the command.
- Import errors after generation — check module/package paths and `__init__.py`.

### Using the helper script `proto.sh`

This repository includes a small convenience wrapper, `proto.sh`, to compile one or more `.proto` files using the locally available Python interpreter (it prefers `python` and falls back to `python3`). It calls `python -m grpc_tools.protoc` under the hood and mirrors the same options shown above.

Prerequisites:
- Python on PATH (either `python` or `python3`)
- `grpcio` and `grpcio-tools` installed in that Python environment

Install the tools if needed:

```bash
# using python (or replace with python3)
python -m pip install --upgrade pip
python -m pip install grpcio grpcio-tools
```

Basic usage (from project root):

```bash
./proto.sh calculator.proto
# or compile multiple files into a specific directory
./proto.sh -o proto_out calculator.proto other.proto
```

What `proto.sh` does:
- Detects `python` or `python3` and uses it to run `grpc_tools.protoc`.
- Verifies `grpc_tools.protoc` is importable and prints an install hint if not.
- Writes generated files (`*_pb2.py`, `*_pb2.pyi`, `*_pb2_grpc.py`) to the current directory by default or to the directory provided with `-o`.

Notes:
- If you see "python or python3 not found in PATH" — install Python or adjust your PATH.
- If you see "grpc_tools.protoc not found" — install `grpcio-tools` into the same Python environment that `proto.sh` is using (see install commands above).
- `proto.sh` is a convenience; for CI or reproducible builds prefer running `python -m grpc_tools.protoc` inside a pinned virtual environment or container.

## 3) Implement the server (`calculator_server.py`)
- Import generated modules: `import calculator_pb2, calculator_pb2_grpc`
- Implement a Servicer class inheriting from `calculator_pb2_grpc.CalculatorServicer` and implement Add, Sub, Multiply, Divide.
- Start a gRPC server listening on port 50051 (the default used in many examples).

Example server flow (high level):
- Create servicer class with methods returning `calculator_pb2.UnaryResult(result=...)`.
- Create a gRPC server with `grpc.server(...)` and add servicer using `calculator_pb2_grpc.add_CalculatorServicer_to_server(servicer, server)`.
- Listen with `server.add_insecure_port('[::]:50051')` and `server.start()`.

Server skeleton (`calculator_server.py`):

```python
import grpc
from concurrent import futures
import time

import calculator_pb2
import calculator_pb2_grpc


class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
  """Implements the Calculator service methods defined in calculator.proto"""

  def Add(self, request, context):
    result = request.a + request.b
    return calculator_pb2.UnaryResult(result=result)

  def Sub(self, request, context):
    result = request.a - request.b
    return calculator_pb2.UnaryResult(result=result)

  def Multiply(self, request, context):
    result = request.a * request.b
    return calculator_pb2.UnaryResult(result=result)

  def Divide(self, request, context):
    if request.b == 0:
      context.set_details('Division by zero')
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      return calculator_pb2.UnaryResult()
    result = request.a / request.b
    return calculator_pb2.UnaryResult(result=result)


def serve(host='[::]:50051'):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)
  server.add_insecure_port(host)
  server.start()
  print(f"gRPC server running on {host}")
  try:
    while True:
      time.sleep(86400)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  serve()
```

## 4) Implement the client (`calculator_client.py`)
- Create a channel: `grpc.insecure_channel('localhost:50051')`.
- Create a stub: `stub = calculator_pb2_grpc.CalculatorStub(channel)`.
- Call methods on stub, e.g. `stub.Add(calculator_pb2.BinaryOp(a=1, b=2))`.

Example client flow (high level):
- Build request messages using generated classes.
- Use stub to call RPCs and print returned `result` field.

Client skeleton (`calculator_client.py`):

```python
import grpc

import calculator_pb2
import calculator_pb2_grpc


def run(host='localhost:50051'):
  with grpc.insecure_channel(host) as channel:
    stub = calculator_pb2_grpc.CalculatorStub(channel)

    a, b = 10, 5

    resp = stub.Add(calculator_pb2.BinaryOp(a=a, b=b))
    print(f"Add({a}, {b}) = {resp.result}")

    resp = stub.Sub(calculator_pb2.BinaryOp(a=a, b=b))
    print(f"Sub({a}, {b}) = {resp.result}")

    resp = stub.Multiply(calculator_pb2.BinaryOp(a=a, b=b))
    print(f"Multiply({a}, {b}) = {resp.result}")

    try:
      resp = stub.Divide(calculator_pb2.BinaryOp(a=a, b=b))
      print(f"Divide({a}, {b}) = {resp.result}")
    except grpc.RpcError as e:
      print(f"RPC error: {e.code()} - {e.details()}")


if __name__ == '__main__':
  run()
```

## 5) Run and test locally
1. Start the server in one terminal:

```bash
python calculator_server.py
```

2. Run the client in another terminal:

```bash
python calculator_client.py
```

You should see the results of Add/Sub/Multiply/Divide printed by the client.

## 6) Containerize the service (Docker)
Create a `Dockerfile` in the project root. Minimal example for a Python gRPC server:

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 50051
CMD ["python", "calculator_server.py"]
```

Create `requirements.txt` with at least:

```
grpcio
grpcio-tools
```

Build image (from project root):

```bash
docker build . -t grpc-calculator:v1
```

Verify image exists:

```bash
docker images ls | grep grpc-calculator
```

Run container (maps host port 50051 to container 50051):

```bash
docker run -d -p 50051:50051 --name calculator-service grpc-calculator:v1
```

Test from host (run client locally or inside a temporary client container):

```bash
python calculator_client.py
# or inside container
docker run --rm --network host grpc-calculator:v1 python calculator_client.py
```

Notes on Docker networking:
- Mac/Windows Docker Desktop uses a VM; `--network host` doesn't behave the same as Linux. For testing locally, mapping ports with `-p` is sufficient.

## 7) Publish the container image (optional)
1. Tag and push to Docker Hub (example):

```bash
docker tag grpc-calculator:v1 your-dockerhub-username/grpc-calculator:v1
docker push your-dockerhub-username/grpc-calculator:v1
```

2. Pull on another machine and run:

```bash
docker pull your-dockerhub-username/grpc-calculator:v1
docker run -d -p 50051:50051 your-dockerhub-username/grpc-calculator:v1
```

## Troubleshooting & tips
- Python path / Imports: If generated files are in a package, ensure the package has `__init__.py` and you use the correct relative or absolute imports.
- Python venv: Use a virtualenv to avoid system package conflicts: `python -m venv .venv && source .venv/bin/activate` then install dependencies.
- Regenerate when proto changes: Re-run the protoc command whenever you modify `calculator.proto`.
- Version mismatch: Ensure `grpcio` and `grpcio-tools` versions are compatible. Upgrading both often resolves issues.
- Linting/typing: `--pyi_out` generates type stubs for better editor support.

## Example file list (what this repo contains)
- `calculator.proto` — gRPC service definition
- `calculator_server.py` — Example server implementation
- `calculator_client.py` — Example client that calls the server
- `Dockerfile` — Dockerfile to containerize the server

## Additional resources
- gRPC Python Quickstart: https://grpc.io/docs/languages/python/
- Protocol Buffers language guide: https://developers.google.com/protocol-buffers/docs/proto3

## Helper script: `docker.sh` — build & run a Python script in Docker

For convenience there's a small script `docker.sh` that creates a minimal Docker build context for a given Python script, builds an image, and runs a container mapping port 50051.

Usage:

```bash
# from project root
./docker.sh path/to/script.py [image_name] [container_name]

# Example using the included calculator server
./docker.sh calculator_server.py
```

What it does:
- Creates a temporary build context containing the script (and `requirements.txt` if present).
- Writes a simple `Dockerfile` based on `python:3.10-slim`.
- If `requirements.txt` exists, it installs dependencies from it; otherwise it installs `grpcio` and `grpcio-tools` by default.
- Builds a Docker image (tag based on the script name unless you provide `image_name`).
- Runs the container mapping host port 50051 to the container's 50051.

Notes and troubleshooting:
- Requires Docker installed and the current user able to run `docker` commands.
- The script uses a temporary build directory and cleans up after itself.
- If a container with the chosen name already exists it will be stopped/removed before starting a new one.

