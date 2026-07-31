from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from models import db, UserModel

UserBlueprint = Blueprint("users", "users", url_prefix="/users", description="Operations on users")

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)

@UserBlueprint.route("/")
class UserList(UserBlueprint.MethodView):
    @UserBlueprint.response(200, UserSchema(many=True))
    def get(self):
        """List all users"""
        return UserModel.query.all()

    @UserBlueprint.arguments(UserSchema)
    @UserBlueprint.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user"""
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(409, message="Username already exists.")
            
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

@UserBlueprint.route("/<int:user_id>")
class UserResource(UserBlueprint.MethodView):
    @UserBlueprint.response(200, UserSchema)
    def get(self, user_id):
        """Get user by ID"""
        user = db.session.get(UserModel, user_id)
        if not user:
            abort(404, message="User not found.")
        return user
