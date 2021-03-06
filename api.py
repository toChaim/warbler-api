from flask import Flask, request
from flask_restful import Resource, Api, fields, marshal
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/warbler'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)

# marshal with fields
user_fields = {
  'user_name': fields.String,
  'warbles': fields.List(fields.Nested({'text': fields.String})),
  'follows': fields.List(fields.Nested({'user_name': fields.String})), 
  'followers': fields.List(fields.Nested({'user_name': fields.String}))
  }

# tables
# users = {'Chaim':{'user_name': 'me'}, 'Sarah':{'user_name': 'you'}}
Favorites= db.Table("favorites",
  db.Column('id', db.Integer, primary_key=True),
  db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade') ),
  db.Column('warble_id', db.Integer, db.ForeignKey('warbles.id', ondelete='cascade'))
  )

Followers= db.Table("followers",
  db.Column('id', db.Integer, primary_key=True),
  db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade') ),
  db.Column('follower_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
)

class User_model (db.Model):
  __tablename__ = "users"

  id = db.Column('id', db.Integer, primary_key=True)
  user_name = db.Column('user_name', db.Text, unique=True )
  password = db.Column('password', db.Text)
  warbles=db.relationship('Warble_model', backref='author')
  follows=db.relationship('User_model', secondary=Followers, primaryjoin=id==Followers.c.follower_id, secondaryjoin=id==Followers.c.user_id)
  followers=db.relationship('User_model', secondary=Followers, primaryjoin=id==Followers.c.user_id, secondaryjoin=id==Followers.c.follower_id)

  def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

  def __repr__(self):
    return "<user:{}>".format(self.user_name)

class Warble_model (db.Model):
  __tablename__ = "warbles"

  id=db.Column('id', db.Integer, primary_key=True)
  text=db.Column('text', db.String(120))
  user_id=db.Column(db.Integer, db.ForeignKey('users.id') )

  def __init__(self, text, user_id):
    self.text = text
    self.user_id = user_id

  def __repr__(self):
    return "<username:{} text:{}>".format(self.author.user_name, self.text)

favorites = {}

# modles
class User(Resource):
  def get(self, user_id):
    return marshal(User_model.query.get(user_id),user_fields)

class Users(Resource):
  def get(self):             
    return marshal(User_model.query.all(), user_fields)

  def post(self):
    data = request.form
    user = User_model(data['user_name'], data['password'])
    db.session.add(user)
    db.session.commit()
    return marshal(user, user_fields)

class Warble(Resource):
  def get(self, user_id):
    return marshal(User_model.query.get(user_id), {'warbles': fields.List(fields.Nested({'text': fields.String}))})

  def post(self, user_id):
    data = request.form
    warble = Warble_model(data['text'], user_id)
    db.session.add(warble)
    db.session.commit()
    return marshal(warble, {'text': fields.String})


class Follow(Resource):
  def post(self, user_id):
    data = request.form
    user = User_model.query.get(user_id)
    user.followers.append(User_model.query.get(data['follower']))
    db.session.add(user)
    db.session.commit()
    return marshal(user, user_fields)

#routes
api.add_resource(User, '/users/<string:user_id>')
api.add_resource(Users, '/users/')
api.add_resource(Follow, '/users/<string:user_id>/followers')
api.add_resource(Warble, '/users/<string:user_id>/warbles')

if __name__ == '__main__':
  app.run(debug=True)