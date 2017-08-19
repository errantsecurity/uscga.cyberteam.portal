#!/usr/bin/env python

import flask
import flask_login
import sqlite3
import string
from passlib.hash import sha256_crypt
import markdown
import os
import shutil
import subprocess
import json
from werkzeug.utils import secure_filename
import convert
import socket



DATABASE="database.db"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'json', 'md', 'html'])

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'my super secret'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
login_manager.login_message_category = 'warn'

server_ip

def get_server_ip():
	global server_ip
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	server_ip = s.getsockname()[0]
	s.close()
	return server_ip

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


class User( flask_login.UserMixin ):
	def __init__( self, email ):
		super( flask_login.UserMixin, self ).__init__()
		
		self.email = email

		cursor = flask.g.db.execute('SELECT * FROM users WHERE email = (?)', [self.email])
		db_values = cursor.fetchone()
		
		for i in range(len(cursor.description)):
			db_column = cursor.description[i][0]
			vars(self)[db_column] = db_values[i]
	
		self.vagrant_path = os.path.join(os.getcwd(), 'vagrant' )
		self.vm_path = os.path.join( self.vagrant_path, ( '%s_%d' % ( self.name.replace(' ','_'), self.id )) )
	
	def update_score( self, new_score ):
		cur = flask.g.db.execute("UPDATE users SET score = (?), last_submission = (SELECT strftime('%s')) WHERE id = (?)", [
					new_score, 
					self.id
				] );

		flask.g.db.commit()

	def update_solved_challenges( self, new_solved_challenges ):
		cur = flask.g.db.execute("UPDATE users SET solved_challenges = (?) WHERE id = (?)", [
					new_solved_challenges, 
					self.id
				] );

		flask.g.db.commit()


	def get_id( self ): return self.id
	def is_active( self ): return True
	def is_anonymous( self ): return False
	def is_authenticated( self ): return True

def parse_email_for_name( email ):

	name =  email.split('@')[0].split('.')
	first_name = name[0][0].upper() + name[0][1:]  # I dont use .title() here because it removes the other caps
	last_name = name[-1][0].upper() + name[-1][1:] # I dont use .title() here because it removes the other caps

	for digit in string.digits: 
		first_name = first_name.replace(digit, '')
		last_name = last_name.replace(digit, '')

	name = first_name + " " + last_name
	return name

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def connect_db(): return sqlite3.connect( app.config['DATABASE'] )

@app.before_request
def before_request(): flask.g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(flask.g, 'db', None)
	if db is not None: db.close()


def get_registered_emails():
	cursor = flask.g.db.execute('SELECT email FROM users')
	return [ row[0] for row in cursor.fetchall() ]

def get_email_from_id( id ):
	cursor = flask.g.db.execute('SELECT email FROM users WHERE id = (?)', [id])
	email = cursor.fetchone()
	if email != None: email = email[0]
	return email

def get_user_ids():
	cursor = flask.g.db.execute('SELECT id FROM users')
	return [ row[0] for row in cursor.fetchall() ]

def user_login( email ):

	user = User( email )

	flask.flash("Hello " + user.name.split()[0] + "!", 'success')
	flask_login.login_user(user)

	if not os.path.exists(flask_login.current_user.vm_path): os.makedirs(flask_login.current_user.vm_path)

	# Copy the file if we don't need to do any special provisioning
	shutil.copy( os.getcwd() + '/vagrant/Vagrantfile', flask_login.current_user.vm_path )
	
	turn_on_user_virtual_machine()
	launch_user_virtual_machine()

def turn_on_user_virtual_machine():
	subprocess.Popen( str('gotty -w -p ' + str(8080 + flask_login.current_user.id) + ' vagrant up --provision').split(), cwd = flask_login.current_user.vm_path )

def launch_user_virtual_machine():
	subprocess.Popen( str('gotty -w -p ' + str(8080 + flask_login.current_user.id) + ' vagrant ssh').split(), 
		cwd = flask_login.current_user.vm_path )




@login_manager.user_loader
def user_loader( user_id ):
	# This is passed as a tuple for some reason. 
	if ( user_id in get_user_ids() ):  return User( get_email_from_id(user_id) )
	else:  return


