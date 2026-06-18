from app.extensions import db

class WhyHireMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(50), default="⚡")
    title = db.Column(db.String(150), nullable=False)
    points = db.Column(db.Text, nullable=False)  # newline-separated points
    display_order = db.Column(db.Integer, default=0)

    @classmethod
    def get_defaults(cls):
        return [
            cls(
                icon="⚡",
                title="Backend Engineering",
                points="REST APIs\nAuthentication\nPostgreSQL\nDatabase Design\nMicroservices\nFlask\nDjango\nFastAPI",
                display_order=1
            ),
            cls(
                icon="🤖",
                title="AI / Machine Learning",
                points="YOLOv8\nComputer Vision\nScikit-Learn\nPandas\nNumPy\nModel Training\nData Processing",
                display_order=2
            ),
            cls(
                icon="📈",
                title="Data Eng & Analytics",
                points="ETL Pipelines\nData Cleaning\nAnalytics\nData Visualization\nData Processing\nAutomation\nReporting",
                display_order=3
            )
        ]
