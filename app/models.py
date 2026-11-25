from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    profile = db.relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    college = db.Column(db.String(180), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    academic_year = db.Column(db.String(30), nullable=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=True)

    user = db.relationship("User", back_populates="profile")
    career = db.relationship("Career")


class Career(db.Model):
    __tablename__ = "careers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)


class CareerSkill(db.Model):
    __tablename__ = "career_skills"
    __table_args__ = (
        db.UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),
    )

    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, index=True)
    target_level = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    career = db.relationship("Career", back_populates="skills")
    skill = db.relationship("Skill")


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, unique=True)
    title = db.Column(db.String(150), nullable=False)
    skill = db.relationship("Skill")
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    quiz = db.relationship("Quiz", back_populates="questions")
    options = db.relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(db.Model):
    __tablename__ = "question_options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)

    question = db.relationship("Question", back_populates="options")


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    __table_args__ = (
        db.UniqueConstraint("user_id", "quiz_id", name="uq_user_quiz_attempt"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)
    score_level = db.Column(db.Integer, nullable=False)
    attempted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    responses = db.relationship("QuizResponse", back_populates="attempt", cascade="all, delete-orphan")


class QuizResponse(db.Model):
    __tablename__ = "quiz_responses"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey("question_options.id"), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    attempt = db.relationship("QuizAttempt", back_populates="responses")


class SkillAssessment(db.Model):
    __tablename__ = "skill_assessments"
    __table_args__ = (
        db.UniqueConstraint("user_id", "skill_id", name="uq_user_skill_assessment"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, index=True)
    self_level = db.Column(db.Integer, nullable=False)
    quiz_level = db.Column(db.Integer, nullable=True)
    final_level = db.Column(db.Integer, nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    skill = db.relationship("Skill")


class AssessmentHistory(db.Model):
    __tablename__ = "assessment_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False, index=True)
    self_level = db.Column(db.Integer, nullable=False)
    quiz_level = db.Column(db.Integer, nullable=True)
    final_level = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    skill = db.relationship("Skill")


class RoadmapItem(db.Model):
    __tablename__ = "roadmap_items"
    __table_args__ = (
        db.UniqueConstraint("user_id", "skill_id", name="uq_user_roadmap_skill"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    recommended_project = db.Column(db.String(180), nullable=False)
    estimated_duration = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="To Do")
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    skill = db.relationship("Skill")


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    learning_outcome = db.Column(db.Text, nullable=False)
    career_slug = db.Column(db.String(100), nullable=True)
    project_skills = db.relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan")


class ProjectSkill(db.Model):
    __tablename__ = "project_skills"
    __table_args__ = (
        db.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),
    )

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)

    project = db.relationship("Project", back_populates="project_skills")
    skill = db.relationship("Skill")


class ProjectRecommendation(db.Model):
    __tablename__ = "project_recommendations"
    __table_args__ = (
        db.UniqueConstraint("user_id", "project_id", name="uq_user_project_recommendation"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    project = db.relationship("Project")
