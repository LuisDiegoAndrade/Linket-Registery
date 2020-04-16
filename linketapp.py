from flask import Flask
from flask_socketio import SocketIO, emit, send, join_room,leave_room, disconnect
from flask_sqlalchemy import SQLAlchemy
from flask import request, Response, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from flask_cors import CORS
import jwt
import datetime
import json
import re
from Forms import SignUpForm, LoginForm
from linketvalidator import clean_whitespace, is_allowed

app = Flask(__name__)
CORS(app, resources = r'/api/*')
socketio = SocketIO(app)

#Token generated using python interpreter:
# $ python
# >>> import secrets
# >>> secrets.token_hex(16)
# >>> a65643b9b52d637a11b3182e923e5703
app.config["SECRET_KEY"] = 'f91ed5f95371fd892dadab02fa26c871'

#Using SQLite for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linket.db'

#Flask-Login class helper
#Lets you "decorate" functions/routes
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

###***** Users Table ******###
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(89))
    username = db.Column(db.String(89))
    pwd = db.Column(db.String(128))
    dateJoined = db.Column(db.DateTime, nullable=False,
        default=datetime.datetime.utcnow)

    def check_password(self, userinputPwd):
        return check_password_hash(self.pwd, userinputPwd)

    def get_id(self):
        return self.email

