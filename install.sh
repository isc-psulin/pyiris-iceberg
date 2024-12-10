#!/bin/sh

python3 -c "import os; print(os.getcwd())"
python3 load_data.py

pip install .

mkdir /tmp/iceberg


