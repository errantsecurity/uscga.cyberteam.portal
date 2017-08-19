#!/bin/bash

###########################

sudo apt-get install python-software-properties
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install nodejs
git clone "https://github.com/codemirror/CodeMirror" 


#####################

pip install markdown


########################################
brew install yudai/gotty/gotty

export PATH=$PATH:/home/john/.linuxbrew/bin/
echo "export PATH=$PATH:/home/john/.linuxbrew/bin/" >> ~/.bashrc
