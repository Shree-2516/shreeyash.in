from flask import Flask, flash, redirect, request, url_for
from werkzeug.exceptions import RequestEntityTooLarge

from .config import Config
from .extensions import db, login_manager, migrate
from .services.cloudinary_storage import configure_cloudinary

def create_app(include_main=True, include_admin=True, admin_prefix="/admin"):
    app = Flask(__name__)
    app.config.from_object(Config)
    configure_cloudinary(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    if include_admin:
        login_manager.login_view = "admin.login"
        login_manager.login_message_category = "info"

    from .models.user import User
    from .models.project import Project
    from .models.experience import Experience
    from .models.skill import Skill
    from .models.portfolio import PortfolioProfile
    from .models.education import Education
    from .models.certificate import Certificate
    from .models.why_hire_me import WhyHireMe
    from .routes.admin_routes import (
        ensure_certificate_schema,
        ensure_portfolio_schema,
        ensure_project_image_schema,
        ensure_project_schema,
    )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def bootstrap_database():
        if app.extensions.get("database_bootstrap_complete"):
            return
        db.create_all()
        ensure_project_schema()
        ensure_portfolio_schema()
        ensure_project_image_schema()
        ensure_certificate_schema()
        
        # Seed default WhyHireMe content if table is empty
        if WhyHireMe.query.count() == 0:
            for item in WhyHireMe.get_defaults():
                db.session.add(item)
            db.session.commit()

        app.extensions["database_bootstrap_complete"] = True

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(error):
        flash(
            f"Image is too large. Please upload a file smaller than {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)} MB.",
            "error",
        )

        if request.endpoint == "admin.edit_project":
            return redirect(request.url)
        if request.endpoint == "admin.add_project":
            return redirect(url_for("admin.add_project"))
        return redirect(request.referrer or "/")

    if include_main:
        from .routes.main_routes import main
        app.register_blueprint(main)

    if include_admin:
        from .routes.admin_routes import admin
        app.register_blueprint(admin, url_prefix=admin_prefix)

    return app
