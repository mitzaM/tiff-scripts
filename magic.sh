#!/bin/bash

MONITORING_SCRIPT_URL=https://github.com/mitzaM/tiff-scripts/raw/master/tiff-monitoring.py
SUBTIVALS_DEB_URL=https://github.com/mitzaM/tiff-scripts/raw/master/subtivals_1.7.4-1-trusty_amd64.deb

SUBTIVALS_DEB=subtivals_1.7.4-1tiff15_amd64.deb
MONITORING_SCRIPT=tiff-monitoring.py

mkdir -p ~tiff/TIFF
cd $_

echo -n "Downloading online resources..."
if [ ! -f $SUBTIVALS_DEB ]; then
  wget $SUBTIVALS_DEB_URL -O $SUBTIVALS_DEB
else
  rm -rf $SUBTIVALS_DEB
  wget $SUBTIVALS_DEB_URL -O $SUBTIVALS_DEB
fi
if [ ! -f $MONITORING_SCRIPT ]; then
  wget $MONITORING_SCRIPT_URL -O $MONITORING_SCRIPT
else
  rm -rf $MONITORING_SCRIPT
  wget $MONITORING_SCRIPT_URL -O $MONITORING_SCRIPT
fi
echo " done."

echo "----"
echo "Will now attempt to install packages (might ask for your sudo password)"
sudo apt-get -y autoremove
sudo apt-get update -qq > /dev/null 2>&1
sudo apt-get -y --force-yes install python-pkg-resources=3.3-1ubuntu1
sudo apt-get -y install python-virtualenv acpi
echo "----"
echo "Will now install the custom Subtivals version"
sudo dpkg -i subtivals_1.7.4-1tiff15_amd64.deb
echo "----"
echo "TIFF monitoring dependencies installed"

echo "----"
echo "Creating a Python3 virtual environment for monitoring"
virtualenv -p /usr/bin/python3 .
bin/pip3 install dropbox

echo "----"
echo -n "Will now set up the monitoring cron job..."
# echo "* * * * * DROPBOX_TOKEN=aXptIDIf7dAAAAAAAAAAJg5GTxERq5NJuLn6Vcs3bOTJ8qMkMaX_b1d7UBgnPMMk sudo -Hutiff ~tiff/TIFF/bin/python3 ~tiff/TIFF/tiff-monitoring.py" > tiffcron
# echo "" >> tiffcon
# crontab tiffcron
echo "* * * * * tiff DROPBOX_TOKEN=aXptIDIf7dAAAAAAAAAAJg5GTxERq5NJuLn6Vcs3bOTJ8qMkMaX_b1d7UBgnPMMk ~tiff/TIFF/bin/python3 ~tiff/TIFF/tiff-monitoring.py" | sudo tee /etc/cron.d/tiff
echo " done."

cd -
