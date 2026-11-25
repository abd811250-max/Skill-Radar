from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.models import (
    Skill, SkillAssessment, AssessmentHistory, Quiz, QuizAttempt,
    QuizResponse, StudentProfile, QuestionOption,
)
from app.routes.auth import login_required
from app.services.skill_engine import combine_assessment_scores, quiz_score_to_level


assessment_bp = Blueprint("assessment", __name__)


@assessment_bp.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    user_id = session["user_id"]
    if request.method == "POST":
        skill_id = request.form.get("skill_id", type=int)
        self_level = request.form.get("self_level", type=int)
        skill = db.session.get(Skill, skill_id)
        if not skill or self_level not in range(1, 6):
            flash("Select a valid skill and rating.", "danger")
            return redirect(url_for("assessment.assessment"))

        existing = SkillAssessment.query.filter_by(user_id=user_id, skill_id=skill_id).first()
        quiz_attempt = QuizAttempt.query.join(Quiz).filter(
            QuizAttempt.user_id == user_id,
            Quiz.skill_id == skill_id,
        ).first()
        quiz_level = quiz_attempt.score_level if quiz_attempt else None
        final_level, is_verified = combine_assessment_scores(self_level, quiz_level)

        if existing:
            existing.self_level = self_level
            existing.quiz_level = quiz_level
            existing.final_level = final_level
            existing.is_verified = is_verified
        else:
            db.session.add(SkillAssessment(
                user_id=user_id, skill_id=skill_id, self_level=self_level,
                quiz_level=quiz_level, final_level=final_level,
                is_verified=is_verified,
            ))
        db.session.add(AssessmentHistory(
            user_id=user_id, skill_id=skill_id, self_level=self_level,
            quiz_level=quiz_level, final_level=final_level,
        ))
        db.session.commit()
        flash(f"{skill.name} assessment saved.", "success")
        return redirect(url_for("assessment.assessment"))

    skills = Skill.query.order_by(Skill.name).all()
    assessments = {
        item.skill_id: item
        for item in SkillAssessment.query.filter_by(user_id=user_id).all()
    }
    return render_template("assessment.html", skills=skills, assessments=assessments)


@assessment_bp.route("/quizzes")
@login_required
def quizzes():
    quizzes = Quiz.query.join(Skill).order_by(Skill.name).all()
    attempted_ids = {
        attempt.quiz_id for attempt in QuizAttempt.query.filter_by(user_id=session["user_id"]).all()
    }
    return render_template("quizzes.html", quizzes=quizzes, attempted_ids=attempted_ids)


@assessment_bp.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def take_quiz(quiz_id):
    user_id = session["user_id"]
    quiz = db.session.get(Quiz, quiz_id)
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for("assessment.quizzes"))

    existing = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if request.method == "GET" and existing:
        flash("You have already completed this quiz.", "warning")
        return redirect(url_for("assessment.quiz_result", quiz_id=quiz_id))
    if request.method == "POST" and existing:
        flash("This quiz can only be submitted once.", "warning")
        return redirect(url_for("assessment.quiz_result", quiz_id=quiz_id))

    if request.method == "POST":
        answers = []
        correct_count = 0
        for question in quiz.questions:
            selected_id = request.form.get(f"question_{question.id}", type=int)
            if not selected_id:
                flash("Answer every question before submitting.", "danger")
                return render_template("quiz.html", quiz=quiz)
            selected = db.session.get(QuestionOption, selected_id)
            if not selected or selected.question_id != question.id:
                flash("An invalid answer was submitted.", "danger")
                return render_template("quiz.html", quiz=quiz)
            is_correct = selected.is_correct
            correct_count += int(is_correct)
            answers.append((question, selected, is_correct))

        score = round((correct_count / len(quiz.questions)) * 100, 1) if quiz.questions else 0
        level = quiz_score_to_level(score)
        attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id, score=score, score_level=level)
        db.session.add(attempt)
        db.session.flush()
        for question, selected, is_correct in answers:
            db.session.add(QuizResponse(
                attempt_id=attempt.id, question_id=question.id,
                selected_option_id=selected.id, is_correct=is_correct,
            ))

        assessment = SkillAssessment.query.filter_by(user_id=user_id, skill_id=quiz.skill_id).first()
        if assessment:
            final_level, verified = combine_assessment_scores(assessment.self_level, level)
            assessment.quiz_level = level
            assessment.final_level = final_level
            assessment.is_verified = verified
            db.session.add(AssessmentHistory(
                user_id=user_id, skill_id=quiz.skill_id,
                self_level=assessment.self_level, quiz_level=level,
                final_level=final_level,
            ))
        else:
            db.session.add(SkillAssessment(
                user_id=user_id, skill_id=quiz.skill_id, self_level=level,
                quiz_level=level, final_level=level, is_verified=True,
            ))
            db.session.add(AssessmentHistory(
                user_id=user_id, skill_id=quiz.skill_id,
                self_level=level, quiz_level=level, final_level=level,
            ))
        db.session.commit()
        return redirect(url_for("assessment.quiz_result", quiz_id=quiz_id))

    return render_template("quiz.html", quiz=quiz)


@assessment_bp.route("/quiz/<int:quiz_id>/result")
@login_required
def quiz_result(quiz_id):
    attempt = QuizAttempt.query.filter_by(
        user_id=session["user_id"], quiz_id=quiz_id
    ).first()
    if not attempt:
        return redirect(url_for("assessment.quizzes"))
    quiz = db.session.get(Quiz, quiz_id)
    responses = {response.question_id: response for response in attempt.responses}
    return render_template("quiz_result.html", quiz=quiz, attempt=attempt, responses=responses)
