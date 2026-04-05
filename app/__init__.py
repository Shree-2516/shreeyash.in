import os

from flask import Flask, flash, redirect, request, url_for
from werkzeug.exceptions import RequestEntityTooLarge

from .config import Config
from .extensions import db, login_manager, migrate

def create_app(include_main=True, include_admin=True, admin_prefix="/admin"):
    app = Flask(__name__)
    app.config.from_object(Config)

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

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def bootstrap_database():
        if app.extensions.get("database_bootstrap_complete"):
            return
        db.create_all()
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
