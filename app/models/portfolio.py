from app.extensions import db


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

    @classmethod
    def get_or_create(cls):
        profile = cls.query.first()
        if profile is None:
            profile = cls()
            db.session.add(profile)
            db.session.commit()
        return profile
