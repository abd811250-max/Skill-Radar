import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config_object=None):
    app = Flask(__name__)

    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object("config.Config")

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.assessment import assessment_bp
    from app.routes.careers import careers_bp
    from app.routes.roadmap import roadmap_bp
    from app.routes.projects import projects_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(careers_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(projects_bp)

    with app.app_context():
        db.create_all()
        from seed import seed_database
        seed_database()

    return app
