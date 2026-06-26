from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import inspect, text

from app.extensions import db
from app.models.experience import Experience
from app.models.portfolio import PortfolioProfile
from app.models.project import Project, ProjectImage
from app.models.skill import Skill
from app.models.user import User
from app.models.education import Education
from app.models.certificate import Certificate
from app.models.why_hire_me import WhyHireMe
from app.services.cloudinary_storage import cloudinary_enabled, delete_media, store_media

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
    if "image_public_id" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN image_public_id VARCHAR(255)"))
    if "slug" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN slug VARCHAR(200) UNIQUE"))
    if "short_description" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN short_description TEXT"))
    if "live_demo_link" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN live_demo_link VARCHAR(255)"))
    if "category" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN category VARCHAR(100)"))
    if "architecture" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN architecture TEXT"))
    if "challenges" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN challenges TEXT"))
    if "key_features" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN key_features TEXT"))
    if "featured_project" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN featured_project BOOLEAN DEFAULT FALSE"))
    if "display_order" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN display_order INTEGER DEFAULT 0"))
    if "project_status" not in columns:
        db.session.execute(text("ALTER TABLE project ADD COLUMN project_status VARCHAR(50) DEFAULT 'Completed'"))

    db.session.commit()

    # Automatically populate missing slugs for existing projects
    from app.models.project import Project
    projects_without_slug = Project.query.filter(Project.slug == None).all()
    if projects_without_slug:
        import re
        for p in projects_without_slug:
            slug = re.sub(r'[^a-z0-9]+', '-', p.title.lower()).strip('-')
            exists = Project.query.filter_by(slug=slug).first()
            if exists:
                slug = f"{slug}-{p.id}"
            p.slug = slug
        db.session.commit()


def ensure_portfolio_schema():
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("portfolio_profile")}

    if "profile_photo_filename" not in columns:
        db.session.execute(text("ALTER TABLE portfolio_profile ADD COLUMN profile_photo_filename VARCHAR(255)"))
    if "profile_photo_public_id" not in columns:
        db.session.execute(text("ALTER TABLE portfolio_profile ADD COLUMN profile_photo_public_id VARCHAR(255)"))
    if "resume_filename" not in columns:
        db.session.execute(text("ALTER TABLE portfolio_profile ADD COLUMN resume_filename VARCHAR(255)"))
    if "resume_public_id" not in columns:
        db.session.execute(text("ALTER TABLE portfolio_profile ADD COLUMN resume_public_id VARCHAR(255)"))
    if "system_metrics" not in columns:
        db.session.execute(text("ALTER TABLE portfolio_profile ADD COLUMN system_metrics TEXT"))
        db.session.execute(text("UPDATE portfolio_profile SET system_metrics = 'Python: 90\nFlask: 80\nMachine Learning: 80\nSQL: 85\nAWS: 60' WHERE system_metrics IS NULL"))

    db.session.commit()


def ensure_certificate_schema():
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("certificate")}

    if "image_public_id" not in columns:
        db.session.execute(text("ALTER TABLE certificate ADD COLUMN image_public_id VARCHAR(255)"))

    db.session.commit()


def ensure_project_image_schema():
    inspector = inspect(db.engine)
    columns = {column["name"] for column in inspector.get_columns("project_image")}

    if "image_public_id" not in columns:
        db.session.execute(text("ALTER TABLE project_image ADD COLUMN image_public_id VARCHAR(255)"))

    db.session.commit()


def allowed_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def allowed_resume_file(filename):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in current_app.config["ALLOWED_RESUME_EXTENSIONS"]


def store_project_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    return store_media(
        file_storage,
        current_app.config["CLOUDINARY_PROJECT_FOLDER"],
        "UPLOAD_FOLDER",
    )