@app.route('/check_answer', methods=["POST"])
def check_answer():
	
	training_id = int(flask.request.referrer.split('/')[-1])
	challenge_id = int(flask.request.form['challenge_id'])	

	global_challenge_id = "%d:%d" % (training_id, challenge_id)

	if global_challenge_id in flask_login.current_user.solved_challenges:
		return json.dumps({'correct': -1});

	cursor = flask.g.db.execute("SELECT possible_answers, points FROM challenges WHERE id = (?)", [challenge_id])
	response = cursor.fetchone()
	if response: response, points = response[0].split('<DELIMETER>'), response[1]
	
	correct_answers = [ answer.lower().lstrip().rstrip() for answer in response ]

	if ( flask.request.form['answer'].lower().lstrip().rstrip() in correct_answers ):
		
		new_score = flask_login.current_user.score + points
		new_solved_challenges = flask_login.current_user.solved_challenges + " " + global_challenge_id
		
		flask_login.current_user.update_score(new_score)
		flask_login.current_user.update_solved_challenges(new_solved_challenges)

		return json.dumps({'correct': 1, 'new_score': new_score});
	else:
		return json.dumps({'correct': 0});


@app.route('/register', methods=['GET', 'POST'])
def register():

	email = password = confirm = ""
	
	if ( flask.request.method == "POST" ):

		# Grab the variables sent by the form POST...
		email = flask.request.form['email']
		password = flask.request.form['password']
		confirm = flask.request.form['confirm']

		# Get the users that already exist in the database...
		registered_emails = get_registered_emails()

		# Start to errorcheck.
		if email == "": flask.flash("You must supply an email address!", "error")
		elif unicode(email) in registered_emails: flask.flash("This e-mail address is already registered!", "error")
		elif (not email.endswith('@uscga.edu')): flask.flash('You must use a @uscga.edu domain e-mail address!', "error")
		elif password == "": flask.flash("You must supply a password!", "error")
		elif password != confirm: flask.flash("Your passwords do not match!", "error")

		# If they pass all the error tests, go ahead and register them!
		if not flask.get_flashed_messages():
			
			name = parse_email_for_name(email)
			cursor = flask.g.db.execute('INSERT INTO users \
			(email, password, name, solved_challenges, last_submission, score) values \
			( ?,    ?,        ?,         ?,            ?,               ? )', [ 

				email, 
				sha256_crypt.encrypt( password ),
				name,
				"", # No challenges solved
				0,  # No last submission time
				0,  # No current score
			] )

			flask.g.db.commit()
			# And log in the user.
			user_login(email)

			return flask.redirect('/')
	
	# As a catch-all, just return the page as necessary.
	return flask.render_template( "register.html", email=email, confirm=confirm, password=password )


# -------------------------------------------------------------------------------------
#
# These three functions are all the same. Can we clean them up a little bit??
#  

@app.route('/training/<category>')
@flask_login.login_required
def trainings( category ): 
	cursor = flask.g.db.execute("SELECT name, id, author, image FROM training WHERE category = (?)", [category])
	response = cursor.fetchall()
	trainings = [ { "name": row[0], "id" : row[1], "author": row[2], "image": row[3] } for row in response ]


	if category == "homemade": template = "homemade.html"
	elif category == "ctf": template = "ctfs.html"
	elif category == "wargame": template = "wargames.html"
	else:

		flask.flash( "There are no trainings that match this category!", 'error' )
		return flask.redirect( flask.url_for('trainings', category = 'wargame' ) )

	return flask.render_template( template, trainings = trainings )


@app.route('/challenges')
@flask_login.login_required
def challenges(): 
	cursor = flask.g.db.execute("SELECT name, id, author, image FROM training WHERE category = 'homemade'")
	response = cursor.fetchall()
	trainings = [ { "name": row[0], "id" : row[1], "author": row[2], "image": row[3] } for row in response ]

	return flask.render_template('homemade.html', trainings = trainings)

@app.route('/wargames')
@flask_login.login_required
def wargames(): 
	cursor = flask.g.db.execute("SELECT name, id, author, image FROM training WHERE category = 'wargame'")
	response = cursor.fetchall()
	trainings = [ { "name": row[0], "id" : row[1], "author" : row[2], "image": row[3] } for row in response ]

	return flask.render_template('wargames.html', trainings = trainings)

