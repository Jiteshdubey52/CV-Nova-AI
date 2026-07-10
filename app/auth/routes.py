from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from app.auth.forms import LoginForm, RegisterForm, ResetPasswordForm, ResetRequestForm
from app.extensions import db, limiter, mail, oauth
from app.models import User
from app.services.security import token_serializer

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("12 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("An account already exists for that email.", "warning")
            return redirect(url_for("auth.login"))
        user = User(name=form.name.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_verification(user)
        login_user(user)
        flash("Welcome to CVNova AI. Check your inbox to verify your email.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per hour")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get("next") or url_for("dashboard.index"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/google")
def google_login():
    if "google" not in oauth._clients:
        flash("Google sign-in is not configured yet.", "warning")
        return redirect(url_for("auth.login"))
    return oauth.google.authorize_redirect(url_for("auth.google_callback", _external=True))


@bp.route("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    profile = oauth.google.parse_id_token(token)
    user = User.query.filter_by(google_sub=profile["sub"]).first() or User.query.filter_by(email=profile["email"].lower()).first()
    if not user:
        user = User(name=profile.get("name", "CVNova User"), email=profile["email"].lower(), google_sub=profile["sub"], is_email_verified=True)
        db.session.add(user)
    user.google_sub = profile["sub"]
    user.is_email_verified = True
    db.session.commit()
    login_user(user)
    return redirect(url_for("dashboard.index"))


@bp.route("/verify/<token>")
def verify_email(token: str):
    serializer = token_serializer(current_app.config["SECRET_KEY"])
    email = serializer.loads(token, salt="email-verify", max_age=86400)
    user = User.query.filter_by(email=email).first_or_404()
    user.is_email_verified = True
    db.session.commit()
    flash("Email verified.", "success")
    return redirect(url_for("dashboard.index"))


@bp.route("/password/reset", methods=["GET", "POST"])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset(user)
        flash("If an account exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_request.html", form=form)


@bp.route("/password/reset/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    serializer = token_serializer(current_app.config["SECRET_KEY"])
    email = serializer.loads(token, salt="password-reset", max_age=3600)
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


def send_verification(user: User) -> None:
    token = token_serializer(current_app.config["SECRET_KEY"]).dumps(user.email, salt="email-verify")
    send_mail(user.email, "Verify your CVNova AI account", url_for("auth.verify_email", token=token, _external=True))


def send_password_reset(user: User) -> None:
    token = token_serializer(current_app.config["SECRET_KEY"]).dumps(user.email, salt="password-reset")
    send_mail(user.email, "Reset your CVNova AI password", url_for("auth.reset_password", token=token, _external=True))


def send_mail(to: str, subject: str, body: str) -> None:
    if not current_app.config.get("MAIL_SERVER"):
        current_app.logger.info("%s: %s", subject, body)
        return
    mail.send(Message(subject=subject, recipients=[to], body=body))
