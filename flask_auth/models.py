from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Modelo simple de usuario: id, username, password_hash."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
