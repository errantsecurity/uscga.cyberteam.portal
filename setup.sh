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
	sudo brew install yudai/gotty/gotty
	export PATH=$PATH:/home/john/.linuxbrew/bin/
	echo "export PATH=$PATH:/home/john/.linuxbrew/bin/" >> ~/.bashrc

}


function configure_nginx(){

	sudo /etc/init.d/nginx start
	sudo rm /etc/nginx/sites-enabled/default
	sudo touch /etc/nginx/sites-available/flask-settings
	sudo ln -s /etc/nginx/sites-available/flask-settings \
			   /etc/nginx/sites-enabled/flask-settings

	cat <<EOF > /etc/nginx/sites-enabled/flask_settings
server {
		location / {
				proxy_pass http://127.0.0.1:8000;

				proxy_set_header Host $header;
				proxy_set_header X-Real-IP $remote_addr;
		}
}
EOF

	sudo /etc/init.d/nginx start
}


install_dependencies
configure_nginx