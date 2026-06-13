from app.extensions import db
from app.services.cloudinary_storage import build_media_url

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    github_link = db.Column(db.String(255))
    tech_stack = db.Column(db.String(255))
    image_filename = db.Column(db.String(255))
    image_public_id = db.Column(db.String(255))
    
    # New Fields
    slug = db.Column(db.String(200), unique=True, nullable=True)
    short_description = db.Column(db.Text)
    live_demo_link = db.Column(db.String(255))
    category = db.Column(db.String(100))
    architecture = db.Column(db.Text)
    challenges = db.Column(db.Text)
    key_features = db.Column(db.Text)
    featured_project = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    project_status = db.Column(db.String(50), default="Completed")

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
            "slug": self.slug,
            "short_description": self.short_description,
            "live_demo_link": self.live_demo_link,
            "category": self.category,
            "architecture": self.architecture,
            "challenges": self.challenges,
            "key_features": self.key_features,
            "featured_project": self.featured_project,
            "display_order": self.display_order,
            "project_status": self.project_status,
        }

    @property
    def image_url(self):
        return build_media_url(
            public_id=self.image_public_id,
            filename=self.image_filename,
            local_prefix="uploads/projects",
        )


class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    image_public_id = db.Column(db.String(255))

    project = db.relationship('Project', backref=db.backref('images', lazy=True, cascade='all, delete-orphan'))

    @property
    def image_url(self):
        return build_media_url(
            public_id=self.image_public_id,
            filename=self.image_filename,
            local_prefix="uploads/projects",
        )
