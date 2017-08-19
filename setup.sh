#!/bin/bash
# ---------------------------------------------------------------------------
# Author: John Hammond
# Date: August 19th, 2017

# Description: This is the  setup script for the USCGA Cyber Team Portal.
# It should install dependencies, configure the site, and show the user
# how to deploy.
# ---------------------------------------------------------------------------


DEPENDENCIES="python python-pip git vagrant docker python-markdown \
python-software-properties nodejs linuxbrew-wrapper nginx"


# Ensure you are root!
if [ $UID -ne 0 ]
then
	echo "You must run this script as root!"
	exit
fi

function install_dependencies(){

	# Get nodejs 
	curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash - 
	# Install dependencies...
	sudo apt-get update && sudo apt install -y $DEPENDENCIES

	# Let brew configure itself
	echo "" | brew

	# Have brew install gotty
	brew install yudai/gotty/gotty
	export PATH=$PATH:/home/john/.linuxbrew/bin/
	echo "export PATH=$PATH:/home/john/.linuxbrew/bin/" >> ~/.bashrc

}

install_dependencies