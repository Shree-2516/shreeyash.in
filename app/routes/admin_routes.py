import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import inspect, text
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.experience import Experience
from app.models.portfolio import PortfolioProfile
from app.models.project import Project
from app.models.skill import Skill
from app.models.user import User

admin = Blueprint('admin', __name__)


@admin.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("admin.login"))


@admin.before_request
def ensure_admin_account():
    if current_app.extensions.get("admin_bootstrap_complete"):
        return

    db.create_all()
    ensure_project_schema()
    User.ensure_admin(
        username=current_app.config["ADMIN_USERNAME"],
        password=current_app.config["ADMIN_PASSWORD"],
    )
    current_app.extensions["admin_bootstrap_complete"] = True


def ensure_project_schema():
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("project")}

    if "github_link" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN github_link VARCHAR(255)"))
    if "tech_stack" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN tech_stack VARCHAR(255)"))

    db.session.commit()


def allowed_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def save_project_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    destination = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file_storage.save(destination)
    return filename


@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username, is_admin=True).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@admin.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))


@admin.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    profile = PortfolioProfile.get_or_create()

    if request.method == "POST":
        profile.name = request.form.get("name", "").strip()
        profile.tagline = request.form.get("tagline", "").strip()
        profile.location = request.form.get("location", "").strip()
        profile.internship_status = request.form.get("internship_status", "").strip()
        profile.tech_stack_summary = request.form.get("tech_stack_summary", "").strip()
        profile.leetcode_summary = request.form.get("leetcode_summary", "").strip()
        profile.about_summary = request.form.get("about_summary", "").strip()
        profile.linkedin_url = request.form.get("linkedin_url", "").strip()
        profile.github_url = request.form.get("github_url", "").strip()
        profile.email = request.form.get("email", "").strip()
        profile.resume_url = request.form.get("resume_url", "").strip()
        profile.degree = request.form.get("degree", "").strip()
        profile.university = request.form.get("university", "").strip()
        profile.coursework = request.form.get("coursework", "").strip()
        profile.achievements = request.form.get("achievements", "").strip()
        db.session.commit()
        flash("Portfolio content updated.", "success")
        return redirect(url_for("admin.dashboard"))

    projects = Project.query.all()
    skills = Skill.query.order_by(Skill.category.asc(), Skill.name.asc()).all()
    experiences = Experience.query.order_by(Experience.id.desc()).all()
    return render_template(
        "admin/dashboard.html",
        profile=profile,
        projects=projects,
        skills=skills,
        experiences=experiences,
    )

@admin.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        image = request.files.get("image")
        image_filename = None

        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Please upload a valid image file.", "error")
                return render_template("admin/add_project.html")
            image_filename = save_project_image(image)

        p = Project(
            title=request.form["title"].strip(),
            problem=request.form["problem"].strip(),
            solution=request.form["solution"].strip(),
            result=request.form["result"].strip(),
            github_link=request.form.get("github_link", "").strip(),
            tech_stack=request.form.get("tech_stack", "").strip(),
            image_filename=image_filename,
        )
        db.session.add(p)
        db.session.commit()
        flash("Project created.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_project.html")


@admin.route("/projects/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_project(id):
    project = db.session.get(Project, id)
    if project is None:
        flash("Project not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        image = request.files.get("image")

        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Please upload a valid image file.", "error")
                return render_template("admin/edit_project.html", project=project)

            if project.image_filename:
                old_image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], project.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            project.image_filename = save_project_image(image)

        project.title = request.form["title"].strip()
        project.tech_stack = request.form.get("tech_stack", "").strip()
        project.github_link = request.form.get("github_link", "").strip()
        project.problem = request.form["problem"].strip()
        project.solution = request.form["solution"].strip()
        project.result = request.form["result"].strip()
        db.session.commit()
        flash("Project updated.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/edit_project.html", project=project)


@admin.route("/skills/add", methods=["POST"])
@login_required
def add_skill():
    skill = Skill(
        category=request.form.get("category", "").strip(),
        name=request.form.get("name", "").strip(),
    )
    if not skill.name:
        flash("Skill name is required.", "error")
        return redirect(url_for("admin.dashboard"))

    db.session.add(skill)
    db.session.commit()
    flash("Skill added.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/skills/delete/<int:id>", methods=["POST"])
@login_required
def delete_skill(id):
    skill = db.session.get(Skill, id)
    if skill is None:
        flash("Skill not found.", "error")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(skill)
    db.session.commit()
    flash("Skill deleted.", "info")
    return redirect(url_for("admin.dashboard"))


@admin.route("/experience/add", methods=["POST"])
@login_required
def add_experience():
    experience = Experience(
        role=request.form.get("role", "").strip(),
        company=request.form.get("company", "").strip(),
        description=request.form.get("impact", "").strip(),
    )
    if not experience.role:
        flash("Experience role is required.", "error")
        return redirect(url_for("admin.dashboard"))

    db.session.add(experience)
    db.session.commit()
    flash("Experience added.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/experience/delete/<int:id>", methods=["POST"])
@login_required
def delete_experience(id):
    experience = db.session.get(Experience, id)
    if experience is None:
        flash("Experience not found.", "error")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(experience)
    db.session.commit()
    flash("Experience deleted.", "info")
    return redirect(url_for("admin.dashboard"))

@admin.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    p = db.session.get(Project, id)
    if p is None:
        flash("Project not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if p.image_filename:
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], p.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(p)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("admin.dashboard"))
