---
title: JSON - JavaScript Object Notation
description: The universal data format of modern web APIs — how to serialize, deserialize, and work with JSON in Python and Flask
chapter: 00-Foundations
tags:
  - json
  - serialization
  - data-format
  - api
  - foundations
difficulty: Beginner
prerequisites:
  - [[00-Foundations/HTTP]]
---

# JSON — JavaScript Object Notation

> JSON is the lingua franca of web APIs. Every REST endpoint you build in Flask will likely accept JSON in requests and return JSON in responses. Understanding JSON thoroughly — its syntax, its limitations, and how Python maps to it — is essential.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain JSON's syntax and data types
- Serialize Python objects to JSON and deserialize JSON to Python
- Handle datetime, Decimal, and other types that JSON does not natively support
- Parse and generate JSON in Flask requests and responses
- Understand JSON's limitations compared to Python dictionaries
- Handle large JSON payloads efficiently
- Validate JSON against schemas

## What Is JSON?

**JSON (JavaScript Object Notation)** is a lightweight, text-based, language-independent data interchange format. It was derived from JavaScript object syntax but is now used by virtually every programming language.

Douglas Crockford specified JSON in the early 2000s. Its design goals were:
- **Minimal**: Simple syntax, easy to parse
- **Readable**: Human-readable text format
- **Universal**: Language-independent
- **Pragmatic**: Supports the data types that most programming languages share

JSON became the default data format for web APIs because it is simpler than XML, natively parsed by JavaScript (the language of browsers), and maps cleanly to the data structures of most programming languages.

## JSON Syntax

JSON has two structures:

### Objects (Key-Value Pairs)

```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "is_active": true,
    "roles": ["user", "editor"],
    "profile": {
        "bio": "Software developer",
        "website": "https://johndoe.com"
    }
}
```

Rules:
- Keys must be **double-quoted strings**
- Values can be: string, number, object, array, boolean, or null
- No trailing commas allowed
- No comments allowed

### Arrays (Ordered Lists)

```json
[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]
```

## JSON Data Types

| JSON Type | Example | Python Equivalent |
|-----------|---------|-------------------|
| String | `"hello"` | `str` |
| Number | `42`, `3.14` | `int`, `float` |
| Boolean | `true`, `false` | `True`, `False` |
| Null | `null` | `None` |
| Object | `{"a": 1}` | `dict` |
| Array | `[1, 2, 3]` | `list` |

> [!WARNING]
> JSON does not distinguish between integers and floats — all numbers are just "number." JSON has no `datetime`, `Decimal`, `set`, `bytes`, or `tuple` types. You must handle these conversions manually.

## JSON in Python

Python's standard library includes the `json` module:

### Serialization (Python → JSON)

```python
import json

data = {
    'name': 'John Doe',
    'age': 30,
    'is_active': True,
    'roles': ['user', 'editor'],
    'profile': {'bio': 'Developer'}
}

json_string = json.dumps(data)
# '{"name": "John Doe", "age": 30, "is_active": true, "roles": ["user", "editor"], "profile": {"bio": "Developer"}}'
```

### Deserialization (JSON → Python)

```python
import json

json_string = '{"name": "John", "age": 30}'
data = json.loads(json_string)
# {'name': 'John', 'age': 30}
```

### Pretty-Printing

```python
print(json.dumps(data, indent=2))
# {
#   "name": "John Doe",
#   "age": 30,
#   "is_active": true
# }
```

### File I/O

```python
# Write to file
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Read from file
with open('data.json', 'r') as f:
    data = json.load(f)
```

## Handling Non-JSON Types

JSON's limited type system creates challenges for Python developers. Common solutions:

### Datetime

```python
from datetime import datetime
import json

def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

data = {'created_at': datetime.now()}
json_string = json.dumps(data, default=datetime_serializer)
# '{"created_at": "2024-07-15T10:30:00"}'

# Deserialization requires manual parsing
def datetime_parser(dct):
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return dct

data = json.loads(json_string, object_hook=datetime_parser)
```

### Decimal

```python
from decimal import Decimal

data = {'price': Decimal('19.99')}
json_string = json.dumps(data, default=lambda x: str(x) if isinstance(x, Decimal) else x)

# Parse back
data = json.loads(json_string, parse_float=Decimal)
```

### UUID

```python
from uuid import UUID
import json

data = {'id': UUID('12345678-1234-1234-1234-123456789abc')}
json_string = json.dumps(data, default=lambda x: str(x) if isinstance(x, UUID) else x)
```

## JSON in Flask

Flask provides built-in JSON support through the `jsonify` function and `request.get_json()` method.