@app.route('/ctfs')
@flask_login.login_required
def ctfs(): 
	cursor = flask.g.db.execute("SELECT name, id, author, image FROM training WHERE category = 'ctf'")
	response = cursor.fetchall()
	trainings = [ { "name": row[0], "id" : row[1], "author": row[2], "image": row[3] } for row in response ]

	return flask.render_template('ctfs.html', trainings = trainings)

#
# -------------------------------------------------------------------------------------

@app.route('/training/<int:training_id>')
@flask_login.login_required
def training( training_id ): 

	global skeleton

	cursor = flask.g.db.execute("SELECT name, description, image, author FROM training WHERE id = (?)", [training_id])
	response = cursor.fetchone()
	if response: name, description, image, author = response
	else: 
		flask.flash("There is no training associated with this ID number!", "error")
		return flask.redirect( flask.request.referrer )

	cursor = flask.g.db.execute("SELECT name, author, prompt, points, downloadable_files, id FROM challenges WHERE association = (?)", [training_id])
	response = cursor.fetchall()
	challenges = [ { "name": row[0], "author" : row[1], "prompt" : row[2], "points": row[3], "downloadable_files": row[4], "id": row[5] } for row in response ]
	for challenge in challenges:
		challenge['downloadable_files'] = [ x for x in challenge['downloadable_files'].split('<DELIMETER>') if x ]


	return flask.render_template('training.html', name = name, url = "", description = description, challenges = challenges, training_id = training_id, author = author )






@app.route('/users/<int:user_id>')
def specific_user(user_id): 

	email = get_email_from_id(user_id)
	if ( email ):
		user = User(email)

		cursor = flask.g.db.execute("SELECT name, id, association FROM writeups WHERE author = (?)",
			[ user.name ])
		response = cursor.fetchall()
		if response:
			writeups = [ { 'name': row[0], "id": row[1], "association": row[2]} for row in response ]
		else:
			writeups = None

		seen_trainings = {}
		challenges = user.solved_challenges.split()
		for challenge in challenges:
			training_id, challenge_id = [ int(x) for x in challenge.split(":") ]
			if training_id not in seen_trainings:
				
				cursor = flask.g.db.execute("SELECT name FROM training WHERE id = (?)",
					[ training_id ])
				response = cursor.fetchone()
				if response:
					seen_trainings[training_id] = {'name': response[0]} 
			
					cursor = flask.g.db.execute("SELECT name, id, points FROM challenges WHERE association = (?)",
						[ training_id ])
					response = cursor.fetchall()
					challenges = [ { "name": row[0], "id" : row[1], "points" : row[2] } for row in response ]
					seen_trainings[training_id]['challenges'] = challenges

			for challenge in seen_trainings[training_id]['challenges']:
				if challenge['id'] == challenge_id:
					challenge['completed'] = True

		return flask.render_template('specific_user.html', user=user, writeups = writeups, seen_trainings = seen_trainings)
	else:
		flask.flash("Sorry, that user does not exist!", "error")
		return flask.redirect( flask.request.referrer )



@app.route('/users')
@flask_login.login_required
def users(): 

	cursor = flask.g.db.execute('SELECT name, score, id FROM users ORDER BY score DESC, last_submission ASC')
	response = cursor.fetchall()
	
	users = [ { "name": row[0], "score": row[1], "id": row[2] } for row in response]

	return flask.render_template('users.html', users = users)


@app.route('/writeups/<int:writeup_id>')
@flask_login.login_required
def specific_writeup(writeup_id):
	cursor = flask.g.db.execute("SELECT name, author, body FROM writeups WHERE id = (?)", [writeup_id])
	response = cursor.fetchone()

	if response: name, author, writeup_content = response
	else: writeup_content = '<h1 style="color:red"> Error: There is no writeup with this ID. </h1>' 
	
	writeup_content = markdown.markdown(writeup_content)

	return flask.render_template('specific_writeup.html', writeup_content = writeup_content, author = author, writeup_id = writeup_id, name=name)


