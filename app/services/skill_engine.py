def quiz_score_to_level(score_percent):
    if score_percent <= 0:
        return 1
    if score_percent < 20:
        return 1
    if score_percent < 40:
        return 2
    if score_percent < 60:
        return 3
    if score_percent < 80:
        return 4
    return 5


def combine_assessment_scores(self_level, quiz_level=None):
    if quiz_level is None:
        return int(round(self_level)), False
    final_score = (0.40 * self_level) + (0.60 * quiz_level)
    return max(1, min(5, int(round(final_score)))), True


def career_match(profile_skill_levels, career_requirements):
    if not career_requirements:
        return 0.0
    weighted_sum = 0.0
    total_weight = 0
    for requirement in career_requirements:
        target = requirement.target_level
        weight = requirement.weight
        current = profile_skill_levels.get(requirement.skill_id, 0)
        ratio = min(current / target, 1.0) if target else 0.0
        weighted_sum += ratio * weight
        total_weight += weight
    if not total_weight:
        return 0.0
    return round((weighted_sum / total_weight) * 100, 1)


def analyze_skills(profile_skill_levels, career_requirements):
    gaps = []
    strengths = []
    for requirement in career_requirements:
        current = profile_skill_levels.get(requirement.skill_id, 0)
        gap = max(requirement.target_level - current, 0)
        item = {
            "skill_id": requirement.skill_id,
            "skill_name": requirement.skill.name,
            "current": current,
            "target": requirement.target_level,
            "gap": gap,
            "weight": requirement.weight,
            "priority": gap * requirement.weight,
        }
        if gap > 0:
            gaps.append(item)
        elif current >= requirement.target_level:
            strengths.append(item)
    gaps.sort(key=lambda item: (-item["priority"], -item["gap"], item["skill_name"]))
    strengths.sort(key=lambda item: (-item["current"], item["skill_name"]))
    return gaps, strengths
