# from flask import Flask, request, jsonify, render_template, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
# import datetime
# import os
# from functools import wraps

# app = Flask(__name__)
# app.config['SECRET_KEY'] = '9231c9496752f3887965250eeda37e544232680d0b23a760b8caa8d9112d9618'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:post12345@localhost:5432/farqad_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # User model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

#     def __repr__(self):
#         return f'<User {self.username}>'

# # Create tables
# with app.app_context():
#     db.create_all()

# # JWT token functions
# def create_token(user_id, username):
#     payload = {
#         'user_id': user_id,
#         'username': username,
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
#     }
#     return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         if 'Authorization' in request.headers:
#             token = request.headers['Authorization'].split(' ')[1]
        
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401
        
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#             current_user = User.query.get(data['user_id'])
#         except:
#             return jsonify({'message': 'Token is invalid'}), 401
        
#         return f(current_user, *args, **kwargs)
    
#     return decorated

# # Routes
# @app.route('/')
# def index():
#     return render_template('main.html')

# @app.route('/login')
# def login_page():
#     return render_template('login.html')

# @app.route('/register')
# def register_page():
#     return render_template('register.html')

# @app.route('/chat')
# def chat_page():
#     return render_template('chatpage.html')

# # API endpoints
# @app.route('/api/register', methods=['POST'])
# def register():
#     data = request.get_json()
    
#     # Check if user already exists
#     if User.query.filter_by(username=data['username']).first():
#         return jsonify({'message': 'Username already exists'}), 400
    
#     if User.query.filter_by(email=data['email']).first():
#         return jsonify({'message': 'Email already exists'}), 400
    
#     # Create new user
#     hashed_password = generate_password_hash(data['password'])
#     new_user = User(
#         username=data['username'],
#         email=data['email'],
#         password=hashed_password
#     )
    
#     db.session.add(new_user)
#     db.session.commit()
    
#     return jsonify({'message': 'User created successfully'}), 201

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.get_json()
    
#     # Find user by email
#     user = User.query.filter_by(email=data['email']).first()
    
#     if not user or not check_password_hash(user.password, data['password']):
#         return jsonify({'message': 'Invalid email or password'}), 401
    
#     # Create token
#     token = create_token(user.id, user.username)
    
#     return jsonify({
#         'token': token,
#         'username': user.username
#     }), 200

# @app.route('/api/user', methods=['GET'])
# @token_required
# def get_user(current_user):
#     return jsonify({
#         'id': current_user.id,
#         'username': current_user.username,
#         'email': current_user.email
#     }), 200

# if __name__ == '__main__':
#     app.run(debug=True) 