def create_new_writeup( name, author, association, body ):

	flask.g.db.execute("INSERT INTO writeups (name, author, association, body) VALUES \
											 (?,     ?,      ?,           ?)",
											  [ name, author, association, body] ) 

	flask.g.db.commit()

	cursor = flask.g.db.execute("SELECT id FROM writeups ORDER BY id DESC LIMIT 1")
	writeup_id = cursor.fetchone()
	if writeup_id: writeup_id = writeup_id[0]
	else: flask.flash("Writeup not found!", "error")

	return writeup_id


def create_new_training( name, author, category, description, image ):

	flask.g.db.execute("INSERT INTO training (name, author, category, description, image) VALUES \
											 (?,     ?,      ?,           ?,		?)",
											  [ name, author, category, description, image] ) 

	flask.g.db.commit()

	cursor = flask.g.db.execute("SELECT id FROM training ORDER BY id DESC LIMIT 1")
	training_id = cursor.fetchone()
	if training_id: training_id = training_id[0]
	else: flask.flash("Training not found!", "error")

	return training_id

@app.route('/writeups/new/' )
@flask_login.login_required
def new_writeup(  ):

	writeup_id = create_new_writeup( "", flask_login.current_user.name, "No Association Selected", "" )
	return flask.redirect( flask.url_for( 'edit_writeup', writeup_id = writeup_id ) )

@app.route('/training/new_json', methods = ["GET", "POST"])
@flask_login.login_required
def new_json_training():


	if flask.request.method == "GET":
		return flask.render_template('new_json_training.html')	

	if flask.request.method == "POST":
		
		category = flask.request.form['category']
		if ( category == "" ):
			flask.flash("You must select a category for the training!", "error")
			return flask.render_template('new_json_training.html')

		file = flask.request.files['image']
		filename = secure_filename( file.filename )
		if filename != '':
			save_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(save_location)
			image = flask.url_for('uploaded_file', filename = filename)

		file = flask.request.files['json_configuration']
		if ( not file ):
			flask.flash('You need to supply a JSON configuration file for this training!')
			return flask.render_template('new_json_training.html')
		else:

			filename = secure_filename( file.filename )
			if filename != '':
				save_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
				file.save(save_location)
				json_configuration = flask.url_for('uploaded_file', filename = filename)
		
			output = convert.json_to_sql( save_location, author = "John Hammond " + flask_login.current_user.name, category = category )
			if '[!!] JSON ERROR' in output:
				flask.flash("Your JSON config file had an error!", "error")
				return flask.render_template('new_json_training.html', errors = output)
			else:
				
				for line in output.split('\n'):
					cursor = flask.g.db.execute(line)
					flask.g.db.commit()
				
				flask.flash("Training successfully added!", 'success')
				return flask.redirect( flask.url_for( 'trainings', category = 'homemade') )




@app.route('/training/new/<category>' )
@flask_login.login_required
def new_training( category ):

	training_id = create_new_training( "", flask_login.current_user.name, category, "", "" )
	return flask.redirect( flask.url_for( 'edit_training', training_id = training_id ) )

@app.route('/writeups/delete/<int:writeup_id>' )
def delete_writeup( writeup_id ):

	cursor = flask.g.db.execute("SELECT author FROM writeups WHERE id = (?)", [writeup_id])
	response = cursor.fetchone()

	if response:
		author = response[0]

		if ( flask_login.current_user.name in author ):
			flask.flash("Writeup deleted!", 'success');
			flask.g.db.execute("DELETE FROM writeups WHERE id = (?)", [writeup_id])
			flask.g.db.commit()
		else:
			
			flask.flash("You are not the author of this writeup!", 'error')
	else:
		flask.flash("Writeup not found!", 'error')

	return  flask.redirect(flask.url_for('writeups'))

@app.route('/training/delete/<int:training_id>' )
def delete_training( training_id ):

	cursor = flask.g.db.execute("SELECT author FROM training WHERE id = (?)", [training_id])
	response = cursor.fetchone()

	if response:
		author = response[0]

		if ( flask_login.current_user.name in author ):
			flask.flash("Training deleted!", 'success');
			flask.g.db.execute("DELETE FROM training WHERE id = (?)", [training_id])
			flask.g.db.commit()
		else:
			
			flask.flash("You are not the author of this training!", 'error')
	else:
		flask.flash("Training not found!", 'error')

	return  flask.redirect(flask.request.referrer)


