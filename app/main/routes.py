from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/healthz")
def healthz():
    return {"status": "ok", "service": "cvnova-ai"}


@bp.route("/about")
def about():
    return render_template("main/about.html")


@bp.route("/contact")
def contact():
    return render_template("main/contact.html")


@bp.route("/privacy")
def privacy():
    return render_template("main/privacy.html")


@bp.route("/terms")
def terms():
    return render_template("main/terms.html")
