from app import db
from app.models import RoadmapItem


ROADMAP_DETAILS = {
    "Python": ("Python fundamentals and small automation projects", "A 3-project practice plan", "Build a CSV data cleaner"),
    "SQL": ("SQL querying and relational database design", "Database drills and reporting queries", "Create a sales reporting database"),
    "Excel": ("Excel formulas, tables, PivotTables, and charts", "Workbook exercises with real datasets", "Build an expense analysis workbook"),
    "Statistics": ("Descriptive statistics and probability", "Worked examples and interpretation exercises", "Analyze a public survey dataset"),
    "Web Development": ("HTML, CSS, JavaScript, and responsive UI", "Build progressively interactive web pages", "Build a responsive portfolio dashboard"),
    "Git": ("Git commits, branches, merges, and collaboration", "Practice a feature branch workflow", "Publish a versioned team project"),
    "Machine Learning": ("Data preparation, model training, and evaluation", "Notebook-based supervised learning exercises", "Train and compare churn prediction models"),
}


def generate_roadmap(user_id, gaps):
    for gap in gaps:
        existing = RoadmapItem.query.filter_by(user_id=user_id, skill_id=gap["skill_id"]).first()
        topic, description, project = ROADMAP_DETAILS.get(
            gap["skill_name"],
            (f"{gap['skill_name']} fundamentals", f"Study and practice core {gap['skill_name']} concepts.", f"Build a beginner {gap['skill_name']} project"),
        )
        duration = "2-3 weeks" if gap["gap"] >= 3 else "1-2 weeks"
        if existing:
            existing.priority = gap["priority"]
            existing.topic = topic
            existing.description = description
            existing.recommended_project = project
            existing.estimated_duration = duration
        else:
            db.session.add(RoadmapItem(
                user_id=user_id,
                skill_id=gap["skill_id"],
                priority=gap["priority"],
                topic=topic,
                description=description,
                recommended_project=project,
                estimated_duration=duration,
                status="To Do",
            ))
    db.session.commit()