### Returning JSON

```python
from flask import jsonify

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })
```

`jsonify` automatically:
- Sets `Content-Type: application/json`
- Serializes Python objects to JSON
- Returns a proper Flask Response object

### Parsing JSON Requests

```python
from flask import request

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 422
    
    user = User(name=data['name'], email=data.get('email'))
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'id': user.id, 'name': user.name}), 201
```

`request.get_json()`:
- Parses the request body as JSON
- Returns `None` if no JSON data or parsing fails
- Set `force=True` to parse even if Content-Type is not `application/json` (not recommended)
- Set `silent=False` to raise an exception on parse errors

### Custom JSON Encoder

For consistent handling of special types across your application:

```python
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)

# Now all jsonify() calls handle datetime, Decimal, and UUID automatically
@app.route('/api/order/<int:order_id>')
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'total': order.total,           # Decimal → string
        'created_at': order.created_at,  # datetime → ISO string
        'uuid': order.uuid               # UUID → string
    })
```

## JSON Schema Validation

For API robustness, validate incoming JSON against a schema:

```python
from jsonschema import validate, ValidationError

USER_SCHEMA = {
    'type': 'object',
    'required': ['name', 'email'],
    'properties': {
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
        'email': {'type': 'string', 'format': 'email'},
        'age': {'type': 'integer', 'minimum': 0, 'maximum': 150}
    },
    'additionalProperties': False
}

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        validate(instance=data, schema=USER_SCHEMA)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 422
    
    # Data is valid, proceed...
```

## Common Mistakes

**Mistake: Using `json.dumps()` instead of `jsonify()` in Flask**
`json.dumps()` returns a string. `jsonify()` returns a proper Flask Response with correct headers. Always use `jsonify()` in Flask.

**Mistake: Not handling missing JSON data**
`request.get_json()` returns `None` if no JSON body is present. Always check before accessing.

**Mistake: Serializing datetime without a custom encoder**
`json.dumps()` raises `TypeError` on datetime objects. Always provide a `default` handler or custom JSON provider.

**Mistake: Using floats for monetary values**
JSON's number type becomes Python `float`. For money, use `Decimal` and serialize as strings.

## Best Practices

- Use `jsonify()` for all JSON responses in Flask
- Always check for `None` from `request.get_json()`
- Implement a custom JSON encoder for datetime, Decimal, UUID
- Validate incoming JSON with schemas
- Use ISO 8601 format for dates (`2024-07-15T10:30:00Z`)
- Serialize monetary values as strings, not numbers
- Set `ensure_ascii=False` when serializing non-ASCII text

## Exercises

1. **Serialize Complex Object**: Create a Python class `User` with datetime fields. Serialize it to JSON properly, then deserialize it back.

2. **JSON Schema Validation**: Write a JSON schema for a blog post (title, content, author, tags, published_at). Validate sample data against it.

3. **Custom Encoder**: Implement a Flask JSON encoder that handles datetime, Decimal, UUID, and sets.

4. **Large JSON**: Generate a JSON file with 10,000 user records. Measure `json.load()` vs. `json.loads()` performance. Explore `orjson` as a faster alternative.

## Quiz

**Question 1**: What are the six data types in JSON? What Python types do they map to?

**Question 2**: Why does `json.dumps(datetime.now())` raise a TypeError? How do you fix it?

**Question 3**: What is the difference between `json.dumps()` and Flask's `jsonify()`?

**Question 4**: Why should monetary values be serialized as strings in JSON rather than numbers?

**Question 5**: What happens when `request.get_json()` receives invalid JSON? How do you handle it?

## Interview Questions

1. "What are JSON's limitations as a data format? What types does it not support?"

2. "How would you serialize a Python object with datetime and Decimal fields to JSON?"

3. "What is the difference between `json.dumps()` and `jsonify()` in Flask? When would you use each?"

4. "How do you handle large JSON payloads in a Flask application to avoid memory issues?"

## Related Chapters

- Previous: [[00-Foundations/REST-APIs]]
- Next: [[00-Foundations/Web-Technologies]]
- [[10-Advanced/REST-API-Development]] — Building production REST APIs

## Official Documentation References

- [JSON.org](https://www.json.org/)
- [RFC 8259 - JSON](https://datatracker.ietf.org/doc/html/rfc8259)
- [Python json module documentation](https://docs.python.org/3/library/json.html)
- [Flask jsonify documentation](https://flask.palletsprojects.com/en/latest/api/#flask.json.jsonify)

---

*Previous: [[00-Foundations/REST-APIs]] | Next: [[00-Foundations/Web-Technologies]]*