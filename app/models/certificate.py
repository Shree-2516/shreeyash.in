from app.extensions import db
from app.services.cloudinary_storage import build_media_url

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.String(100))
    credential_id = db.Column(db.String(255))
    credential_url = db.Column(db.String(255))
    image_filename = db.Column(db.String(255))
    image_public_id = db.Column(db.String(255))
    skills_covered = db.Column(db.String(255))
    featured = db.Column(db.Boolean, default=False, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "organization": self.organization,
            "issue_date": self.issue_date,
            "credential_id": self.credential_id,
            "credential_url": self.credential_url,
            "image_filename": self.image_filename,
            "skills_covered": self.skills_covered,
            "featured": self.featured,
            "display_order": self.display_order
        }

    @property
    def image_url(self):
        return build_media_url(
            public_id=self.image_public_id,
            filename=self.image_filename,
            local_prefix="uploads/projects",
        )
