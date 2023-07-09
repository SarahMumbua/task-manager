from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import User, Task, Category, db
from flask_jwt_extended import JWTManager
from config import Config
from flask_cors import CORS

app = Flask(__name__)
#configure database connection : type of database management,user,password,host,database_name
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/recipe_db'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://taskmanagerdatabase_vbg5_user:OFZql5CvO1dZ95N9ME9waqC3DNTHoP4F@dpg-cilc1p95rnuvtgrja2c0-a.oregon-postgres.render.com/taskmanagerdatabase_vbg5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config.from_object(Config)
#allow Cross Origin Resource Sharing
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)
#jwt is for login. generate token
jwt = JWTManager(app)
from .routes import route
app.register_blueprint(route)