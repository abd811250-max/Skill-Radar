from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.models import Career, StudentProfile
from app.routes.auth import login_required


careers_bp = Blueprint("careers", __name__)


@careers_bp.route("/careers", methods=["GET", "POST"])
@login_required
def select_career():
    careers = Career.query.order_by(Career.name).all()
    profile = StudentProfile.query.filter_by(user_id=session["user_id"]).first()
    if request.method == "POST":
        career_id = request.form.get("career_id", type=int)
        career = db.session.get(Career, career_id)
        if not career:
            flash("Please select a valid career.", "danger")
        else:
            profile.career_id = career.id
            db.session.commit()
            flash(f"{career.name} selected as your target career.", "success")
            return redirect(url_for("assessment.assessment"))
    return render_template("careers.html", careers=careers, profile=profile)