def store_profile_photo(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    return store_media(
        file_storage,
        current_app.config["CLOUDINARY_PROFILE_FOLDER"],
        "PROFILE_UPLOAD_FOLDER",
    )


def store_resume_file(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_resume_file(file_storage.filename):
        return None

    return store_media(
        file_storage,
        current_app.config["CLOUDINARY_RESUME_FOLDER"],
        "RESUME_UPLOAD_FOLDER",
        resource_type="raw",
    )


def store_certificate_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    return store_media(
        file_storage,
        current_app.config["CLOUDINARY_CERTIFICATE_FOLDER"],
        "UPLOAD_FOLDER",
    )


def remove_project_media(public_id=None, filename=None):
    delete_media(
        public_id=public_id,
        filename=filename,
        folder_key="UPLOAD_FOLDER",
    )


def remove_profile_photo(public_id=None, filename=None):
    delete_media(
        public_id=public_id,
        filename=filename,
        folder_key="PROFILE_UPLOAD_FOLDER",
    )


def remove_resume_file(public_id=None, filename=None):
    delete_media(
        public_id=public_id,
        filename=filename,
        folder_key="RESUME_UPLOAD_FOLDER",
        resource_type="raw",
    )


def build_dashboard_context(profile):
    return {
        "profile": profile,
        "projects": Project.query.order_by(Project.display_order.asc(), Project.id.desc()).all(),
        "skills": Skill.query.order_by(Skill.category.asc(), Skill.name.asc()).all(),
        "experiences": Experience.query.order_by(Experience.id.desc()).all(),
        "educations": Education.query.order_by(Education.display_order.asc(), Education.id.desc()).all(),
        "certificates": Certificate.query.order_by(Certificate.display_order.asc(), Certificate.id.desc()).all(),
        "why_hire_entries": WhyHireMe.query.order_by(WhyHireMe.display_order.asc(), WhyHireMe.id.asc()).all(),
    }


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
        profile_photo = request.files.get("profile_photo")
        resume_file = request.files.get("resume_file")
        remove_profile_photo_flag = request.form.get("remove_profile_photo") == "on"
        remove_resume_file_flag = request.form.get("remove_resume_file") == "on"

        if profile_photo and profile_photo.filename:
            if not allowed_file(profile_photo.filename):
                flash("Please upload a valid profile photo image file.", "error")
                return render_template("admin/dashboard.html", **build_dashboard_context(profile))
            remove_profile_photo(profile.profile_photo_public_id, profile.profile_photo_filename)
            upload_result = store_profile_photo(profile_photo)
            if upload_result:
                profile.profile_photo_filename = upload_result["filename"]
                profile.profile_photo_public_id = upload_result["public_id"]

        if remove_profile_photo_flag:
            remove_profile_photo(profile.profile_photo_public_id, profile.profile_photo_filename)
            profile.profile_photo_filename = None
            profile.profile_photo_public_id = None

        if resume_file and resume_file.filename:
            if not allowed_resume_file(resume_file.filename):
                flash("Please upload a PDF resume file.", "error")
                return render_template("admin/dashboard.html", **build_dashboard_context(profile))
            remove_resume_file(profile.resume_public_id, profile.resume_filename)
            upload_result = store_resume_file(resume_file)
            if upload_result:
                profile.resume_filename = upload_result["filename"]
                profile.resume_public_id = upload_result["public_id"]
                
                if cloudinary_enabled():
                    from app.services.cloudinary_storage import build_media_url
                    profile.resume_url = build_media_url(
                        public_id=upload_result["public_id"],
                        resource_type="raw"
                    )
                else:
                    profile.resume_url = upload_result.get("secure_url") or profile.resume_url

        if remove_resume_file_flag:
            remove_resume_file(profile.resume_public_id, profile.resume_filename)
            profile.resume_filename = None
            profile.resume_public_id = None

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
        
        # Only update resume_url from text field if no file was uploaded
        if not (resume_file and resume_file.filename):
            profile.resume_url = request.form.get("resume_url", "").strip()
            
        profile.degree = request.form.get("degree", "").strip()
        profile.university = request.form.get("university", "").strip()
        profile.coursework = request.form.get("coursework", "").strip()
        profile.achievements = request.form.get("achievements", "").strip()
        profile.system_metrics = request.form.get("system_metrics", "").strip()
        db.session.commit()
        flash("Portfolio content updated.", "success")
        return redirect(url_for("admin.dashboard"))

    if not cloudinary_enabled():
        flash("Warning: Cloudinary is not configured. Uploaded images will be stored locally on Render's temporary filesystem and will be lost on the next redeploy. Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in your environment variables.", "error")
    return render_template("admin/dashboard.html", **build_dashboard_context(profile))

@admin.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        image = request.files.get("image")
        image_filename = None
        image_public_id = None

        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Please upload a valid image file.", "error")
                return render_template("admin/add_project.html")
            upload_result = store_project_image(image)
            if upload_result:
                image_filename = upload_result["filename"]
                image_public_id = upload_result["public_id"]

        # Generate slug if not provided
        slug = request.form.get("slug", "").strip()
        if not slug:
            import re
            slug = re.sub(r'[^a-z0-9]+', '-', request.form["title"].lower()).strip('-')
            base_slug = slug
            counter = 1
            while Project.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

        p = Project(
            title=request.form["title"].strip(),
            slug=slug,
            short_description=request.form.get("short_description", "").strip(),
            live_demo_link=request.form.get("live_demo_link", "").strip(),
            category=request.form.get("category", "").strip(),
            architecture=request.form.get("architecture", "").strip(),
            challenges=request.form.get("challenges", "").strip(),
            key_features=request.form.get("key_features", "").strip(),
            featured_project=True if request.form.get("featured_project") == "on" else False,
            display_order=int(request.form.get("display_order", "0") or 0),
            project_status=request.form.get("project_status", "Completed").strip(),
            problem=request.form["problem"].strip(),
            solution=request.form["solution"].strip(),
            result=request.form["result"].strip(),
            github_link=request.form.get("github_link", "").strip(),
            tech_stack=request.form.get("tech_stack", "").strip(),
            image_filename=image_filename,
            image_public_id=image_public_id,
        )
        db.session.add(p)
        db.session.commit()

        # Handle image gallery uploads
        gallery_images = request.files.getlist("gallery_images")
        for file in gallery_images:
            if file and file.filename:
                if allowed_file(file.filename):
                    upload_result = store_project_image(file)
                    if upload_result:
                        img = ProjectImage(
                            project_id=p.id,
                            image_filename=upload_result["filename"],
                            image_public_id=upload_result["public_id"],
                        )
                        db.session.add(img)
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

            remove_project_media(project.image_public_id, project.image_filename)
            upload_result = store_project_image(image)
            if upload_result:
                project.image_filename = upload_result["filename"]
                project.image_public_id = upload_result["public_id"]

        # Generate slug if empty
        slug = request.form.get("slug", "").strip()
        if not slug:
            import re
            slug = re.sub(r'[^a-z0-9]+', '-', request.form["title"].lower()).strip('-')
            base_slug = slug
            counter = 1
            while Project.query.filter(Project.slug == slug, Project.id != project.id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

        project.title = request.form["title"].strip()
        project.slug = slug
        project.short_description = request.form.get("short_description", "").strip()
        project.live_demo_link = request.form.get("live_demo_link", "").strip()
        project.category = request.form.get("category", "").strip()
        project.architecture = request.form.get("architecture", "").strip()
        project.challenges = request.form.get("challenges", "").strip()
        project.key_features = request.form.get("key_features", "").strip()
        project.featured_project = True if request.form.get("featured_project") == "on" else False
        project.display_order = int(request.form.get("display_order", "0") or 0)
        project.project_status = request.form.get("project_status", "Completed").strip()
        project.tech_stack = request.form.get("tech_stack", "").strip()
        project.github_link = request.form.get("github_link", "").strip()
        project.problem = request.form["problem"].strip()
        project.solution = request.form["solution"].strip()
        project.result = request.form["result"].strip()

        # Handle image gallery deletions
        delete_ids = request.form.getlist("delete_images")
        for img_id in delete_ids:
            img = db.session.get(ProjectImage, int(img_id))
            if img:
                remove_project_media(img.image_public_id, img.image_filename)
                db.session.delete(img)

        # Handle new image gallery uploads
        gallery_images = request.files.getlist("gallery_images")
        for file in gallery_images:
            if file and file.filename:
                if allowed_file(file.filename):
                    upload_result = store_project_image(file)
                    if upload_result:
                        img = ProjectImage(
                            project_id=project.id,
                            image_filename=upload_result["filename"],
                            image_public_id=upload_result["public_id"],
                        )
                        db.session.add(img)

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

    remove_project_media(p.image_public_id, p.image_filename)
    for img in p.images:
        remove_project_media(img.image_public_id, img.image_filename)

    db.session.delete(p)
    db.session.commit()
    flash("Project deleted.", "info")
    return redirect(url_for("admin.dashboard"))


@admin.route("/education/add", methods=["GET", "POST"])
@login_required
def add_education():
    if request.method == "POST":
        edu = Education(
            education_type=request.form.get("education_type", "").strip(),
            institution=request.form.get("institution", "").strip(),
            program=request.form.get("program", "").strip(),
            specialization=request.form.get("specialization", "").strip(),
            start_year=request.form.get("start_year", "").strip(),
            end_year=request.form.get("end_year", "").strip(),
            current_education=True if request.form.get("current_education") == "on" else False,
            description=request.form.get("description", "").strip(),
            display_order=int(request.form.get("display_order", "0") or 0),
            featured=True if request.form.get("featured") == "on" else False
        )
        db.session.add(edu)
        db.session.commit()
        flash("Education entry added successfully.", "success")
        return redirect(url_for("admin.dashboard") + "#education")
    return render_template("admin/add_education.html")


@admin.route("/education/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_education(id):
    edu = db.session.get(Education, id)
    if edu is None:
        flash("Education record not found.", "error")
        return redirect(url_for("admin.dashboard") + "#education")

    if request.method == "POST":
        edu.education_type = request.form.get("education_type", "").strip()
        edu.institution = request.form.get("institution", "").strip()
        edu.program = request.form.get("program", "").strip()
        edu.specialization = request.form.get("specialization", "").strip()
        edu.start_year = request.form.get("start_year", "").strip()
        edu.end_year = request.form.get("end_year", "").strip()
        edu.current_education = True if request.form.get("current_education") == "on" else False
        edu.description = request.form.get("description", "").strip()
        edu.display_order = int(request.form.get("display_order", "0") or 0)
        edu.featured = True if request.form.get("featured") == "on" else False

        db.session.commit()
        flash("Education record updated successfully.", "success")
        return redirect(url_for("admin.dashboard") + "#education")

    return render_template("admin/edit_education.html", education=edu)


@admin.route("/education/delete/<int:id>", methods=["POST"])
@login_required
def delete_education(id):
    edu = db.session.get(Education, id)
    if edu is None:
        flash("Education record not found.", "error")
        return redirect(url_for("admin.dashboard") + "#education")

    db.session.delete(edu)
    db.session.commit()
    flash("Education record deleted.", "info")
    return redirect(url_for("admin.dashboard") + "#education")


@admin.route("/certificate/add", methods=["GET", "POST"])
@login_required
def add_certificate():
    if request.method == "POST":
        image = request.files.get("image")
        image_filename = None
        image_public_id = None
        if image and image.filename:
            if allowed_file(image.filename):
                upload_result = store_certificate_image(image)
                if upload_result:
                    image_filename = upload_result["filename"]
                    image_public_id = upload_result["public_id"]

        cert = Certificate(
            name=request.form.get("name", "").strip(),
            organization=request.form.get("organization", "").strip(),
            issue_date=request.form.get("issue_date", "").strip(),
            credential_id=request.form.get("credential_id", "").strip(),
            credential_url=request.form.get("credential_url", "").strip(),
            skills_covered=request.form.get("skills_covered", "").strip(),
            featured=True if request.form.get("featured") == "on" else False,
            display_order=int(request.form.get("display_order", "0") or 0),
            image_filename=image_filename,
            image_public_id=image_public_id,
        )
        db.session.add(cert)
        db.session.commit()
        flash("Certificate added successfully.", "success")
        return redirect(url_for("admin.dashboard") + "#certificates")
    return render_template("admin/add_certificate.html")


@admin.route("/certificate/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_certificate(id):
    cert = db.session.get(Certificate, id)
    if cert is None:
        flash("Certificate not found.", "error")
        return redirect(url_for("admin.dashboard") + "#certificates")

    if request.method == "POST":
        image = request.files.get("image")
        if image and image.filename:
            if allowed_file(image.filename):
                remove_project_media(cert.image_public_id, cert.image_filename)
                upload_result = store_certificate_image(image)
                if upload_result:
                    cert.image_filename = upload_result["filename"]
                    cert.image_public_id = upload_result["public_id"]

        cert.name = request.form.get("name", "").strip()
        cert.organization = request.form.get("organization", "").strip()
        cert.issue_date = request.form.get("issue_date", "").strip()
        cert.credential_id = request.form.get("credential_id", "").strip()
        cert.credential_url = request.form.get("credential_url", "").strip()
        cert.skills_covered = request.form.get("skills_covered", "").strip()
        cert.featured = True if request.form.get("featured") == "on" else False
        cert.display_order = int(request.form.get("display_order", "0") or 0)

        db.session.commit()
        flash("Certificate updated successfully.", "success")
        return redirect(url_for("admin.dashboard") + "#certificates")

    return render_template("admin/edit_certificate.html", certificate=cert)


@admin.route("/certificate/delete/<int:id>", methods=["POST"])
@login_required
def delete_certificate(id):
    cert = db.session.get(Certificate, id)
    if cert is None:
        flash("Certificate not found.", "error")
        return redirect(url_for("admin.dashboard") + "#certificates")

    if cert.image_filename:
        remove_project_media(cert.image_public_id, cert.image_filename)

    db.session.delete(cert)
    db.session.commit()
    flash("Certificate deleted.", "info")
    return redirect(url_for("admin.dashboard") + "#certificates")


@admin.route("/why_hire_me/add", methods=["GET", "POST"])
@login_required
def add_why_hire_me():
    if request.method == "POST":
        entry = WhyHireMe(
            title=request.form.get("title", "").strip(),
            icon=request.form.get("icon", "").strip(),
            points=request.form.get("points", "").strip(),
            display_order=int(request.form.get("display_order", "0") or 0)
        )
        db.session.add(entry)
        db.session.commit()
        flash("Why Hire Me card added successfully.", "success")
        return redirect(url_for("admin.dashboard") + "#why-hire-me")
    return render_template("admin/add_why_hire.html")


@admin.route("/why_hire_me/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_why_hire_me(id):
    entry = db.session.get(WhyHireMe, id)
    if entry is None:
        flash("Card not found.", "error")
        return redirect(url_for("admin.dashboard") + "#why-hire-me")

    if request.method == "POST":
        entry.title = request.form.get("title", "").strip()
        entry.icon = request.form.get("icon", "").strip()
        entry.points = request.form.get("points", "").strip()
        entry.display_order = int(request.form.get("display_order", "0") or 0)

        db.session.commit()
        flash("Why Hire Me card updated successfully.", "success")
        return redirect(url_for("admin.dashboard") + "#why-hire-me")

    return render_template("admin/edit_why_hire.html", entry=entry)


@admin.route("/why_hire_me/delete/<int:id>", methods=["POST"])
@login_required
def delete_why_hire_me(id):
    entry = db.session.get(WhyHireMe, id)
    if entry is None:
        flash("Card not found.", "error")
        return redirect(url_for("admin.dashboard") + "#why-hire-me")

    db.session.delete(entry)
    db.session.commit()
    flash("Why Hire Me card deleted successfully.", "info")
    return redirect(url_for("admin.dashboard") + "#why-hire-me")
