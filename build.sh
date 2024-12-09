#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

git lfs install
git lfs pull
pip install -r requirements.txt
