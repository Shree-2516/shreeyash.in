from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def ensure_admin(cls, username, password):
        admin = cls.query.filter_by(username=username).first()
        if admin is None:
            admin = cls(username=username, is_admin=True)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
        return admin