@app.route('/challenge/delete/<int:challenge_id>' )
def delete_challenge( challenge_id ):

	cursor = flask.g.db.execute("SELECT author FROM challenges WHERE id = (?)", [challenge_id])
	response = cursor.fetchone()

	if response:
		author = response[0]

		if ( flask_login.current_user.name in author ):
			flask.flash("Challenge deleted!", 'success');
			flask.g.db.execute("DELETE FROM challenges WHERE id = (?)", [ challenge_id ])
			flask.g.db.commit()
		else:
			
			flask.flash("You are not the author of this challenge!", 'error')
	else:
		flask.flash("Challenge not found!", 'error')

	return  flask.redirect(flask.request.referrer)

@app.route('/writeups/edit/<int:writeup_id>', methods = [ "GET", "POST" ])
@flask_login.login_required
def edit_writeup(writeup_id):


	cursor = flask.g.db.execute('SELECT name, author, association, body FROM writeups WHERE id = (?)', [ writeup_id] )
	response =  cursor.fetchone()
	if response == None: 
		flask.flash("Writeup not found!", "error")
		return flask.redirect(flask.url_for('specific_writeup', id = writeup_id))
	else:
		name, author, association, content = response

	if ( flask_login.current_user.name not in author  ):
		flask.flash("You are not the author of this writeup, you cannot edit it!", 'error')
		return flask.redirect( flask.url_for( 'writeups') )

	if ( flask.request.method == "POST" ):

		# Retrieve the passed values...
		name = flask.request.form['name']
		association = flask.request.form['association']
		content = flask.request.form['content']
		html_content = markdown.markdown(content)

		# Error check...
		if ( name == "" ): 
			flask.flash("You must supply a name for this writeup!", "error")
		elif ( content == "" ):
			flask.flash("You must enter some content for the writeup!", "error")
		elif ( association == "" ):
			flask.flash("You must select an association for this writeup!", "error")
		else:

		# Process the input...
			flask.flash("Writeup saved!", "success")
			cursor = flask.g.db.execute('UPDATE writeups SET name = (?), association = (?), body = (?) WHERE id = (?)', 
				[ name, association, content, writeup_id ])

			flask.g.db.commit()

	cursor = flask.g.db.execute("SELECT name FROM training")
	response = cursor.fetchall()
	possible_associations = [ { "name": row[0] } for row in response ]

	return flask.render_template('edit_writeup.html', possible_associations = possible_associations, name = name, association = association, content = content, writeup_id = writeup_id )

@app.route('/challenge/edit/<int:challenge_id>', methods = [ "GET", "POST" ])
@flask_login.login_required
def edit_challenge(challenge_id):

	cursor = flask.g.db.execute('SELECT name, association, author, prompt, possible_answers, points, hint FROM challenges WHERE id = (?)', [ challenge_id ] )
	response =  cursor.fetchone()
	if response == None: 
		flask.flash("Challenge not found!", "error")
		return flask.redirect( flask.request.referrer )
	else:
		name, association, author, prompt, possible_answers, points, hint = response
		possible_answers = possible_answers.replace('<DELIMETER>', ', ')

	if ( flask_login.current_user.name not in author ):
		flask.flash("You are not the author of this challenge, you cannot edit it!", 'error')
		return flask.redirect( flask.request.referrer )

	if ( flask.request.method == "POST" ):

		name = flask.request.form['name']
		prompt = flask.request.form['prompt']
		possible_answers = flask.request.form['possible_answers']
		points = flask.request.form['points']
		hint = flask.request.form['hint']
		
		# possible_answers = possible_answers.replace(',',"<DELIMETER>")
		possible_answers = "<DELIMETER>".join([ x.strip() for x in possible_answers.split(',') ])

		if ( name == "" ): 
			flask.flash("You must supply a name for this challenge!", "error")
		if ( possible_answers == "" ): 
			flask.flash("You must supply a flag for this challenge!", "error")
		if ( points == "" ): 
			flask.flash("You must supply a point value for this challenge!", "error")
		else:
		
			flask.flash("Challenge saved!", "success")
			cursor = flask.g.db.execute('UPDATE challenges SET name = (?), prompt = (?), possible_answers = (?), points = (?), hint = (?) WHERE id = (?)', 
				[ name, prompt, possible_answers, points, hint, challenge_id ])
			flask.g.db.commit()

	return flask.render_template('edit_challenge.html', challenge_id = challenge_id, name = name, prompt = prompt, possible_answers = possible_answers, points = points, hint = hint, training_id = association )



