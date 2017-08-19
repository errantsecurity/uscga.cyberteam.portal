#!/bin/bash

cd $1
vagrant up --provision 
vagrant ssh