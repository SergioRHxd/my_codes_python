from datetime import datetime

from flask_login import UserMixin

from extensions import db


class User(UserMixin, db.Model):
    """Modelo de usuario: id, username, password_hash (+ fecha de registro)."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"
