from flask import Blueprint, render_template, session

from app import db
from app.models import StudentProfile, SkillAssessment, ProjectRecommendation, RoadmapItem
from app.routes.auth import login_required
from app.services.skill_engine import analyze_skills
from app.services.recommendation_engine import generate_recommendations


projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
@login_required
def projects():
    user_id = session["user_id"]
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    levels = {
        item.skill_id: item.final_level
        for item in SkillAssessment.query.filter_by(user_id=user_id).all()
    }
    requirements = profile.career.skills if profile and profile.career else []
    gaps, _ = analyze_skills(levels, requirements)
    roadmap_items = RoadmapItem.query.filter_by(user_id=user_id).all()
    if profile and profile.career:
        generate_recommendations(user_id, profile.career.slug, gaps, roadmap_items)
    recommendations = ProjectRecommendation.query.filter_by(user_id=user_id).all()
    return render_template(
        "projects.html", recommendations=recommendations,
        profile=profile, gaps=gaps,
    )
