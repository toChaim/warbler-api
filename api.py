from flask import Flask, request
from flask_restful import Resource, Api, fields, marshal
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
  warbles=db.relationship('Warble_model', backref='author')

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

Favorites= db.Table("favorites",
  db.Column('id', db.Integer, primary_key=True),
  db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade') ),
  db.Column('warble_id', db.Integer, db.ForeignKey('warbles.id', ondelete='cascade'))
)

Followers= db.Table("followers",
  db.Column('id', db.Integer, primary_key=True),
  db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade') ),
  db.Column('follow_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
)






warbles = {}
favorites = {}

# modles
class User(Resource):
  def get(self, user_id):
    return {user_id: User_model.query.get(user_id)}

class Users(Resource):
  def get(self):
    return User_model.query.all()

  def post(self):
    data = request.form
    user = User_model(data['user_name'], data['password'])
    db.session.add(user)
    db.session.commit()
    resource_fields = {
                    'id': fields.Integer,
                    'password': fields.String,
                    'user_name': fields.String
                }
    #from IPython import embed; embed()
    return marshal(user, resource_fields)

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