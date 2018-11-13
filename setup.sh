#!/bin/bash
# ---------------------------------------------------------------------------
# Author: John Hammond
# Date: August 19th, 2017

# Description: This is the  setup script for the USCGA Cyber Team Portal.
# It should install dependencies, configure the site, and show the user
# how to deploy.
# ---------------------------------------------------------------------------


DEPENDENCIES="python python-pip git vagrant docker python-markdown \
python-software-properties nodejs linuxbrew-wrapper nginx python-flask \
gunicorn python-passlib virtualbox-qt docker.io"


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
	apt-get update && sudo apt install -y $DEPENDENCIES

	# Get flask login...
	pip install flask_login

	# Let brew configure itself
	# echo "" | brew

	# # Have brew install gotty
	# su `logname` -c "brew install yudai/gotty/gotty"
	# export PATH=$PATH:$HOME/.linuxbrew/bin/
	# echo "export PATH=$PATH:$HOME/.linuxbrew/bin/" >> ~/.bashrc
	
}

function build_training_wheels(){

	echo "training wheels"
}


function configure_nginx(){

	# sudo rm -f /etc/nginx/sites-enabled/default
	sudo touch /etc/nginx/sites-available/flask-settings
	sudo ln -f -s /etc/nginx/sites-available/flask-settings \
			   /etc/nginx/sites-enabled/flask-settings

	cat <<EOF>/etc/nginx/sites-enabled/flask-settings
server {
		location / {
				proxy_pass http://127.0.0.1:8000;
		}
}
EOF

	sudo service nginx restart
}


# function configure_docker(){

# 	# Add ourselves to the Docker group. We have to log back in and out
# 	# to ensure we are running with the correct credentials..
# 	usermod -aG docker `logname`
# 	cd training_wheels

# 	docker build -t training_wheels .

# 	cd ..


# }

# function configure_gotty(){
# 	cat <<EOF > ~/.gotty
# preferences {
#     font_size = 14
# }
# EOF

# }

# function prepare_gunicorn(){

# 	cat <<EOF > /etc/init/the_portal.conf
# description "Gunicorn Flask server running the USCGA Cyber Team Portal."

# start on runlevel [2345]
# stop on runlevel [!2345]

# respawn
# setuid user
# setgid www-data

# env PATH=/home/cyberteam/portal/
# chdir /home/cyberteam/portal
# exec gunicorn server:app
# EOF

# 	# Make sure to run the app as a regular user. We shouldn't have to be
# 	# root...
# 	su `logname` -c "gunicorn server:app &"
# }

install_dependencies
configure_nginx
# configure_gotty
# configure_docker
# prepare_gunicorn