from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.models import StudentProfile, SkillAssessment, RoadmapItem
from app.routes.auth import login_required
from app.services.skill_engine import analyze_skills
from app.services.roadmap_engine import generate_roadmap


roadmap_bp = Blueprint("roadmap", __name__)


@roadmap_bp.route("/roadmap")
@login_required
def roadmap():
    user_id = session["user_id"]
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    levels = {
        item.skill_id: item.final_level
        for item in SkillAssessment.query.filter_by(user_id=user_id).all()
    }
    requirements = profile.career.skills if profile and profile.career else []
    gaps, _ = analyze_skills(levels, requirements)
    generate_roadmap(user_id, gaps)
    items = RoadmapItem.query.filter_by(user_id=user_id).order_by(RoadmapItem.priority.desc()).all()
    completed = sum(1 for item in items if item.status == "Completed")
    progress = round((completed / len(items)) * 100, 1) if items else 0
    return render_template("roadmap.html", items=items, progress=progress, profile=profile)


@roadmap_bp.route("/roadmap/<int:item_id>/status", methods=["POST"])
@login_required
def update_status(item_id):
    item = RoadmapItem.query.filter_by(id=item_id, user_id=session["user_id"]).first()
    status = request.form.get("status")
    if not item:
        flash("Roadmap item not found.", "danger")
        return redirect(url_for("roadmap.roadmap"))
    if status not in {"To Do", "In Progress", "Completed"}:
        flash("Invalid roadmap status.", "danger")
        return redirect(url_for("roadmap.roadmap"))
    item.status = status
    db.session.commit()
    flash("Roadmap progress updated.", "success")
    return redirect(url_for("roadmap.roadmap"))
