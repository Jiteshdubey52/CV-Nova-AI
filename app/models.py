from __future__ import annotations

from datetime import datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default=Role.USER.value, nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    google_sub = db.Column(db.String(255), unique=True)
    headline = db.Column(db.String(180), default="")
    resumes = db.relationship("Resume", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return bool(self.password_hash and check_password_hash(self.password_hash, password))

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value


class Resume(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    target_role = db.Column(db.String(160), default="")
    template = db.Column(db.String(80), default="nova", nullable=False)
    content = db.Column(db.JSON, nullable=False, default=dict)
    ats_score = db.Column(db.Integer, default=0, nullable=False)
    user = db.relationship("User", back_populates="resumes")
    versions = db.relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resume.id"), nullable=False, index=True)
    label = db.Column(db.String(120), nullable=False)
    content = db.Column(db.JSON, nullable=False)
    ats_score = db.Column(db.Integer, default=0, nullable=False)
    resume = db.relationship("Resume", back_populates="versions")


class GeneratedDocument(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resume.id"))
    kind = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    body = db.Column(db.Text, nullable=False)


class AuditLog(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(64), default="")


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))
