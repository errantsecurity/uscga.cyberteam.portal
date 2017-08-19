#!/usr/bin/env python

import json
from textwrap import dedent
import sys

def error_out( string ):
	print "[!!] JSON ERROR:", string
	exit(-1)

try:
	filename = sys.argv[1]
except:
	error_out( "You must supply a filename!")


handle = open(filename)
contents = handle.read().replace('\t', '').replace('\n', '')

json_object = json.loads(contents)

try:
	assert( json_object.has_key('challenges') )
except:
	error_out( "The JSON file does not have a top-level 'challenges' array!" )
try:
	assert( not False in [ challenge.has_key('possible_answers') for challenge in json_object['challenges'] ] )
except:
	error_out( "Not all challenge objects have a 'possible_answers' array!" )
try:
	assert( not False in [ challenge.has_key('title') for challenge in json_object['challenges'] ] )
except:
	error_out( "Not all challenge objects have a 'title' string!" )
try:
	assert( not False in [ challenge.has_key('points') for challenge in json_object['challenges'] ] )
except:
	error_out( "Not all challenge objects have a 'points' integer value!" )
try:
	assert( not False in [ challenge.has_key('prompt') for challenge in json_object['challenges'] ] )
except:
	error_out( "Not all challenge objects have a 'prompt' string!" )


if json_object.has_key('description'): json_object['app_about'] = json_object['description']
elif json_object.has_key('app_about'): json_object['description'] = json_object['app_about']

if json_object.has_key('name'): json_object['app_title'] = json_object['name']
elif json_object.has_key('app_title'): json_object['name'] = json_object['app_title']

for challenge in json_object['challenges']:
	if challenge.has_key('name'): challenge['title'] = challenge['name']
	elif challenge.has_key('title'): challenge['name'] = challenge['title']


# -------------------------------------

print \
str('''
INSERT INTO training (name, author, category, description,  image )
 VALUES ( %s, %s, %s, %s, %s );
''' % ( repr(str(json_object['name'])),
		repr(str("John Hammond")),
		repr(str("wargame")),
		repr(str(json_object['description'])),
		repr(str(""))
)).replace('\n','')

for challenge in json_object["challenges"]:

	string = str(dedent(\
	'''
	INSERT INTO challenges 
	(name, author, prompt, possible_answers, points, downloadable_files, hint, association)
	 VALUES ( %s, %s, %s, %s, %s, %s, %s, %s );
	''' % ( repr(str(challenge['name'])),
			repr(str("John Hammond")),
			repr(str(challenge['prompt'])).replace("\\'",'&apos;'),
			repr(str("<DELIMETER>".join([ x for x in challenge['possible_answers'] ] ))),
			challenge['points'],
			repr(str("<DELIMETER>".join([ x for x in challenge['downloadable_files'] ] ))) if challenge.has_key('downloadable_files') else repr(""),
			repr(str(challenge['hint'])) if challenge.has_key('hint') else repr(""),
			# repr("")
			"(SELECT id FROM training WHERE name = %s)" % repr(str(json_object['name'])),
	))).replace('\n','')
	print string