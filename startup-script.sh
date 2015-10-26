#! /bin/bash

# Install Dependencies
apt-get update
apt-get -y install git pip
pip install opentuner

cd /

# Clone Measurement Server Repository
git clone https://github.com/phrb/measurement-server.git

# Start Server
cd measurement-server
python server.py

# The VM's Server is now waiting for connections and messages
