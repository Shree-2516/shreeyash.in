from app.extensions import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    github_link = db.Column(db.String(255))
    tech_stack = db.Column(db.String(255))
    image_filename = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "problem": self.problem,
            "solution": self.solution,
            "result": self.result,
            "github_link": self.github_link,
            "tech_stack": self.tech_stack,
            "image_url": self.image_url,
        }

    @property
    def image_url(self):
        if not self.image_filename:
            return None
        return f"/static/uploads/projects/{self.image_filename}"
