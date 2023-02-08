from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
#from dotenv import load_dotenv
#import os
from decouple import config
from sqlalchemy import create_engine
from flask_swagger_ui import get_swaggerui_blueprint

# print(config('USER'))

#load_dotenv()  # take environment variables from .env.

#user=os.getenv('USER')
#print(user)

host = config('HOST')
user = config('USER')
password = config('PASSWORD')
mysqldb = config('DB')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=f'mysql+pymysql://{user}:{password}@{host}/{mysqldb}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False #Configuración por defecto para que no haya un WARNING cuando se ejecute el programa

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), unique=True)
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description

with app.app_context():
    db.create_all()

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

REQUEST_API = Blueprint('request_api', __name__)

def get_blueprint():
    """Return the blueprint for the main app module"""
    return REQUEST_API

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "flask-sqlalchemy-mysql"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(get_blueprint())

@app.route('/', methods=['GET'])
def get_hello():
    return 'Hello Flask'

@app.route('/tasks', methods=['POST'])
def create_task():
    # print(request.json)
    # return 'received'

    title = request.json['title']
    description = request.json['description']

    new_task = Task(title, description)
    db.session.add(new_task)
    db.session.commit()

    return task_schema.jsonify(new_task)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)

@app.route('/tasks/<id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    return task_schema.jsonify(task)

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    
    title = request.json['title']
    description = request.json['description']

    task.title = title
    task.description = description

    db.session.commit()
    return task_schema.jsonify(task)

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)

if __name__ == "__main__":
    app.run(debug=True) #con debug=True reinicia cada vez que se hace un cambio
