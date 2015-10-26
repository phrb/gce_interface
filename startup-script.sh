#! /bin/bash

echo "[INFO] Starting up Script" > startup.log

# Install Dependencies
apt-get update &>> startup.log
apt-get -y install git python-dev python-pip &>> startup.log
git clone https://github.com/jansel/opentuner.git &>> startup.log

cd opentuner
pip install -r requirements.txt &>> startup.log

cd /

# Clone Measurement Server Repository
git clone https://github.com/phrb/measurement-server.git &>> startup.log

echo "[INFO] Startup Done. Starting Server" >> startup.log
# Start Server
cd measurement-server
python server.py &>> server.log

# The VM's Server is now waiting for connections and messages
