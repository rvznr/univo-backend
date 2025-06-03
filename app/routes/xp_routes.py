from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserProgress, QuizResult
from app import db
from sqlalchemy import func, text
import json

xp_bp = Blueprint('xp', __name__, url_prefix='/api')


@xp_bp.route('/user/xp', methods=['GET'])
@jwt_required()
def get_total_xp():
    user_id = get_jwt_identity()

    learn_xp = db.session.query(
        func.coalesce(func.sum(
            UserProgress.xp_from_notes +
            UserProgress.xp_from_exercises +
            func.coalesce(UserProgress.xp_from_feedback, 0)
        ), 0)
    ).filter_by(user_id=user_id).scalar()

    quiz_xp = db.session.query(
        func.coalesce(func.sum(QuizResult.xp), 0)
    ).filter_by(user_id=user_id).scalar()

    total_xp = (learn_xp or 0) + (quiz_xp or 0)

    return jsonify({'total_xp': total_xp}), 200


@xp_bp.route('/user/xp/class', methods=['GET'])
@jwt_required()
def get_class_xp_insights():
    current_user_id = get_jwt_identity()

    learn_xp_sub = db.session.query(
        UserProgress.user_id,
        func.sum(func.coalesce(UserProgress.xp_from_notes, 0) + func.coalesce(UserProgress.xp_from_exercises, 0) + func.coalesce(UserProgress.xp_from_feedback, 0)).label("learn_xp")
    ).group_by(UserProgress.user_id).subquery()

    quiz_xp_sub = db.session.query(
        QuizResult.user_id,
        func.sum(QuizResult.xp).label("quiz_xp")
    ).group_by(QuizResult.user_id).subquery()

    results = db.session.query(
        learn_xp_sub.c.user_id,
        func.coalesce(learn_xp_sub.c.learn_xp, 0) + func.coalesce(quiz_xp_sub.c.quiz_xp, 0)
    ).join(
        quiz_xp_sub, quiz_xp_sub.c.user_id == learn_xp_sub.c.user_id, isouter=True
    ).all()

    data = [{'user_id': r[0], 'total_xp': int(r[1])} for r in results]
    return jsonify({
        'current_user_id': current_user_id,
        'data': data
    }), 200

@xp_bp.route('/user/xp/note', methods=['POST'])
@jwt_required()
def gain_xp_from_note():
    user_id = get_jwt_identity()
    data = request.get_json()
    module_id = data.get('module_id')

    progress = UserProgress.query.filter_by(user_id=user_id, module_id=module_id).first()

    if not progress:
        progress = UserProgress(user_id=user_id, module_id=module_id, xp_from_notes=80, xp_from_exercises=0)
        db.session.add(progress)
    elif progress.xp_from_notes == 0:
        progress.xp_from_notes = 80

    db.session.commit()
    return jsonify({'message': 'XP from note updated.', 'noteXP': 80})

# içinde gain_xp_from_exercise fonksiyonu
@xp_bp.route('/user/xp/exercise', methods=['POST'])
@jwt_required()
def gain_xp_from_exercise():
    user_id = get_jwt_identity()
    data = request.get_json()
    module_id = data.get('module_id')
    gained_xp = data.get('gained_xp', 0)

    max_xp = 0
    try:
        result = db.session.execute(text("""
            SELECT questions FROM exercise WHERE module_id = :mod_id
        """), {"mod_id": module_id}).fetchall()

        for row in result:
            questions = row.questions
            if isinstance(questions, str):
                try:
                    parsed = json.loads(questions)

                    # Nested düzleştirme (örnek: [[{...}]])
                    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], list):
                        parsed = parsed[0]

                    for q in parsed:
                        xp = int(q.get("xp_reward", 15))
                        max_xp += xp
                except Exception as e:
                    print("JSON parse hatası:", e)
                    continue
    except Exception as e:
        print("Veritabanı hatası:", e)

    if gained_xp > max_xp:
        return jsonify({'error': 'Invalid XP submission'}), 400

    progress = UserProgress.query.filter_by(user_id=user_id, module_id=module_id).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            module_id=module_id,
            xp_from_notes=0,
            xp_from_exercises=gained_xp
        )
        db.session.add(progress)
    elif progress.xp_from_exercises < gained_xp:
        progress.xp_from_exercises = gained_xp

    db.session.commit()
    return jsonify({'message': 'XP from exercise updated.', 'exerciseXP': gained_xp})

@xp_bp.route('/user/xp/feedback', methods=['POST'])
@jwt_required()
def gain_xp_from_feedback():
    user_id = get_jwt_identity()

    progress = UserProgress.query.filter_by(user_id=user_id, module_id=None).first()
    if not progress:
        progress = UserProgress(user_id=user_id, module_id=None, xp_from_notes=0, xp_from_exercises=0, xp_from_feedback=160)
        db.session.add(progress)
    elif not progress.xp_from_feedback:
        progress.xp_from_feedback = 160

    db.session.commit()
    return jsonify({'message': 'XP from feedback updated.', 'feedbackXP': 160})

@xp_bp.route('/user/progress/summary', methods=['GET'])
@jwt_required()
def get_module_completion_summary():
    user_id = get_jwt_identity()

    completed_modules = UserProgress.query.filter_by(user_id=user_id)\
        .filter(UserProgress.xp_from_notes > 0, UserProgress.xp_from_exercises > 0).count()

    return jsonify({
        'completed_modules': completed_modules
    }), 200

@xp_bp.route('/user/progress/all', methods=['GET'])
@jwt_required()
def get_all_user_progress():
    all_progress = UserProgress.query.all()
    result = [{
        'user_id': p.user_id,
        'module_id': p.module_id,
        'xp_from_notes': p.xp_from_notes,
        'xp_from_exercises': p.xp_from_exercises,
        'xp_from_feedback': getattr(p, 'xp_from_feedback', 0)
    } for p in all_progress]

    return jsonify(result), 200

@xp_bp.route('/user/progress/mine', methods=['GET'])
@jwt_required()
def get_my_progress():
    user_id = get_jwt_identity()
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    result = [{
        'module_id': p.module_id,
        'xp_from_notes': p.xp_from_notes,
        'xp_from_exercises': p.xp_from_exercises,
        'xp_from_feedback': getattr(p, 'xp_from_feedback', 0)
    } for p in progress]

    return jsonify(result), 200

# Kullanıcının XP detaylarını döner
@xp_bp.route('/user/xp/detail', methods=['GET'])
@jwt_required()
def get_xp_detail():
    user_id = get_jwt_identity()

    notes_xp = db.session.query(
        func.coalesce(func.sum(UserProgress.xp_from_notes), 0)
    ).filter_by(user_id=user_id).scalar()

    exercise_xp = db.session.query(
        func.coalesce(func.sum(UserProgress.xp_from_exercises), 0)
    ).filter_by(user_id=user_id).scalar()

    feedback_xp = db.session.query(
        func.coalesce(func.sum(UserProgress.xp_from_feedback), 0)
    ).filter_by(user_id=user_id).scalar()

    quiz_xp = db.session.query(
        func.coalesce(func.sum(QuizResult.xp), 0)
    ).filter_by(user_id=user_id).scalar()

    learn_xp = (notes_xp or 0) + (exercise_xp or 0) + (feedback_xp or 0)
    total_xp = learn_xp + (quiz_xp or 0)

    return jsonify({
        "notes_xp": notes_xp,
        "exercise_xp": exercise_xp,
        "feedback_xp": feedback_xp,
        "learn_xp": learn_xp,
        "quiz_xp": quiz_xp,
        "total_xp": total_xp
    }), 200
