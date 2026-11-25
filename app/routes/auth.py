from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.models import User, StudentProfile


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route("/")
def landing():
    return render_template("landing.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "").strip()
        academic_year = request.form.get("academic_year", "").strip()

        if len(name) < 2 or "@" not in email or len(password) < 8:
            flash("Enter a valid name, email, and a password of at least 8 characters.", "danger")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        db.session.add(StudentProfile(
            user_id=user.id, name=name, college=college,
            branch=branch, academic_year=academic_year,
        ))
        db.session.commit()
        session["user_id"] = user.id
        session["user_name"] = name
        return redirect(url_for("careers.select_career"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        session["user_id"] = user.id
        session["user_name"] = user.profile.name if user.profile else "Student"
        flash("Welcome back.", "success")
        return redirect(url_for("dashboard.overview"))
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.landing"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile = StudentProfile.query.filter_by(user_id=session["user_id"]).first()
    if request.method == "POST":
        profile.name = request.form.get("name", "").strip()
        profile.college = request.form.get("college", "").strip()
        profile.branch = request.form.get("branch", "").strip()
        profile.academic_year = request.form.get("academic_year", "").strip()
        if len(profile.name) < 2:
            flash("Name must contain at least 2 characters.", "danger")
            return render_template("profile.html", profile=profile)
        db.session.commit()
        session["user_name"] = profile.name
        flash("Profile updated successfully.", "success")
    return render_template("profile.html", profile=profile)
