#!/usr/bin/env bash
# proto.sh - small wrapper to compile .proto files to Python gRPC code
# Usage: ./proto.sh calculator.proto [other.proto ...]
# By default outputs to current directory. Use -o <outdir> to change.

set -euo pipefail

OUTDIR="."
FILES=()

print_usage() {
  cat <<EOF
Usage: $0 [-o OUTDIR] file1.proto [file2.proto ...]

Compiles .proto files using python -m grpc_tools.protoc.

Examples:
  $0 calculator.proto
  $0 -o proto_out calculator.proto other.proto

Requires: Python (python or python3) with grpcio-tools installed:
  python -m pip install grpcio grpcio-tools
  or
  python3 -m pip install grpcio grpcio-tools
EOF
}

if [ "$#" -eq 0 ]; then
  print_usage
  exit 1
fi

# parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--outdir)
      shift
      if [ $# -eq 0 ]; then
        echo "Missing argument for -o" >&2
        exit 2
      fi
      OUTDIR="$1"
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    -* )
      echo "Unknown option: $1" >&2
      print_usage
      exit 2
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

# prefer `python`, fall back to `python3` if needed
PYTHON=""
if command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo "python or python3 not found in PATH. Please install Python and try again." >&2
  exit 3
fi

# check grpc_tools.protoc is importable in the chosen Python
if ! "$PYTHON" -c "import grpc_tools.protoc" >/dev/null 2>&1; then
  echo "grpc_tools.protoc not found in the selected Python environment ($PYTHON)." >&2
  echo "Install with: $PYTHON -m pip install grpcio grpcio-tools" >&2
  exit 4
fi

# create outdir
mkdir -p "$OUTDIR"

# run protoc for each file
for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "File not found: $f" >&2
    exit 5
  fi
  echo "Compiling $f -> $OUTDIR"
  "$PYTHON" -m grpc_tools.protoc -I. --python_out="$OUTDIR" --pyi_out="$OUTDIR" --grpc_python_out="$OUTDIR" "$f"
done

echo "Done. Generated files in $OUTDIR"
