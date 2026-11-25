from app import db
from app.models import (
    Career, Skill, CareerSkill, Quiz, Question, QuestionOption,
    Project, ProjectSkill,
)


def seed_database():
    if Career.query.first():
        return

    skill_names = [
        "Python", "SQL", "Excel", "Statistics", "Web Development",
        "Git", "Machine Learning",
    ]
    skill_categories = {
        "Python": "Programming", "SQL": "Data", "Excel": "Tools",
        "Statistics": "Analytics", "Web Development": "Programming",
        "Git": "Tools", "Machine Learning": "AI",
    }
    skill_descriptions = {
        name: f"Applied knowledge and practical proficiency in {name}."
        for name in skill_names
    }
    skills = {}
    for name in skill_names:
        skill = Skill(name=name, category=skill_categories[name], description=skill_descriptions[name])
        db.session.add(skill)
        skills[name] = skill

    careers_data = {
        "Data Analyst": ("data-analyst", "Analyzes structured data to find trends and support decisions.", {
            "Python": (4, 5), "SQL": (5, 5), "Excel": (4, 4),
            "Statistics": (4, 5), "Machine Learning": (2, 2), "Git": (3, 2),
        }),
        "Web Developer": ("web-developer", "Builds responsive, accessible, and maintainable web applications.", {
            "Python": (3, 3), "SQL": (3, 3), "Web Development": (5, 5),
            "Git": (4, 4), "Statistics": (2, 1),
        }),
        "AI/ML Developer": ("ai-ml-developer", "Develops machine learning models and intelligent software systems.", {
            "Python": (5, 5), "SQL": (4, 3), "Statistics": (5, 5),
            "Machine Learning": (5, 5), "Git": (4, 3), "Web Development": (3, 2),
        }),
        "Python Developer": ("python-developer", "Creates reliable software, automation, APIs, and backend systems.", {
            "Python": (5, 5), "SQL": (4, 4), "Git": (4, 4),
            "Web Development": (3, 3), "Statistics": (3, 2),
        }),
        "Business Analyst": ("business-analyst", "Connects business needs with data-driven, practical solutions.", {
            "Excel": (5, 5), "SQL": (4, 4), "Statistics": (4, 4),
            "Python": (3, 3), "Machine Learning": (2, 1),
        }),
    }

    careers = {}
    for name, (slug, description, requirements) in careers_data.items():
        career = Career(name=name, slug=slug, description=description)
        db.session.add(career)
        careers[name] = career
        db.session.flush()
        for skill_name, (target, weight) in requirements.items():
            db.session.add(CareerSkill(
                career_id=career.id,
                skill_id=skills[skill_name].id,
                target_level=target,
                weight=weight,
            ))

    quiz_data = {
        "Python": [
            ("Which collection type preserves insertion order and allows duplicate values?", ["Set", "Dictionary", "List", "Tuple"], 2,
             "A list preserves insertion order and permits duplicate values."),
            ("What does len([2, 4, 6]) return?", ["2", "3", "6", "None"], 1,
             "The len function returns the number of elements, so the result is 3."),
            ("Which keyword begins a function definition in Python?", ["func", "define", "def", "function"], 2,
             "Python uses the def keyword to define a function."),
        ],
        "SQL": [
            ("Which clause filters grouped rows after aggregation?", ["WHERE", "HAVING", "ORDER BY", "GROUP BY"], 1,
             "HAVING filters grouped records, while WHERE filters rows before grouping."),
            ("Which join returns only matching rows from both tables?", ["LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "INNER JOIN"], 3,
             "An INNER JOIN returns rows that have matching values in both tables."),
            ("Which aggregate returns the number of rows?", ["SUM()", "AVG()", "COUNT()", "MAX()"], 2,
             "COUNT() calculates the number of rows or non-null values."),
        ],
        "Excel": [
            ("Which function totals a range of cells?", ["AVERAGE", "SUM", "COUNTIF", "CONCAT"], 1,
             "SUM adds the numeric values in a selected range."),
            ("What does a $ in an Excel cell reference create?", ["A chart", "A conditional format", "An absolute reference", "A formula error"], 2,
             "Dollar signs create absolute parts of a cell reference."),
            ("Which feature summarizes large datasets by rows and columns?", ["PivotTable", "Data Validation", "Hyperlink", "Sparkline"], 0,
             "A PivotTable summarizes and analyzes large datasets interactively."),
        ],
        "Statistics": [
            ("What is the median of 2, 4, 7, 9, 12?", ["4", "7", "9", "12"], 1,
             "The median is the middle value in an ordered dataset: 7."),
            ("A correlation of -0.8 indicates:", ["Strong positive relationship", "Strong negative relationship", "No relationship", "Causation"], 1,
             "A value near -1 indicates a strong negative relationship."),
            ("Which value divides a probability distribution into 100 groups?", ["Quartile", "Percentile", "Mean", "Variance"], 1,
             "Percentiles divide observations into 100 equal percentage intervals."),
        ],
        "Web Development": [
            ("Which HTML element represents the main navigation?", ["aside", "nav", "footer", "section"], 1,
             "The nav element contains navigation links."),
            ("Which CSS property controls element text color?", ["font-style", "background", "color", "display"], 2,
             "The CSS color property sets foreground text color."),
            ("Which JavaScript method sends an HTTP request in modern browsers?", ["alert()", "fetch()", "console.log()", "querySelector()"], 1,
             "fetch() is used for network requests in modern JavaScript."),
        ],
        "Git": [
            ("Which command creates a local Git snapshot of staged changes?", ["git add", "git commit", "git clone", "git push"], 1,
             "git commit records staged changes in local repository history."),
            ("Which command displays existing branches?", ["git branch", "git status", "git log", "git merge"], 0,
             "git branch lists, creates, or deletes branches."),
            ("What does git clone do?", ["Deletes a repository", "Copies a remote repository", "Stashes changes", "Creates a tag"], 1,
             "git clone creates a local copy of a remote repository."),
        ],
        "Machine Learning": [
            ("Which task predicts a continuous numeric value?", ["Classification", "Regression", "Clustering", "Tokenization"], 1,
             "Regression models predict continuous numeric outputs."),
            ("Which split helps estimate model performance on unseen data?", ["Training split", "Test split", "Encoding split", "Index split"], 1,
             "A test split evaluates a trained model on data it has not seen."),
            ("Which algorithm learns groups without labeled outputs?", ["Linear regression", "Logistic regression", "K-means clustering", "Decision tree"], 2,
             "K-means is an unsupervised clustering algorithm."),
        ],
    }

    for skill_name, questions in quiz_data.items():
        quiz = Quiz(skill=skills[skill_name], title=f"{skill_name} Skill Quiz")
        db.session.add(quiz)
        db.session.flush()
        for text, options, correct_index, explanation in questions:
            question = Question(quiz_id=quiz.id, text=text, explanation=explanation)
            db.session.add(question)
            db.session.flush()
            for index, option_text in enumerate(options):
                db.session.add(QuestionOption(
                    question_id=question.id,
                    text=option_text,
                    is_correct=(index == correct_index),
                ))

    projects = [
        ("Sales Data Dashboard", "Clean a retail sales dataset and build a dashboard that highlights trends and KPIs.", "Intermediate", "Understand data cleaning, visualization, and business reporting.", "data-analyst", ["SQL", "Excel", "Python"]),
        ("Student Expense Tracker", "Create a small application for recording, categorizing, and reviewing expenses.", "Beginner", "Practice CRUD operations and practical data visualization.", "data-analyst", ["Python", "SQL"]),
        ("Responsive Portfolio Website", "Build an accessible personal portfolio with a project gallery and contact section.", "Beginner", "Apply semantic HTML, responsive CSS, and JavaScript interactions.", "web-developer", ["Web Development", "Git"]),
        ("Task Management API", "Implement an authenticated REST API for organizing tasks and due dates.", "Intermediate", "Learn API design, persistence, validation, and testing.", "python-developer", ["Python", "SQL", "Git"]),
        ("Customer Churn Predictor", "Prepare customer data and compare models that predict customer churn.", "Advanced", "Apply ML evaluation, feature engineering, and model comparison.", "ai-ml-developer", ["Python", "Statistics", "Machine Learning"]),
        ("Department Performance Report", "Analyze departmental metrics and present recommendations for leaders.", "Intermediate", "Improve business communication and evidence-based analysis.", "business-analyst", ["Excel", "SQL", "Statistics"]),
    ]
    for title, description, difficulty, outcome, career_slug, skill_names in projects:
        project = Project(
            title=title, description=description, difficulty=difficulty,
            learning_outcome=outcome, career_slug=career_slug,
        )
        db.session.add(project)
        db.session.flush()
        for skill_name in skill_names:
            db.session.add(ProjectSkill(project_id=project.id, skill_id=skills[skill_name].id))

    db.session.commit()
