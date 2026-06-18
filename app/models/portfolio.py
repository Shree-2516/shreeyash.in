from app.extensions import db
from app.services.cloudinary_storage import build_media_url


class PortfolioProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, default="Shreeyash Paraj")
    tagline = db.Column(
        db.String(255),
        nullable=False,
        default="Software Engineer | Data Science Intern | Python Backend Developer",
    )
    location = db.Column(db.String(120), default="India")
    internship_status = db.Column(db.String(120), default="1 Internship")
    tech_stack_summary = db.Column(db.String(160), default="MERN + Python/AI")
    leetcode_summary = db.Column(db.String(120), default="200+")
    about_summary = db.Column(
        db.Text,
        default=(
            "I bridge the gap between robust Backend Architecture (MERN) and "
            "Intelligent Data Insights (AI/ML). Currently optimizing data pipelines "
            "as a Data Science Intern."
        ),
    )
    linkedin_url = db.Column(db.String(255), default="https://linkedin.com/in/your-profile")
    github_url = db.Column(db.String(255), default="https://github.com/your-username")
    email = db.Column(db.String(255), default="yourmail@example.com")
    resume_url = db.Column(db.String(255), default="/static/resume.pdf")
    profile_photo_filename = db.Column(db.String(255))
    profile_photo_public_id = db.Column(db.String(255))
    resume_filename = db.Column(db.String(255))
    resume_public_id = db.Column(db.String(255))
    degree = db.Column(db.String(255), default="Bachelor's Degree in Computer Science / Related Field")
    university = db.Column(db.String(255), default="Add your university name")
    coursework = db.Column(
        db.Text,
        default="Data Structures\nDatabase Management\nMachine Learning\nOperating Systems",
    )
    achievements = db.Column(
        db.Text,
        default=(
            "Completed Google Cloud and Vertex AI labs.\n"
            "Participated in hackathons and problem-solving competitions.\n"
            "Built and tested trading strategy ideas with Pine Script."
        ),
    )
    system_metrics = db.Column(
        db.Text,
        default="Python: 90\nFlask: 80\nMachine Learning: 80\nSQL: 85\nAWS: 60",
    )

    @property
    def system_metrics_list(self):
        if not self.system_metrics:
            return []
        metrics = []
        for line in self.system_metrics.split("\n"):
            line = line.strip()
            if ":" in line:
                name, pct = line.split(":", 1)
                try:
                    pct_val = int(pct.strip().replace("%", ""))
                    metrics.append({"name": name.strip(), "value": pct_val})
                except ValueError:
                    metrics.append({"name": name.strip(), "value": 0})
        return metrics

    @classmethod
    def get_or_create(cls):
        profile = cls.query.first()
        if profile is None:
            profile = cls()
            db.session.add(profile)
            db.session.commit()
        return profile

    @property
    def profile_photo_url(self):
        return build_media_url(
            public_id=self.profile_photo_public_id,
            filename=self.profile_photo_filename,
            local_prefix="uploads/profile",
            default_url="/static/profile_avatar.png",
        )

    @property
    def resume_link(self):
        if self.resume_public_id and self.resume_url and not self.resume_url.startswith("/static/"):
            return self.resume_url
        if self.resume_public_id:
            return build_media_url(
                public_id=self.resume_public_id,
                filename=self.resume_filename,
                local_prefix="uploads/resumes",
                resource_type="raw",
            )
        if self.resume_filename:
            return build_media_url(
                public_id=None,
                filename=self.resume_filename,
                local_prefix="uploads/resumes",
            )
        if self.resume_url:
            return self.resume_url
        return "/static/resume.pdf"
