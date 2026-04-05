from app.extensions import db

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(200))
    company = db.Column(db.String(200))
    description = db.Column(db.Text)