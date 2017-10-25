from api import app,db  
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# connect flask_migrate to our application and SQLAlchemy instance
migrate = Migrate(app, db)

# Initialize the Manager with our application
manager = Manager(app)

# Add a command line command called 'db' which will 
# allow us to use all the built in commands to flask_migrate
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()