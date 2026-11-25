from app import db
from app.models import Project, ProjectRecommendation


def generate_recommendations(user_id, career_slug, gaps, roadmap_items):
    ProjectRecommendation.query.filter_by(user_id=user_id).delete()
    candidates = Project.query.filter(
        db.or_(Project.career_slug == career_slug, Project.career_slug.is_(None))
    ).all()
    gap_names = {gap["skill_name"] for gap in gaps}
    completed_skill_ids = {
        item.skill_id for item in roadmap_items if item.status == "Completed"
    }

    for project in candidates:
        required_names = {link.skill.name for link in project.project_skills}
        if required_names:
            missing = len(required_names & gap_names)
        else:
            missing = 0
        reason = f"{project.difficulty} project matching your selected career"
        if missing:
            reason += f" and {missing} identified skill gap{'s' if missing != 1 else ''}"
        db.session.add(ProjectRecommendation(user_id=user_id, project_id=project.id, reason=reason))
    db.session.commit()
