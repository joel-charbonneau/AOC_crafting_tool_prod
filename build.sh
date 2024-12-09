#!/bin/bash

# Install Git LFS
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs -y

# Initialize Git LFS
git lfs install
git lfs pull

# Install Python dependencies
pip install -r requirements.txt

