from app.extensions import db

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    education_type = db.Column(db.String(50), nullable=False) # SSC, HSC, Diploma, Degree, Master's, Other
    institution = db.Column(db.String(255), nullable=False)
    program = db.Column(db.String(255))
    specialization = db.Column(db.String(255))
    start_year = db.Column(db.String(50))
    end_year = db.Column(db.String(50))
    current_education = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "education_type": self.education_type,
            "institution": self.institution,
            "program": self.program,
            "specialization": self.specialization,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "current_education": self.current_education,
            "description": self.description,
            "display_order": self.display_order,
            "featured": self.featured
        }
