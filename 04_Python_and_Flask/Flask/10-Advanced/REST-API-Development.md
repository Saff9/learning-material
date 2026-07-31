---
title: REST API Development
description: Building production REST APIs with Flask — design patterns, authentication, versioning, and documentation
chapter: 10-Advanced
tags:
  - rest-api
  - api-design
  - json
  - authentication
  - flask
difficulty: Advanced
prerequisites:
  - [[00-Foundations/REST-APIs]]
  - [[01-Flask-Core/Request-Response]]
  - [[03-Database/SQLAlchemy-ORM]]
---

# REST API Development

> Building a REST API is one of the most common uses of Flask. Whether you are serving a single-page application, a mobile app, or third-party integrations, a well-designed API is critical. This chapter covers the complete process of building production-grade REST APIs with Flask.

## Learning Objectives

After completing this chapter, you will be able to:

- Design RESTful API endpoints following industry conventions
- Implement CRUD operations with proper HTTP status codes
- Add authentication and authorization to API endpoints
- Version your API to maintain backward compatibility
- Document your API with OpenAPI/Swagger
- Handle errors consistently across all endpoints
- Implement pagination, filtering, and sorting

## API Design Principles

### Resource-Based URLs

```
GET    /users              # List all users
POST   /users              # Create a new user
GET    /users/123          # Get user 123
PUT    /users/123          # Update user 123 (full)
PATCH  /users/123          # Update user 123 (partial)
DELETE /users/123          # Delete user 123
GET    /users/123/posts    # Get posts by user 123
```

### Consistent Response Format

```python
def success_response(data, status_code=200):
    return jsonify({
        'success': True,
        'data': data
    }), status_code

def error_response(message, status_code=400, errors=None):
    response = {
        'success': False,
        'error': {
            'message': message,
            'code': status_code
        }
    }
    if errors:
        response['error']['details'] = errors
    return jsonify(response), status_code
```

## Flask-RESTful

Flask-RESTful is an extension for quickly building REST APIs:

```python
from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal_with

app = Flask(__name__)
api = Api(app, prefix='/api/v1')

# Request parser
user_parser = reqparse.RequestParser()
user_parser.add_argument('username', required=True, help='Username is required')
user_parser.add_argument('email', required=True, help='Email is required')

# Response fields
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'uri': fields.Url('userresource')
}

class UserList(Resource):
    @marshal_with(user_fields)
    def get(self):
        return User.query.all()
    
    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        return user, 201

class UserResource(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user
    
    @marshal_with(user_fields)
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        args = user_parser.parse_args()
        for key, value in args.items():
            setattr(user, key, value)
        db.session.commit()
        return user
    
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

api.add_resource(UserList, '/users')
api.add_resource(UserResource, '/users/<int:user_id>', endpoint='userresource')
```

## API Authentication

### API Keys

```python
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        key = APIKey.query.filter_by(key=api_key, is_active=True).first()
        if not key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        request.api_key = key
        return f(*args, **kwargs)
    return decorated

@app.route('/api/data')
@require_api_key
def get_data():
    return jsonify({'data': 'secret data'})
```

### Token Authentication (see [[10-Advanced/JWT-Authentication]])

## API Versioning

### URL Versioning (Recommended)

```python
from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

@api_v1.route('/users')
def get_users_v1():
    return jsonify({'version': '1.0', 'users': [...]})

@api_v2.route('/users')
def get_users_v2():
    return jsonify({'version': '2.0', 'users': [...], 'meta': {...}})

app.register_blueprint(api_v1)
app.register_blueprint(api_v2)
```

## Pagination

```python
from flask import request, url_for

def paginate(query, schema, per_page_default=20):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', per_page_default, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'data': schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'next_url': url_for(request.endpoint, page=pagination.next_num, 
                               per_page=per_page, _external=True) if pagination.has_next else None,
            'prev_url': url_for(request.endpoint, page=pagination.prev_num,
                               per_page=per_page, _external=True) if pagination.has_prev else None
        }
    })
```

## API Documentation with Flask-RESTX

```python
from flask_restx import Api, Resource, fields

api = Api(app, version='1.0', title='My API',
          description='A production Flask API',
          doc='/docs/')

ns = api.namespace('users', description='User operations')

user_model = api.model('User', {
    'id': fields.Integer(readonly=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'created_at': fields.DateTime(readonly=True),
})

@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    def get(self):
        return User.query.all()
    
    @ns.doc('create_user')
    @ns.expect(user_model)
    @ns.marshal_with(user_model, code=201)
    def post(self):
        new_user = User(**api.payload)
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201
```

## Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/data')
@limiter.limit("10 per minute")
def get_data():
    return jsonify({'data': 'value'})

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    pass
```

## Request Validation

```python
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    age = fields.Int(validate=validate.Range(min=13, max=120))

@app.route('/api/users', methods=['POST'])
def create_user():
    schema = UserSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return schema.dump(user), 201
```

## Exercises

1. **CRUD API**: Build a complete CRUD API for a resource with pagination.

2. **Authentication**: Add API key authentication to all endpoints.

3. **Versioning**: Implement URL-based API versioning.

4. **Documentation**: Document your API using Flask-RESTX or flasgger.

5. **Rate Limiting**: Add rate limiting to your API endpoints.

## Quiz

**Question 1**: What are the characteristics of a well-designed REST API?

**Question 2**: What is the difference between PUT and PATCH?

**Question 3**: How would you implement API versioning in Flask?

**Question 4**: Why is rate limiting important for APIs?

**Question 5**: What tools can you use to document a Flask API?

## Interview Questions

1. "How would you design a REST API for a blog platform using Flask?"

2. "What is the difference between Flask-RESTful and plain Flask for APIs?"

3. "How would you handle authentication for a Flask API?"

4. "Explain API versioning strategies. Which do you prefer?"

5. "How would you implement rate limiting in a Flask API?"

## Related Chapters

- [[10-Advanced/JWT-Authentication]] — Token-based API authentication
- [[00-Foundations/REST-APIs]] — REST principles
- [[00-Foundations/JSON]] — JSON data format

## Official Documentation References

- [Flask-RESTful Documentation](https://flask-restful.readthedocs.io/)
- [Flask-RESTX Documentation](https://flask-restx.readthedocs.io/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/)

---

*Previous: [[10-Advanced/CI-CD]] | Next: [[10-Advanced/JWT-Authentication]]*