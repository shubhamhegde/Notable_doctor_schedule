from flask import Flask
from config import Config
from extensions import db
from models import Doctor
from routes import bp as main_bp

def create_sample_doctors():
    doctors = [
        Doctor(first_name="John", last_name="Smith"),
        Doctor(first_name="Michael", last_name="Johnson"),
        Doctor(first_name="Emily", last_name="Williams"),
        Doctor(first_name="Daniel", last_name="Brown"),
        Doctor(first_name="Sarah", last_name="Davis")
    ]
    db.session.add_all(doctors)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)
    
    with app.app_context():
        db.create_all()
        # Create sample doctors when the application starts
        create_sample_doctors()

    return app

def register_extensions(app):
    db.init_app(app)

def register_blueprints(app):
    app.register_blueprint(main_bp)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)
