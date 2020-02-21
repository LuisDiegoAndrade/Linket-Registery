from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask_cors import CORS
import jwt
import datetime
import json

app = Flask(__name__)
CORS(app, resources = r'/api/*')

#Token generated using python interpreter:
# $ python
# >>> import secrets
# >>> secrets.token_hex(16)
# >>> a65643b9b52d637a11b3182e923e5703
app.config["SECRET_KEY"] = 'f91ed5f95371fd892dadab02fa26c871'

#Using SQLite for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linket.db'

db = SQLAlchemy(app)
###***** Users Table ******###
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    # FIXME: Still working on database scheme (e.g how many tables)

    # For now This Users table will be used to store the following columns:
    # username (String)
    # Full name (String)
    # Email (String)
    # password (String)
    # is artist (int 1 for true 0 for false)
    # is artist (int 1 for true 0 for false)
    username = db.Column(db.String(89))
    fullname = db.Column(db.String(89))
    email = db.Column(db.String(89))
    pwd = db.Column(db.String(128))
    isArtist = db.Column(db.String(2))
    isProducer = db.Column(db.String(2))

    def check_password(self, userinputPwd):
        return check_password_hash(self.pwd, userinputPwd)

    def get_id(self):
        return self.email
###***** Users Table ******###



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
    app.run(host="0.0.0.0", port="7777")
