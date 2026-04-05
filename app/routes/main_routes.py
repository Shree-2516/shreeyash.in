from flask import Blueprint, jsonify, render_template
from app.models.experience import Experience
from app.models.portfolio import PortfolioProfile
from app.models.project import Project
from app.models.skill import Skill

main = Blueprint('main', __name__)

@main.route("/")
def home():
    profile = PortfolioProfile.get_or_create()
    projects = Project.query.all()
    experiences = Experience.query.all()
    skills = Skill.query.all()

    return render_template("index.html",
                           profile=profile,
                           projects=projects,
                           experiences=experiences,
                           skills=skills)


@main.route("/journey")
def journey():
    profile = PortfolioProfile.get_or_create()
    return render_template("journey.html", profile=profile)


@main.route("/api/projects")
def api_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify([project.to_dict() for project in projects])
