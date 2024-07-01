from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def get_messages():
    
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_list = [message.to_dict() for message in messages]
        return jsonify(messages_list), 200
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return make_response(jsonify({"errors": ["Invalid input"]}), 400)

        body = data.get('body')
        username = data.get('username')

        if body is None or username is None:
            return make_response(jsonify({"errors": ["Price, pizza_id, and restaurant_id are required"]}), 400)
        new_message = Message(
            body=body,
            username = username
            )
        db.session.add(new_message)
        db.session.commit()
        return make_response(jsonify(new_message.to_dict()), 201)
    

@app.route('/messages/<int:id>', methods=['GET', 'PATCH','DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()

    if not message:
        return make_response({"error": "Message not found"}, 404)

    if request.method == 'GET':
        message_dict = message.to_dict()
        return make_response(message_dict, 200)

    elif request.method == 'PATCH':
        try:
            data = request.json
            for attr, value in data.items():
                setattr(message, attr, value)
                
            db.session.add(message)
            db.session.commit()
            
            message_dict = message.to_dict()
            return make_response(message_dict, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

    elif request.method == 'DELETE':
        try:
            db.session.delete(message)
            db.session.commit()
            
            response_body = {
                'delete_successful': True,
                'message': "Message Deleted!"
            }
            return make_response(response_body, 202)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

    

if __name__ == "__main__":
    app.run(port=5555, debug=True)
