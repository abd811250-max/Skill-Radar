from app.services.skill_engine import career_match, combine_assessment_scores, quiz_score_to_level


class Requirement:
    def __init__(self, skill_id, target_level, weight):
        self.skill_id = skill_id
        self.target_level = target_level
        self.weight = weight


def test_combined_assessment_formula():
    final_level, verified = combine_assessment_scores(4, 5)
    assert final_level == 5
    assert verified is True


def test_unverified_assessment():
    final_level, verified = combine_assessment_scores(3, None)
    assert final_level == 3
    assert verified is False


def test_quiz_score_boundaries():
    assert quiz_score_to_level(0) == 1
    assert quiz_score_to_level(50) == 3
    assert quiz_score_to_level(100) == 5


def test_career_match_caps_skill_ratio():
    requirements = [
        Requirement(1, 4, 2),
        Requirement(2, 5, 3),
    ]
    levels = {1: 5, 2: 3}
    assert career_match(levels, requirements) == 76.0