###***** Linkets Table ******###
class Linkets(UserMixin, db.Model):
    __tablename__ = "Linkets"
    id = db.Column(db.Integer, primary_key=True)
    linket = db.Column(db.String(68), nullable=True)
    linketBare = db.Column(db.String(68), nullable=True)
    timeStamp = db.Column(db.DateTime, nullable=False,
        default=datetime.datetime.utcnow)
    appId = db.Column(db.String(32), nullable=True)
    host = db.Column(db.String(16), nullable=True)
    port = db.Column(db.String(16), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    owner = db.relationship('Users', foreign_keys=owner_id)

###***** Users Table ******###

#~~~~~~~~~~
#look for a user in users table via email
@login_manager.user_loader
def load_user(userInputEmail):
    return Users.query.filter_by(email=userInputEmail).first()
#~~~~~~~~~~~

#"root" path; index; home
@app.route('/')
def index():
    return redirect(url_for('register'))


##################~~~Signup~~~####################
@app.route('/signup', methods= ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard_home"))

    form = SignUpForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            flash('Please enter valid credentials!', 'danger')
            return redirect(url_for('register'))


        #Check if username already exists
        #Make password atleast 8 charlong
        #Take to "finish making profile" one time page
        if not Users.query.filter_by(username=request.form['username']).first() and not Users.query.filter_by(email=request.form['email']).first():
            print('Query responded with None.')
            #create a row in DataBases

            newUser = Users(email=request.form['email'],
                           username=request.form['username'],
                           pwd= generate_password_hash(str(request.form['password'])),
                           )

            db.session.add(newUser)
            db.session.commit()
            flash('Thanks for signing up, you will now be able to login!', 'success')
            return redirect(url_for('login'))


        if Users.query.filter_by(username=request.form['username']).first():
            flash('That username is taken! Select another.', 'danger')
            return redirect(url_for('register'))

        if Users.query.filter_by(email=request.form['email']).first():
            flash('That email cannot be used.', 'danger')
            return redirect(url_for('register'))

        return redirect(url_for('register'))

    if request.method == "GET":
        return render_template('signup.html', form=form)
##################~~~Signup END~~~####################


##################~~~Logout ~~~####################
@app.route("/signout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
##################~~~Logout ~~~####################


##################~~~Login ~~~####################
@app.route('/login', methods= ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard_home"))
    form = LoginForm()
    if request.method == "POST":
        if not Users.query.filter_by(email=request.form['email']).first():
            flash('No user with that email!', 'danger')
            return redirect(url_for('login'))

        user = load_user(str(request.form['email']))
        if not user.check_password(request.form['password']):
            flash('Wrong password!', 'danger')
            return redirect(url_for('login'))


        print(type(user))
        login_user(user)
        return redirect(url_for('dashboard_home'))



    return render_template('login.html', form=form)
##################~~~Login END~~~####################

@app.route("/getusername", methods= ['GET', 'POST'])
@login_required
def get_username():
    if request.method == "POST":
        return json.dumps({"username": current_user.username})
    else:
        return redirect(url_for('dashboard_home'))

@app.route("/dashboard")
@login_required
def dashboard_home():
    try:
        myLinkets = Linkets.query.filter_by(owner_id=current_user.id).all()
        print(myLinkets)
    except:
        myLinkets = "You have no Linket(s) registered!"

    return render_template('dashboard.html', myLinkets=myLinkets)



@app.route('/dashboard/registerlinket', methods= ['GET', 'POST'])
@login_required
def register_linket():
    if request.method == "POST":
        if request.form['linket']:
            requestLinket = clean_whitespace(request.form['linket'].lower())
            #print(request.form['linket'])
            check = Linkets.query.filter_by(linketBare=requestLinket).first()

            if (check):
                return json.dumps({'status': 0})

            stripped = clean_whitespace(request.form['linket'])
            if not is_allowed(stripped):
                return json.dumps({'status': 0})

            print(request.form['linket'])
            return json.dumps({'status': 1})
        else:
            return json.dumps({'status': 0})


    if request.method == "GET":
        return render_template('registerlinket.html')

@app.route('/dashboard/confirmlinket', methods= ['GET', 'POST'])
@login_required
def add_new_linket():
    if request.method == "POST":
        if request.form['newlinket']:

            #print(request.form['linket'])
            requestLinket = clean_whitespace(request.form['newlinket'].lower())

            check = Linkets.query.filter_by(linketBare=requestLinket).first()
            print(check)

            if (check):
                return render_template('takenlinket.html')

            stripped = clean_whitespace(request.form['newlinket'])
            if not is_allowed(stripped):
                return json.dumps({'status': 0})

            newLinket = Linkets( linket = clean_whitespace(request.form['newlinket']),
                           linketBare=requestLinket,
                           owner_id=current_user.id
                           )

            db.session.add(newLinket)
            db.session.commit()


            return render_template('successforlinket.html')
        else:
            return redirect(url_for('dashboard_home'))
    return render_template('successforlinket.html')


##########~~~WebRTC: Signaling Implementation~~~###########

''' Store connections in a list for reference. '''
peersList = []

# This might change as the front end evolves
def remove_duplicate_peer(un):
    for user in peersList:
        if user['username'] == un:
            peersList.pop(peersList.index(user))


@socketio.on('New Connection')
def new_connection(data):
    # if somehow an unauthenticated user connects to the WS server, disconnect.
    if not current_user.is_authenticated:
        disconnect()
        return redirect(url_for('login'))

    data = json.loads(data)

    remove_duplicate_peer(current_user.username)

    peersList.append(
        {"username": current_user.username, "sid": request.sid, "status": data['status']}
    )
    print(peersList)


''' Route messages to appropiate peer(s). '''
''' Note that the server doesn't have to know what these messages are.'''
''' We just need to relay it too a specific user. '''

@socketio.on('message')
def handle_msg(data):
    # if somehow an unauthenticated user connects to the WS server, disconnect.
    if not current_user.is_authenticated:
        disconnect()
        return redirect(url_for('login'))

    print("Transporting message!")
    data = json.loads(data)
    # look for target peer in peersList, once found pass
    # peers sid to room argument
    # if not found return an error message
    print(data)

    for user in peersList:
        if user["username"] == data['target']:
            print("Found user!")
            send(json.dumps(data), room=user["sid"])


@app.route("/api/data")
def deep_link():
  data = {'status':200}
  response = app.response_class(
      response=json.dumps(data),
      status=200,
      mimetype='application/json'
  )
  return response

@app.route('/deeplink')
def link():
    html = '''
        <a style="font-size:40px" href="linket://deeplink/startgame?with=LOoe">linket://deeplink/startgame?with=LOoe</a><br>
        <a style="font-size:40px" href="linket://deeplink/startgame?with=LOoe">linket://deeplink/startgame?with=tictactoemaster</a>
    '''
    return html

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port="7777", ssl_context='adhoc')

'''
!!!!references!!!!
re.sub(' +', ' ', 'The     quick brown    fox')
'''