@app.route('/training/edit/<int:training_id>', methods = [ "GET", "POST" ])
@flask_login.login_required
def edit_training(training_id):

	cursor = flask.g.db.execute('SELECT name, category, description, author, image FROM training WHERE id = (?)', [ training_id] )
	response =  cursor.fetchone()
	if response == None: 
		flask.flash("Training not found!", "error")
		return flask.redirect( flask.request.referrer )
	else:
		name, category, description, author, image = response

	if ( flask_login.current_user.name not in author ):
		flask.flash("You are not the author of this training, you cannot edit it!", 'error')
		return flask.redirect( flask.request.referrer )

	if ( flask.request.method == "POST" ):

		name = flask.request.form['name']
		category = flask.request.form['category']
		description = flask.request.form['description']
	

		if ( name == "" ): 
			flask.flash("You must supply a name for this training!", "error")
		elif ( category == "" ):
			flask.flash("You must select a category for the training!", "error")
		else:
		
			file = flask.request.files['image']
			filename = secure_filename( file.filename )
			if filename != '':
				save_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
				file.save(save_location)
				image = flask.url_for('uploaded_file', filename = filename)

			if category == "ctf":
				description = markdown.markdown(description)

			flask.flash("Training saved!", "success")
			cursor = flask.g.db.execute('UPDATE training SET name = (?), category = (?), description = (?), image = (?) WHERE id = (?)', 
				[ name, category, description, image, training_id ])
			flask.g.db.commit()

	return flask.render_template('edit_training.html', training_id = training_id, name = name, category = category, description = description, image = image )


@app.route('/writeups')
@flask_login.login_required
def writeups():

	cursor = flask.g.db.execute("SELECT name, author, association, id FROM writeups ORDER BY id DESC")
	response = cursor.fetchall()
	writeups = [ { "name": row[0], "author": row[1], "association": row[2], "id": row[3] } for row in response ]

	return flask.render_template('writeups.html', writeups = writeups)




@app.route('/shell')
@flask_login.login_required
def shell(): 

	turn_on_user_virtual_machine()
	launch_user_virtual_machine()

	return flask.render_template('shell.html', server_ip=server_ip, port=str(8080+flask_login.current_user.id))

@app.route('/login', methods=['GET', 'POST'])
def login():

	email = password = ""
	
	if ( flask.request.method == 'POST' ):

		# Grab the variables from the form
		email = flask.request.form['email']
		password = flask.request.form['password']
	
		if ( email == "" or password == "" ): 
			flask.flash("You must supply all fields!", "error")
			return flask.render_template( 'login.html', email = email, password = password)

		# Get the usernames and passwords from the database.
		cursor = flask.g.db.execute('SELECT email, password FROM users')
		users = dict(( row[0], row[1] ) for row in cursor.fetchall())
		
		# Error check.
		if ( email not in users.iterkeys() ): flask.flash("This username is not in the database!", "error")
		if not ( sha256_crypt.verify( flask.request.form['password'], users[flask.request.form['email']] ) ):
				flask.flash("Incorrect password!",'error')
		else:
			# If they passed all the checks, log them in!
			if not flask.get_flashed_messages():
				
				user_login(email)

				return flask.redirect('/')

	return flask.render_template( 'login.html', email = email, password = password)

@app.route('/logout')
@flask_login.login_required
def logout():
	flask_login.logout_user()
	flask.flash("You have been logged out.", "success")

	return flask.redirect(flask.url_for('login'))

@app.route('/')
def index(): 
	return flask.render_template( "index.html" )

if ( __name__ == "__main__" ):

	subprocess.call( 'pkill gotty'.split() )
	app.run( debug=True, host='0.0.0.0' )