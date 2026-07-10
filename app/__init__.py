import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template

from app.config import config_by_name
from app.extensions import csrf, db, limiter, login_manager, mail, migrate, oauth


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    env = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    if app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET"):
        oauth.register(
            "google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    from app.admin.routes import bp as admin_bp
    from app.ai.routes import bp as ai_bp
    from app.auth.routes import bp as auth_bp
    from app.dashboard.routes import bp as dashboard_bp
    from app.main.routes import bp as main_bp
    from app.resumes.routes import bp as resumes_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(resumes_bp, url_prefix="/resumes")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="The page you requested does not exist."), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Unhandled application error: %s", error)
        return render_template("error.html", code=500, message="Something went wrong on our side."), 500

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    return app
