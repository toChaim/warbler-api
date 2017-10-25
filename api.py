from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/warbler'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)

# tables
# users = {'Chaim':{'user_name': 'me'}, 'Sarah':{'user_name': 'you'}}
class User_model (db.Model):
  __tablename__ = "users"

  id = db.Column('id', db.Integer, primary_key=True)
  user_name = db.Column('user_name', db.Text, unique=True )
  password = db.Column('password', db.Text)

  def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

  def __repr__(self):
    return "<{user_name}>".format(self.user_name)

warbles = {}
favorites = {}

# modles
class User(Resource):
  def get(self, user_id):
    return {user_id: User_model.query.get(user_id)}

class Users(Resource):
  def get(self):
    return User_model.query.all()

  def put(self, user_id):
    from IPython import embed; embed()
    data = request.form['data']
    user = User_model(data.user_name, data.password)
    db.session.add(user)
    db.session.commit()
    # users[user_id] = request.form['data']
    return user

class Warble(Resource):
  def get(self, warble_id):
    return {warble_id: warbles[warble_id]}

  def put(self, warble_id):
    warbles[warble_id] = request.form['data']

#routes
api.add_resource(User, '/users/<string:user_id>')
api.add_resource(Users, '/users/')

if __name__ == '__main__':
  app.run(debug=True)