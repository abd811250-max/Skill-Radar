# SkillRadar

SkillRadar is a full-stack Flask and SQLite student skill intelligence platform.

## Windows PowerShell setup

```powershell
cd "E:\Skill Radar"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

## Database initialization

The SQLite database is created automatically at startup and populated by `seed.py`.
To manually initialize it:

```powershell
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

## Tests

```powershell
python -m pytest -q
```

## Assessment formula

Verified skill level = 40% of the 1–5 self-assessment plus 60% of the quiz
level, where quiz percentage bands are 0–19%, 20–39%, 40–59%, 60–79%,
and 80–100% for levels 1–5. Skills without a quiz remain provisional.
