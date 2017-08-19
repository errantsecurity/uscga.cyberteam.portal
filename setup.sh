#!/bin/bash

# Author: John Hammond
# Date: August 19th, 2017

# Description: This is the  setup script for the USCGA Cyber Team Portal.
# It should install dependencies, configure the site, and show the user
# how to deploy.

DEPENDENCIES="python python-pip git vagrant docker python-markdown"

if [ $UID -ne 0 ]
then
	echo "You must run this script as root!"
	exit
fi

sudo apt-get update && sudo apt-get -y $DEPENDENCIES

