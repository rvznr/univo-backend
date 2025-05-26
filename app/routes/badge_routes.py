from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserProgress, QuizResult
from app import db
from sqlalchemy import func
from flask_cors import cross_origin

badge_bp = Blueprint('badge', __name__)

@badge_bp.route('/user/badges', methods=['GET', 'OPTIONS'])
@jwt_required()
@cross_origin(origin='http://localhost:3000', supports_credentials=True)
def get_user_badges():
    user_id = get_jwt_identity()

    learn_xp = db.session.query(
        func.coalesce(func.sum(UserProgress.xp_from_notes + UserProgress.xp_from_exercises), 0)
    ).filter_by(user_id=user_id).scalar()

    quiz_xp = db.session.query(
        func.coalesce(func.sum(QuizResult.xp), 0)
    ).filter_by(user_id=user_id).scalar()

    total_xp = (learn_xp or 0) + (quiz_xp or 0)

    quiz_count = QuizResult.query.filter_by(user_id=user_id).count()
    completed_modules = UserProgress.query.filter_by(user_id=user_id)\
        .filter(UserProgress.xp_from_notes > 0, UserProgress.xp_from_exercises > 0).count()
    exercises_done = UserProgress.query.filter_by(user_id=user_id)\
        .filter(UserProgress.xp_from_exercises > 0).count()

    badges = []

    if quiz_count >= 1:
        badges.append({"badge_id": 1, "name": "Erstes Quiz gelöst", "imageUrl": "/badges/1.svg"})
    if completed_modules >= 1:
        badges.append({"badge_id": 2, "name": "Erstes Modul abgeschlossen", "imageUrl": "/badges/2.svg"})
    if completed_modules >= 3:
        badges.append({"badge_id": 3, "name": "3 Module abgeschlossen", "imageUrl": "/badges/3.svg"})
    if total_xp >= 500:
        badges.append({"badge_id": 4, "name": "500 XP erreicht", "imageUrl": "/badges/4.svg"})
    if quiz_count >= 5:
        badges.append({"badge_id": 5, "name": "5 Quizze gelöst", "imageUrl": "/badges/5.svg"})
    if quiz_count >= 5 and completed_modules >= 3 and total_xp >= 500:
        badges.append({"badge_id": 8, "name": "Alles abgeschlossen!", "imageUrl": "/badges/8.svg"})

    return jsonify({"badges": badges}), 200
