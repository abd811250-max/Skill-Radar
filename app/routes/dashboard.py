from flask import Blueprint, render_template, session

from app import db
from app.models import (
    StudentProfile, SkillAssessment, AssessmentHistory, RoadmapItem,
)
from app.routes.auth import login_required
from app.services.skill_engine import career_match, analyze_skills


dashboard_bp = Blueprint("dashboard", __name__)


def dashboard_context(user_id):
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    assessments = SkillAssessment.query.filter_by(user_id=user_id).all()
    levels = {item.skill_id: item.final_level for item in assessments}
    requirements = profile.career.skills if profile and profile.career else []
    match = career_match(levels, requirements)
    gaps, strengths = analyze_skills(levels, requirements)
    overall = round(sum(levels.values()) / len(levels), 1) if levels else 0
    roadmap = RoadmapItem.query.filter_by(user_id=user_id).all()
    completed = sum(1 for item in roadmap if item.status == "Completed")
    progress = round((completed / len(roadmap)) * 100, 1) if roadmap else 0
    return profile, assessments, levels, requirements, match, gaps, strengths, overall, roadmap, progress


@dashboard_bp.route("/dashboard")
@login_required
def overview():
    context = dashboard_context(session["user_id"])
    profile, assessments, levels, requirements, match, gaps, strengths, overall, roadmap, progress = context
    history = AssessmentHistory.query.filter_by(user_id=session["user_id"]).order_by(
        AssessmentHistory.recorded_at.desc()
    ).limit(8).all()
    return render_template(
        "dashboard.html",
        profile=profile, assessments=assessments, levels=levels,
        requirements=requirements, match=match, gaps=gaps,
        strengths=strengths, overall=overall, roadmap=roadmap,
        progress=progress, history=history,
    )


@dashboard_bp.route("/skills")
@login_required
def skills():
    context = dashboard_context(session["user_id"])
    profile, assessments, levels, requirements, match, gaps, strengths, overall, roadmap, progress = context
    return render_template("skills.html", assessments=assessments, profile=profile,
                           gaps=gaps, strengths=strengths)


@dashboard_bp.route("/career-match")
@login_required
def career_match_page():
    context = dashboard_context(session["user_id"])
    profile, assessments, levels, requirements, match, gaps, strengths, overall, roadmap, progress = context
    calculation_rows = []
    total_weight = 0
    weighted_sum = 0
    for requirement in requirements:
        current = levels.get(requirement.skill_id, 0)
        ratio = min(current / requirement.target_level, 1.0) if requirement.target_level else 0
        weighted_sum += ratio * requirement.weight
        total_weight += requirement.weight
        calculation_rows.append({
            "skill": requirement.skill.name,
            "current": current,
            "target": requirement.target_level,
            "weight": requirement.weight,
            "ratio": ratio,
        })
    return render_template(
        "career_match.html", profile=profile, match=match, requirements=requirements,
        levels=levels, gaps=gaps, strengths=strengths,
        calculation_rows=calculation_rows, weighted_sum=weighted_sum,
        total_weight=total_weight,
    )


@dashboard_bp.route("/gaps")
@login_required
def gaps():
    context = dashboard_context(session["user_id"])
    profile, assessments, levels, requirements, match, skill_gaps, strengths, overall, roadmap, progress = context
    return render_template(
        "gaps.html", profile=profile, levels=levels, requirements=requirements,
        gaps=skill_gaps, strengths=strengths,
    )


@dashboard_bp.route("/progress")
@login_required
def progress_page():
    user_id = session["user_id"]
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    assessments = AssessmentHistory.query.filter_by(user_id=user_id).order_by(
        AssessmentHistory.recorded_at.asc()
    ).all()
    roadmap = RoadmapItem.query.filter_by(user_id=user_id).all()
    completed = sum(1 for item in roadmap if item.status == "Completed")
    roadmap_progress = round((completed / len(roadmap)) * 100, 1) if roadmap else 0
    return render_template(
        "progress.html", profile=profile, assessments=assessments,
        roadmap=roadmap, roadmap_progress=roadmap_progress,
    )
