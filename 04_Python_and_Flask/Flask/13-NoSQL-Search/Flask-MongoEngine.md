---
title: Flask-MongoEngine
tags:
  - flask
  - nosql
  - mongodb
  - odm
  - document
  - querying
aliases:
  - MongoEngine in Flask
  - MongoDB ODM
  - FME
related:
  - "[[Flask-SQLAlchemy]]"
  - "[[Flask-PynamoDB]]"
  - "[[Marshmallow]]"
  - "[[Flask-Admin]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-MongoEngine

#flask #nosql #mongodb #odm #document #querying

> [!info] The document database ODM for Flask
> Flask-MongoEngine is a thin Flask wrapper around [MongoEngine](http://mongoengine.org/), an **ODM** (Object-Document Mapper) for MongoDB. Where [[Flask-SQLAlchemy]] maps Python classes to SQL rows, Flask-MongoEngine maps them to **BSON documents** in collections. If your data is hierarchical, polymorphic, schema-flexible, or grows without bound, MongoDB is often a better fit than Postgres — and MongoEngine is the most mature Python ODM for it.

This note covers document design, fields, references, querying with `Q` objects, signals, indexes, and the architectural differences vs. SQL databases.

---

## 1. Overview & Metaphor

### What is a document database?

A **relational** database stores rows in tables — flat, fixed-schema. A **document** database stores JSON-like documents in collections — nested, schema-flexible.

```json
// SQL: 3 tables, 3 joins to get a user with addresses and tags
// MongoDB: one document
{
  "_id": ObjectId("..."),
  "username": "alice",
  "email": "alice@example.com",
  "addresses": [
    {"label": "home", "city": "Berlin"},
    {"label": "work", "city": "Munich"}
  ],
  "tags": ["admin", "vip"],
  "meta": {"joined_at": "2024-01-15", "plan": "pro"}
}
```

No joins needed to read it; one round trip. The trade-off: data is **denormalized**, so updating a city name across 1M users is harder.

> [!tip] The metaphor
> If a SQL row is a **single cell in a spreadsheet**, a MongoDB document is a **whole folder** with subfolders inside. You read the folder in one go — but if the same information lives in many folders, updating it everywhere is your problem.

### When MongoDB, when Postgres?

| Concern | Choose MongoDB | Choose Postgres |
|---|---|---|
| Hierarchical data (orders → items → variants) | ✅ Nested documents | ⚠️ Needs JSONB or joins |
| Schema evolves rapidly | ✅ Add fields anytime | ⚠️ Migrations |
| Polymorphic records (events with different shapes) | ✅ Native | ⚠️ Single-table inheritance |
| Joins across many collections/tables | ⚠️ `$lookup` is limited | ✅ First-class |
| Multi-document ACID transactions | ⚠️ Available but slower | ✅ Native |
| Strict schema, foreign keys | ⚠️ Optional validation | ✅ Native |
| Geographic / time-series at huge scale | ✅ Sharding built-in | ⚠️ Needs extensions |

> [!warning] Don't use MongoDB because it's "easier"
> MongoDB's schema flexibility is a double-edged sword. Without discipline, every collection becomes a junk drawer of inconsistent documents. Use MongoEngine's `required=True`, `choices=`, and validation to enforce a schema in the application layer.

### What Flask-MongoEngine adds

Plain MongoEngine needs ~10 lines of boilerplate: a `connect()` call, a `db` alias, an app-context manager. Flask-MongoEngine gives you:

- A single `db = MongoEngine()` instance (extensions pattern, see [[Project-Structure]])
- Connection config from `app.config["MONGODB_SETTINGS"]`
- A `db.Document` base class with Flask-aware querysets
- Teardown hooks that clean up connections per request
- Integration with [[Flask-Admin]] (via `mongoengine` contrib) and [[Marshmallow]]

---

## 2. Installation

```bash
(venv) $ pip install flask-mongoengine
```

Versions referenced in this note:

| Package | Version |
|---|---|
| Flask | 3.0.x |
| flask-mongoengine | 1.0.0 |
| mongoengine | 0.27.x |
| pymongo | 4.6.x (transitive) |

You'll also need a running MongoDB server — locally or in the cloud (MongoDB Atlas is the easiest hosted option):

```bash
# Local: Docker
$ docker run -d -p 27017:27017 --name mongo mongo:7

# Or install via Homebrew / apt
```

---

## 3. Configuration

### Minimal config

```python
# app/extensions.py
from flask_mongoengine import MongoEngine

db = MongoEngine()
```

```python
# app/__init__.py
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config["MONGODB_SETTINGS"] = {
        "db": "myapp",
        "host": "localhost",
        "port": 27017,
    }
    db.init_app(app)
    return app
```

### All configuration options

| Option | Default | Description |
|---|---|---|
| `MONGODB_SETTINGS` | `{}` | Dict (or list of dicts) of connection kwargs passed to `mongoengine.connect()`. |
| `MONGODB_HOST` | `None` | Shortcut — full URI like `mongodb://user:pass@host:27017/db?replicaSet=rs0` |
| `MONGODB_CONNECT` | `False` | If `True`, connect immediately (defers otherwise until first query). |
| `MONGODB_IS_TESTING` | `False` | If `True`, allows dropping databases in tests. |

### Connection URI forms

```python
# Single node
app.config["MONGODB_SETTINGS"] = {"host": "mongodb://localhost:27017/myapp"}

# Replica set (production)
app.config["MONGODB_SETTINGS"] = {
    "host": "mongodb://user:pass@rs1:27017,rs2:27017,rs3:27017/myapp?replicaSet=rs0",
    "replicaSet": "rs0",
    "read_preference": "secondaryPreferred",
}

# Atlas (TLS)
app.config["MONGODB_SETTINGS"] = {
    "host": "mongodb+srv://user:pass@cluster0.xyz.mongodb.net/myapp?retryWrites=true&w=majority",
    "tls": True,
    "tlsAllowInvalidCertificates": False,
}

# Multiple databases (multi-document)
app.config["MONGODB_SETTINGS"] = [
    {"db": "myapp", "alias": "default"},
    {"db": "analytics", "alias": "analytics"},
]
```

### Production-grade config

```python
# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGODB_SETTINGS = {
        "host": os.environ["MONGODB_URI"],
        "tz_aware": True,           # store datetimes with tz info
        "connectTimeoutMS": 5000,
        "socketTimeoutMS": 30000,
        "serverSelectionTimeoutMS": 5000,
        "maxPoolSize": 100,         # connection pool size
        "minPoolSize": 5,
        "retryWrites": True,
        "w": "majority",            # write concern
        "read_preference": "primaryPreferred",
    }


class TestingConfig(Config):
    MONGODB_SETTINGS = {"db": "myapp_test", "host": "mongomock://localhost"}
```

> [!tip] Use `mongomock` for fast unit tests
> The `mongomock` library provides an in-memory MongoDB-compatible engine. Set the URI to `mongomock://localhost` and tests run in milliseconds without a real MongoDB server. Caveats: not 100% feature-complete — `aggregate`, `$lookup`, and change streams may behave differently.

---

## 4. Basic Usage

### Defining a document

```python
# app/models/user.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Document):
    username = db.StringField(required=True, unique=True, max_length=64)
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    is_active_user = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    last_login = db.DateTimeField()

    meta = {
        "collection": "users",        # collection name (default: class name lowercase)
        "indexes": ["username", "email", "created_at"],
        "ordering": ["-created_at"],
    }

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __str__(self) -> str:
        return f"<User {self.username}>"
```

### CRUD operations

```python
# CREATE
user = User(username="alice", email="alice@example.com")
user.set_password("hunter2")
user.save()              # INSERT — `user.id` is now populated

# READ
user = User.objects.get(id="65a8...")              # by ObjectId
user = User.objects(username="alice").first()       # by field
users = User.objects(email__endswith="@example.com")  # queryset

# UPDATE
user.email = "alice@newdomain.com"
user.save()                 # full-document replace

# Partial update (only changed fields) — faster, atomic
User.objects(id=user.id).update(set__email="alice@newdomain.com")

# DELETE
user.delete()
User.objects(username="spammer").delete()  # bulk
```

> [!warning] `save()` overwrites the whole document
> `user.save()` reads the in-memory object and writes the entire document back — clobbering any concurrent updates from other processes. For atomic partial updates, use `Model.objects(id=...).update(set__field=value)` (the **update operator** API). See §10.

### Querysets are lazy

`User.objects(...)` does **not** hit the database until you iterate, slice, or call `.first()` / `.count()`:

```python
qs = User.objects(is_active_user=True)   # no query yet
qs = qs.filter(email__endswith="@example.com")  # still no query
qs = qs.order_by("-created_at").limit(10)       # still no query
users = list(qs)                                # NOW it queries
```

### EmbeddedDocument vs Document

```python
class Address(db.EmbeddedDocument):
    label = db.StringField(required=True)         # "home", "work"
    street = db.StringField()
    city = db.StringField(required=True)
    country = db.StringField(default="DE")
    geo = db.DictField()                          # {"lat": ..., "lng": ...}


class User(db.Document):
    # ...
    addresses = db.ListField(db.EmbeddedDocumentField(Address))
```

```python
user = User(username="alice", email="alice@example.com")
user.addresses = [
    Address(label="home", city="Berlin", geo={"lat": 52.5, "lng": 13.4}),
    Address(label="work", city="Munich"),
]
user.save()
```

Embedded documents live **inside** the parent — no separate collection, no separate query. Updating them updates the parent document. Compare with `ReferenceField` (§5).

```mermaid
erDiagram
  USER ||--o{ POST : writes
  USER ||--o{ ADDRESS : "embeds (in-document)"
  POST ||--o{ COMMENT : "embeds (in-document)"
  POST }o--o{ TAG : references
  USER }o--o{ USER : follows

  USER {
    ObjectId _id PK
    string username UK
    string email UK
    string password_hash
    bool is_active_user
    datetime created_at
  }
  ADDRESS {
    string label
    string city
    string country
    dict geo
  }
  POST {
    ObjectId _id PK
    string title
    text body
    ObjectId author_id FK
    list comments
    datetime created_at
  }
  COMMENT {
    text body
    ObjectId author_id FK
    datetime created_at
  }
  TAG {
    ObjectId _id PK
    string name UK
  }
```

---

## 5. Fields & References

### Field types

| Field | Python type | Storage | Notes |
|---|---|---|---|
| `StringField` | `str` | String | `max_length`, `regex`, `required`. |
| `URLField` | `str` | String | URL validation. |
| `EmailField` | `str` | String | Email validation. |
| `IntField` | `int` | Int32 | `min_value`, `max_value`. |
| `LongField` | `int` | Int64 | Larger integers. |
| `FloatField` | `float` | Double | |
| `DecimalField` | `Decimal` | String | Exact precision (e.g., money). |
| `BooleanField` | `bool` | Boolean | |
| `DateTimeField` | `datetime` | Date | `tz_aware=True` recommended. |
| `ListField` | `list` | Array | Wraps another field; e.g., `ListField(StringField())`. |
| `DictField` | `dict` | Object | Free-form — schema-less escape hatch. |
| `MapField` | `dict` | Object | Like `DictField` but all values share one field type. |
| `ReferenceField` | `Document` | ObjectId (DBRef) | Foreign-key-like; lazy by default. |
| `EmbeddedDocumentField` | `EmbeddedDocument` | Sub-document | Nested structured object. |
| `ObjectIdField` | `ObjectId` | ObjectId | Manual ObjectId storage. |
| `UUIDField` | `UUID` | Binary | UUIDs stored as BSON Binary. |
| `FileField` | GridFS file | GridFS | Large binary; see §9. |
| `ImageField` | Image | GridFS | Requires `Pillow`. |
| `SequenceField` | `int` | Counter doc | Auto-incrementing (uses a separate counter collection). |
| `BinaryField` | `bytes` | BinData | Small blobs. |
| `PointField` | `(lat, lng)` | GeoJSON Point | For `$near` queries. |
| `PolygonField` | list of points | GeoJSON Polygon | For `$geoIntersects`. |
| `GenericReferenceField` | any Document | ObjectId + `_cls` | Polymorphic references. |

### ReferenceField (lazy references)

```python
class Post(db.Document):
    title = db.StringField(required=True)
    body = db.StringField()
    author = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    tags = db.ListField(db.ReferenceField("Tag"))
    created_at = db.DateTimeField(default=datetime.utcnow)


class Tag(db.Document):
    name = db.StringField(required=True, unique=True)


post = Post(title="Hello", body="World", author=user)
post.tags = [Tag(name="flask").save(), Tag(name="python").save()]
post.save()

# Dereference (lazy)
print(post.author.username)        # SELECT-by-id under the hood

# Eager-load references (avoid N+1)
posts = Post.objects().select_related()       # follows all RefFields
posts = Post.objects().select_related("author")  # follow specific
```

`reverse_delete_rule` controls what happens when the referenced document is deleted:

| Rule | Behavior |
|---|---|
| `db.DENY` (default) | Prevent deletion if references exist. |
| `db.NULLIFY` | Set references to `None`. |
| `db.CASCADE` | Delete documents that reference it. |
| `db.PULL` | Remove the reference from `ListField(ReferenceField(...))`. |
| `db.DELETE` | Same as CASCADE for ListField. |

### GenericReferenceField (polymorphic)

```python
class Activity(db.Document):
    actor = db.ReferenceField(User, required=True)
    target = db.GenericReferenceField()      # can point to Post, Comment, anything
    verb = db.StringField()                   # "posted", "commented", "liked"

activity = Activity(actor=user, target=post, verb="posted").save()
activity.target  # returns the actual Post instance, fetched lazily
```

### Validation

```python
class Account(db.Document):
    email = db.EmailField(required=True)
    age = db.IntField(min_value=13, max_value=120)
    handle = db.StringField(regex=r"^[a-z0-9_]{3,20}$")
    plan = db.StringField(choices=("free", "pro", "enterprise"))

account = Account(email="not-an-email", age=200, handle="UPPER CASE", plan="gold")
account.validate()  # raises ValidationError listing all problems
```

`save()` calls `validate()` automatically unless you pass `validate=False`.

---

## 6. Querying

### Basic queries

```python
User.objects()                                   # all
User.objects(username="alice").first()
User.objects(email__endswith="@example.com")
User.objects(created_at__gte=datetime(2024, 1, 1))
User.objects(is_active_user=True).limit(10)
User.objects(username__in=["alice", "bob", "carol"])
User.objects(username__icontains="li")           # case-insensitive substring
User.objects(addresses__city="Berlin")           # query into embedded list
User.objects(addresses__0__city="Berlin")        # first address's city
```

### Query operators

| Suffix | Mongo operator | Example |
|---|---|---|
| `__exact` (default) | `$eq` | `name="alice"` |
| `__ne` | `$ne` | `name__ne="alice"` |
| `__lt`, `__lte` | `$lt`, `$lte` | `age__lt=18` |
| `__gt`, `__gte` | `$gt`, `$gte` | `created_at__gte=...` |
| `__in` | `$in` | `id__in=[...]` |
| `__nin` | `$nin` | `status__nin=["banned"]` |
| `__all` | `$all` | `tags__all=["flask", "python"]` |
| `__exists` | `$exists` | `bio__exists=True` |
| `__size` | `$size` | `tags__size=3` |
| `__startswith`, `__endswith`, `__contains` | regex | `name__startswith="A"` |
| `__icontains` | regex (case-insensitive) | `name__icontains="li"` |
| `__near` | `$near` | `loc__near=[52.5, 13.4]` |
| `__within_distance`, `__within_polygon` | `$geoWithin` | geo queries |

### `Q` objects (boolean combinations)

```python
from mongoengine.queryset.visitor import Q

# (active AND pro) OR (admin)
qs = User.objects(
    (Q(is_active_user=True) & Q(plan="pro")) | Q(is_admin=True)
)

# NOT (banned OR deleted)
qs = User.objects(~Q(status="banned") & ~Q(deleted_at__exists=True))
```

`Q` translates to a MongoDB query document — the same logic that would take raw `{$or: [{$and: [...]}, {...}]}` in the shell, but readable in Python.

```mermaid
flowchart LR
  A["Q(is_active=True) &<br/>Q(plan='pro')"] --> B{"Compose"}
  C["Q(is_admin=True)"] --> B
  B --> D["Q(($and) | is_admin)"]
  D --> E["MongoEngine<br/>queryset"]
  E --> F["{ $or: [ { $and: [ ... ] }, { is_admin: true } ] }"]
  F --> G[(MongoDB)]
  style G fill:#f9f,stroke:#333
```

### Aggregation

```python
# Count
User.objects(is_active_user=True).count()

# Distinct
User.objects().distinct("email")

# Aggregate pipeline
from mongoengine.connection import get_db

pipeline = [
    {"$match": {"is_active_user": True}},
    {"$group": {"_id": "$plan", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
]
results = list(get_db().users.aggregate(pipeline))
# [{'_id': 'free', 'count': 1234}, {'_id': 'pro', 'count': 56}, ...]
```

For complex aggregations, drop down to the raw `pymongo` collection via `get_db()` — MongoEngine's querysets cover most cases but `$facet`, `$lookup`, and `$graphLookup` need raw access.

### Atomic find-and-modify

```python
# Increment view_count atomically (no race conditions)
Post.objects(id=post.id).update(inc__view_count=1)

# Atomic find + update — pop the next pending job
job = Job.objects(status="pending").find_and_modify(
    {"$set": {"status": "running", "worker_id": worker_id}},
    upsert=False,
    new=True,
)
```

---

## 7. Indexes

Indexes are declared in `meta`:

```python
class User(db.Document):
    username = db.StringField()
    email = db.EmailField()
    plan = db.StringField()
    created_at = db.DateTimeField()

    meta = {
        "indexes": [
            "username",                       # single-field, ascending
            {"fields": ["email"], "unique": True},
            {"fields": ["plan", "created_at"], "name": "plan_created_idx"},
            {"fields": ["$bio_text"], "weights": {"bio": 2}},   # text index
            {"fields": ["loc"], "type": "2dsphere"},            # geo index
        ],
        "index_opts": {"background": True},   # build index without locking
    }
```

> [!warning] Building indexes on huge collections
> Set `"background": True` in production — otherwise index creation locks the collection and your app stalls. For collections > 1M documents, prefer creating indexes during a maintenance window via the Mongo shell, not via `db.Document.ensure_indexes()`.

---

## 8. Pagination

```python
# Manual offset/limit
page = 1
per_page = 20
users = User.objects().order_by("-created_at").skip((page - 1) * per_page).limit(per_page)

# A helper class
class Pagination:
    def __init__(self, queryset, page, per_page):
        self.total = queryset.count()
        self.pages = (self.total + per_page - 1) // per_page
        self.items = queryset.skip((page - 1) * per_page).limit(per_page)
        self.page = page
        self.per_page = per_page

    @property
    def has_prev(self): return self.page > 1
    @property
    def has_next(self): return self.page < self.pages
```

> [!tip] `.skip()` is O(n) — use range queries instead
> Skipping 1M rows to read page 50,000 forces MongoDB to walk through 1M documents. For deep pagination, use a **range query** on an indexed field:
> ```python
> # Instead of .skip(100000).limit(20)
> last_id = ...  # saved from the previous page's last item
> qs = Post.objects(id__gt=last_id).order_by("+id").limit(20)
> ```

---

## 9. File Storage with GridFS

```python
class Asset(db.Document):
    name = db.StringField(required=True)
    file = db.FileField()
    owner = db.ReferenceField(User)

asset = Asset(name="report.pdf", owner=user).save()
with open("report.pdf", "rb") as f:
    asset.file.put(f, content_type="application/pdf")
asset.save()

# Read back
out = asset.file.read()           # bytes
asset.file.delete()               # remove from GridFS
```

GridFS chunks files > 16MB across multiple BSON documents, so it works for any file size — but a real object store (S3, MinIO) is usually faster and cheaper.

---

## 10. Signals & Events

MongoEngine emits signals on document lifecycle events.

```python
from mongoengine import signals


class Post(db.Document):
    title = db.StringField(required=True)
    body = db.StringField()
    slug = db.StringField(required=True, unique=True)
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()


@signals.pre_save.connect
def pre_save_post(sender, document, **kwargs):
    if not document.slug:
        document.slug = document.title.lower().replace(" ", "-")
    document.updated_at = datetime.utcnow()
    if not document.created_at:
        document.created_at = datetime.utcnow()


@signals.post_save.connect
def post_save_post(sender, document, created, **kwargs):
    if created:
        from app.tasks.search import index_post
        index_post.delay(document.id)  # Celery task


@signals.pre_delete.connect
def pre_delete_post(sender, document, **kwargs):
    from app.tasks.search import unindex_post
    unindex_post.delay(document.id)
```

Available signals: `pre_init`, `post_init`, `pre_save`, `post_save`, `pre_bulk_insert`, `pre_update`, `post_update`, `pre_delete`, `post_delete`, `pre_bulk_delete`.

> [!warning] `pre_save` runs in Python, not in the DB
> A signal can't enforce a constraint atomically — another process could insert a duplicate between the time `pre_save` checks and `save()` commits. Use unique indexes (`unique=True` on the field) for hard guarantees; signals are for derivations and side-effects only.

---

## 11. Testing

Use `mongomock` for fast, isolated tests:

```python
# tests/conftest.py
import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config["MONGODB_SETTINGS"] = {"host": "mongomock://localhost", "db": "test"}
    _db.init_app(app)
    with app.app_context():
        yield app
        # mongomock is in-memory; nothing to drop
    # If using real Mongo: for cls in _db.Document._subclasses: drop collections


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()
```

```python
# tests/test_models.py
def test_user_creation(db):
    user = User(username="alice", email="alice@example.com")
    user.set_password("hunter2")
    user.save()

    fetched = User.objects.get(id=user.id)
    assert fetched.username == "alice"
    assert fetched.check_password("hunter2")


def test_unique_email(db):
    User(username="a", email="dup@example.com").save()
    with pytest.raises(db.NotUniqueError):
        User(username="b", email="dup@example.com").save()
```

> [!tip] Always run a subset against real Mongo
> `mongomock` doesn't implement everything: `$facet`, `$lookup`, change streams, transactions, and some geo operators behave differently or are missing. Run your integration tests against a real MongoDB (Docker is fine) at least in CI.

---

## 12. Performance Tips

1. **Avoid full-document `save()` for partial updates.** Use `Model.objects(id=...).update(set__field=value)` — it's atomic and only writes the changed field.
2. **Use `select_related()` for `ReferenceField`s** to avoid N+1 queries.
3. **Index fields you query on.** Especially `__exact`, `__in`, and sort fields. `explain()` in the Mongo shell shows whether a query is using an index.
4. **Use `$inc` for counters.** `Post.objects(id=...).update(inc__view_count=1)` is atomic; reading then writing back is not.
5. **Cap large lists.** MongoDB documents have a 16MB hard limit. If `addresses` can grow unboundedly, store them as a separate collection with `ReferenceField` instead of `EmbeddedDocumentField`.
6. **Use `batch_size` for huge querysets.** `User.objects().batch_size(500)` reduces round trips.
7. **Use covered queries.** If you only need `username` and `email`, build a compound index on them and use `.only("username", "email")` — MongoDB can answer from the index without fetching documents.
8. **Avoid `$where` and large regex.** Both trigger collection scans. Use prefix-anchored regex (`^alice`) which can use an index, or use a text index for full-text search.

---

## 13. Integration with Other Extensions

### [[Flask-Login]]

Same pattern as [[Flask-SQLAlchemy]] — your `User` document needs `UserMixin`:

```python
from flask_login import UserMixin

class User(UserMixin, db.Document):
    # ...
    def get_id(self):
        return str(self.id)   # ObjectId -> str for the session
```

### [[Marshmallow]]

Generate schemas from MongoEngine documents with `marshmallow-mongoengine`:

```python
from marshmallow_mongoengine import ModelSchema

class PostSchema(ModelSchema):
    class Meta:
        model = Post
        model_skip_values = ("file",)   # don't serialize FileField

schema = PostSchema(many=True)
schema.dump(Post.objects().limit(10))
```

### [[Flask-Admin]]

```python
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView

admin = Admin(app, name="Admin")
admin.add_view(ModelView(User))
admin.add_view(ModelView(Post))
```

### [[Flask-Caching]]

MongoDB queries are not particularly cache-friendly (different query plans, no statement cache). Use [[Flask-Caching]] for **results** — e.g., cache the result of a slow aggregation for 5 minutes:

```python
from app.extensions import cache

@cache.cached(timeout=300, key_prefix="daily_stats")
def daily_stats():
    return list(get_db().events.aggregate([...]))
```

---

## 14. Full Real-World Example: A Blog

```python
# app/models/post.py
from datetime import datetime
from app.extensions import db


class Comment(db.EmbeddedDocument):
    body = db.StringField(required=True)
    author_name = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)


class Post(db.Document):
    title = db.StringField(required=True, max_length=200)
    slug = db.StringField(required=True, unique=True)
    body = db.StringField(required=True)
    author = db.ReferenceField("User", reverse_delete_rule=db.DENY)
    tags = db.ListField(db.ReferenceField("Tag"))
    comments = db.ListField(db.EmbeddedDocumentField(Comment))
    is_published = db.BooleanField(default=False)
    view_count = db.IntField(default=0)
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        "indexes": [
            "slug",
            "author",
            "tags",
            {"fields": ["is_published", "created_at"]},
            {"fields": ["$title", "$body"]},   # text index
        ],
        "ordering": ["-created_at"],
    }

    def add_comment(self, body, author_name):
        self.comments.append(Comment(body=body, author_name=author_name))
        self.save()


class Tag(db.Document):
    name = db.StringField(required=True, unique=True)
    slug = db.StringField(required=True, unique=True)
```

```python
# Usage
alice = User(username="alice", email="alice@example.com").save()
alice.set_password("hunter2"); alice.save()

flask_tag = Tag(name="flask", slug="flask").save()
python_tag = Tag(name="python", slug="python").save()

post = Post(
    title="Flask + MongoEngine",
    slug="flask-mongoengine-complete",
    body="A complete example...",
    author=alice,
    tags=[flask_tag, python_tag],
    is_published=True,
)
post.save()

# Text search across title and body
results = Post.objects.search_text("flask mongodb").order_by("$text_score")

# Atomic view increment
Post.objects(id=post.id).update(inc__view_count=1)

# Add a comment
post.add_comment(body="Great!", author_name="Bob")
```

### Document schema design (read vs. write workload)

```mermaid
flowchart TB
  A["Decision: embed or reference?"] --> B{"Read pattern?"}
  B -->|Always together| C["Embed (EmbeddedDocument)"]
  B -->|Queried separately| D["Reference (ReferenceField)"]
  C --> E{"Will it grow<br/>unboundedly?"}
  E -->|Yes| F["Switch to reference<br/>(16MB doc limit)"]
  E -->|No| G["OK — embed"]
  D --> H{"Will referenced doc<br/>change often?"}
  H -->|Yes| I["Reference (single source of truth)"]
  H -->|No| J["Consider denormalizing<br/>— embed a snapshot"]
  style F fill:#fdd
  style G fill:#dfd
  style I fill:#dfd
  style J fill:#ffd
```

### Query execution flow

```mermaid
sequenceDiagram
  participant C as Flask view
  participant Q as QuerySet
  participant ME as MongoEngine
  participant P as PyMongo
  participant M as MongoDB

  C->>Q: User.objects(is_active_user=True).filter(email__endswith="@x")
  Q->>Q: Build query dict (no I/O)
  C->>Q: .limit(10)
  Q->>Q: Add options (no I/O)
  C->>Q: list(qs)
  Q->>ME: Serialize to BSON query
  ME->>P: db.users.find({...}).limit(10)
  P->>M: Wire query
  M-->>P: Cursor with docs
  P-->>ME: BSON documents
  ME-->>Q: List of User instances (deserialized)
  Q-->>C: List[User]
```

---

## 15. Common Pitfalls & Troubleshooting

> [!danger] Top 10 MongoEngine mistakes
> 1. **Using `save()` instead of `update()` for partial updates** — race conditions and overwrites.
> 2. **Forgetting `unique=True` indexes** — MongoEngine's `unique=True` builds the index on first save, but if you add it later, run `User.ensure_indexes()` manually.
> 3. **Exceeding 16MB document size** — embed lists grow until they crash.
> 4. **Storing `datetime` without `tz_aware=True`** — naive datetimes cause subtle bugs across deployments.
> 5. **N+1 from `ReferenceField` dereferences** — use `select_related()`.
> 6. **`.skip(100000)` for deep pagination** — use range queries on `_id`.
> 7. **Reading `User.objects(...).first()` then mutating** — the in-memory object is now stale; another process may have changed it.
> 8. **Cascading deletes you didn't intend** — `reverse_delete_rule=db.CASCADE` is dangerous on popular references.
> 9. **Calling `Document.objects.delete()` without a filter** — deletes the entire collection. Always scope.
> 10. **Not handling `OperationFailure`** — connections drop, indexes get dropped by ops, server selection times out. Wrap critical writes in try/except + retry.

### `DoesNotExist`

```python
try:
    user = User.objects.get(username="alice")
except User.DoesNotExist:
    # MongoEngine generates a per-class DoesNotExist
    ...
```

`DoesNotExist` is **per-document-class** — `User.DoesNotExist` is not the same as `Post.DoesNotExist`.

### `NotUniqueError` vs. duplicate-key errors

MongoEngine raises `NotUniqueError` only when an explicit `unique=True` index is violated at insert time. If you create a unique index outside MongoEngine (e.g., via `createIndex` in the shell) and then violate it, you'll get a raw `pymongo.errors.DuplicateKeyError` instead.

### `OperationFailure: server selection timed out`

The driver couldn't reach any server within `serverSelectionTimeoutMS` (default 30s). Causes: firewall blocking the port, wrong credentials, replica set down, network partition.

---

## 16. Comparison: MongoEngine vs. PyMongo vs. SQLAlchemy

| Aspect | PyMongo (raw) | MongoEngine | SQLAlchemy |
|---|---|---|---|
| Abstraction | None — dicts/BSON | ODM, Python classes | ORM, Python classes |
| Schema | None (free-form) | App-layer validation | DB-layer (DDL) |
| Query syntax | `db.users.find({...})` | `User.objects(...)` | `select(User).where(...)` |
| Joins | `$lookup` (limited) | Manual or references | First-class SQL JOINs |
| Transactions | Multi-doc ACID (4.0+) | Supported via context manager | Native |
| Migrations | None (schema-less) | Optional via `mongoengine-migrate` | Alembic, mature |
| Best for | Simple CRUD, scripts | Most Flask apps on Mongo | Relational data |

> [!tip] When to drop to PyMongo
> Use `get_db()` for: aggregations beyond `aggregate`-pipeline sugar (e.g., `$facet`, `$lookup` with multiple `let`/`pipeline`), change streams, raw bulk operations, transactions with custom retry logic. Anything else, stay in MongoEngine for type safety.

---

## 17. Best Practices

> [!tip] MongoEngine best practices
> 1. **Treat MongoDB as if it had a schema.** Mark every field `required=True` or have a strong reason not to.
> 2. **Use `EmbeddedDocument` for tightly-coupled sub-objects** that you always read with the parent.
> 3. **Use `ReferenceField` for shared, mutable, or large entities.**
> 4. **Always declare indexes in `meta`.** Don't rely on ad-hoc shell-created indexes — they won't be in source control.
> 5. **Prefer `update(set__field=value)` over `obj.field = value; obj.save()`.** Atomic, fast, race-free.
> 6. **Use `select_related()` for reference fields** when you'll access them in a loop.
> 7. **Use range queries, not `.skip()`, for deep pagination.**
> 8. **Store `datetime` with `tz_aware=True`.** Always.
> 9. **Don't put GridFS files in MongoDB for production.** Use S3 / MinIO.
> 10. **Run a real MongoDB in CI.** `mongomock` will miss bugs.

---

## 18. References & Further Reading

- [Flask-MongoEngine docs](https://flask-mongoengine.readthedocs.io/) — the wrapper.
- [MongoEngine docs](https://docs.mongoengine.org/) — the ODM.
- [MongoDB Manual](https://www.mongodb.com/docs/manual/) — server docs.
- [PyMongo docs](https://pymongo.readthedocs.io/) — the underlying driver.
- [MongoDB Data Modeling](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/) — embed vs. reference patterns.
- [MongoDB Transactions](https://www.mongodb.com/docs/manual/core/transactions/) — multi-document ACID.

---

## 19. Cheat Sheet

```python
# Create
doc = Model(field="value")
doc.save()

# Read
doc = Model.objects.get(id="...")
doc = Model.objects(field="value").first()
qs = Model.objects(field__gte=10).order_by("-created_at").limit(10)
docs = list(qs)

# Update (atomic)
Model.objects(id=doc.id).update(set__field="new")
Model.objects(id=doc.id).update(inc__counter=1)
Model.objects(id=doc.id).update(push__tags="flask")
Model.objects(id=doc.id).update(pull__tags="old")

# Delete
doc.delete()
Model.objects(field="value").delete()

# Q objects
from mongoengine.queryset.visitor import Q
qs = Model.objects((Q(a=1) & Q(b=2)) | Q(c=3))

# Aggregation
from mongoengine.connection import get_db
list(get_db().mycollection.aggregate([{"$group": ...}]))

# Eager load references
Model.objects().select_related("author")

# Pagination (range query — preferred)
last_id = ...
qs = Model.objects(id__gt=last_id).order_by("+id").limit(20)

# Text search
Model.objects.search_text("flask mongodb").order_by("$text_score")

# Transactions
from mongoengine import connection
with connection.get_db().client.start_session() as session:
    with session.start_transaction():
        User.objects(...).update(..., session=session)
        Post.objects(...).update(..., session=session)
```

---

*See also: [[Flask-SQLAlchemy]] · [[Flask-PynamoDB]] · [[Flask-Redis]] · [[Flask-Elasticsearch]] · [[Marshmallow]] · [[Flask-Admin]] · [[Project-Structure]] · [[00-Map-of-Content]]*
