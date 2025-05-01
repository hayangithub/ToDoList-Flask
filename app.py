from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import datetime

app = Flask(__name__)

# MySQL config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flaskuser:flaskpass@localhost/flask_todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '9a3c9f70f9f83a68a1e5e20cd56bd118e6ec292b70ae8a54310a0f5345c418bc'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Model
class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username != 'testuser' or password != 'testpassword':
        return jsonify({"msg": "Bad credentials"}), 401
    token = create_access_token(identity=username)
    return jsonify(access_token=token)

@app.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([{"id": t.id, "task": t.task, "completed": t.completed} for t in todos])

@app.route('/todos', methods=['POST'])
@jwt_required()
def add_todo():
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({"msg": "Task required"}), 400
    todo = TodoItem(task=task)
    db.session.add(todo)
    db.session.commit()
    return jsonify({"msg": "To-Do created", "id": todo.id}), 201

@app.route('/todos/<int:id>', methods=['PUT'])
@jwt_required()
def update_todo(id):
    data = request.get_json()
    todo = TodoItem.query.get(id)
    if not todo:
        return jsonify({"msg": "Not found"}), 404
    todo.task = data.get('task', todo.task)
    todo.completed = data.get('completed', todo.completed)
    db.session.commit()
    return jsonify({"msg": "Updated"})

@app.route('/todos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_todo(id):
    todo = TodoItem.query.get(id)
    if not todo:
        return jsonify({"msg": "Not found"}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"msg": "Deleted"})

if __name__ == '__main__':
    app.run(debug=True)
