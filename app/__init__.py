from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(
        __name__,
        static_folder="app/static",
        static_url_path="/static"
    )

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from app.routes.auth_routes import auth_bp
    from app.routes.quiz_routes import quiz_bp
    from app.routes.quizresult_routes import quizresult_bp
    from app.routes.feedback import feedback_bp
    from app.routes.learn_routes import learn_bp
    from app.routes.xp_routes import xp_bp
    from app.routes.useranswer_routes import useranswer_bp
    from app.routes.recommendation_routes import recommendation_bp
    from app.routes.badge_routes import badge_bp
    from app.routes.note_routes import note_bp
    from app.routes.image_routes import image_bp
    from app.routes.exercise_routes import exercise_bp
    from app.routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
    app.register_blueprint(quizresult_bp, url_prefix="/api")
    app.register_blueprint(feedback_bp, url_prefix="/api")
    app.register_blueprint(learn_bp, url_prefix="/api")
    app.register_blueprint(xp_bp, url_prefix="/api")
    app.register_blueprint(useranswer_bp, url_prefix="/api")
    app.register_blueprint(recommendation_bp, url_prefix="/api")
    app.register_blueprint(badge_bp, url_prefix="/api")
    app.register_blueprint(note_bp, url_prefix="/api")
    app.register_blueprint(image_bp)
    app.register_blueprint(exercise_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # ✅ Tabloları otomatik oluştur (eksikse)
    with app.app_context():
        db.create_all()
        print("✅ Veritabanı tabloları oluşturuldu.")
        print("📂 DB yolu:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app
