from flask import Blueprint, jsonify, render_template
from app.models.experience import Experience
from app.models.portfolio import PortfolioProfile
from app.models.project import Project
from app.models.skill import Skill
from app.models.education import Education
from app.models.certificate import Certificate
from app.models.why_hire_me import WhyHireMe

main = Blueprint('main', __name__)

@main.route("/")
def home():
    profile = PortfolioProfile.get_or_create()
    projects = Project.query.order_by(Project.display_order.asc(), Project.id.desc()).all()
    experiences = Experience.query.all()
    skills = Skill.query.all()
    educations = Education.query.order_by(Education.display_order.asc(), Education.id.desc()).all()
    certificates = Certificate.query.order_by(Certificate.display_order.asc(), Certificate.id.desc()).all()
    why_hire_entries = WhyHireMe.query.order_by(WhyHireMe.display_order.asc(), WhyHireMe.id.asc()).all()

    return render_template("index.html",
                           profile=profile,
                           projects=projects,
                           experiences=experiences,
                           skills=skills,
                           educations=educations,
                           certificates=certificates,
                           why_hire_entries=why_hire_entries)


@main.route("/health")
def health():
    return "OK", 200


@main.route("/journey")
def journey():
    profile = PortfolioProfile.get_or_create()
    return render_template("journey.html", profile=profile)


@main.route("/api/projects")
def api_projects():
    projects = Project.query.order_by(Project.display_order.asc(), Project.id.desc()).all()
    return jsonify([project.to_dict() for project in projects])


@main.route("/project/<slug>")
def project_detail(slug):
    profile = PortfolioProfile.get_or_create()
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template("project_detail.html", profile=profile, project=project)
