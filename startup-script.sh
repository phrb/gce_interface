#! /bin/bash

echo "[INFO] Starting up Script" > startup.log

cd /

apt-get update &>> startup.log
apt-get install -y git python-pip python-dev python-matplotlib libsqlite3-dev libfreetype6-dev &>> startup.log
pip install --upgrade oauth2client google-api-python-client &>> startup.log
pip install opentuner &>> startup.log
git clone https://github.com/jansel/opentuner.git &>> startup.log
git clone https://github.com/phrb/measurement-server.git &>> startup.log

echo "[INFO] Startup Done. Starting Server" >> startup.log
# Start Server
cd measurement-server
python server.py &>> server.log

# The VM's Server is now waiting for connections and messages
